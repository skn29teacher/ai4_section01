"""여러 실습에서 함께 사용하는 입력 함수."""

def read_int(prompt):
    """정수가 아닌 값을 입력하면 다시 입력받습니다."""
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("정수를 입력하세요. 예: 10")
