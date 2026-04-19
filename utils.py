import bcrypt
import jwt
import re
import smtplib
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from functools import wraps
from flask import current_app, g, redirect, request, url_for
from models import get_user_by_id

PASSWORD_RULES = [
    (r"[A-Z]", "Add at least one uppercase letter"),
    (r"[a-z]", "Add at least one lowercase letter"),
    (r"[0-9]", "Add at least one number"),
    (r"[^A-Za-z0-9]", "Add at least one symbol"),
]

def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(password, password_hash):
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

def password_strength(password):
    score = 0
    if len(password) >= 8:
        score += 1
    for pattern, _message in PASSWORD_RULES:
        if re.search(pattern, password or ""):
            score += 1
    if score <= 2:
        label = "Weak"
    elif score <= 4:
        label = "Medium"
    else:
        label = "Strong"
    return score, label

def validate_password_policy(password):
    errors = []
    if len(password or "") < 8:
        errors.append("Use at least 8 characters")
    for pattern, message in PASSWORD_RULES:
        if not re.search(pattern, password or ""):
            errors.append(message)
    return errors

def create_jwt(user, remember=False):
    now = datetime.now(timezone.utc)
    exp_minutes = current_app.config["JWT_EXP_MINUTES"]
    if remember:
        exp = now + timedelta(days=current_app.config["JWT_REMEMBER_DAYS"])
    else:
        exp = now + timedelta(minutes=exp_minutes)
    payload = {
        "sub": user["id"],
        "email": user["email"],
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    token = jwt.encode(payload, current_app.config["JWT_SECRET"], algorithm=current_app.config["JWT_ALG"])
    return token

def decode_jwt(token):
    return jwt.decode(token, current_app.config["JWT_SECRET"], algorithms=[current_app.config["JWT_ALG"]])

def get_token_from_request():
    auth_header = request.headers.get("Authorization", "")
    if auth_header.lower().startswith("bearer "):
        return auth_header.split(" ", 1)[1].strip()
    return request.cookies.get("auth_token")

def get_user_from_request():
    token = get_token_from_request()
    if not token:
        return None
    try:
        payload = decode_jwt(token)
    except jwt.PyJWTError:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    user = get_user_by_id(user_id)
    if not user:
        return None
    user_data = dict(user)
    last_login = user_data.get("last_login")
    if last_login:
        try:
            user_data["last_login"] = datetime.fromisoformat(last_login)
        except ValueError:
            pass
    return user_data

def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if g.get("user") is None:
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)
    return wrapper

def api_login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if g.get("user") is None:
            return {"error": "Unauthorized"}, 401
        return view_func(*args, **kwargs)
    return wrapper

def set_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response

def send_reset_email(to_email, reset_url):
    msg = EmailMessage()
    msg["Subject"] = "Reset your password"
    msg["From"] = current_app.config["SMTP_FROM"]
    msg["To"] = to_email
    text_body = (
        "Hello,\n\n"
        "We received a request to reset your password.\n"
        f"Use the link below to reset your password:\n{reset_url}\n\n"
        "This link expires in 2 hours. If you did not request this, you can ignore this email."
    )
    html_body = f"""
    <div style="background-color:#f8fafc;padding:32px;font-family:Arial,Helvetica,sans-serif;">
      <table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="max-width:560px;margin:0 auto;background-color:#ffffff;border-radius:20px;border:1px solid #e2e8f0;overflow:hidden;">
        <tr>
          <td style="padding:28px 32px;background:linear-gradient(135deg,#0f172a,#1e293b);color:#ffffff;">
            <h1 style="margin:0;font-size:20px;letter-spacing:0.08em;text-transform:uppercase;">Nimbus Security</h1>
            <p style="margin:8px 0 0;font-size:14px;color:#e2e8f0;">Password reset request</p>
          </td>
        </tr>
        <tr>
          <td style="padding:28px 32px;color:#0f172a;">
            <h2 style="margin:0 0 12px;font-size:22px;">Reset your password</h2>
            <p style="margin:0 0 16px;font-size:15px;line-height:1.6;color:#475569;">
              We received a request to reset your password. Click the button below to set a new one.
              This link expires in 2 hours.
            </p>
            <a href="{reset_url}" style="display:inline-block;padding:12px 20px;background-color:#0f172a;color:#ffffff;text-decoration:none;border-radius:999px;font-size:14px;font-weight:600;">Reset password</a>
            <p style="margin:20px 0 0;font-size:12px;line-height:1.6;color:#94a3b8;">
              If the button does not work, copy and paste this link into your browser:<br />
              <span style="color:#0f172a;">{reset_url}</span>
            </p>
          </td>
        </tr>
        <tr>
          <td style="padding:20px 32px;background-color:#f1f5f9;color:#64748b;font-size:12px;">
            If you did not request this password reset, you can safely ignore this email.
          </td>
        </tr>
      </table>
    </div>
    """
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")
    host = current_app.config["SMTP_HOST"]
    port = current_app.config["SMTP_PORT"]
    username = current_app.config["SMTP_USERNAME"]
    password = current_app.config["SMTP_PASSWORD"]
    use_tls = current_app.config["SMTP_USE_TLS"]

    if not host:
        current_app.logger.warning("SMTP_HOST not configured; skipping reset email.")
        return

    try:
        with smtplib.SMTP(host, port, timeout=10) as server:
            server.ehlo()
            if use_tls:
                server.starttls()
                server.ehlo()
            if username:
                server.login(username, password)
            server.send_message(msg)
    except (smtplib.SMTPException, OSError) as exc:
        current_app.logger.error("Failed to send reset email: %s", exc)
