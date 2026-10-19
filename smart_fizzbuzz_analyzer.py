def analyze_fizzbuzz(limit: int) -> dict:
    """1부터 limit까지 각 숫자를 하나의 범주로 분류해 개수를 반환한다."""
    counts = {"FizzBuzz": 0, "Fizz": 0, "Buzz": 0, "Number": 0}

    for number in range(1, limit + 1):
        # 공통 배수를 먼저 검사해 Fizz나 Buzz로 중복 집계하지 않는다.
        if number % 3 == 0 and number % 5 == 0:
            counts["FizzBuzz"] += 1
        elif number % 3 == 0:
            counts["Fizz"] += 1
        elif number % 5 == 0:
            counts["Buzz"] += 1
        else:
            counts["Number"] += 1

    return counts


def run_validation_pipeline() -> None:
    """명시적 사례, 수학적 기대값, 누적 변화와 반환값 독립성을 검증한다."""
    if not __debug__:
        raise RuntimeError("assert 검증을 위해 -O 옵션 없이 실행해주세요.")

    # 1단계: 빈 범위, 각 분기의 첫 발생, 공통 배수 전후의 정확한 결과
    cases = [
        (-100, (0, 0, 0, 0)),
        (-1, (0, 0, 0, 0)),
        (0, (0, 0, 0, 0)),
        (1, (0, 0, 0, 1)),
        (2, (0, 0, 0, 2)),
        (3, (0, 1, 0, 2)),
        (5, (0, 1, 1, 3)),
        (14, (0, 4, 2, 8)),
        (15, (1, 4, 2, 8)),
        (16, (1, 4, 2, 9)),
        (30, (2, 8, 4, 16)),
        (100, (6, 27, 14, 53)),
    ]
    keys = ("FizzBuzz", "Fizz", "Buzz", "Number")
    for limit, values in cases:
        expected = dict(zip(keys, values))
        actual = analyze_fizzbuzz(limit)
        assert actual == expected, (limit, expected, actual)
    print(f"[통과] 명시적 사례 {len(cases)}개")

    # 2단계: 구현과 다른 방식인 나눗셈 공식으로 넓은 범위를 교차 검증
    limits = list(range(-20, 501)) + [999, 1000, 1001, 10000, 100000]
    for limit in limits:
        n = max(limit, 0)
        common = n // 15
        expected = {
            "FizzBuzz": common,
            "Fizz": n // 3 - common,
            "Buzz": n // 5 - common,
            "Number": n - n // 3 - n // 5 + common,
        }
        actual = analyze_fizzbuzz(limit)
        assert isinstance(actual, dict), (limit, actual)
        assert set(actual) == set(keys), (limit, actual)
        assert all(type(value) is int and value >= 0 for value in actual.values())
        assert sum(actual.values()) == n, (limit, actual)
        assert actual == expected, (limit, expected, actual)
    print(f"[통과] 공식 교차 검증 및 반환 형식·합계 검증 {len(limits)}개")

    # 3단계: 상한을 1 늘릴 때 정확히 하나의 범주만 1 증가하는지 검사
    previous = analyze_fizzbuzz(0)
    category_by_remainder = (
        "FizzBuzz", "Number", "Number", "Fizz", "Number",
        "Buzz", "Fizz", "Number", "Number", "Fizz",
        "Buzz", "Number", "Fizz", "Number", "Number",
    )
    for limit in range(1, 301):
        current = analyze_fizzbuzz(limit)
        changed_key = category_by_remainder[limit % 15]
        for key in keys:
            expected_delta = 1 if key == changed_key else 0
            assert current[key] - previous[key] == expected_delta, (limit, key)
        previous = current
    print("[통과] 숫자별 단일 범주 증가 검증 300개")

    # 4단계: 호출 간 누적 상태나 공유 딕셔너리가 없는지 검사
    first = analyze_fizzbuzz(15)
    second = analyze_fizzbuzz(15)
    assert first is not second
    first["FizzBuzz"] = -999
    assert second == {"FizzBuzz": 1, "Fizz": 4, "Buzz": 2, "Number": 8}
    assert analyze_fizzbuzz(15) == second
    empty = analyze_fizzbuzz(0)
    empty["Number"] = 999
    assert analyze_fizzbuzz(-1) == dict.fromkeys(keys, 0)
    assert analyze_fizzbuzz(0) == dict.fromkeys(keys, 0)
    print("[통과] 반환값 독립성 및 반복 호출 검증")
    print("모든 assert 검증을 통과했습니다.")


if __name__ == "__main__":
    run_validation_pipeline()
