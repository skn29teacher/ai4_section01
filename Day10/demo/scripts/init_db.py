import argparse
from getpass import getpass
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from werkzeug.security import generate_password_hash
from app.config import load_config
from app.db import connect, now

DEMO_PASSWORD = "DemoOnly123!"


def initialize(path, admin_password, demo=False, admin_email="admin@example.com"):
    """Initialize once; refuse existing schema instead of silently reseeding."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    db = connect(str(path))
    try:
        if db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchone():
            raise ValueError("기존 DB는 변경하지 않습니다. 백업 후 새 DB 경로로 초기화하세요.")
        if not 8 <= len(admin_password) <= 128 or not admin_password.strip():
            raise ValueError("관리자 비밀번호는 8~128자로 지정하세요.")
        db.executescript((ROOT / "db" / "schema.sql").read_text(encoding="utf-8"))
        timestamp = now()
        with db:
            db.execute("INSERT INTO users(email,nickname,password_hash,role,created_at) VALUES(?,?,?,'ADMIN',?)", (admin_email.strip().lower(), "관리자", generate_password_hash(admin_password), timestamp))
            seed = json.loads((ROOT / "db" / "seed.json").read_text(encoding="utf-8"))
            db.executemany("INSERT INTO mask_rules(expression,created_at) VALUES(?,?)", [(word.lower(), timestamp) for word in seed["expressions"]])
            if demo:
                for number in (1, 2):
                    db.execute("INSERT INTO users(email,nickname,password_hash,created_at) VALUES(?,?,?,?)", (f"user{number}@example.com", f"사용자{number}", generate_password_hash(DEMO_PASSWORD), timestamp))
                for number in range(1, 22):
                    db.execute("INSERT INTO posts(author_id,title,content,created_at,updated_at) VALUES(2,?,?,?,?)", (f"노트 {number:02d} · 오늘의 기록", f"{number}번째 데모 게시글입니다.\n배운 내용과 생각을 자유롭게 기록하세요.", timestamp, timestamp))
                db.execute("INSERT INTO comments(post_id,author_id,content,created_at) VALUES(21,3,?,?)", ("좋은 기록 감사합니다.", timestamp))
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="최초 DB 생성. 기존 DB를 덮어쓰지 않습니다.")
    parser.add_argument("--demo", action="store_true", help="로컬 전용 공개 데모 계정·예제 데이터")
    parser.add_argument("--admin-email", default="admin@example.com")
    args = parser.parse_args()
    config = load_config()
    if args.demo and config.get("PRODUCTION"):
        parser.error("공개 배포에서는 --demo를 사용할 수 없습니다.")
    import re
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", args.admin_email) or len(args.admin_email) > 254:
        parser.error("관리자 이메일을 확인하세요.")
    password = DEMO_PASSWORD if args.demo else getpass("관리자 비밀번호 (8~128자): ")
    if not args.demo and password != getpass("관리자 비밀번호 확인: "):
        parser.error("비밀번호 확인이 일치하지 않습니다.")
    try:
        initialize(config["DATABASE_PATH"], password, args.demo, args.admin_email)
    except ValueError as error:
        parser.error(str(error))
    print("DB 초기 생성 완료. 기존 파일은 이후 코드 업데이트 시 보존하세요.")


if __name__ == "__main__":
    main()
