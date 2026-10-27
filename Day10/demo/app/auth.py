import secrets
import time
from functools import wraps
from urllib.parse import urlsplit

from flask import g, request, session
from .db import get_db


def fail(status, message):
    error = abort_exception(status, message)
    raise error


def abort_exception(status, message):
    from werkzeug.exceptions import default_exceptions
    error = default_exceptions[status](description=message)
    error.custom_message = True
    return error


def current_user():
    if "user" not in g:
        g.user = None
        uid = session.get("user_id")
        if uid is not None:
            issued = session.get("issued_at", 0)
            if not isinstance(issued, (int, float)) or not 0 <= time.time() - issued < 28800:
                session.clear()
                return None
            row = get_db().execute("SELECT id, email, nickname, role, session_version FROM users WHERE id=?", (uid,)).fetchone()
            if row and row["session_version"] == session.get("session_version"):
                g.user = dict(row)
            else:
                session.clear()
    return g.user


def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    return session["csrf_token"]


def protect_request():
    if not request.path.startswith("/api/"):
        return
    current_user()
    if request.method not in ("GET", "HEAD", "OPTIONS"):
        origin = request.headers.get("Origin")
        if origin and urlsplit(origin).netloc != request.host:
            fail(403, "다른 출처의 요청은 허용하지 않습니다.")
        expected, actual = session.get("csrf_token"), request.headers.get("X-CSRF-Token", "")
        if not expected or not secrets.compare_digest(expected.encode("utf-8"), actual.encode("utf-8")):
            fail(403, "요청 확인이 만료되었습니다. 화면을 새로고침하세요.")


def require_login(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not current_user():
            fail(401, "로그인이 필요합니다.")
        return fn(*args, **kwargs)
    return wrapped


def require_admin(fn):
    @wraps(fn)
    @require_login
    def wrapped(*args, **kwargs):
        if current_user()["role"] != "ADMIN":
            fail(403, "관리자만 이용할 수 있습니다.")
        return fn(*args, **kwargs)
    return wrapped
