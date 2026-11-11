# 개인화 여행 챗봇 — 피드백 수집과 무료 클라우드 배포

[오늘 수업 안내](TODAY_GUIDE.md)부터 읽고 [1차시](lesson01/README.md)를 시작합니다. Day20의 Groq 여행 챗봇을 이어 사용하며, 여행 선호에 맞춘 답변과 답변별 피드백을 더합니다.

| 차시 | 교안 | 새로 확인할 결과 |
| --- | --- | --- |
| 1 | [여행 프로필 적용](lesson01/README.md) | 같은 질문에도 선택한 여행 조건을 반영 |
| 2 | [답변별 피드백 연결](lesson02/README.md) | 평가가 어떤 답변의 것인지 구분 |
| 3 | [동의와 최소 로그](lesson03/README.md) | 동의한 평가만 필요한 항목으로 내보내기 |
| 4 | [Supabase 영속 저장](lesson04/README.md) | 앱을 다시 시작해도 DB에 평가 유지 |
| 5 | [저장 실패 복구](lesson05/README.md) | 실패한 평가를 같은 번호로 재전송 |
| 6 | [공개 서비스 운영 제한](lesson06/README.md) | 긴 입력과 연속 호출을 안내하며 제어 |
| 7 | [Streamlit 무료 배포](lesson07/README.md) | 다른 기기에서 접속할 개인 서비스 주소 |
| 8 | [피드백으로 개선·재배포](lesson08/README.md) | 버전별 평가와 수정한 여행 안내 비교 |

각 차시 폴더의 `main.py`가 해당 시점의 실행 파일입니다. 과제를 마치지 않아도 다음 차시 파일에서 계속 진행할 수 있습니다. `.env.example`을 `.env`로 복사해 본인의 값을 입력하고, 실제 `.env`는 Git에 올리지 않습니다.

4차시부터 연결할 서비스는 [BACKEND_GUIDE.md](BACKEND_GUIDE.md), 배포 절차는 [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)를 참고합니다. 로컬 실습은 Windows CMD와 기존 Python 환경에서 진행합니다.
