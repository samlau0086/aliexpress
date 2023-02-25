import re
url = 'https://login.aliexrepss.com'
print(re.search('login\.(?=aliexrepss\.)', url, re.I))