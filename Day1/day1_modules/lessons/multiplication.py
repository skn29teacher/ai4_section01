"""실습 4: multiplication."""

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
