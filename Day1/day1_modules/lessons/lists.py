"""실습 3: lists."""

from ..input_utils import read_int

def practice_3():
    """원본: day1-3.py / 리스트, append(), for, range(), %, f-string."""
    print("\n[3] 리스트에서 짝수 찾기")
    print("목표: 정수 5개를 리스트에 저장하고 짝수만 출력합니다.")
    scores = []
    for i in range(5):
        score = read_int(f"{i + 1}번째 숫자를 입력하세요: ")
        scores.append(score)

    print("리스트의 값:", scores)
    print("짝수:")
    for number in scores:
        if number % 2 == 0:
            print(number)
    print("확인: 1, 2, 3, 4, 5를 입력하면 2와 4가 출력됩니다.")
    print("추가 과제: 홀수만 출력하고 짝수의 개수도 구하세요.")
