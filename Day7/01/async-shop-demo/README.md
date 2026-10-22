# 재고 조회로 배우는 FastAPI 동기·비동기

일반적인 쇼핑몰의 재고 조회를 예로 들어 다음 세 가지 처리 방식을 비교하는 학습 앱입니다.

- `blocking`: `async def` 안에서 `time.sleep()`을 사용하는 의도적인 문제 상황
- `async`: `await asyncio.sleep()`으로 비동기 I/O를 흉내 낸 방식
- `threaded`: 기존 동기 함수를 `asyncio.to_thread()`로 작업 스레드에 넘기는 방식

브라우저는 상품 세 개의 재고 요청을 거의 동시에 보냅니다. 각 요청 시간, 전체 완료 시간,
처리 도중 `/api/health`가 얼마나 빨리 응답하는지를 화면에서 확인할 수 있습니다.

## 실행 방법

PowerShell에서 프로젝트 폴더로 이동합니다.

```powershell
cd C:\AI4\Day7\async-shop-demo
```

현재 프로젝트의 가상환경에 필요한 패키지가 이미 있다면 바로 실행합니다.

```powershell
..\..\.venv\Scripts\python.exe -m uvicorn app:app --port 8010
```

패키지가 없다는 오류가 나오면 먼저 설치합니다.

```powershell
..\..\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

서버가 실행되면 브라우저에서 다음 주소를 엽니다.

```text
http://127.0.0.1:8010
```

종료할 때는 서버를 실행한 터미널에서 `Ctrl+C`를 누릅니다.

## 터미널에서도 비교하기

서버를 계속 실행한 상태에서 새 PowerShell을 열고 다음 명령을 실행합니다.

```powershell
cd C:\AI4\Day7\async-shop-demo
..\..\.venv\Scripts\python.exe probe.py
```

단일 worker 기준으로 보통 다음과 비슷한 결과가 나타납니다.

| 방식 | 요청 3개 전체 시간 | `/api/health` 응답 |
|---|---:|---|
| 블로킹 | 약 6초 | 블로킹 작업 뒤로 밀림 |
| 비동기 | 약 2초 | 즉시 응답 가능 |
| 스레드 | 약 2초 | 즉시 응답 가능 |

실제 시간은 컴퓨터 환경에 따라 조금 달라질 수 있습니다.

## 파일 구성

```text
async-shop-demo/
├─ app.py              # FastAPI 서버와 세 가지 재고 API
├─ probe.py            # httpx + asyncio.gather 성능 확인
├─ requirements.txt
├─ README.md
└─ static/
   ├─ index.html       # 학습 화면
   ├─ styles.css       # 반응형 스타일
   └─ app.js           # 동시 요청, 시간 측정, 결과 시각화
```

## 주요 API

- `GET /api/products/blocking/{id}`: 이벤트 루프를 막는 예제
- `GET /api/products/async/{id}`: 비동기 대기 예제
- `GET /api/products/threaded/{id}`: 동기 함수를 스레드에서 실행하는 예제
- `GET /api/health`: 서버가 다른 요청에 응답할 수 있는지 확인
- `GET /docs`: FastAPI 자동 API 문서

