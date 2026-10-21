"""05장 학생 실습: 강좌와 수강생의 중첩 관계 모델링."""
from pydantic import BaseModel


# TODO 1: Learner(name:str, score:int 0~100)
class Learner(BaseModel):
    pass


# TODO 2: Course(title:str, learners:list[Learner] 최소 1명)
class Course(BaseModel):
    pass


def main() -> None:
    print('TODO: dict 데이터를 중첩 모델로 검증하세요.')


if __name__ == '__main__':
    main()
