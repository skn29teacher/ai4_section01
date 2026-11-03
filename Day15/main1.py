# fastapi에서 supabase postgreSQL 과 Redis의 응답을 확인
import os
import psycopg  # supabase
from redis import Redis, RedisError

# .env http json
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse

#환경변수
load_dotenv(override=True) 
DB_URL = os.getenv('SUPABASE_DB_URL',"")
REDIS_URL = os.getenv('REDIS_URL',"")

# 환경변수 값 체크
if not DB_URL:
    raise RuntimeError('SUPABASE_DB_URL 설정확인')
if not REDIS_URL:
    raise RuntimeError('REDIS_URL 설정확인')

# backend fastapi
app = FastAPI()

# api 동작확인
@app.get('/health')
def health():
    checks = {'supabase':'down', 'redis':'down'}
    try:
        with psycopg.connect(
            DB_URL,
            connect_timeout=5,
            sslmode='require',
        ) as conn:
            with conn.cursor() as cur:  # sql 실행과 결과
                cur.execute('select 1 as ok')
                row = cur.fetchone()  # 기본반환형은 튜플 (1,)
                if row == (1,):
                    checks['supabase'] ='up'

    except psycopg.Error:
        pass
    try:
        with Redis.from_url(
            REDIS_URL,
            socket_connect_timeout=3,
            socket_timeout=3,
        )as client:
            if client.ping():
                checks['redis'] = 'up'
    except (RedisError, ValueError):
        pass

    ready = all( value == "up"  for value in checks.values() )
    return JSONResponse(
        status_code=200 if ready else 503,
        content={'ready':ready, 'checks':checks}
    )

