# 8차시. 피드백 원인으로 개선하고 다시 배포하기

## 1. 학습목표

[오늘 수업 안내](../TODAY_GUIDE.md)를 읽습니다. 앱이 공개된 뒤에는 평가를 모으는 것에 더해 무엇부터 고칠지 정해야 합니다. 평가 수와 원인, 프롬프트 버전을 함께 보고 여행 응답 지침 한 곳을 개선합니다.

- 평가를 제출한 답변만 분모로 유용성 비율을 계산할 수 있습니다.
- 전체 운영 로그와 현재 연결의 요약을 구분할 수 있습니다.
- 지침 버전을 바꿔 새 답변의 평가에만 새 버전이 붙는지 확인할 수 있습니다.

## 2. 중요 알고리즘 및 코드를 읽을 때 반드시 알아야 할 내용

‘개선 필요’ 평가가 두 개 있다는 사실만으로 모델 전체가 나쁘다고 결론 내릴 수 없습니다. 어떤 여행 조건에서 어떤 이유가 반복됐는지 보면 고칠 후보를 좁힐 수 있습니다. 평가하지 않은 답변을 자동으로 불만족으로 계산하면 비율도 왜곡됩니다.

`show_feedback_summary()`는 현재 연결에서 저장에 성공한 평가 수와 개선 원인 수를 요약합니다. 도움 비율은 아래의 SQL로 계산합니다. 예를 들어 서로 다른 답변 3개에 도움 2개·개선 필요 1개가 있으면 도움 비율은 `2 / 3 × 100 = 66.7%`입니다. 미평가 답변은 분모에 들어가지 않습니다. 같은 답변 재평가는 최신 평가 하나로 계산합니다.

전체 운영 로그는 Supabase SQL Editor에서 조회합니다. 공개 앱에는 다른 방문자의 평가 목록을 보여 주지 않습니다. 표본이 적거나 질문 조건이 다르면 버전별 비율 차이를 성능 개선의 증거로 단정하지 않고, 다음에 확인할 가설로 사용합니다.

`improvement_policy()`는 지침 버전과 추가할 여행 규칙을 한 쌍으로 돌려줍니다. 함수 호출을 받는 `version, improvement = ...`는 반환값 두 개를 각각 다른 변수로 받는 문법입니다. 답변 성공 시 버전을 붙여 두므로 이전 답변을 나중에 평가해도 생성 당시 버전으로 기록됩니다.

