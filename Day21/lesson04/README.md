# 4차시. 피드백을 Supabase에 영속 저장하기

## 1. 학습목표

[오늘 수업 안내](../TODAY_GUIDE.md)를 읽습니다. 지금까지의 피드백은 브라우저 연결에만 남았습니다. 이번에는 기존에 사용한 Supabase에 평가를 보관하고 앱의 임시 메모리와 DB의 보관 범위를 구분합니다.

- 서버의 DB 연결 값으로 피드백 테이블을 준비할 수 있습니다.
- 평가 하나를 저장하고 Supabase SQL Editor에서 찾을 수 있습니다.
- 서버를 재시작해도 DB의 평가가 남는지 확인할 수 있습니다.

## 2. 중요 알고리즘 및 코드를 읽을 때 반드시 알아야 할 내용

브라우저를 새로 연결하거나 서버를 다시 시작하면 세션의 평가 기록은 사라질 수 있습니다. 무료 클라우드의 로컬 파일도 계속 보관된다고 보장할 수 없습니다. 여러 번 배포하면서 평가를 이어 보려면 서버 밖의 DB에 저장해야 합니다.

앱의 서버가 `DATABASE_URL`로 Supabase Postgres에 연결합니다. 공개 웹 화면에는 이 값을 전달하지 않습니다. `prepare_database()`의 SQL이 피드백 테이블을 만들고, 공개 REST 접근 권한을 닫습니다. 전체 평가 조회는 프로젝트 소유자의 SQL Editor에서만 진행합니다.

```python
with database_connection() as conn:
    conn.execute(...)
```

`with` 블록이 정상 종료되면 DB 변경을 확정합니다. SQL 실행 중 오류가 발생하면 변경을 되돌립니다. 실제 코드의 `execute()`는 SQL과 값을 별도 인자로 받으며 `%s` 자리에 값을 안전하게 전달합니다. 사용자 값을 문자열로 붙여 SQL을 만들지 않습니다.

저장 SQL의 `ON CONFLICT (message_id)`는 같은 답변 번호가 이미 있으면 평가와 이유를 갱신한다는 뜻입니다. 같은 평가를 다시 저장해도 새 행을 계속 늘리지 않습니다. 생성 조건과 버전은 처음 저장한 답변의 값으로 유지합니다.

참고: [Supabase PostgreSQL 연결](https://supabase.com/docs/guides/database/connecting-to-postgres), [psycopg 값 전달](https://www.psycopg.org/psycopg3/docs/basic/params.html), [Streamlit 데이터 연결과 보관](https://docs.streamlit.io/develop/concepts/connections/connecting-to-data).

## 3. 코드 제공

실행 파일은 [main.py](main.py)입니다. 먼저 [서비스 연결 안내](../BACKEND_GUIDE.md)의 Supabase 준비를 진행합니다. Connect의 **Session pooler** URI에 본인의 DB 비밀번호를 넣어 `.env`의 `DATABASE_URL`로 저장합니다. 예시 주소를 그대로 사용하지 않습니다.

Windows CMD에서 패키지를 설치한 뒤 앱을 실행합니다. `.env`가 이미 있으면 복사를 생략합니다.

```bat
cd /d C:\AI4\KDT_Personal_Travel\lesson04
python -m pip install -r requirements.txt
copy .env.example .env
notepad .env
python -m streamlit run main.py
```

`GROQ_API_KEY`와 `DATABASE_URL`이 필요합니다. Local URL을 열고 사이드바의 **피드백 테이블 준비**를 누릅니다. `피드백 테이블 준비 완료`를 확인한 뒤 대화를 시작합니다. 종료는 Ctrl+C입니다.

### 1단계. 첫 평가를 DB에서 찾기

‘제주에서 자가용으로 여행할 하루 일정을 제안해 주세요’라고 보냅니다. 완성 답변에서 ‘개선 필요’와 ‘조건 미반영’을 선택하고 저장에 동의해 **피드백 저장**을 누릅니다. `피드백 저장 완료`가 보이면 답변 ID를 확인합니다.

Supabase SQL Editor에서 다음 조회를 실행합니다. 이 코드는 데이터를 바꾸지 않고 최근 기록만 보여 줍니다.

```sql
select message_id, rating, reason, profile, prompt_version
from public.kdt_travel_feedback
order by created_at desc
limit 10;
```

화면의 답변 ID와 같은 행을 찾습니다. `rating`은 0, `reason`은 `조건 미반영`입니다. 현재 `database_record()`의 `return dict(record)`는 원래 평가 항목을 그대로 DB 저장에 사용합니다.

### 2단계. DB에 저장할 이유 표시 바꾸기

`database_record()` 함수만 교체합니다.

```python
def database_record(record):
    row = dict(record)
    if row["rating"] == 0:
        row["reason"] = "개선:" + row["reason"]
    return row
```

`dict(record)`는 저장용 복사본을 만듭니다. 복사본의 이유 앞에 `개선:`을 붙이므로 화면의 원래 선택값은 바뀌지 않습니다. 내보내기 정책과 DB 저장 정책은 바꾸는 위치가 다릅니다.

### 3단계. 같은 평가를 저장하고 보관 확인

같은 답변을 다시 평가해 저장한 뒤 SQL을 다시 실행합니다. 같은 `message_id`의 `reason`이 `개선:조건 미반영`으로 바뀌고 해당 번호의 행은 하나인지 확인합니다. 코드 변경으로 연결이 초기화됐다면 같은 질문의 새 답변을 평가하고 새 ID로 비교합니다.

CMD에서 Ctrl+C로 앱을 종료한 뒤 같은 실행 명령으로 시작합니다. 새 연결의 화면에는 이전 대화가 복원되지 않아도, SQL Editor에서 저장한 평가가 남아 있어야 합니다. 공개 앱의 **이 연결에서 저장한 피드백**은 전체 DB 목록이 아닙니다.

### 예상 결과

| 조작 | 결과 |
| --- | --- |
| 테이블 준비 성공 | `피드백 테이블 준비 완료` |
| 평가 저장 성공 | `피드백 저장 완료`, DB에 같은 답변 ID |
| 수정 전 rating=0 | `reason = 조건 미반영` |
| 수정 후 rating=0 | `reason = 개선:조건 미반영` |
| 같은 답변 재저장 | 같은 번호의 행 하나 유지 |
| 서버 재시작 | 화면의 세션은 초기화될 수 있으나 DB 행 유지 |

<details>
<summary>DB 준비 실패가 보일 때</summary>

프로젝트가 활성 상태인지, Session pooler 주소·사용자 이름·DB 비밀번호가 올바른지 확인합니다. URI의 비밀번호 예약문자는 URL 인코딩해야 합니다. 수정한 `.env`는 앱을 종료하고 다시 실행해 반영합니다. 연결 문자열을 화면이나 로그에 출력하지 않습니다.

</details>

## 4. 복습 과제

같은 답변을 ‘도움이 됨’으로 다시 평가합니다. SQL Editor에서 해당 답변의 `rating`이 1로 바뀌고 같은 ID의 행은 하나인지 확인합니다. 새로운 답변을 평가하면 다른 ID의 행이 생긴다는 차이를 기록합니다.

현재 세션 다운로드와 DB 조회에서 `reason`의 표시가 다른 이유를 `database_record()`의 역할로 설명합니다. 다음 차시는 제공되는 기본 저장 정책으로 시작합니다.
