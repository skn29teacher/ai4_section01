import math
import re
import secrets
import time

from flask import Blueprint, jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from ..auth import current_user, csrf_token, fail, require_admin, require_login
from ..db import get_db, now
from ..services.masking import mask_text

api = Blueprint("api", __name__, url_prefix="/api")


def payload():
    value = request.get_json(silent=True)
    if not isinstance(value, dict):
        fail(422, "JSON 객체 형식으로 입력하세요.")
    return value


def field(data, key, label, maximum, minimum=1, strip=True):
    value = data.get(key)
    if not isinstance(value, str):
        fail(422, f"{label}을(를) 입력하세요.")
    value = value.strip() if strip else value
    if not value.strip() or not minimum <= len(value) <= maximum:
        fail(422, f"{label}은(는) {minimum}~{maximum}자로 입력하세요.")
    return value


def email_value(data):
    email = field(data, "email", "이메일", 254).lower()
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        fail(422, "올바른 이메일 주소를 입력하세요.")
    return email


def public_user(user):
    return {key: user[key] for key in ("id", "email", "nickname", "role")} if user else None


def rules():
    return [r[0] for r in get_db().execute("SELECT expression FROM mask_rules ORDER BY id")]


def post_or_404(post_id, owner=False):
    post = get_db().execute("SELECT * FROM posts WHERE id=?", (post_id,)).fetchone()
    if post is None:
        fail(404, "존재하지 않거나 삭제된 게시글입니다.")
    if owner and post["author_id"] != current_user()["id"]:
        fail(403, "작성자 본인만 변경하거나 원문을 조회할 수 있습니다.")
    return dict(post)


@api.get("/auth/me")
def me():
    return jsonify(user=public_user(current_user()), csrf_token=csrf_token())


@api.post("/auth/signup")
def signup():
    data = payload()
    email = email_value(data)
    nickname = field(data, "nickname", "닉네임", 50)
    password = field(data, "password", "비밀번호", 128, 8, strip=False)
    db = get_db()
    if db.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone():
        fail(409, "이미 가입된 이메일입니다.")
    with db:
        db.execute("INSERT INTO users(email,nickname,password_hash,role,created_at) VALUES(?,?,?,'USER',?)", (email, nickname, generate_password_hash(password), now()))
    return jsonify(message="회원가입이 완료되었습니다. 로그인하세요."), 201


@api.post("/auth/login")
def login():
    data = payload()
    email = email_value(data)
    password = field(data, "password", "비밀번호", 128, strip=False)
    row = get_db().execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    if not row or not check_password_hash(row["password_hash"], password):
        fail(401, "이메일 또는 비밀번호를 확인하세요.")
    session.clear()
    session.permanent = True
    session.update(user_id=row["id"], session_version=row["session_version"], issued_at=time.time(), csrf_token=secrets.token_urlsafe(32))
    return jsonify(user=public_user(row), csrf_token=csrf_token())


@api.post("/auth/logout")
@require_login
def logout():
    db = get_db()
    with db:
        db.execute("UPDATE users SET session_version=session_version+1 WHERE id=?", (current_user()["id"],))
    session.clear()
    return jsonify(message="로그아웃했습니다. 같은 계정의 다른 기기도 로그아웃됩니다.")


@api.post("/auth/forgot-password")
def forgot():
    email_value(payload())
    return jsonify(message="데모 기능입니다. 실제 메일은 발송되지 않으며 비밀번호도 변경되지 않습니다.")


@api.get("/posts")
def posts():
    db = get_db()
    total = db.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
    pages = max(1, math.ceil(total / 10))
    try:
        page = int(request.args.get("page", "1"))
    except ValueError:
        page = 1
    page = max(1, min(page, pages))
    rows = db.execute("SELECT id,title,author_id FROM posts ORDER BY created_at DESC,id DESC LIMIT 10 OFFSET ?", ((page - 1) * 10,)).fetchall()
    expressions = rules()
    user = current_user()
    return jsonify(items=[dict(id=r["id"], title=mask_text(r["title"], expressions), is_mine=bool(user and user["id"] == r["author_id"])) for r in rows], page=page, pages=pages, total=total, page_size=10)


