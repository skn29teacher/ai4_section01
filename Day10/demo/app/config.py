import json
import os
from pathlib import Path


def load_config(overrides=None):
    if overrides is not None:
        values = dict(overrides)
    else:
        filename = os.environ.get("NOTE_DEMO_CONFIG")
        if not filename:
            raise RuntimeError("NOTE_DEMO_CONFIG에 비공개 설정 파일의 절대 경로를 지정하세요.")
        config_path = Path(filename)
        if not config_path.is_absolute():
            raise RuntimeError("설정 파일 경로는 절대 경로여야 합니다.")
        values = json.loads(config_path.read_text(encoding="utf-8"))
    secret = values.get("SECRET_KEY", "")
    if not isinstance(secret, str) or len(secret) < 32 or secret.startswith("REPLACE_"):
        raise RuntimeError("32자 이상의 임의 SECRET_KEY를 설정하세요.")
    database = values.get("DATABASE_PATH", "")
    if not database or not Path(database).is_absolute():
        raise RuntimeError("DATABASE_PATH는 절대 경로여야 합니다.")
    if values.get("PRODUCTION") and not values.get("TRUSTED_HOSTS"):
        raise RuntimeError("공개 배포에는 TRUSTED_HOSTS가 필요합니다.")
    values.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=bool(values.get("PRODUCTION")),
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_REFRESH_EACH_REQUEST=False,
        PERMANENT_SESSION_LIFETIME=28800,
        MAX_CONTENT_LENGTH=128 * 1024,
        DEBUG=False,
    )
    return values
