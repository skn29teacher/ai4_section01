"""실습 5: guess_number."""

import random

from ..input_utils import read_int

def practice_5():
    """원본: day1-5.py / random.randint(), while, 조건문, +=, break."""
    print("\n[5] 숫자 맞추기 게임")
    print("목표: 컴퓨터가 고른 1~100의 정수를 맞힐 때까지 반복합니다.")
    print("randint(1, 100)은 1과 100을 모두 포함합니다.")
    com_number = random.randint(1, 100)
    count = 0
    while True:
        user_number = read_int("1~100 사이의 숫자를 입력하세요: ")
        if not 1 <= user_number <= 100:
            print("1~100 사이로 입력하세요. 이번 입력은 시도 횟수에 포함하지 않습니다.")
            continue

        count += 1
        if user_number > com_number:
            print("입력한 숫자가 정답보다 큽니다.")
        elif user_number < com_number:
            print("입력한 숫자가 정답보다 작습니다.")
        else:
            print(f"정답입니다! 총 시도 횟수: {count}")
            break
    print("추가 과제: 시도를 7번으로 제한하고 실패하면 정답을 공개하세요.")
