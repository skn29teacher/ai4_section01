"""함수 버전(day3-3-fixed.py)을 Order 클래스로 리팩토링한 예제.

기존: calc_order(등급, 단가, 수량, 쿠폰)으로 매번 데이터를 전달합니다.
변경: Order(등급, 단가, 수량, 쿠폰)로 주문 객체를 만들고,
      객체의 calculate_total() 메서드로 최종 금액을 구합니다.
"""

from decimal import Decimal


class Order:
    """주문 데이터와 해당 주문의 금액 계산 동작을 함께 관리합니다.

    등급은 0(비회원), 1(5%), 2(10%), 3(20%)을 허용합니다.
    단가는 0 이상의 유한한 숫자, 수량은 1 이상의 정수입니다.
    쿠폰은 bool 또는 YES/NO 문자열을 받습니다.
    회원 할인 → 쿠폰 차감 → 최소 0 → 소수점 버림 순서를 유지합니다.
    """

    # 변경: 모든 주문이 공유하는 정책을 클래스 속성으로 옮겼습니다.
    DISCOUNT_PERCENT = {0: 0, 1: 5, 2: 10, 3: 20}
    COUPON_AMOUNT = 3000

    def __init__(
        self,
        u_type: int,
        price: int | float | Decimal,
        qty: int,
        coupon: str | bool,
    ) -> None:
        """객체를 생성할 때 입력을 검사하고 주문 데이터를 저장합니다."""
        # 변경: 계산할 때마다 검사하던 입력을 객체 생성 시 검사합니다.
        # bool도 int의 하위 타입이므로 정확한 타입을 확인합니다.
        if type(u_type) is not int:
            raise TypeError("회원 등급은 정수여야 합니다.")
        if u_type not in self.DISCOUNT_PERCENT:
            raise ValueError("회원 등급은 0, 1, 2, 3 중 하나여야 합니다.")
        if type(qty) is not int:
            raise TypeError("수량은 정수여야 합니다.")
        if qty < 1:
            raise ValueError("수량은 1 이상이어야 합니다.")

        # 변경: 입력 변환을 보조 메서드에 맡겨 생성자의 역할을 명확히 합니다.
        decimal_price = self._normalize_price(price)
        use_coupon = self._normalize_coupon(coupon)

        # 변경: 함수의 지역 변수를 각 주문 객체의 인스턴스 속성으로 저장합니다.
        # self는 현재 주문 객체입니다. 각 객체는 서로 다른 주문값을 가집니다.
        # _ 접두사는 외부에서 직접 수정하지 않는 내부 속성이라는 관례입니다.
        self._u_type = u_type
        self._price = decimal_price
        self._qty = qty
        self._use_coupon = use_coupon

    # 변경: 일반 인스턴스 메서드로 정의하여 첫 매개변수로 self를 받습니다.
    # self._normalize_price(price) 호출 시 self는 파이썬이 자동 전달합니다.
    def _normalize_price(self, price: int | float | Decimal) -> Decimal:
        """단가를 검증하고 계산에 사용할 십진수로 통일합니다."""
        if isinstance(price, bool) or not isinstance(price, (int, float, Decimal)):
            raise TypeError("단가는 int, float 또는 Decimal이어야 합니다.")
        # float는 str(price)에 나타난 십진수 값을 기준으로 해석합니다.
        decimal_price = price if isinstance(price, Decimal) else Decimal(str(price))
        if not decimal_price.is_finite() or decimal_price < 0:
            raise ValueError("단가는 0 이상의 유한한 숫자여야 합니다.")
        return decimal_price

    # 변경: 쿠폰 변환도 self를 받는 일반 인스턴스 메서드로 통일합니다.
    def _normalize_coupon(self, coupon: str | bool) -> bool:
        """다양한 쿠폰 입력 표기를 True/False로 통일합니다."""
        if isinstance(coupon, bool):
            return coupon
        if isinstance(coupon, str):
            normalized_coupon = coupon.strip().upper()
            if normalized_coupon not in ("YES", "NO"):
                raise ValueError("쿠폰 문자열은 YES 또는 NO여야 합니다.")
            return normalized_coupon == "YES"
        raise TypeError("쿠폰은 bool 또는 YES/NO 문자열이어야 합니다.")

    def calculate_total(self) -> int:
        """저장된 주문 데이터로 최종 금액을 계산합니다. 주문값은 바꾸지 않습니다."""
        # 변경: 매개변수 대신 self의 속성에서 현재 주문 데이터를 읽습니다.
        # 정확한 분수와 정수 연산을 사용하는 기존 정밀도 개선은 유지합니다.
        numerator, denominator = self._price.as_integer_ratio()
        remaining_percent = 100 - self.DISCOUNT_PERCENT[self._u_type]
        total_numerator = numerator * self._qty * remaining_percent
        total_denominator = denominator * 100

        # 기존 정책 유지: 회원 할인 후 쿠폰 금액을 차감합니다.
        if self._use_coupon:
            total_numerator -= self.COUPON_AMOUNT * total_denominator

        # 기존 정책 유지: 음수는 0으로 보정하고 마지막에 소수점을 버립니다.
        return max(0, total_numerator) // total_denominator


if __name__ == "__main__":
    # 변경 전: result = calc_order(1, 100, 20, "yes")
    # 변경 후: 주문 생성과 금액 계산을 두 단계로 나눕니다.
    order = Order(u_type=1, price=100, qty=20, coupon="yes")
    print(f"최종 결제 금액: {order.calculate_total():,}원")

    # 각 객체가 자신의 주문 데이터를 가지므로 여러 주문을 독립적으로 다룹니다.
    another_order = Order(u_type=1, price=2.3, qty=200, coupon=False)
    print(f"다른 주문 금액: {another_order.calculate_total():,}원")
