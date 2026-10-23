"""SQLite connection and query helpers for Retail Pulse."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = ROOT_DIR / "data" / "retail_pulse.db"


def ensure_database_seeded(db_path: Path | None = None) -> Path:
    """Ensure the SQLite database exists; if missing, run the deterministic seeder."""
    target = db_path or DEFAULT_DB_PATH
    if not target.exists():
        from data.seed_retail_data import seed_all
        seed_all()
    return target


def get_db_connection(db_path: Path | None = None) -> sqlite3.Connection:
    """Return a SQLite connection configured with sqlite3.Row factory."""
    target = ensure_database_seeded(db_path)
    conn = sqlite3.connect(str(target))
    conn.row_factory = sqlite3.Row
    return conn


def fetch_all(query: str, params: tuple[Any, ...] = (), db_path: Path | None = None) -> list[dict[str, Any]]:
    """Execute a read query and return all rows as dictionaries."""
    with get_db_connection(db_path) as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]


def fetch_one(query: str, params: tuple[Any, ...] = (), db_path: Path | None = None) -> dict[str, Any] | None:
    """Execute a read query and return a single row dictionary or None."""
    with get_db_connection(db_path) as conn:
        row = conn.execute(query, params).fetchone()
        return dict(row) if row is not None else None


def execute_write(query: str, params: tuple[Any, ...] = (), db_path: Path | None = None) -> int:
    """Execute an INSERT/UPDATE/DELETE statement and return affected row count."""
    with get_db_connection(db_path) as conn:
        cur = conn.execute(query, params)
        conn.commit()
        return cur.rowcount
