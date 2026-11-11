# 7차시. 나의 Streamlit 챗봇을 무료 클라우드에 배포하기

## 1. 학습목표

[오늘 수업 안내](../TODAY_GUIDE.md)를 읽습니다. 개인화·평가 저장·호출 제한이 있는 앱을 인터넷에서 열 수 있게 만듭니다. 이번에는 모델 코드를 다시 만드는 대신 실행 장소와 비밀값 전달 방식을 바꿉니다.

- 본인 GitHub 저장소의 `lesson07/main.py`를 배포 진입 파일로 지정할 수 있습니다.
- Cloud Secrets에 키를 넣고 휴대전화에서 챗봇을 열 수 있습니다.
- 표시 버전을 바꿔 GitHub에 전송한 뒤 배포 반영을 확인할 수 있습니다.

## 2. 중요 알고리즘 및 코드를 읽을 때 반드시 알아야 할 내용

내 PC의 `localhost` 주소를 다른 사람에게 보내도 그 사람의 기기에서는 앱이 열리지 않습니다. `localhost`는 주소를 연 기기 자신을 가리킵니다. 클라우드 배포는 인터넷에 있는 서버가 내 `main.py`를 실행하게 만드는 과정입니다.

GitHub에는 코드와 패키지 목록을 올립니다. Groq 키와 DB 연결 문자열은 Cloud Secrets에 따로 넣습니다. Community Cloud의 최상위 Secrets 키는 환경변수로 전달되므로 현재 앱의 `os.getenv()`가 그대로 읽습니다. 이때 브라우저가 Groq 키를 받아 호출하는 것이 아니라 Streamlit 서버가 호출합니다.

### 배포할 파일을 정하는 곳

| 설정 | 이번 값 | 역할 |
| --- | --- | --- |
| Branch | `main` | 어느 코드 이력을 사용할지 선택 |
| Main file path | `lesson07/main.py` | 어떤 앱을 실행할지 선택 |
| 패키지 파일 | `lesson07/requirements.txt` | 서버에 필요한 라이브러리 설치 |
| Secrets | 최상위 `GROQ_API_KEY`, `DATABASE_URL` | 서버가 읽는 본인 연결 값 |

`release_label()`은 현재 화면의 배포 표시를 만듭니다. 표시를 한 곳에서 바꾸면 새 코드가 반영됐는지 눈으로 비교할 수 있습니다. 이 표시 자체가 코드 전송이나 배포를 실행하는 것은 아닙니다.

참고: [Community Cloud 배포](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy), [Secrets 관리](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management).

## 3. 코드 제공

실행 파일은 [main.py](main.py)입니다. 로컬 실행은 Windows CMD에서 이 차시 폴더로 이동합니다. 아래 명령의 `copy`는 `.env`가 아직 없을 때만 실행합니다. 기존 파일이 있으면 복사를 생략하고 값을 확인합니다.

```bat
cd /d C:\AI4\KDT_Personal_Travel\lesson07
python -m pip install -r requirements.txt
copy .env.example .env
notepad .env
python -m streamlit run main.py
```

`GROQ_API_KEY`와 `DATABASE_URL`을 본인 값으로 저장합니다. 새 DB라면 [서비스 연결 안내](../BACKEND_GUIDE.md)의 로컬 테이블 준비를 먼저 진행합니다. `SHOW_DEMO_TOOLS=true`로 재실행해 준비하고, 완료 뒤 다시 `false`로 돌려 재실행합니다. 클라우드에 올릴 때에는 `SHOW_DEMO_TOOLS=false`를 사용합니다. Local URL을 열어 대화와 평가 저장을 확인한 뒤 CMD에서 Ctrl+C로 종료합니다.

### 1단계. 기존 화면과 DB 연결 확인

프로필을 적용하고 ‘속초에서 대중교통으로 반나절 일정을 제안해 주세요’라고 보냅니다. 답변을 평가하고 Supabase SQL Editor에서 저장된 평가를 확인합니다. 모델 답변은 매번 달라도 평가 저장 안내와 DB의 답변 번호는 대응해야 합니다.

### 2단계. 개인 저장소와 Secrets로 배포

[배포 안내](../DEPLOY_GUIDE.md)의 1~4번을 순서대로 진행합니다. 저장소의 `.env` 제외 여부를 확인하고 본인 GitHub 저장소에 커밋합니다. Community Cloud의 **Main file path**에는 `lesson07/main.py`를 정확히 입력합니다.

Secrets의 최상위 키에 본인의 연결 값을 입력하고 Deploy를 누릅니다. 휴대전화에서 `streamlit.app` 주소를 열어 새 프로필과 질문을 제출합니다. 공개 URL을 연 새 연결에는 로컬 PC의 프로필이나 대화가 자동으로 따라오지 않습니다.

### 3단계. 배포 표시 한 곳을 바꾸고 다시 전송

현재 `release_label()`의 시작 반환문은 `return "개인화 여행 챗봇 · 공개 실습판"`입니다. 이 함수만 아래의 짧은 함수로 교체합니다.

```python
def release_label():
    return "나의 여행 챗봇 · 공개 2판"
```

로컬 화면에서 바뀐 문구를 확인한 뒤 [배포 안내의 코드 수정 반영](../DEPLOY_GUIDE.md#5-코드-수정-반영하기)에 따라 커밋하고 `git push`합니다. 앱을 다시 열어 같은 문구가 보이는지 확인합니다. 반영 전 브라우저가 열려 있었다면 새로고침합니다.

### 예상 결과

| 조작 | 보일 결과 |
| --- | --- |
| 휴대전화에서 로컬 URL 열기 | 내 PC에서 쓰던 앱 주소로 접속할 수 없음 |
| 배포 URL 열기 | 여행 프로필과 입력창 표시 |
| Cloud에서 질문 제출 | 답변이 생성되고 본인 프로필 조건 표시 |
| 평가 저장 | Supabase에 답변 번호와 평가 저장 |
| 함수 수정 후 GitHub 전송 | `나의 여행 챗봇 · 공개 2판` 표시 |

**AI 답변 예시:** ‘시내에서 출발해 버스로 이동 가능한 두 곳을 묶고, 환승 시간을 여유 있게 잡겠습니다. 최신 운행 시간은 출발 전에 확인하세요.’ 문장 일치 대신 선택한 이동 수단과 여행 속도가 반영되는지 봅니다.

<details>
<summary>설치 화면에서 멈추거나 키 안내가 보일 때</summary>

Community Cloud의 앱 로그에서 설치 오류인지 실행 오류인지 먼저 구분합니다. 설치 오류이면 `lesson07/requirements.txt`와 Python 버전을 확인합니다. 키 안내이면 Secrets가 최상위 키인지 확인한 뒤 저장하고 앱을 재시작합니다. 비밀값을 로그에 출력해 확인하지 않습니다. DB 연결 오류이면 Supabase 프로젝트의 활성 상태와 Session pooler 연결 문자열을 확인합니다.

</details>

## 4. 복습 과제

표시 문구에 자신의 서비스 이름을 넣고 한 번 더 배포합니다. 휴대전화에서 보이는 문구와 앱 URL을 기록합니다. 제출 자료에는 Secrets와 DB 연결 문자열을 넣지 않습니다.

다른 브라우저 창에서 서로 다른 여행 프로필을 적용합니다. 한 창의 대화가 다른 창에 나타나지 않는지 확인하고, 평가 저장은 같은 Supabase 테이블에 모인다는 차이를 한 문장으로 설명합니다.
