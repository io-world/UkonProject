"""Thin Postgres helpers (psycopg 3)."""
from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from .config import DATABASE_URL


@contextmanager
def connect():
    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    try:
        with conn.cursor() as cur:
            cur.execute("SET search_path TO ukon")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def j(value):
    """Wrap a Python value for a JSONB column."""
    return Jsonb(value)


def user_id(conn, name):
    row = conn.execute("SELECT id FROM users WHERE name = %s", (name,)).fetchone()
    if not row:
        raise ValueError(f"unknown user {name!r}")
    return row["id"]


def client_by_slug(conn, slug):
    row = conn.execute("SELECT * FROM clients WHERE slug = %s", (slug,)).fetchone()
    if not row:
        raise ValueError(f"unknown client {slug!r}")
    return row