참고: [PostgreSQL 집계 함수](https://www.postgresql.org/docs/current/functions-aggregate.html), [Community Cloud 앱 관리](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app), [Groq Responses API](https://console.groq.com/docs/responses-api).

## 3. 코드 제공

실행 파일은 [main.py](main.py)입니다. Windows CMD에서 실행합니다. `.env`가 이미 있으면 복사 명령을 생략합니다.

```bat
cd /d C:\AI4\KDT_Personal_Travel\lesson08
python -m pip install -r requirements.txt
copy .env.example .env
notepad .env
python -m streamlit run main.py
```

`GROQ_API_KEY`, `DATABASE_URL`을 입력하고 공개할 앱은 `SHOW_DEMO_TOOLS=false`로 설정합니다. 새 DB를 사용할 때만 [서비스 연결 안내](../BACKEND_GUIDE.md)의 로컬 테이블 준비를 진행합니다. 종료는 Ctrl+C입니다.

### 1단계. 원인과 버전별 평가 보기

현재 시작 함수에는 다음 줄이 있습니다.

```python
def improvement_policy():
    return "p2", "각 일정에 예상 비용과 확인이 필요한 항목을 구분해 적는다."
```

다음 질문을 보내 답변을 보고 평가를 저장합니다.

> 부산에서 대중교통으로 하루 코스를 짜 줘. 이동이 복잡하지 않게 해 줘.

Supabase SQL Editor에서 버전별 평가 수와 도움 비율을 확인합니다.

```sql
select prompt_version,
       count(*) as evaluated_answers,
       sum(rating) as helpful_answers,
       round(100.0 * sum(rating) / count(*), 1) as helpful_percent
from public.kdt_travel_feedback
group by prompt_version
order by prompt_version;
```

`count(*)`는 저장된 평가 행 수이고 `sum(rating)`은 1인 도움 평가 수입니다. 그룹에 행이 있는 경우만 출력되므로 미평가 버전이 0%로 만들어지지 않습니다. 이어 원인별 개선 필요 평가를 봅니다.

```sql
select prompt_version, reason, count(*) as needs_improvement
from public.kdt_travel_feedback
where rating = 0
group by prompt_version, reason
order by needs_improvement desc, prompt_version;
```

예를 들어 ‘조건 미반영’이 반복되고 실제 질문에 복잡한 환승이 문제였다면 이동수단과 환승 안내를 개선 후보로 정합니다. 실제 데이터에 그런 원인이 없다면 수치를 만들어 결론 내리지 말고 개선 가설로 구분합니다.

### 2단계. 지침과 버전을 한 함수에서 바꾸기

`improvement_policy()` 함수만 교체합니다.

```python
def improvement_policy():
    return "p3", "각 일정에 예상 비용과 확인 필요 항목을 나눈다. 대중교통 일정에는 구간별 이동수단을 적고 환승이 많은 대안은 따로 표시한다."
```

파일을 저장하고 **새 대화**를 눌러 이전 답변 내용이 새 답변에 영향을 주지 않게 합니다. 같은 프로필과 같은 질문으로 답변을 만들고 다시 평가를 저장합니다. 새 답변의 평가가 `p3`, 이전 평가가 `p2`로 남는지 SQL을 다시 실행합니다.

### 3단계. 같은 배포 주소에 개선판 반영

7차시에서 만든 Git 저장소 루트로 이동합니다. 8차시 ZIP만 사용한다면 아래 복사 단계를 생략하고 [배포 안내](../DEPLOY_GUIDE.md)에 따라 `lesson08/main.py`를 진입 파일로 배포합니다. 이미 7차시 주소가 있는 경우에만 다음처럼 같은 경로를 유지합니다. 아래 명령은 `lesson07/main.py`를 이번 8차시 파일로 덮어씁니다. 원래 ZIP과 Git 이력을 보관하고 진행합니다. 두 차시의 패키지와 환경변수 이름은 같습니다.

```bat
cd /d C:\AI4\KDT_Personal_Travel
copy lesson08\main.py lesson07\main.py
git add lesson07/main.py lesson08/main.py
git commit -m "Improve travel guidance from feedback"
git push
```

Cloud의 진입 파일은 계속 `lesson07/main.py`입니다. [배포 안내](../DEPLOY_GUIDE.md)에 따라 반영을 기다린 뒤 휴대전화에서 같은 앱 URL을 열어 새 질문과 평가를 보냅니다. `p3` 평가는 새로 생성된 답변에 붙어야 합니다.

일반 창과 시크릿 창에서 서로 다른 프로필을 설정해 두 창의 대화가 독립인지 확인합니다. Cloud 앱을 재시작하고 SQL Editor의 평가 행이 남아 있는지 봅니다. 배포된 서비스 주소, 새 지침 버전, 개선하려는 원인 한 가지를 기록합니다.

### 예상 결과

| 조작 | 결과 |
| --- | --- |
| 서로 다른 답변 도움 2개·개선 필요 1개 | 화면 요약은 전체 3개·개선 필요 1개, SQL 도움 비율 66.7% |
| 답변을 평가하지 않음 | 평가 비율의 분모에 추가하지 않음 |
| 수정 전 새 답변 평가 | `prompt_version = p2` |
| 수정 후 새 답변 평가 | `prompt_version = p3` |
| 이전 답변을 나중에 평가 | 이전 생성 버전 유지 |
| 앱 재시작 | DB의 과거 평가·버전 유지 |

**AI 답변 예시:** ‘구간별로 지하철 또는 버스를 적고 환승이 많은 대안은 따로 표시하겠습니다. 예상 비용과 현장 확인이 필요한 요금도 나눠 안내합니다.’ 문장 일치보다 이동 구간·확인 필요 항목을 실제로 구분하는지 봅니다. 지침 변경이 항상 품질 상승을 보장하지는 않습니다.

## 4. 복습 과제

운영 집계에서 개선 후보 하나를 고르고 ‘관찰한 평가 수·원인·재현 질문·바꿀 지침·다음에 확인할 결과’를 다섯 문장 이내로 기록합니다. 아직 평가가 적다면 표본이 작다는 점을 함께 적습니다.

다른 여행 질문 2개로 수정 지침을 확인합니다. 두 질문 모두에서 꼭 포함해야 할 항목 하나와 사실처럼 단정하면 안 되는 항목 하나를 정합니다. 이 기록과 버전별 피드백을 다음 단원의 응답 품질 점검 자료로 이어 사용합니다.
