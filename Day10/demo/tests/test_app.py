import importlib
import json
import sqlite3
import sys
import time

import pytest

from app import create_app
from app.db import get_db, now
from app.services.masking import mask_text
from scripts.backup_db import backup
from scripts.init_db import initialize, DEMO_PASSWORD
from conftest import login, mutate


def test_signup_normalization_hash_and_role(client, app):
    result = mutate(client, "/api/auth/signup", data=dict(email=" NEW@Example.COM ", nickname=" 새 사용자 ", password="NewPassword123!", role="ADMIN"))
    assert result.status_code == 201
    assert mutate(client, "/api/auth/login", data=dict(email="new@example.com", password="NewPassword123!")).status_code == 200
    me = client.get("/api/auth/me").json["user"]
    assert me["role"] == "USER" and me["nickname"] == "새 사용자"
    assert "password" not in json.dumps(me)
    with app.app_context():
        row = get_db().execute("SELECT password_hash FROM users WHERE email='new@example.com'").fetchone()
        assert row[0] != "NewPassword123!"


@pytest.mark.parametrize("data", [{}, {"email":"bad", "nickname":"x", "password":"Password123"},
    {"email":"new@example.com", "nickname":" ", "password":"Password123"},
    {"email":"new@example.com", "nickname":"x", "password":"short"},
    {"email":"new@example.com", "nickname":"x"*51, "password":"Password123"}])
def test_signup_validation(client, data):
    assert mutate(client, "/api/auth/signup", data=data).status_code == 422


def test_duplicate_signup(client):
    assert mutate(client, "/api/auth/signup", data=dict(email="USER1@example.com", nickname="x", password="Password123")).status_code == 409


def test_login_wrong_password(client):
    assert mutate(client, "/api/auth/login", data=dict(email="user1@example.com", password="wrong")).status_code == 401


def test_csrf_and_origin(client):
    assert client.post("/api/auth/login", json={}).status_code == 403
    token = client.get("/api/auth/me").json["csrf_token"]
    assert client.post("/api/auth/login", json={}, headers={"X-CSRF-Token":"한글"}).status_code == 403
    assert client.post("/api/auth/login", json={}, headers={"X-CSRF-Token":token,"Origin":"https://evil.example"}).status_code == 403


def test_reload_and_logout_replay(app, client):
    assert login(client).status_code == 200
    cookie = client.get_cookie("session").value
    new_app = create_app(dict(app.config))
    second = new_app.test_client()
    second.set_cookie("session", cookie)
    assert second.get("/api/auth/me").json["user"]["id"] == 2
    assert mutate(client, "/api/auth/logout").status_code == 200
    second.set_cookie("session", cookie)
    assert second.get("/api/auth/me").json["user"] is None
    assert mutate(second, "/api/posts", data=dict(title="x",content="y")).status_code == 401


def test_expired_session(client):
    login(client)
    with client.session_transaction() as session:
        session["issued_at"] = time.time() - 28801
    assert client.get("/api/auth/me").json["user"] is None


def test_forgot_is_mock(client, app):
    with app.app_context():
        before = get_db().execute("SELECT password_hash FROM users WHERE id=2").fetchone()[0]
    result = mutate(client, "/api/auth/forgot-password", data={"email":"user1@example.com"})
    assert result.status_code == 200 and "발송되지" in result.json["message"]
    with app.app_context():
        assert before == get_db().execute("SELECT password_hash FROM users WHERE id=2").fetchone()[0]
    assert mutate(client, "/api/auth/forgot-password", data={"email":"wrong"}).status_code == 422


@pytest.mark.parametrize("count,lengths", [(0,[0]), (1,[1]), (10,[10]), (11,[10,1]), (21,[10,10,1])])
def test_pagination_boundaries(app, client, count, lengths):
    with app.app_context():
        db=get_db()
        with db:
            db.execute("DELETE FROM posts WHERE id>?", (count,))
    seen=[]
    for page, length in enumerate(lengths, 1):
        result=client.get(f"/api/posts?page={page}").json
        assert result["page_size"] == 10 and len(result["items"]) == length
        assert result["total"] == count and result["pages"] == len(lengths)
        assert all(set(p)=={"id","title","is_mine"} and p["is_mine"] is False for p in result["items"])
        seen.extend(p["id"] for p in result["items"])
    assert seen == list(range(count,0,-1))


@pytest.mark.parametrize("email,owner_id", [(None,None),("user1@example.com",2),("user2@example.com",3),("admin@example.com",1)])
def test_list_ownership_uses_current_session(app,client,email,owner_id):
    with app.app_context():
        db=get_db()
        with db:
            for author in (1,3):
                db.execute("INSERT INTO posts(author_id,title,content,created_at,updated_at) VALUES(?,?,?,?,?)", (author,"다른 작성자의 글","내용",now(),now()))
        authors=dict(db.execute("SELECT id,author_id FROM posts").fetchall())
    if email:
        assert login(client,email).status_code==200
    # A query parameter must not let visitors impersonate another author.
    items=client.get("/api/posts?user_id=2").json["items"]
    assert len(items)==10
    assert all(p["is_mine"] is (authors[p["id"]]==owner_id) for p in items)
    assert all("author_id" not in p and "content" not in p for p in items)
    if email:
        mutate(client,"/api/auth/logout")
        assert all(p["is_mine"] is False for p in client.get("/api/posts").json["items"])


