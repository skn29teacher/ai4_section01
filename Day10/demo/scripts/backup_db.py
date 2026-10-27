import argparse
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.config import load_config


def backup(source, destination):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if not source.is_file():
        raise ValueError("백업할 DB가 없습니다.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb"):
        pass
    src = sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)
    dst = sqlite3.connect(str(destination))
    try:
        src.backup(dst)
    finally:
        dst.close()
        src.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SQLite 수동 백업 (기존 백업 덮어쓰기 금지)")
    parser.add_argument("destination")
    args = parser.parse_args()
    backup(load_config()["DATABASE_PATH"], args.destination)
    print("백업 완료. 비공개 위치에 보관하세요.")
