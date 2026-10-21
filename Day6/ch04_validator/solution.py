from datetime import date
from pydantic import BaseModel, ValidationError, field_validator, model_validator


class EventBooking(BaseModel):
    event_name: str
    start_date: date
    end_date: date
    coupon: str | None = None

    @field_validator('coupon')
    @classmethod
    def normalize_coupon(cls, value: str | None) -> str | None:
        return value.strip().upper() if value is not None else None

    @model_validator(mode='after')
    def dates_in_order(self) -> 'EventBooking':
        if self.end_date < self.start_date:
            raise ValueError('종료일이 시작일보다 빠릅니다')
        return self


def main() -> None:
    data = EventBooking(event_name='특강', start_date='2026-10-21',
                        end_date='2026-10-22', coupon='  fall10  ')
    print(data.coupon)
    try:
        EventBooking(event_name='특강', start_date='2026-10-22', end_date='2026-10-21')
    except ValidationError as error:
        print(error.errors()[0]['type'])
    print('04장 정답 실행 성공')


if __name__ == '__main__':
    main()
