# 리스에서 불량을 모두 지우고 정상만 남게 
items = ['정상','불량','불량','정상']
# target = items[:]  # 복사

# for item in target :
#     if item == '불량':
#         items.remove('불량')

# result = [ item for item in items if item != '불량' ]
result = []
for item in items:
    if item != '불량':
        result.append(item)

print(f'검수결과 : {result}')