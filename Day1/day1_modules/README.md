# Python 기초 모듈 실습

기존 `day1_practice.py`의 설명, 추가 과제와 실행 기능을 주제별 모듈로 분리했습니다.
Python 3만 있으면 실행할 수 있으며 추가 패키지 설치는 필요하지 않습니다.

## 실행 방법

### 브라우저에서 실습

`web/index.html` 파일을 더블 클릭하면 브라우저에서 열립니다.
다섯 실습의 입력과 결과를 웹 화면에서 확인할 수 있습니다.
HTML, CSS, JavaScript만 사용하므로 서버, 인터넷 연결, 패키지 설치가 필요 없습니다.
브라우저에서는 JavaScript로 같은 실습 동작을 구현하며, Python 코드를 직접 실행하지 않습니다.
각 화면의 “Python 예제 보기”를 펼치면 대응하는 학습 코드를 볼 수 있습니다.

### Python으로 실습

`C:\AI4`에서 실행:

```powershell
python -m day1_modules
```

또는 실습 폴더 안에서 실행:

```powershell
cd C:\AI4\day1_modules
python main.py
```

메뉴에서 1~5를 선택하면 실습이 실행되고 메뉴로 돌아옵니다. 0은 종료입니다.

## 파일 구성

```text
day1_modules/
├── __init__.py          # 패키지 표시
├── __main__.py          # python -m 실행 진입점
├── main.py              # 직접 실행 진입점, 종료 처리
├── menu.py              # 실습 모듈 연결 및 메뉴
├── input_utils.py       # 공통 정수 입력 함수
└── lessons/
    ├── __init__.py
    ├── variables.py     # 실습 1: 변수와 연산
    ├── conditions.py    # 실습 2: 입력과 조건문
    ├── lists.py         # 실습 3: 리스트와 반복문
    ├── multiplication.py # 실습 4: 중첩 반복문과 구구단
    └── guess_number.py  # 실습 5: 숫자 맞추기 게임
```

## 복습 방법

1. 원하는 실습의 `lessons` 모듈을 열고 코드를 읽습니다.
2. 메뉴에서 해당 실습을 실행하여 결과를 확인합니다.
3. 실습 마지막에 나오는 추가 과제를 해당 모듈에 구현합니다.
4. 프로그램을 다시 실행해 변경 결과를 확인합니다.

`from ... import ...`는 다른 모듈의 함수를 가져옵니다. 실습 모듈의
`from ..input_utils import read_int`에서 `..`는 상위 패키지를 뜻합니다.
각 실습 파일은 메뉴를 통해 실행하세요.
