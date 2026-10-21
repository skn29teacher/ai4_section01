from pydantic import BaseModel, Field


class Product(BaseModel):
    # TODO title: 최소 2자, 최대 60자
    # TODO price: 0보다 커야 함
    # TODO stock: 0 이상, 기본값 0
    # TODO sku: SKU-와 숫자 네 자리 패턴
    pass


def main() -> None:
    print('TODO: 정상 상품 및 잘못된 상품을 테스트하세요.')


if __name__ == '__main__':
    main()