@pytest.mark.parametrize("page,expected", [("garbage",1),("-1",1),("0",1),("999",3),("1.5",1)])
def test_bad_page(client,page,expected):
    assert client.get("/api/posts?page="+page).json["page"]==expected


def test_post_owner_and_cascade(app, client):
    login(client)
    result=mutate(client,"/api/posts",data={"title":"새로운 기록","content":"원문","author_id":3})
    post_id=result.json["id"]
    assert result.status_code == 201
    assert client.get(f"/api/posts/{post_id}").json["post"]["author_id"]==2
    assert mutate(client,f"/api/posts/{post_id}","PATCH",{"title":"수정","content":"수정 내용"}).status_code==200
    assert mutate(client,f"/api/posts/{post_id}/comments",data={"content":"댓글"}).status_code==201
    login(client,"user2@example.com")
    for method in ("PATCH","DELETE"):
        assert mutate(client,f"/api/posts/{post_id}",method,{"title":"변경","content":"내용"}).status_code==403
    assert client.get(f"/api/posts/{post_id}/edit").status_code==403
    login(client,"admin@example.com")
    assert mutate(client,f"/api/posts/{post_id}","DELETE").status_code==403
    login(client)
    assert mutate(client,f"/api/posts/{post_id}","DELETE").status_code==200
    assert client.get(f"/api/posts/{post_id}").status_code==404
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM comments WHERE post_id=?",(post_id,)).fetchone()[0]==0


def test_last_page_delete(client,app):
    login(client)
    with app.app_context():
        db=get_db()
        with db:db.execute("DELETE FROM posts WHERE id>11")
    assert mutate(client,"/api/posts/1","DELETE").status_code==200
    result=client.get("/api/posts?page=2").json
    assert result["page"]==1 and len(result["items"])==10


@pytest.mark.parametrize("path,method,data",[("/api/posts","POST",{"title":"x","content":"y"}),
    ("/api/posts/1","PATCH",{"title":"x","content":"y"}), ("/api/posts/1","DELETE",{}),
    ("/api/posts/1/comments","POST",{"content":"x"}), ("/api/admin/mask-rules","POST",{"expression":"x"})])
def test_anonymous_writes_rejected(client,path,method,data):
    assert mutate(client,path,method,data).status_code==401


@pytest.mark.parametrize("data",[{"title":" ","content":"x"},{"title":"x","content":"\n\t"},
    {"title":"x"*201,"content":"x"},{"title":"x","content":"x"*10001}])
def test_post_validation(client,data):
    login(client)
    assert mutate(client,"/api/posts",data=data).status_code==422


def test_comments(client):
    login(client)
    assert mutate(client,"/api/posts/1/comments",data={"content":" \t"}).status_code==422
    assert mutate(client,"/api/posts/1/comments",data={"content":"x"*2001}).status_code==422
    assert mutate(client,"/api/posts/1/comments",data={"content":"first","author_id":3}).status_code==201
    assert mutate(client,"/api/posts/1/comments",data={"content":"second"}).status_code==201
    assert [c["content"] for c in client.get("/api/posts/1/comments").json["items"]]==["first","second"]
    assert client.get("/api/posts/2/comments").json["items"]==[]
    assert mutate(client,"/api/posts/999/comments",data={"content":"x"}).status_code==404


@pytest.mark.parametrize("email,owner_id",[(None,None),("user1@example.com",2),("user2@example.com",3),("admin@example.com",1)])
def test_comment_ownership_uses_current_session(app,client,email,owner_id):
    with app.app_context():
        db=get_db()
        with db:
            # Identical nicknames must not imply identical ownership.
            db.execute("UPDATE users SET nickname='같은 닉네임'")
            for author in (2,3,1):
                db.execute("INSERT INTO comments(post_id,author_id,content,created_at) VALUES(1,?,?,?)", (author,"댓글",now()))
    if email:
        assert login(client,email).status_code==200
    comments=client.get("/api/posts/1/comments?user_id=2").json["items"]
    assert len(comments)==3
    assert [c["is_mine"] for c in comments]==[author==owner_id for author in (2,3,1)]
    assert all("author_id" not in c for c in comments)
    if email:
        mutate(client,"/api/auth/logout")
        assert all(c["is_mine"] is False for c in client.get("/api/posts/1/comments").json["items"])


@pytest.mark.parametrize("text,keywords,expected",[("bad BAD bad",["bad"],"*** *** ***"),
    ("ababa",["aba","bab"],"*****"),("a.b axb",["a.b"],"*** axb"),
    ("평범한 기록",["금지어"],"평범한 기록"),("bad b-a-d",["bad"],"*** b-a-d")])
