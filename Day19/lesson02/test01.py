merge1 = []
merge2 = []
test1 = [1,2,3]
test2 = [10,11,12]
merge1.append(test1)
merge1.append(test2)
print(merge1)  # [  [1,2,3], [10,11,12]      ]

merge2.extend(test1)
merge2.extend(test2)
print(merge2)  # [1,2,3,10,11,12]
