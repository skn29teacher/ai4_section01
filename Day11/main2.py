import json
from pathlib import Path
from getpass import getpass

# pip install "psycopg[binary]"
import psycopg

# config.json 설정파일을 로드
config_path = Path(__file__).with_name('config.json')
config = json.loads(config_path.read_text(encoding='utf-8'))

# supabase 플랫폼의 database 접속
with psycopg.connect(
    host = config['host'],
    port=config['port'],
    dbname = config.get('dbname',config.get('database')),
    user = config['user'],
    password = config['password'],
    sslmode = 'require',
    connect_timeout=10,
)as conn:
    # 데이터 베이스(스키마) 생성
    conn.execute(
        "create schema if not exist ch2;"
    )

    conn.execute(
"""
create table if not exist users(
  id bigint generated always as identity primary key,
  name text not null,
  email text not null unique
);
"""
    )
print('테이블 준비완료')    
# 사용자 2명 입력