def test_masking_cases(text,keywords,expected):
    assert mask_text(text,keywords)==expected
    assert mask_text(text,list(reversed(keywords)))==expected


def test_rule_changes_apply_to_old_content(client):
    login(client)
    id=mutate(client,"/api/posts",data={"title":"Keyword 제목","content":"KEYWORD 내용"}).json["id"]
    mutate(client,f"/api/posts/{id}/comments",data={"content":"keyword 댓글"})
    login(client,"admin@example.com")
    rule=mutate(client,"/api/admin/mask-rules",data={"expression":" KeyWord "})
    assert rule.status_code==201
    post=client.get(f"/api/posts/{id}").json["post"]
    assert post["title"].startswith("*******") and post["content"].startswith("*******")
    assert client.get(f"/api/posts/{id}/comments").json["items"][0]["content"].startswith("*******")
    assert client.get("/api/posts").json["items"][0]["title"].startswith("*******")
    assert client.get(f"/api/posts/{id}/edit").status_code==403
    assert mutate(client,"/api/admin/mask-rules",data={"expression":"KEYWORD"}).status_code==409
    assert mutate(client,"/api/admin/mask-rules",data={"expression":"x","rule_type":"REGEX"}).status_code==422
    assert mutate(client,"/api/admin/mask-rules",data={"expression":" "}).status_code==422
    assert mutate(client,f"/api/admin/mask-rules/{rule.json['id']}","DELETE").status_code==200
    assert client.get(f"/api/posts/{id}").json["post"]["title"]=="Keyword 제목"
    login(client)
    assert client.get(f"/api/posts/{id}/edit").json["post"]["content"]=="KEYWORD 내용"


def test_admin_access(client):
    assert client.get("/api/admin/mask-rules").status_code==401
    login(client)
    assert client.get("/api/admin/mask-rules").status_code==403
    assert mutate(client,"/api/admin/mask-rules",data={"expression":"x"}).status_code==403
    assert mutate(client,"/api/admin/mask-rules/1","DELETE").status_code==403


def test_db_constraints_and_initialization(app):
    with app.app_context():
        db=get_db()
        assert db.execute("PRAGMA foreign_keys").fetchone()[0]==1
        for statement in ("DELETE FROM users WHERE id=2", "UPDATE posts SET title='' WHERE id=1", "UPDATE users SET role='ROOT' WHERE id=1", "UPDATE posts SET author_id=999 WHERE id=1"):
            with pytest.raises(sqlite3.IntegrityError):
                with db:db.execute(statement)
    with pytest.raises(ValueError):initialize(app.config["DATABASE_PATH"],DEMO_PASSWORD,True)


def test_backup(app,tmp_path):
    target=tmp_path/"backup.db"
    backup(app.config["DATABASE_PATH"],target)
    with sqlite3.connect(target) as db:
        assert db.execute("SELECT COUNT(*) FROM posts").fetchone()[0]==21
    with pytest.raises(FileExistsError):backup(app.config["DATABASE_PATH"],target)


def test_wsgi_import_and_storage(app,monkeypatch,tmp_path):
    path=tmp_path/"config.json"
    path.write_text(json.dumps({k:app.config[k] for k in ("DATABASE_PATH","SECRET_KEY")}),encoding="utf-8")
    monkeypatch.setenv("NOTE_DEMO_CONFIG",str(path))
    sys.modules.pop("wsgi",None)
    imported=importlib.import_module("wsgi")
    assert imported.application.test_client().get("/api/posts").json["total"]==21


def test_production_cookie_and_bad_host(app):
    config=dict(app.config,PRODUCTION=True,TRUSTED_HOSTS=["demo.pythonanywhere.com"])
    deployed=create_app(config).test_client()
    response=deployed.get("/api/auth/me",base_url="https://demo.pythonanywhere.com")
    cookie=response.headers["Set-Cookie"]
    assert "Secure" in cookie and "HttpOnly" in cookie and "SameSite=Lax" in cookie
    assert deployed.get("/",base_url="https://evil.example").status_code==400


@pytest.mark.parametrize("path",["/","/login","/signup","/forgot-password","/posts/new","/posts/1","/posts/1/edit","/admin/mask-rules","/static/app.js","/static/style.css"])
def test_pages_and_static(client,path):
    assert client.get(path).status_code==200


def test_xss_payload_remains_json_text(client):
    login(client)
    text='<img src=x onerror=alert(1)>'
    id=mutate(client,"/api/posts",data={"title":text,"content":text}).json["id"]
    response=client.get(f"/api/posts/{id}")
    assert response.is_json and response.json["post"]["content"]==text
    assert "script-src 'self'" in response.headers["Content-Security-Policy"]
    assert client.get("/data/note_demo.db").status_code==404
    assert client.get("/.local/config.json").status_code==404


def test_missing_configuration_fails(monkeypatch):
    monkeypatch.delenv("NOTE_DEMO_CONFIG",raising=False)
    with pytest.raises(RuntimeError):create_app()
    with pytest.raises(RuntimeError):create_app({"SECRET_KEY":"short","DATABASE_PATH":"relative"})
