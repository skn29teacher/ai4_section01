# 개인 Streamlit 챗봇 배포하기

## 1. 본인 저장소에 실행 파일 올리기

압축을 푼 `C:\AI4\KDT_Personal_Travel` 폴더를 사용합니다. GitHub에서 본인 계정의 새 저장소를 만들고 이름을 `personal-travel-chatbot`으로 정합니다. 처음에는 README·.gitignore 자동 생성을 선택하지 않아 빈 저장소로 준비합니다. 저장소 주소의 **Code → HTTPS** 값을 복사합니다. 공개 저장소에는 코드만 올리고 실제 비밀값과 로그는 제외합니다.

기존 수업 저장소 밖에서 아래 명령을 실행합니다. `본인_저장소_HTTPS_URL` 부분은 복사한 실제 주소로 바꿉니다. `git add .`는 이 폴더의 파일을 다음 커밋에 포함하며, 실제 `.env`와 Secrets는 `.gitignore`로 제외해야 합니다.

```bat
cd /d C:\AI4\KDT_Personal_Travel
git init -b main
git check-ignore lesson07/.env
git add .
git status --short
```

`git check-ignore`는 `lesson07/.env`를 출력해야 합니다. 개별 ZIP에 `lesson06` 또는 `lesson08`만 있다면 이 명령의 경로를 해당 차시의 `.env`로 바꾸고, 아래 Main file path도 해당 `lessonXX/main.py`로 지정합니다. 다른 절차는 같습니다. `git status --short`에 실제 `.env`·키 파일·평가 파일이 보이면 커밋 전에 제외 규칙을 바로잡습니다. `.env.example`은 가짜 값의 양식이므로 포함합니다. 이후 원본 코드를 커밋해 GitHub로 전송합니다.

```bat
git commit -m "Add personal travel chatbot"
git remote add origin 본인_저장소_HTTPS_URL
git push -u origin main
```

`origin`이 이미 있다면 `git remote -v`로 본인 저장소인지 확인하고 기존 연결을 사용합니다. GitHub 로그인은 브라우저 또는 기존 Git 인증 창에서 진행합니다. 비밀번호나 토큰을 명령어에 붙이지 않습니다.

## 2. Community Cloud에서 앱 생성하기

[Streamlit Community Cloud](https://share.streamlit.io)에 GitHub 계정으로 로그인합니다. **Create app**에서 기존 앱을 배포하는 항목을 선택하고 다음 값을 입력합니다.

| 항목 | 입력할 값 |
| --- | --- |
| Repository | 본인 계정의 `personal-travel-chatbot` |
| Branch | `main` |
| Main file path | `lesson07/main.py` |
| App URL | 사용 가능한 본인 앱 이름 |
| Advanced settings의 Python | 실습과 맞는 Python 3.12 |

패키지는 `lesson07/requirements.txt`에서 설치됩니다. 저장소의 여러 차시 파일 중 어떤 파일을 실행할지는 **Main file path**가 결정합니다.

## 3. Secrets 입력 후 배포하기

**Advanced settings → Secrets**에 최상위 TOML 키를 입력합니다. 값은 로컬 `.env`에서 본인의 값을 옮기며, 아래는 가짜 예시입니다.

```toml
GROQ_API_KEY = "example-groq-key"
DATABASE_URL = "postgresql://postgres.example:example-password@example.pooler.supabase.com:5432/postgres?sslmode=require"
SHOW_DEMO_TOOLS = "false"
```

`[keys]` 같은 묶음 제목을 만들지 않습니다. 최상위 키가 환경변수로 전달되어 기존 `os.getenv()` 코드가 읽습니다. 클라우드에서 `.env`를 Git으로 올릴 필요는 없습니다. 비밀값을 수정한 뒤에는 설정을 저장하고 앱을 재시작합니다.

로컬 앱에서 같은 DB의 피드백 테이블을 먼저 준비합니다. [서비스 연결 안내](BACKEND_GUIDE.md)의 6~8차시 로컬 준비 절차를 따라 준비한 뒤 도구 설정을 `false`로 돌립니다. 클라우드 화면에는 테이블 준비 버튼을 표시하지 않습니다.

**Deploy**를 누르고 설치와 시작이 끝나기를 기다립니다. 표시되는 `https://본인앱.streamlit.app` 주소를 새 창에서 엽니다. 여행 질문과 평가 저장을 실행합니다. 로컬에서 미리 준비한 같은 테이블을 그대로 사용합니다.

Community Cloud에서는 저장소 루트가 작업 폴더입니다. 현재 앱은 클라우드 환경변수에서 키를 읽으므로 로컬 `.env`가 없는 상태로 실행됩니다. 상대 경로로 로컬 키 파일을 찾도록 코드를 바꾸지 않습니다.

## 4. 다른 기기에서 확인하기

휴대전화에서 앱 URL을 엽니다. 여행 프로필을 선택하고 ‘부산에서 반나절 여행 일정을 제안해 주세요’라고 보냅니다. 답변이 완성되면 피드백 수집에 동의하고 평가를 제출합니다. Supabase SQL Editor에서 새 행이 추가됐는지 확인합니다.

다른 브라우저나 시크릿 창에서는 프로필과 대화를 새로 시작합니다. 한 창의 대화가 다른 창에 보이지 않는지 확인합니다. Cloud 앱을 재시작한 뒤 DB의 평가가 남아 있는지 확인합니다.

## 5. 코드 수정 반영하기

`lesson07/main.py`의 표시 문구를 바꾸고 저장합니다. 같은 배포 경로를 커밋해 전송하면 앱에 반영됩니다. 개별 ZIP의 다른 차시 경로를 배포했다면 아래 `git add`에도 실제 배포한 `lessonXX/main.py` 경로를 사용합니다.

```bat
cd /d C:\AI4\KDT_Personal_Travel
git add lesson07/main.py
git commit -m "Update chatbot release label"
git push
```

8차시 ZIP만으로 `lesson08/main.py`를 직접 배포했다면 복사를 생략하고 `git add lesson08/main.py`로 수정 사항을 커밋합니다.

7차시 배포를 이어서 8차시에서 개선한 앱으로 바꿀 때에는 `lesson08/main.py`를 현재 배포 경로인 `lesson07/main.py`에 복사합니다. 이 명령은 로컬 `lesson07/main.py`를 덮어씁니다. 수정 전 파일을 다시 사용하려면 배포 ZIP 원본 또는 Git 이력을 보관합니다.

```bat
copy lesson08\main.py lesson07\main.py
git add lesson07/main.py lesson08/main.py
git commit -m "Improve travel advice from feedback"
git push
```

클라우드 화면에 표시되는 버전을 확인하고 새 피드백의 버전이 바뀌었는지 SQL Editor에서 대조합니다. GitHub 전송은 모델을 자동 학습시키지 않습니다. 이번 수정은 앱이 모델에 주는 응답 지침을 개선하는 것입니다.

Community Cloud는 무료 호스팅입니다. Groq·Supabase의 무료 사용 범위와 계정 한도는 별도로 확인합니다. 세션 단위 호출 제한만으로 전체 이용자의 비용이나 오용을 막을 수는 없으므로 개인 실습 범위에서 사용량을 확인합니다.

참고: [배포 설정](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy), [Secrets 관리](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management), [패키지 설치](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies).
