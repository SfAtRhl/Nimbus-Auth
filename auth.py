import secrets
from datetime import datetime, timedelta, timezone
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_limiter.util import get_remote_address
from decorators import guest_required
from extensions import limiter
from forms import ForgotPasswordForm, LoginForm, RegisterForm, ResetPasswordForm
from models import (
    create_password_reset,
    create_user,
    delete_password_reset,
    get_password_reset,
    get_user_by_email,
    set_last_login,
    update_user_password,
)
from utils import create_jwt, hash_password, login_required, password_strength, send_reset_email, send_welcome_email, verify_password

auth_bp = Blueprint("auth", __name__)

def login_limit_key():
    email = request.form.get("email", "").lower()
    return f"{get_remote_address()}:{email}"

@auth_bp.route("/register", methods=["GET", "POST"])
@guest_required
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        password_hash = hash_password(form.password.data)
        create_user(form.full_name.data.strip(), form.email.data.lower(), password_hash)
        send_welcome_email(form.email.data.lower(), form.full_name.data.strip())
        flash("Account created. Please log in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("register.html", form=form)

@auth_bp.route("/login", methods=["GET", "POST"])
@guest_required
@limiter.limit(lambda: current_app.config["RATE_LIMIT"], key_func=login_limit_key)
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = get_user_by_email(form.email.data.lower())
        if not user or not verify_password(form.password.data, user["password_hash"]):
            flash("Invalid email or password.", "error")
            return render_template("login.html", form=form)
        token = create_jwt(user, remember=form.remember.data)
        set_last_login(user["id"])
        response = redirect(url_for("auth.dashboard"))
        max_age = None
        if form.remember.data:
            max_age = int(timedelta(days=current_app.config["JWT_REMEMBER_DAYS"]).total_seconds())
        response.set_cookie(
            "auth_token",
            token,
            httponly=True,
            secure=current_app.config["COOKIE_SECURE"],
            samesite="Lax",
            max_age=max_age,
        )
        return response
    return render_template("login.html", form=form)

@auth_bp.route("/forgot-password", methods=["GET", "POST"])
@guest_required
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = get_user_by_email(form.email.data.lower())
        if user:
            token = secrets.token_urlsafe(32)
            expires_at = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
            create_password_reset(user["email"], token, expires_at)
            reset_url = url_for("auth.reset_password", token=token, _external=True)
            send_reset_email(user["email"], reset_url)
        flash("If that email exists, a reset link was sent.", "success")
        return redirect(url_for("auth.login"))
    return render_template("forgot-password.html", form=form)

@auth_bp.route("/reset/<token>", methods=["GET", "POST"])
def reset_password(token):
    form = ResetPasswordForm()
    record = get_password_reset(token)
    if not record:
        flash("Reset token is invalid or expired.", "error")
        return redirect(url_for("auth.forgot_password"))
    expires_at = datetime.fromisoformat(record["expires_at"])
    if expires_at < datetime.now(timezone.utc):
        delete_password_reset(token)
        flash("Reset token has expired.", "error")
        return redirect(url_for("auth.forgot_password"))
    if form.validate_on_submit():
        password_hash = hash_password(form.password.data)
        update_user_password(record["email"], password_hash)
        delete_password_reset(token)
        flash("Password reset successful. Please log in.", "success")
        return redirect(url_for("auth.login"))
    score, label = password_strength(form.password.data or "")
    return render_template("reset-password.html", form=form, score=score, label=label)

@auth_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@auth_bp.route("/logout")
def logout():
    response = redirect(url_for("auth.login"))
    response.delete_cookie("auth_token")
    flash("You have been logged out.", "success")
    return response
