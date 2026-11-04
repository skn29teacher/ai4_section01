
import requests
import json

# API 기본 주소
BASE_URL = "https://apis.data.go.kr/1760000/PblJobService/getItemPosition"

# 공공데이터포털에서 발급받은 인증키
SERVICE_KEY = 'U5i63xpIWM48raIRQBYpUXbA/wKd0iO6n/n1+JISyoEW1gWcEiz2No2fHPeid5TZoQN0HV85WyGv6LPwaQ8n4w=='

# 요청 파라미터
params = {
    "serviceKey": SERVICE_KEY,
    "idx": 8
}

try:
    response = requests.get(
        BASE_URL,
        params=params,
        timeout=10
    )

    # HTTP 상태 코드 확인
    response.raise_for_status()

    print("HTTP 상태 코드:", response.status_code)
    print("응답 데이터:")

    # JSON 응답 처리
    try:
        data = response.json()
        print(json.dumps(data, indent=4, ensure_ascii=False))

    except ValueError:
        # XML 응답일 경우
        import xmltodict

        # API 응답이 requests의 response인 경우
        data = xmltodict.parse(response.text)

        # XML이 이미 문자열 변수에 있다면
        # data = xmltodict.parse(xml_string)

        # items = data["response"]["body"]["items"]["item"]

        # for item in items:
        #     print(item)
        # XML 문자열 → 딕셔너리
        data = xmltodict.parse(response.text, force_list=("item",))

        # 딕셔너리 → JSON 문자열 출력
        print(json.dumps(data, ensure_ascii=False, indent=2))

except requests.exceptions.RequestException as e:
    print("API 호출 오류:", e)
