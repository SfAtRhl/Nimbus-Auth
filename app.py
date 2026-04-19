import os
from flask import Flask, g, render_template
from auth import auth_bp
from extensions import csrf, limiter
from models import close_db, init_db
from utils import get_user_from_request, set_security_headers

def create_app():
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret"),
        DATABASE_PATH=os.environ.get("DATABASE_PATH", "database.db"),
        JWT_SECRET=os.environ.get("JWT_SECRET", "dev-jwt-secret"),
        JWT_ALG=os.environ.get("JWT_ALG", "HS256"),
        JWT_EXP_MINUTES=int(os.environ.get("JWT_EXP_MINUTES", "30")),
        JWT_REMEMBER_DAYS=int(os.environ.get("JWT_REMEMBER_DAYS", "14")),
        COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "false").lower() == "true",
        SMTP_HOST=os.environ.get("SMTP_HOST", ""),
        SMTP_PORT=int(os.environ.get("SMTP_PORT", "587")),
        SMTP_USERNAME=os.environ.get("SMTP_USERNAME", ""),
        SMTP_PASSWORD=os.environ.get("SMTP_PASSWORD", ""),
        SMTP_USE_TLS=os.environ.get("SMTP_USE_TLS", "true").lower() == "true",
        SMTP_FROM=os.environ.get("SMTP_FROM", "no-reply@example.com"),
        RATE_LIMIT=os.environ.get("RATE_LIMIT", "5 per minute"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        WTF_CSRF_TIME_LIMIT=None,
    )

    csrf.init_app(app)
    limiter.init_app(app)

    app.teardown_appcontext(close_db)

    @app.before_request
    def load_user():
        g.user = get_user_from_request()

    @app.after_request
    def apply_security_headers(response):
        return set_security_headers(response)

    @app.route("/")
    def landing():
        return render_template("landing.html")

    app.register_blueprint(auth_bp)

    with app.app_context():
        init_db()

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=os.environ.get("FLASK_ENV") == "development")
