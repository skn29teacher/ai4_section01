# 포함관계(in ,not in)
role = 'admin'

# if role == 'admin' or role =='manager or role == 'staffe'

# allowed_roles = ['admin','manager','staffe']
if role in ['admin','manager','staffe']:
    print('접근 허용')
else:
    print('접근 불가')