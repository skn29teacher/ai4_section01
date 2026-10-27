"""Create private configuration without displaying secrets."""
import argparse
import json
from pathlib import Path
import secrets

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description="비공개 설정 생성")
    parser.add_argument("--output", default=str(ROOT / ".local" / "config.json"))
    parser.add_argument("--database", default=str(ROOT / "data" / "note_demo.db"))
    parser.add_argument("--production", action="store_true")
    parser.add_argument("--host", action="append", default=[])
    args = parser.parse_args()
    output = Path(args.output).expanduser().resolve()
    if args.production and not args.host:
        parser.error("공개 배포에는 --host가 필요합니다.")
    values = dict(SECRET_KEY=secrets.token_urlsafe(48), DATABASE_PATH=str(Path(args.database).expanduser().resolve()),
                  PRODUCTION=args.production, TRUSTED_HOSTS=args.host or ["localhost", "127.0.0.1"])
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with output.open("x", encoding="utf-8") as file:
            json.dump(values, file, ensure_ascii=False, indent=2)
        output.chmod(0o600)
    except FileExistsError:
        parser.error("설정 파일이 이미 있습니다. 기존 키를 보존하기 위해 덮어쓰지 않습니다.")
    print(f"설정 생성: {output} (비밀값은 출력하지 않음)")


if __name__ == "__main__":
    main()
