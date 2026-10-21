"""04장 학생 실습: 예약 기간과 쿠폰 코드 검증."""
from datetime import date
from pydantic import BaseModel, field_validator, model_validator


class EventBooking(BaseModel):
    event_name: str
    start_date: date
    end_date: date
    coupon: str | None = None

    # TODO 1: field_validator로 쿠폰을 대문자로 정규화
    # TODO 2: model_validator(mode='after')로 종료일 >= 시작일 확인


def main() -> None:
    print('TODO: 정상/역전된 날짜를 각각 입력하세요.')


if __name__ == '__main__':
    main()
