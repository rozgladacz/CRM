from __future__ import annotations

from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """Base configuration for the CRM backend."""

    PORT = int(os.getenv("PORT", "5000"))

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'crm.sqlite3'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SMTP settings
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.example.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "noreply@example.com")

    # Security settings
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    REMEMBER_COOKIE_SECURE = os.getenv("REMEMBER_COOKIE_SECURE", "false").lower() == "true"
    PREFERRED_URL_SCHEME = os.getenv("PREFERRED_URL_SCHEME", "https")
