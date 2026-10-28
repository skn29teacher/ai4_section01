# note-demo

Flask + SQLite로 만든 한국어 게시판 데모입니다. 회원가입·로그인·로그아웃, 제목만 표시하는 10개 단위 목록, 본인 글 수정·삭제, 댓글, 키워드 마스킹과 관리자 표현 사전 관리를 제공합니다. 비밀번호 찾기는 실제 메일을 보내지 않는 목업입니다.

로그인한 사용자가 작성한 글에는 목록 제목 옆에 **내 글** 배지가 표시됩니다. 다른 사용자의 글과 비로그인 상태에는 표시하지 않습니다.

댓글에도 본인이 작성한 경우 닉네임 옆에 **내 댓글** 배지가 표시됩니다. 닉네임이 같아도 회원 ID를 기준으로 구분합니다.

**문서 확인일: 2026-10-27 (한국 시간).** 아래 PythonAnywhere 절차는 확인일의 공식 자료를 바탕으로 작성했습니다. 실제 계정에서 업로드·공개 배포는 수행하지 않았습니다.

## 0. 실제 로컬 프로젝트 구조

프로젝트 루트는 **`C:\AI4\Day10\demo`**입니다. 아래 구조에서 CMD 명령을 실행합니다. 화면 캡처 아래쪽에 보이지 않는 `wsgi.py`도 루트에 있으며 배포에 필요합니다.

```text
demo/
├─ .local/
│  └─ config.json              # 로컬 비공개 설정·SECRET_KEY·DB 절대 경로
├─ .venv/                     # 로컬 Python 가상환경
├─ app/
│  ├─ __init__.py             # Flask 앱 생성
│  ├─ auth.py                 # 로그인 상태·권한·CSRF 검사
│  ├─ config.py               # 비공개 설정 읽기
│  ├─ db.py                   # SQLite 연결
│  ├─ routes/api.py           # 회원·게시글·댓글·관리 API
│  ├─ services/masking.py     # 키워드 마스킹
│  └─ static/                 # index.html·app.js·style.css
├─ data/
│  └─ note_demo.db            # 실제 회원·게시글·댓글·표현 사전 데이터
├─ db/
│  ├─ schema.sql              # 테이블·제약·인덱스 정의
│  └─ seed.json               # 초기 표현 사전
├─ docs/                      # 검증 기록·출처·화면 캡처
├─ scripts/                   # 설정 생성·DB 최초 생성·백업 도구
├─ tests/                     # 자동 테스트
├─ __pycache__/               # Python 실행 캐시
├─ .pytest_cache/             # 테스트 실행 캐시
├─ .gitignore
├─ ai_agent_prompt.md
├─ implementation_plan.md
├─ prompt.md
├─ config.example.json        # 비밀값이 없는 설정 형식 예제
├─ README.md
├─ requirements.txt           # 배포용 실행 의존성
├─ requirements-dev.txt       # 로컬 테스트 의존성
└─ wsgi.py                    # 배포 서버가 불러오는 진입점
```

`db/`는 **DB를 만드는 설계·초기 데이터 파일**, `data/`는 **실제로 사용 중인 DB 파일**입니다. 코드 수정 때 `data/`나 `.local/`을 삭제할 필요가 없습니다.

| 로컬 항목 | PythonAnywhere 최초 배포 시 처리 |
| --- | --- |
| `app/`, `db/`, `scripts/` | 하위 구조 그대로 업로드; 내부 `__pycache__`·`.pyc` 제외 |
| `wsgi.py`, `requirements.txt` | 서버 프로젝트 루트에 업로드 |
| `docs/`, README·설계 문서, `config.example.json` | 필요하면 업로드; 실행 필수 항목은 아님 |
| `.venv/` | 업로드하지 않고 서버에서 별도 생성 |
| `.local/` | 업로드하지 않고 서버용 비공개 설정을 별도 생성 |
| `data/` | 이 안내의 최초 배포는 새 DB를 서버에서 생성; 로컬 데모 DB는 업로드하지 않음 |
| `tests/`, `requirements-dev.txt`, 실행 캐시 | 배포 실행에 불필요 |

