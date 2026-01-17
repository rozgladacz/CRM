from __future__ import annotations

from pathlib import Path
from urllib.parse import unquote, urlparse

from flask import Flask

from backend.config import BASE_DIR, Config
from backend.models import db


def _resolve_sqlite_path(database_url: str | None = None) -> Path:
    url = database_url or Config.SQLALCHEMY_DATABASE_URI
    parsed = urlparse(url)
    if parsed.scheme != "sqlite":
        raise ValueError("Only sqlite databases are supported for initialization.")

    raw_path = unquote(parsed.path)
    if not raw_path:
        raise ValueError("SQLite database path is missing.")

    db_path = Path(raw_path)
    if not db_path.is_absolute():
        db_path = BASE_DIR / db_path

    return db_path


def init_db(database_url: str | None = None) -> Path:
    """Initialize the SQLite database and create required tables."""
    db_path = _resolve_sqlite_path(database_url)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    app = Flask(__name__)
    app.config.from_object(Config)
    if database_url:
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    db.init_app(app)

    with app.app_context():
        db.create_all()

    return db_path
