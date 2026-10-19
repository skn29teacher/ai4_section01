"""직접 실행: python main.py 또는 python day1_modules/main.py."""

if __package__:
    from .menu import main
else:
    # 파일을 직접 실행해도 상위 폴더의 패키지를 찾도록 설정합니다.
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from day1_modules.menu import main


def run():
    """입력 종료나 Ctrl+C로 실습을 종료합니다."""
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\n실습을 종료합니다.")


if __name__ == "__main__":
    run()
