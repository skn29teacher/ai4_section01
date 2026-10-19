class AgeOverError(Exception):
    pass

for i in range(5):
    try:
        age = int(input('나이 입력하세요'))
        if age >100 or age < 0:
            raise AgeOverError()
    except AgeOverError as e:
        print('0과 100사이의 값을 입력하세요')
    except Exception as e:
        print('숫자만 입력하세요')
    else:
        print('데이터 입력이 정상입니다.')
        break
    finally:
        print('총 시도횟수 : ', i+1)

    