"""회원 할인과 쿠폰을 적용하는 주문 금액 계산 예제."""

from decimal import Decimal


# 변경: 등급과 할인율을 한곳에서 관리합니다. 0은 비회원입니다.
DISCOUNT_PERCENT = {0: 0, 1: 5, 2: 10, 3: 20}
COUPON_AMOUNT = 3000


def calc_order(
    u_type: int,
    price: int | float | Decimal,
    qty: int,
    coupon: str | bool,
) -> int:
    """최종 결제 금액을 정수로 반환합니다.

    등급: 0(비회원), 1(5%), 2(10%), 3(20%).
    단가: 0 이상의 유한한 int, float, Decimal. 수량: 1 이상의 int.
    쿠폰: bool 또는 YES/NO 문자열(대소문자와 앞뒤 공백 무시).
    계산 정책: 회원 할인 → 쿠폰 차감 → 최소 0 → 소수점 버림.
    float 단가는 str(price)로 표현되는 십진수 값을 기준으로 계산합니다.
    """
    # 변경: bool은 int의 하위 타입이므로 type 검사로 따로 배제합니다.
    if type(u_type) is not int:
        raise TypeError("회원 등급은 정수여야 합니다.")
    if u_type not in DISCOUNT_PERCENT:
        raise ValueError("회원 등급은 0, 1, 2, 3 중 하나여야 합니다.")
    if type(qty) is not int:
        raise TypeError("수량은 정수여야 합니다.")
    if qty < 1:
        raise ValueError("수량은 1 이상이어야 합니다.")

    # 변경: 음수, 문자열, bool, NaN, 무한대 단가를 계산 전에 거릅니다.
    if isinstance(price, bool) or not isinstance(price, (int, float, Decimal)):
        raise TypeError("단가는 int, float 또는 Decimal이어야 합니다.")
    decimal_price = price if isinstance(price, Decimal) else Decimal(str(price))
    if not decimal_price.is_finite() or decimal_price < 0:
        raise ValueError("단가는 0 이상의 유한한 숫자여야 합니다.")

    # 변경: 'yes', ' YES '도 허용하되, 오타를 무쿠폰으로 숨기지 않습니다.
    if isinstance(coupon, bool):
        use_coupon = coupon
    elif isinstance(coupon, str):
        normalized_coupon = coupon.strip().upper()
        if normalized_coupon not in ("YES", "NO"):
            raise ValueError("쿠폰 문자열은 YES 또는 NO여야 합니다.")
        use_coupon = normalized_coupon == "YES"
    else:
        raise TypeError("쿠폰은 bool 또는 YES/NO 문자열이어야 합니다.")

    # 변경: 십진수 단가를 정확한 분수로 바꿔 정수 연산만 수행합니다.
    # 예: 2.3 = 23/10. float 오차로 437이 436으로 버려지는 일을 막습니다.
    numerator, denominator = decimal_price.as_integer_ratio()
    remaining_percent = 100 - DISCOUNT_PERCENT[u_type]
    total_numerator = numerator * qty * remaining_percent
    total_denominator = denominator * 100

    # 기존 정책 유지: 회원 할인 후 쿠폰 3,000을 차감합니다.
    if use_coupon:
        total_numerator -= COUPON_AMOUNT * total_denominator

    # 기존 정책 유지: 최소 금액은 0이며, 마지막에 소수점을 버립니다.
    return max(0, total_numerator) // total_denominator


# 변경: 다른 파일에서 import할 때 예제 실행과 출력이 발생하지 않습니다.
if __name__ == "__main__":
    result = calc_order(1, 100, 20, "yes")
    print(f"최종 결제 금액: {result:,}원")
