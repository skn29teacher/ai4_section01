from uuid import UUID

from psycopg import Connection


def find_user_by_email(connection: Connection, email: str) -> dict | None:
    return connection.execute(
        """
        SELECT id, email, password_hash, name, phone, address, deleted_at, created_at
        FROM public.users
        WHERE email = %s
        """,
        (email,),
    ).fetchone()


def find_user_by_id(connection: Connection, user_id: UUID) -> dict | None:
    return connection.execute(
        """
        SELECT id, email, name, phone, address, deleted_at, created_at
        FROM public.users
        WHERE id = %s
        """,
        (user_id,),
    ).fetchone()


def insert_user(
    connection: Connection,
    *,
    email: str,
    password_hash: str,
    name: str,
    phone: str | None,
    address: str | None,
) -> dict:
    # 입력값은 항상 바인딩하며 SQL 문자열에 이어 붙이지 않습니다.
    return connection.execute(
        """
        INSERT INTO public.users (email, password_hash, name, phone, address)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id, email, name, phone, address, created_at
        """,
        (email, password_hash, name, phone, address),
    ).fetchone()