@api.post("/posts")
@require_login
def create_post():
    data = payload()
    title = field(data, "title", "제목", 200)
    content = field(data, "content", "내용", 10000)
    db = get_db()
    timestamp = now()
    with db:
        cursor = db.execute("INSERT INTO posts(author_id,title,content,created_at,updated_at) VALUES(?,?,?,?,?)", (current_user()["id"], title, content, timestamp, timestamp))
    return jsonify(id=cursor.lastrowid), 201


@api.get("/posts/<int:post_id>")
def detail(post_id):
    post = post_or_404(post_id)
    expressions = rules()
    for key in ("title", "content"):
        post[key] = mask_text(post[key], expressions)
    post["can_edit"] = bool(current_user() and current_user()["id"] == post["author_id"])
    return jsonify(post=post)


@api.get("/posts/<int:post_id>/edit")
@require_login
def edit_post(post_id):
    return jsonify(post=post_or_404(post_id, owner=True))


@api.patch("/posts/<int:post_id>")
@require_login
def update_post(post_id):
    post_or_404(post_id, owner=True)
    data = payload()
    title, content = field(data, "title", "제목", 200), field(data, "content", "내용", 10000)
    db = get_db()
    with db:
        db.execute("UPDATE posts SET title=?,content=?,updated_at=? WHERE id=?", (title, content, now(), post_id))
    return jsonify(message="수정했습니다.")


@api.delete("/posts/<int:post_id>")
@require_login
def delete_post(post_id):
    post_or_404(post_id, owner=True)
    db = get_db()
    with db:
        db.execute("DELETE FROM posts WHERE id=?", (post_id,))
    return jsonify(message="삭제했습니다.")


@api.get("/posts/<int:post_id>/comments")
def comments(post_id):
    post_or_404(post_id)
    expressions = rules()
    rows = get_db().execute("SELECT c.id,c.author_id,c.content,c.created_at,u.nickname FROM comments c JOIN users u ON u.id=c.author_id WHERE c.post_id=? ORDER BY c.created_at,c.id", (post_id,)).fetchall()
    user = current_user()
    return jsonify(items=[dict(id=r["id"], content=mask_text(r["content"], expressions), nickname=r["nickname"], created_at=r["created_at"], is_mine=bool(user and user["id"] == r["author_id"])) for r in rows])


@api.post("/posts/<int:post_id>/comments")
@require_login
def create_comment(post_id):
    post_or_404(post_id)
    content = field(payload(), "content", "댓글", 2000)
    db = get_db()
    with db:
        cursor = db.execute("INSERT INTO comments(post_id,author_id,content,created_at) VALUES(?,?,?,?)", (post_id, current_user()["id"], content, now()))
    return jsonify(id=cursor.lastrowid), 201


@api.get("/admin/mask-rules")
@require_admin
def list_rules():
    rows = get_db().execute("SELECT * FROM mask_rules ORDER BY id DESC").fetchall()
    return jsonify(items=[dict(r) for r in rows])


@api.post("/admin/mask-rules")
@require_admin
def create_rule():
    data = payload()
    if data.get("rule_type", "KEYWORD") != "KEYWORD":
        fail(422, "키워드 규칙만 지원합니다.")
    expression = field(data, "expression", "표현", 255).lower()
    db = get_db()
    if db.execute("SELECT 1 FROM mask_rules WHERE rule_type='KEYWORD' AND expression=?", (expression,)).fetchone():
        fail(409, "이미 등록된 표현입니다.")
    with db:
        cursor = db.execute("INSERT INTO mask_rules(rule_type,expression,created_at) VALUES('KEYWORD',?,?)", (expression, now()))
    return jsonify(id=cursor.lastrowid), 201


@api.delete("/admin/mask-rules/<int:rule_id>")
@require_admin
def delete_rule(rule_id):
    db = get_db()
    with db:
        cursor = db.execute("DELETE FROM mask_rules WHERE id=?", (rule_id,))
        if not cursor.rowcount:
            fail(404, "존재하지 않는 규칙입니다.")
    return jsonify(message="규칙을 삭제했습니다. 기존 글의 원문 표현이 다시 표시될 수 있습니다.")
