import configparser
from os import path, getcwd

if not path.isfile(getcwd() + r'\config.ini'):
    print('从云端下载配置文件')
    import requests
    url = 'https://raw.githubusercontent.com/samlau0086/aliexpress/main/config.ini'
    r = requests.get(url, stream=False)  # , stream=False
    with open(getcwd() + r'\config.ini', "wb") as f:
        f.write(r.content)

if path.isfile(getcwd() + r'\config.ini'):
    config = configparser.RawConfigParser()  # configparser.ConfigParser()
    config.read('config.ini', encoding="utf-8")


def element(key='', *args):
    value = config.get('elements', key)
    if args:
        return eval(value % args) if r'%s' in value or r'%d' in value or r'%f' in value else eval(value)
    else:
        return value if r'%s' in value or r'%d' in value or r'%f' in value else eval(value)