이 문서에서 서버 폴더를 `/home/YOURUSERNAME/note-demo`로 표기한 것은 **배포 경로 예시**입니다. 로컬 `demo` 폴더명을 바꿀 필요는 없습니다. `demo`의 내용물을 서버 `note-demo` 바로 아래에 배치하여 `/home/YOURUSERNAME/note-demo/app/`, `/home/YOURUSERNAME/note-demo/wsgi.py`가 되게 합니다. `note-demo/demo/app/`처럼 폴더가 한 단계 더 생기지 않도록 확인하세요.

## 1. Windows CMD에서 로컬 실행

로컬 터미널은 **Windows 명령 프롬프트(CMD)** 기준입니다. Python 3.10 이상을 사용하세요. 이 프로젝트는 **Python 3.13.12, Flask 3.1.3**으로 테스트했습니다. 명령은 `python`을 사용합니다. `(.venv)`가 프롬프트 앞에 표시되고 `.venv\Scripts\python.exe`가 실제로 존재하면 가상환경 생성 단계를 건너뜁니다. 폴더를 삭제했다면 새 CMD에서 가상환경부터 다시 생성해야 합니다.

### 이미 설정과 DB가 있는 경우: CMD에서 재실행

현재 제공된 작업 폴더에는 `.local/config.json`과 `data/note_demo.db`가 생성되어 있습니다. CMD에서 아래 명령만 실행합니다. 터미널을 새로 열 때마다 `set` 명령을 다시 실행하세요.

```bat
cd /d C:\AI4\Day10\demo
call .venv\Scripts\activate.bat
set "NOTE_DEMO_CONFIG=%CD%\.local\config.json"
python -m flask --app wsgi:application run --reload --host 127.0.0.1 --port 5000
```

이미 프로젝트 폴더에서 `(.venv)` 상태라면 위 명령 중 `set`과 `python -m flask ...` 두 줄만 실행하면 됩니다. `설정 파일이 이미 있습니다`는 기존 키를 보존하기 위한 안내입니다. `configure.py`와 `init_db.py --demo`를 반복할 필요가 없습니다.

### 새 환경 최초 설치: CMD

가상환경·설정·DB가 없는 새 환경에서만 실행합니다. 기존 `.venv` 안에서 `.venv`를 다시 생성하지 마세요.

```bat
cd /d C:\AI4\Day10\demo
python -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install -r requirements-dev.txt
python scripts/configure.py
set "NOTE_DEMO_CONFIG=%CD%\.local\config.json"
python scripts/init_db.py --demo
python -m flask --app wsgi:application run --reload --host 127.0.0.1 --port 5000
```

