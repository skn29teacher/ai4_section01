"""실습 2: conditions."""

from ..input_utils import read_int

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
