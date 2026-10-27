# 요구사항 대응표

| ID | 구현 위치 | 자동 검증 근거 |
| --- | --- | --- |
| R01 회원가입 | app/routes/api.py signup, db/schema.sql users, app/static/app.js authScreen | 가입 정규화·해시·역할 주입, 중복, 필수 입력·길이 검증 |
| R02 인증·권한 | app/auth.py, app/routes/api.py login/logout/me, app/config.py | 비밀번호 실패, CSRF·출처, Reload 로그인 유지, 이전 쿠키 재사용 차단, 만료 |
| R03 찾기 목업 | app/routes/api.py forgot, app/static/app.js authScreen | 목업 메시지와 DB 비밀번호 불변 |
| R04 작성·목록 | app/routes/api.py create_post/posts, app/static/app.js list/editor | 제목과 세션 기준 본인 여부 반환, `내 글` 배지, 비로그인·타인·관리자·로그아웃 구분, 0/1/10/11/21개, 잘못된 페이지, 작성자 조작·공백·길이 |
| R05 수정·삭제 | app/routes/api.py post_or_404/edit_post/update_post/delete_post | 작성자만 변경·원문 조회, 타인·관리자 변경 차단, 삭제 후 404, 마지막 페이지 보정 |
| R06 댓글 | app/routes/api.py comments/create_comment, db/schema.sql comments, app/static/app.js commentList | 로그인·공백·길이·글별 정렬, 고아 댓글 방지, 회원 ID 기준 `내 댓글` 배지, 동일 닉네임·타인·비로그인·로그아웃 구분 |
| R07 마스킹 | app/services/masking.py, 표시 API, app/static/app.js esc | 반복·겹침·리터럴 특수문자·대소문자·일반 문장·원문 편집 분리, HTML 이스케이프는 브라우저 수동 확인 |
| R08 초기 사전 | db/seed.json, docs/masking_sources.md, scripts/init_db.py | 원본·라이선스 웹 조사 및 초기화에 20개 규칙 적재 |
| R09 관리자 사전 | app/routes/api.py list_rules/create_rule/delete_rule, app/static/app.js admin | 일반 사용자·비로그인 차단, 중복·빈 값·정규식 차단, 추가·삭제 후 기존 데이터 재표시 |

테스트 코드는 tests/test_app.py에 있다. DB 제약, 백업, WSGI import, 공개 설정의 Secure 쿠키·허용 호스트, 화면 경로와 정적 파일도 검증한다. 실제 PythonAnywhere 계정에 대한 공개 배포 검증은 별도이며 아직 수행하지 않았다.