브라우저에서 [로컬 게시판](http://127.0.0.1:5000)을 엽니다. 서버 종료는 실행한 터미널에서 `Ctrl+C`입니다. 이미 `.venv`, `.local/config.json`, DB가 있다면 생성·초기화 단계는 건너뛰고 **환경 변수 설정과 마지막 실행 명령**만 사용하세요. 구성 도구와 초기화 도구는 기존 파일을 덮어쓰지 않습니다.

로컬 명령의 `--reload`는 Python 코드 변경을 자동으로 반영합니다. 이미 실행 중인 서버에는 뒤늦게 적용되지 않으므로 기존 서버를 `Ctrl+C`로 종료한 다음 새 명령으로 실행하세요. 화면 파일 수정 후에는 브라우저에서 `Ctrl+F5`로 새로고침합니다. 디버거는 활성화하지 않으며 PythonAnywhere 배포에서는 이 로컬 명령을 사용하지 않습니다.

로컬 `--demo`로만 만들어지는 계정:

| 역할 | 이메일 | 비밀번호 |
| --- | --- | --- |
| 일반 사용자 A | user1@example.com | DemoOnly123! |
| 일반 사용자 B | user2@example.com | DemoOnly123! |
| 관리자 | admin@example.com | DemoOnly123! |

예제 게시글 21개와 댓글이 생성됩니다. 공개 배포에서는 `--demo`가 거부되며 관리자 비밀번호를 직접 입력합니다.

## 2. 테스트

CMD에서 프로젝트 폴더로 이동한 후 실행합니다.

```bat
call .venv\Scripts\activate.bat
python -m pytest -q
```

별도 임시 DB와 테스트 설정을 사용하므로 실제 DB를 초기화하지 않습니다. 검증 범위와 실행 결과는 [검증 기록](docs/verification.md), 요구사항별 연결은 [대응표](docs/requirements_traceability.md)에 있습니다.

## 3. PythonAnywhere 무료 계정에 배포

이 절의 `bash` 명령은 **PythonAnywhere 웹사이트의 Consoles → Bash에서만** 실행합니다. 로컬 CMD에 입력하지 마세요.

### 무료 환경과 선택한 방식

Flask를 **Web 탭의 일반 WSGI 웹 앱**으로 배포합니다. PythonAnywhere 공식 가이드는 가상환경의 Python 버전을 Web 앱 선택 버전과 맞추고 WSGI 설정에서 앱을 import하도록 안내합니다. 콘솔에서 개발 서버를 계속 켜 두는 방식으로 배포하지 않습니다. [공식 Flask 배포 안내](https://help.pythonanywhere.com/pages/Flask/)

확인일 기준 무료 계정은 **웹 앱 1개·워커 1개·512 MiB 디스크·1개월 만료**, CPU·콘솔 제한이 있습니다. 기본 도메인을 사용하고 Web 탭의 만료일과 연장 기능을 확인하세요. 최신 수치는 자신의 대시보드를 우선합니다. [무료 계정 조건](https://help.pythonanywhere.com/pages/FreeAccountsFeatures/)

SQLite는 모든 계정에서 사용할 수 있습니다. 새 무료 계정은 MySQL이나 일일 예약 작업이 있다고 가정하지 않습니다. SQLite는 소규모 데모 용도이며 동시 쓰기와 클라우드 파일 잠금의 한계가 있습니다. [지원 DB](https://help.pythonanywhere.com/pages/KindsOfDatabases)

### 3-1. 파일 업로드

아래 `YOURUSERNAME`은 실제 계정명으로 바꾸세요. 계정에 따라 도메인 접미사가 다를 수 있으므로 **Web 탭에 실제 표시되는 도메인**을 사용합니다.

1. PythonAnywhere의 **Files**에서 `/home/YOURUSERNAME/note-demo` 폴더를 만듭니다.
2. 위 구조표의 `app/`, `db/`, `scripts/`, `wsgi.py`, `requirements.txt`를 서버 프로젝트 루트 바로 아래에 같은 구조로 업로드합니다. 하위 폴더의 `__pycache__`와 `.pyc`는 제외합니다. 문서도 필요하면 함께 업로드합니다.
3. `.venv/`, `.local/`, 로컬 `data/`, 테스트 캐시, 실제 비밀 설정은 올리지 않습니다. 여러 파일은 소스 전용 ZIP으로 올린 후 Bash 콘솔에서 해당 폴더에 풉니다.

### 3-2. 가상환경과 의존성

**Consoles → Bash**를 엽니다. 아래는 Web 탭에서 Python 3.13을 선택할 수 있는 경우의 예입니다. 없다면 **실제로 제공되는 3.10 이상 버전**으로 명령과 Web 앱 설정을 함께 변경하세요.

```bash
cd /home/YOURUSERNAME/note-demo
mkvirtualenv --python=/usr/bin/python3.13 note-demo
python -m pip install -r requirements.txt
```

이후 콘솔을 새로 열면 `workon note-demo`로 같은 환경을 활성화합니다. 테스트 패키지는 배포 시 필수가 아닙니다.

### 3-3. 비공개 설정과 DB 최초 생성

설정 파일은 소스 폴더 바깥의 홈 디렉터리에 생성합니다. `--host`에는 프로토콜이나 경로 없이 실제 공개 호스트명을 넣습니다.

```bash
cd /home/YOURUSERNAME/note-demo
workon note-demo
python scripts/configure.py --production --host YOURUSERNAME.pythonanywhere.com --output /home/YOURUSERNAME/.config/note-demo/config.json --database /home/YOURUSERNAME/note-demo/data/note_demo.db
export NOTE_DEMO_CONFIG=/home/YOURUSERNAME/.config/note-demo/config.json
python scripts/init_db.py --admin-email YOUR_ADMIN_EMAIL
```

`YOUR_ADMIN_EMAIL`을 관리자 로그인용 이메일로 바꾸세요. 이메일 발송은 하지 않습니다. 관리자 비밀번호를 두 번 입력하며 터미널에 표시되지 않습니다. 설정 도구가 고정 임의 SECRET_KEY를 생성하므로 예제 문자열을 직접 사용하지 않아도 됩니다.

최초 초기화는 관리자 1명과 초기 표현 사전만 생성합니다. 공개 사용자 계정과 게시글은 가입·작성을 통해 만듭니다. 설정이나 DB가 이미 있으면 도구가 덮어쓰기를 거부합니다. **Reload 또는 업데이트 때 초기화 명령을 반복하지 마세요.**

### 3-4. Web 앱과 WSGI 설정

1. **Web → Add a new web app → Manual configuration**을 선택합니다.
2. 가상환경 생성 시 사용한 Python 버전을 선택합니다.
3. **Source code / Working directory**: `/home/YOURUSERNAME/note-demo`
4. **Virtualenv**: `/home/YOURUSERNAME/.virtualenvs/note-demo`
5. Web 탭의 **WSGI configuration file** 링크를 열고 기존 예제 코드를 아래 내용으로 바꿉니다. 이는 PythonAnywhere가 생성한 설정 파일이며 프로젝트의 `wsgi.py`와 별개입니다.

```python
import os
import sys

project_path = '/home/YOURUSERNAME/note-demo'
if project_path not in sys.path:
    sys.path.insert(0, project_path)

os.environ['NOTE_DEMO_CONFIG'] = '/home/YOURUSERNAME/.config/note-demo/config.json'

from wsgi import application
```

프로젝트 `wsgi.py`가 Flask 객체를 `application`으로 노출합니다. 이 파일을 import해도 개발 서버나 초기화 작업은 실행되지 않습니다. 콘솔에서 설정한 `export`는 웹 프로세스에 자동 전파되지 않으므로 위 WSGI 설정에도 경로를 지정해야 합니다. [환경 변수 공식 안내](https://help.pythonanywhere.com/pages/EnvironmentVariables/)

### 3-5. 정적 파일과 HTTPS

Web 탭의 **Static files**에 아래 매핑을 추가합니다.

| URL | Directory |
| --- | --- |
| /static/ | /home/YOURUSERNAME/note-demo/app/static/ |

매핑 후 Reload하면 `/static/style.css` 등을 직접 확인할 수 있습니다. DB나 프로젝트 루트, 비공개 설정 폴더는 매핑하지 않습니다. [정적 파일 공식 안내](https://help.pythonanywhere.com/pages/StaticFiles/)

Web 탭에서 **Force HTTPS**를 활성화하고 Reload합니다. 공개 설정에서는 세션 쿠키가 Secure이므로 HTTPS로 접속해야 로그인이 정상 작동합니다. [HTTPS 공식 안내](https://help.pythonanywhere.com/pages/ForcingHTTPS/)

### 3-6. 배포 확인

공개 URL에서 아래 순서로 확인합니다.

1. 목록과 CSS/JavaScript가 정상 표시되는지 확인합니다.
2. 새 회원가입·로그인 후 글과 댓글을 작성합니다.
3. 다른 계정에서 앞선 글을 수정·삭제할 수 없는지 확인합니다.
4. 관리자 로그인 후 시험 키워드를 추가하여 기존 글·댓글의 마스킹을 확인합니다.
5. Web 탭에서 Reload한 뒤 데이터와 만료 전 로그인이 유지되는지 확인합니다.
6. 로그아웃한 이전 세션으로 변경 요청이 허용되지 않는지 확인합니다.

SECRET_KEY와 DB를 보존하면 Reload 후 로그인은 최대 8시간 범위에서 유지됩니다. 로그아웃하면 해당 계정의 다른 기기도 함께 로그아웃됩니다.

## 4. 업데이트·백업·초기화

서버에서 코드 갱신 전 백업합니다. 백업 경로는 정적 폴더 밖으로 지정하며 기존 파일은 덮어쓰지 않습니다.

```bash
workon note-demo
cd /home/YOURUSERNAME/note-demo
export NOTE_DEMO_CONFIG=/home/YOURUSERNAME/.config/note-demo/config.json
python scripts/backup_db.py /home/YOURUSERNAME/backups/note-demo-20261027.db
```

`sqlite3` backup API로 일관된 백업을 생성합니다. 이후에는 코드 파일만 갱신하고 **DB와 비공개 설정을 보존**한 뒤 Web 탭에서 Reload합니다. 백업은 계정 디스크를 사용하므로 필요한 사본을 내려받아 보관하세요.

복구는 Web 탭에서 앱을 비활성화하여 쓰기 요청을 중단하고, 현재 DB도 별도로 보관한 다음 백업 파일을 설정된 DB 경로로 복원하고 앱을 다시 활성화합니다. `PRAGMA integrity_check` 결과가 `ok`인지 확인한 뒤 Reload하세요. 백업 복구는 세션 버전도 과거로 되돌리므로 **SECRET_KEY도 새 임의 값으로 교체해 기존 세션을 모두 종료**하세요. 복구 작업은 자동으로 실행하지 않습니다.

완전 초기화가 필요하면 기존 DB를 지우는 대신 백업 후 설정의 `DATABASE_PATH`를 새 파일의 절대 경로로 바꾸고 `init_db.py`를 실행하세요. 스키마 변경 시에는 별도 마이그레이션이 필요하며 초기화 도구가 기존 데이터를 자동 변환하지 않습니다.

## 5. 자주 발생하는 문제

| 증상 | 확인할 내용 |
| --- | --- |
| 502/504 또는 import 오류 | Web 탭 error/server 로그, 가상환경과 Python 버전, WSGI 프로젝트 경로, 설치 의존성 |
| NOTE_DEMO_CONFIG 오류 | WSGI 파일에서 import 전에 비공개 설정 경로를 지정했는지 |
| 로컬 `python3` 명령이 작동하지 않음 | CMD에서 가상환경 활성화 후 `python` 사용. `(.venv)` 상태에서는 가상환경 재생성 생략 |
| CMD에서 `$env:...` 구문 오류 | `set "NOTE_DEMO_CONFIG=%CD%\.local\config.json"` 사용; PowerShell 문법과 구분 |
| 설정 파일이 이미 있습니다 | 기존 설정 유지. 생성 단계를 건너뛰고 환경 변수 설정 후 서버 실행 |
| DB 오류/503 | 최초 DB 생성 여부, DATABASE_PATH 절대 경로, DB와 상위 디렉터리 쓰기 권한, 파일 잠금 |
| CSS/JS 404 | 정적 파일 매핑과 실제 디렉터리, Reload 및 브라우저 강력 새로고침 |
| 로그인 후 인증이 유지되지 않음 | HTTPS 접속, PRODUCTION 설정, SECRET_KEY 보존, 쿠키 설정 |
| 요청 확인 만료/403 | 새로고침으로 CSRF 토큰 갱신; 다른 기기 로그아웃으로 세션이 만료되었는지 |
| 400 잘못된 호스트 | TRUSTED_HOSTS에 Web 탭의 정확한 도메인이 있는지 |
| 메일이 오지 않음 | 비밀번호 찾기는 안내만 제공하는 목업 |

무료 계정의 외부 인터넷은 허용 목록으로 제한됩니다. 앱은 외부 서비스나 실시간 사전 수집에 의존하지 않습니다. [무료 외부 접근 허용 목록](https://www.pythonanywhere.com/whitelist/)

## 6. 범위와 문서

이 앱은 데모 인증을 제공하며 SNS 로그인, 실제 비밀번호 재설정, 운영용 부정 사용 방지·모니터링은 포함하지 않습니다. 키워드 마스킹은 반복·겹침·영문 대소문자를 처리하지만 문맥 판단이나 공백·기호를 끼운 우회 표현을 완벽히 검출하지 않습니다. 원문은 DB에 보존하며 작성자 편집에만 반환합니다.

- [ERD와 테이블 정의](ai_agent_prompt.md#52-erd)
- [승인된 구현 계획](implementation_plan.md)
- [표현 사전 출처·라이선스·제외 기준](docs/masking_sources.md)
- [요구사항 대응표](docs/requirements_traceability.md)
- [테스트·수동 검증 기록](docs/verification.md)

배포 상세 안내는 이 README를 기준으로 합니다. 구현 파일은 `app/`, 실제 DDL은 `db/schema.sql`, 기본 표현 사전은 `db/seed.json`에 있습니다.
