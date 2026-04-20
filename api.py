import secrets
from datetime import datetime, timedelta, timezone
from flask import Blueprint, current_app, jsonify, make_response, request
from extensions import csrf, limiter
from models import (
    create_password_reset,
    create_user,
    delete_password_reset,
    get_password_reset,
    get_user_by_email,
    set_last_login,
    update_user_password,
)
from utils import (
    api_login_required,
    create_jwt,
    hash_password,
    send_reset_email,
    send_welcome_email,
    validate_password_policy,
    verify_password,
)

api_bp = Blueprint("api", __name__, url_prefix="/api")
csrf.exempt(api_bp)

def serialize_user(user):
    return {
        "id": user["id"],
        "full_name": user["full_name"],
        "email": user["email"],
        "created_at": user["created_at"],
        "last_login": user["last_login"],
    }

def login_limit_key():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").lower()
    return f"{request.remote_addr}:{email}"

@api_bp.post("/auth/register")
def api_register():
    payload = request.get_json(silent=True) or {}
    full_name = (payload.get("full_name") or "").strip()
    email = (payload.get("email") or "").lower().strip()
    password = payload.get("password") or ""
    confirm_password = payload.get("confirm_password") or ""
    remember = bool(payload.get("remember"))

    if not full_name or not email or not password:
        return jsonify({"error": "Full name, email, and password are required."}), 400

    if confirm_password and password != confirm_password:
        return jsonify({"error": "Passwords do not match."}), 400

    if get_user_by_email(email):
        return jsonify({"error": "An account with this email already exists."}), 409

    policy_errors = validate_password_policy(password)
    if policy_errors:
        return jsonify({"error": " ".join(policy_errors)}), 400

    create_user(full_name, email, hash_password(password))
    user = get_user_by_email(email)
    send_welcome_email(email, full_name)
    token = create_jwt(user, remember=remember)
    return jsonify({"token": token, "user": serialize_user(user)}), 201

@api_bp.post("/auth/login")
@limiter.limit(lambda: current_app.config["RATE_LIMIT"], key_func=login_limit_key)
def api_login():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").lower().strip()
    password = payload.get("password") or ""
    remember = bool(payload.get("remember"))

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    user = get_user_by_email(email)
    if not user or not verify_password(password, user["password_hash"]):
        return jsonify({"error": "Invalid email or password."}), 401

    token = create_jwt(user, remember=remember)
    set_last_login(user["id"])
    return jsonify({"token": token, "user": serialize_user(user)}), 200

@api_bp.post("/auth/logout")
def api_logout():
    response = make_response("", 204)
    response.delete_cookie("auth_token")
    return response

@api_bp.get("/me")
@api_login_required
def api_me():
    from flask import g

    return jsonify({"user": serialize_user(g.user)}), 200

@api_bp.post("/auth/forgot-password")
def api_forgot_password():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").lower().strip()
    if not email:
        return jsonify({"error": "Email is required."}), 400

    user = get_user_by_email(email)
    if user:
        token = secrets.token_urlsafe(32)
        expires_at = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
        create_password_reset(email, token, expires_at)
        reset_url = f"{request.host_url.rstrip('/')}/reset/{token}"
        send_reset_email(email, reset_url)
    return jsonify({"message": "If that email exists, a reset link was sent."}), 200

@api_bp.post("/auth/reset-password")
def api_reset_password():
    payload = request.get_json(silent=True) or {}
    token = payload.get("token") or ""
    password = payload.get("password") or ""
    confirm_password = payload.get("confirm_password") or ""

    if not token or not password:
        return jsonify({"error": "Token and password are required."}), 400

    record = get_password_reset(token)
    if not record:
        return jsonify({"error": "Reset token is invalid or expired."}), 400

    expires_at = datetime.fromisoformat(record["expires_at"])
    if expires_at < datetime.now(timezone.utc):
        delete_password_reset(token)
        return jsonify({"error": "Reset token has expired."}), 400

    if confirm_password and password != confirm_password:
        return jsonify({"error": "Passwords do not match."}), 400

    policy_errors = validate_password_policy(password)
    if policy_errors:
        return jsonify({"error": " ".join(policy_errors)}), 400

    update_user_password(record["email"], hash_password(password))
    delete_password_reset(token)
    return jsonify({"message": "Password reset successful."}), 200
