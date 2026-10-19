"""실습 선택 메뉴."""

from .input_utils import read_int
from .lessons.variables import practice_1
from .lessons.conditions import practice_2
from .lessons.lists import practice_3
from .lessons.multiplication import practice_4
from .lessons.guess_number import practice_5


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
