import argparse
import json
import os
import sqlite3
from contextlib import closing  # sqlite 연결을 종료할때 실제 로 close
import redis
from dotenv import load_dotenv
load_dotenv()

DEMO_USERS = {'demo-a':'홍길동', 'demo-b' : '강감찬'}
CACHE_TTL = 60  
MAX_MESSAGES = 6  # 원본 전체 중 최근 6개 메세지만 캐시 / 문맥에 사용

def read_settings():
    host = os.getenv('REDIS_HOST')
    port = os.getenv('REDIS_PORT')
    db_path = os.getenv('SQLITE_PATH')
    if not host or not port or not db_path:
        raise ValueError('필수값 누락')    
    return host,int(port),db_path

def initialize(conn):
    # 정상종료 commit 예외발생 rollback  
    with conn:
        conn.execute("""
        create table if not exists messages (
            id integer primary key autoincrement,
            owner text not null,
            role text not null check(role in ('user','assistant')),
            content text not null
        )
        """)
        if conn.execute("select count(*) from messages").fetchone()[0] == 0:
            conn.executemany(
                "insert into messages(owner, role, content) values(?,?,?)",
                [
                    ('demo-a','user','내 이름은 민수'),
                    ('demo-a','assistant','모의응답: 내 이름은 민수'),
                    ('demo-b','user','내 이름은 지연'),
                    ('demo-b','assistant','모의응답: 내 이름은 지연'),
                ],
            )

def read_source(conn, owner):
    '''owner:사용자  conn:db path'''
    rows = conn.execute(
        "select role,content from messages where owner = ? order by id desc limit ?",
        (owner,MAX_MESSAGES)
    ).fetchall()
    return [ {'role':role,'content':content }   for role,content in rows  ]

host,port,db_path =  read_settings()

with closing(sqlite3.connect(db_path)) as conn:
    initialize(conn)