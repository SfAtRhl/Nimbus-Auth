import os
import logging
from dotenv import load_dotenv
from flask import Flask, current_app, g, render_template, request
from auth import auth_bp
from api import api_bp
from extensions import csrf, limiter
from models import close_db, init_db
from utils import get_user_from_request, set_security_headers
from translations import DEFAULT_LANG, TRANSLATIONS

def create_app():
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
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
        RATE_LIMIT=os.environ.get("RATE_LIMIT", "100 per minute"),
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
        requested_lang = request.args.get("lang")
        if requested_lang in TRANSLATIONS:
            g.lang = requested_lang
            g.set_lang_cookie = requested_lang
        else:
            g.lang = request.cookies.get("lang", DEFAULT_LANG)
            if g.lang not in TRANSLATIONS:
                g.lang = DEFAULT_LANG
        g.dir = "rtl" if g.lang == "ar" else "ltr"

    @app.after_request
    def apply_security_headers(response):
        lang_cookie = getattr(g, "set_lang_cookie", None)
        if lang_cookie:
            response.set_cookie("lang", lang_cookie, samesite="Lax")
        return set_security_headers(response)

    @app.context_processor
    def inject_translations():
        def t(key, **kwargs):
            bundle = TRANSLATIONS.get(getattr(g, "lang", DEFAULT_LANG), TRANSLATIONS[DEFAULT_LANG])
            text = bundle.get(key)
            if text is None:
                text = TRANSLATIONS[DEFAULT_LANG].get(key, key)
                if text == key:
                    current_app.logger.warning(
                        "Missing translation for key: %s (lang=%s)",
                        key,
                        getattr(g, "lang", DEFAULT_LANG),
                    )
            if kwargs:
                try:
                    return text.format(**kwargs)
                except (KeyError, ValueError):
                    return text
            return text

        return {
            "t": t,
            "current_lang": getattr(g, "lang", DEFAULT_LANG),
            "text_dir": getattr(g, "dir", "ltr"),
        }

    @app.route("/")
    def landing():
        return render_template("landing.html")

    @app.errorhandler(404)
    def not_found(error):
        return render_template("error-404.html"), 404

    @app.errorhandler(429)
    def too_many_requests(error):
        return render_template("error-429.html"), 429

    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    app.logger.setLevel(logging.INFO)

    with app.app_context():
        init_db()

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=os.environ.get("FLASK_ENV") == "development")
