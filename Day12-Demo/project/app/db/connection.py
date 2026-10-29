from collections.abc import Iterator

from fastapi import Request
from psycopg import Connection
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.core.config import Settings


def create_pool(settings: Settings) -> ConnectionPool:
    return ConnectionPool(
        conninfo=settings.database_url.get_secret_value(),
        min_size=1,
        max_size=5,
        timeout=5,
        open=False,
        kwargs={
            "row_factory": dict_row,
            "connect_timeout": 5,
            "sslmode": "require",
            # Supabase pooler에서도 서버측 prepared statement 충돌을 피합니다.
            "prepare_threshold": None,
        },
        check=ConnectionPool.check_connection,
    )


def get_connection(request: Request) -> Iterator[Connection]:
    # 성공 시 commit, 예외 시 rollback 후 연결을 풀에 반환합니다.
    with request.app.state.db_pool.connection() as connection:
        yield connection
