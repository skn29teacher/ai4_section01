from pydantic import BaseModel, Field, ValidationError


class Product(BaseModel):
    title: str = Field(min_length=2, max_length=60)
    price: int = Field(gt=0)
    stock: int = Field(default=0, ge=0)
    sku: str = Field(pattern=r'^SKU-[0-9]{4}$')


def main() -> None:
    product = Product(title='키보드', price=50000, sku='SKU-0001')
    print('검증 성공:', product.model_dump())

    invalid_cases = [
        {'title': 'A'},
        {'title': 'A' * 61},
        {'price': 0},
        {'stock': -1},
        {'sku': 'SKU-001'},
    ]
    for changes in invalid_cases:
        data = product.model_dump()
        data.update(changes)
        try:
            Product(**data)
        except ValidationError as error:
            print('검증 실패:', changes)
            for detail in error.errors():
                print(detail['loc'], detail['type'])
        else:
            raise AssertionError(f'잘못된 입력이 검증을 통과했습니다: {changes}')


if __name__ == '__main__':
    main()
