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

def get_user_from_request():
    token = request.cookies.get("auth_token")
    if not token:
        return None
    try:
        payload = decode_jwt(token)
    except jwt.PyJWTError:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    return get_user_by_id(user_id)

def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if g.get("user") is None:
            return redirect(url_for("auth.login"))
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
    msg.set_content(
        f"Hello,\n\nUse the link below to reset your password:\n{reset_url}\n\nIf you did not request this, you can ignore this email."
    )

    host = current_app.config["SMTP_HOST"]
    port = current_app.config["SMTP_PORT"]
    username = current_app.config["SMTP_USERNAME"]
    password = current_app.config["SMTP_PASSWORD"]
    use_tls = current_app.config["SMTP_USE_TLS"]

    with smtplib.SMTP(host, port) as server:
        server.ehlo()
        if use_tls:
            server.starttls()
        if username:
            server.login(username, password)
        server.send_message(msg)
