"""
Python 기초 복습 실습
====================
실행 방법: 터미널에서 python day1_practice.py

학습 순서
1. 변수와 연산 → 2. 입력과 조건문 → 3. 리스트와 반복문
4. 중첩 반복문 → 5. 난수와 while 반복문

사용 방법
- 메뉴에서 실습 번호를 선택하세요. 종료 후 메뉴로 돌아옵니다.
- 각 실습의 코드를 읽고, 아래 추가 과제를 직접 수정하며 풀어 보세요.
- input()은 문자열을 반환하므로 숫자 계산에는 int() 변환이 필요합니다.
- 이 파일은 Python 기본 기능과 표준 라이브러리 random만 사용합니다.
"""

import random


def read_int(prompt):
    """정수가 아닌 값을 입력하면 다시 입력받습니다."""
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("정수를 입력하세요. 예: 10")


def practice_1():
    """원본: day1-1.py / 변수, 정수, 덧셈, print()."""
    print("\n[1] 변수와 연산")
    print("목표: 두 변수에 숫자를 저장하고 합을 출력합니다.")
    number1 = 100
    number2 = 200
    print("number1 + number2 =", number1 + number2)
    print("추가 과제: 두 숫자를 바꾸고 뺄셈, 곱셈, 나눗셈도 출력하세요.")


def practice_2():
    """원본: day1-2.py / input(), int(), 비교 연산, if/else."""
    print("\n[2] 점수로 합격 여부 판단")
    print("목표: 입력한 점수가 60점 이상이면 합격을 출력합니다.")
    score = read_int("점수를 입력하세요: ")
    if score >= 60:
        print("합격")
    else:
        print("불합격")
    print("확인: 59는 불합격, 60과 61은 합격이어야 합니다.")
    print("추가 과제: 0~100 범위만 입력받도록 수정하세요.")


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


def practice_4():
    """원본: day1-4.py / 중첩 for, range(), f-string, end, 탭과 줄바꿈."""
    print("\n[4] 중첩 반복문으로 구구단 출력")
    print("목표: 바깥 반복문과 안쪽 반복문의 실행 순서를 이해합니다.")
    print("range(a, b)는 a부터 b-1까지 생성합니다.")

    print("\n연습 A: 2~4단을 각각 1~4까지 출력")
    for dan in range(2, 5):
        for i in range(1, 5):
            print(f"{dan} x {i} = {dan * i}", end="\t")
        print()

    print("\n연습 B: 한 행에 2~9단을 나란히 출력")
    for multiplier in range(1, 10):
        for dan in range(2, 10):
            print(f"{dan} x {multiplier} = {dan * multiplier}", end="\t")
        print()
    print("추가 과제: 원하는 단을 입력받아 1~9까지 출력하세요.")


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


def main():
    practices = {
        1: practice_1,
        2: practice_2,
        3: practice_3,
        4: practice_4,
        5: practice_5,
    }
    while True:
        print("\n========== Python 기초 복습 ==========")
        print("1. 변수와 연산")
        print("2. 입력과 조건문")
        print("3. 리스트와 반복문")
        print("4. 중첩 반복문과 구구단")
        print("5. 숫자 맞추기 게임")
        print("0. 종료")
        choice = read_int("실습 번호를 선택하세요: ")
        if choice == 0:
            print("실습을 종료합니다.")
            break
        if choice in practices:
            practices[choice]()
        else:
            print("0~5 중에서 선택하세요.")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\n실습을 종료합니다.")
