auth_form = '''---g-
Content-Disposition: form-data; name="LoginForm[email]"

{}
---g-
Content-Disposition: form-data; name="LoginForm[password]"

{}
---g-
Content-Disposition: form-data; name="LoginForm[rememberMe]"

1
---g-
Content-Disposition: form-data; name="_csrf"

{}
---g---'''

multipart_head = {'Content-Type': 'multipart/form-data; boundary=-g-'}

api = 'https://api2.vdsina.ru/'

list_VPS = 'https://api2.vdsina.ru/service/list?ServiceSearch%5Bservice_type_id%5D=1&ServiceSearch%5Bgroup_id%5D=1'

info_VPS = 'https://api2.vdsina.ru/service/view/'

keys_USER = ['real', 'bonus', 'partner']

keys_VPS = ['service_name', 'service_created', 'service_end', 'service_status', 'service_id']