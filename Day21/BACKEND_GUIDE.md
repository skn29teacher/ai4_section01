# 연결할 서비스와 저장 위치

## 차시별 연결

| 차시 | 실행 파일 | 모델 호출 | 피드백 보관 |
| --- | --- | --- | --- |
| 1 | `lesson01/main.py` | Streamlit 서버에서 Groq 호출 | 평가 기능 이전 단계 |
| 2 | `lesson02/main.py` | 동일 | 현재 브라우저 연결의 임시 기록 |
| 3 | `lesson03/main.py` | 동일 | 동의한 평가를 현 세션에 보관·JSONL로 내려받기 |
| 4~5 | 해당 `lessonXX/main.py` | 동일 | Supabase Postgres에 저장 |
| 6~8 | 해당 `lessonXX/main.py` | 동일 | Supabase에 저장하며 공개 서비스 설정 적용 |

Windows에서는 해당 차시 폴더에서 앱 하나만 실행합니다. 앱을 바꾸려면 CMD에서 Ctrl+C로 종료하고 다음 차시 폴더로 이동합니다. 브라우저는 `http://127.0.0.1:8501`을 엽니다. Groq와 Supabase는 원격 서비스이므로 로컬 FastAPI·Redis 서버를 시작하지 않습니다.

## Supabase 연결 준비 — 4차시부터

기존 Supabase 프로젝트를 엽니다. 프로젝트가 일시 중지되어 있으면 먼저 재개합니다. **Connect**에서 PostgreSQL 연결 정보를 열고 **Session pooler**의 URI를 선택합니다. Session pooler는 IPv4 환경에서도 연결하기 위한 중간 접속 주소입니다. 화면에서 받은 주소와 사용자 이름을 그대로 사용하고, DB 비밀번호 자리를 본인의 비밀번호로 바꿉니다. API의 publishable key와 DB 비밀번호는 서로 다른 값입니다.

해당 차시의 `.env`에 다음 값을 넣습니다. 아래 주소·사용자·비밀번호는 형식을 설명하는 가짜 값입니다.

```dotenv
DATABASE_URL=postgresql://postgres.example-project:example-password@aws-0-example.pooler.supabase.com:5432/postgres?sslmode=require
```

URI 비밀번호에 `@`, `:`, `/`, `#`, `%`처럼 주소에서 뜻을 갖는 문자가 있으면 URL 인코딩이 필요합니다. 콘솔에 연결 문자열을 출력하거나 채팅·Git에 붙이지 않습니다. 브라우저에서 선택한 프로젝트의 연결 문자열을 사용하며 예시 호스트를 그대로 입력하지 않습니다.

4~5차시 앱을 로컬에서 실행한 뒤 사이드바의 **피드백 테이블 준비**를 한 번 누릅니다. `main.py`의 초기화 함수가 `public.kdt_travel_feedback` 테이블을 만들고 공개 API 접근을 막는 설정을 적용합니다. 테이블 생성은 별도 SQL 파일을 읽지 않고 실행 파일 안의 SQL로 처리합니다.

6~8차시 ZIP으로 처음 시작하는 경우에도 로컬에서 준비할 수 있습니다. 해당 차시 `.env`의 `SHOW_DEMO_TOOLS=true`로 바꿔 재실행하면 **피드백 테이블 준비**가 보입니다. 준비 완료 뒤 `false`로 되돌리고 앱을 종료·재실행합니다. 이미 같은 DB를 준비했다면 다시 만들 필요가 없습니다. Cloud Secrets는 항상 `SHOW_DEMO_TOOLS="false"`로 두므로 공개 화면에는 준비 버튼이 없습니다.

앱의 DB 계정은 Streamlit 서버에만 있습니다. 공개 방문자는 웹 화면에서 평가를 전송할 뿐, DB 연결 정보를 받지 않습니다. 전체 운영 로그는 프로젝트 소유자의 Supabase SQL Editor에서 확인합니다. 공개 앱에 전체 로그 조회 화면을 추가하지 않습니다.

## 무엇이 남는가

| 정보 | 보관 위치 | 새 연결·서버 재시작 뒤 |
| --- | --- | --- |
| 적용한 여행 프로필 | Streamlit 세션 메모리 | 다시 선택 |
| 질문·완성 답변과 부분 답변 | Streamlit 세션 메모리 | 복원 보장 없음 |
| 동의하고 저장한 평가 | Supabase 테이블 | DB에서 유지 |
| 내려받은 JSONL | 내려받은 기기 | 직접 보관·삭제 |

피드백에는 답변 번호, 선택한 프로필, 평가와 원인, 모델·앱·프롬프트 버전 등이 들어갑니다. 질문과 답변 전문은 DB에 저장하지 않습니다. 피드백의 답변 번호로 현재 화면과 기록을 연결하고, 나중에는 원인과 버전 단위로 개선할 부분을 찾습니다.

Cloud 서버의 로컬 디스크에 파일을 쓰는 것만으로 영속 보관을 대신할 수 없습니다. 서버 재시작이나 재배포와 관계없이 남길 평가는 외부 DB에 보관합니다.

참고: [Supabase PostgreSQL 연결](https://supabase.com/docs/guides/database/connecting-to-postgres), [Streamlit 데이터 연결](https://docs.streamlit.io/develop/concepts/connections/connecting-to-data).
