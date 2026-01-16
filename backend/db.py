from __future__ import annotations

from pathlib import Path
import sqlite3
from urllib.parse import unquote, urlparse

from backend.config import BASE_DIR, Config


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

    with sqlite3.connect(db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                note TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
            );
            """
        )

    return db_path
