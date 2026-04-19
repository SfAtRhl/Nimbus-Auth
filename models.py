import sqlite3
from datetime import datetime, timezone
from flask import current_app, g

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE_PATH"])
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(_exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        );
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS password_resets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            token TEXT NOT NULL,
            expires_at TIMESTAMP
        );
        """
    )
    db.commit()

def get_user_by_email(email):
    db = get_db()
    return db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

def get_user_by_id(user_id):
    db = get_db()
    return db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

def create_user(full_name, email, password_hash):
    db = get_db()
    db.execute(
        "INSERT INTO users (full_name, email, password_hash) VALUES (?, ?, ?)",
        (full_name, email, password_hash),
    )
    db.commit()

def update_user_password(email, password_hash):
    db = get_db()
    db.execute(
        "UPDATE users SET password_hash = ? WHERE email = ?",
        (password_hash, email),
    )
    db.commit()

def set_last_login(user_id):
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()
    db.execute("UPDATE users SET last_login = ? WHERE id = ?", (now, user_id))
    db.commit()

def create_password_reset(email, token, expires_at):
    db = get_db()
    db.execute(
        "INSERT INTO password_resets (email, token, expires_at) VALUES (?, ?, ?)",
        (email, token, expires_at),
    )
    db.commit()

def get_password_reset(token):
    db = get_db()
    return db.execute(
        "SELECT * FROM password_resets WHERE token = ?", (token,)
    ).fetchone()

def delete_password_reset(token):
    db = get_db()
    db.execute("DELETE FROM password_resets WHERE token = ?", (token,))
    db.commit()
