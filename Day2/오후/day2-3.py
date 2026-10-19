# # 리스트 컴프리핸션
# result = []

# list_1 = ['1','2','3','4','5']

# result = [ int(i) for i in list_1 if int(i)>3]

# print(result)

# menu = ['아메리카노','라떠','초코']
# ice_menu = [ '아이스 '+i  for i in menu   ]
# len_menu = [ len(i) for i in menu if len(i)%2==0 ]

# print(len_menu)


ages = [20,15,60,25,30,45,5]
print( [ i for i in ages if i>=20 ] )
print( [ '성인' if i>=20 else '미성년'   for i in ages ] )


bad_words = ['바보','멍충이','','멍텅구리' ,'','멍충이']
words = sorted(set(word for word in bad_words if word), key=len, reverse=True)
print(words)

import re
pattern = "|".join(re.escape(word) for word in words)
print(pattern)
chat_message = '철수는 바보 가 맞습니다.'
result = re.sub(pattern, lambda match: "*" * len(match.group(0)),
                  chat_message, flags=re.IGNORECASE)
print(result)