import sqlite3
from datetime import datetime, timezone
from flask import current_app, g


def now():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def connect(path):
    connection = sqlite3.connect(path, timeout=3)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 3000")
    return connection


def get_db():
    if "db" not in g:
        g.db = connect(current_app.config["DATABASE_PATH"])
    return g.db


def close_db(error=None):
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()
