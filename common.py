from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bit_browser import BitBrowser
from bot import Bot
import time
from email_class import Email
import re
from config import element, configparser
import os


def get_bot(profile_name='test', country='United States', proxy={'type': 'noproxy', 'host': '', 'port': 4600,  'username': '', 'password': ''}):
    chromedriver_path = r"chromedriver.exe"
    chrome_options = Options()
    bit_ = BitBrowser(profile_name=profile_name, country=country, proxy=proxy)
    profile = bit_.get_or_create_profile()
    agency_url = bit_.open(profile['id'])
    chrome_options.add_experimental_option("debuggerAddress", agency_url)
    capabilities = chrome_options.to_capabilities()
    capabilities["pageLoadStrategy"] = "none"
    driver_service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=driver_service,
                              desired_capabilities=capabilities,
                              options=chrome_options)
    driver.implicitly_wait(0.1)
    driver.set_page_load_timeout(30)
    return Bot(driver, bit_)


def get_history(h_type='reg'):
    if not os.path.isfile('%s-history.txt' % h_type):
        open('%s-history.txt' % h_type, 'w')
    with open('%s-history.txt' % h_type, 'r', encoding='utf-8') as f:
        return f.read()


def get_email_code(email, password):
    try:
        email_client = Email(email, password)
        if not email_client.login():
            print('邮箱登录失败， 请确认邮箱账号密码是否正确')
            return None
        msg = email_client.find_email('account@notice.aliexpress.com', 'AliExpress')
        code = re.sub(r'[^\d]', '', re.search(r'>(\d{4})<\/', msg).group())
    except:
        code = None
    finally:
        return code


def solve_slider(bot):
    if bot.element(*element('注册loading')).show():
        print('在loading')
        if not bot.element(*element('注册loading')).until_hide(5):
            if not bot.element(*element('滑动>Iframe')).exists():
                if not bot.element(*element('注册loading')).until_hide(10):
                    print('仍在loading，刷新页面')
                    bot.refresh()
                    time.sleep(3)
                    return True
    if not bot.element(*element('滑动>Iframe')).exists():
        return True
    bot.to_frame(*element('滑动>Iframe'))
    for i in range(3):
        tracks = [
            (bot.element(*element('滑动>容器')).size()['width'] - bot.element(*element('滑动>滑块')).size()['width'] / 2, 0)]
        print('开始滑动')
        bot.element(*element('滑动>滑块')).hold()
        bot.element(*element('滑动>滑块')).move_by_tracks(tracks)
        time.sleep(0.3)
        bot.element(*element('滑动>滑块')).release()
        print('滑动完成，看是否有刷新按钮出现')
        if not bot.element(*element('滑动>刷新提示')).until_show(3):
            break
        else:
            print('刷新按钮仍存在')
            bot.element(*element('滑动>刷新提示')).click()
    bot.to_default()
    return bot.element(*element('滑动提示')).until_hide(3)


def get_account_info(row):
    row = re.sub('\n', '', row)
    temp = row.split('----')
    proxy_ = proxy(temp[2])
    if proxy_['user'] is None:
        proxy_['user'] = ''
    elif '%' in proxy_['user']:
        proxy_['user'] = proxy_['user'] % temp[0]
    return {"email": temp[0], "password": temp[1], "country": temp[2], "proxy": {"type": proxy_['type'], "host": proxy_['host'], "port": proxy_['port'], "username": proxy_['user'], "password": proxy_['password']}}


proxy_config = configparser.RawConfigParser()
proxy_config.read('proxy.ini', encoding="utf-8")


def proxy(country=''):
    if not country:
        return None
    if not proxy_config.has_option(country, 'type'):
        return None
    return {'type': proxy_config.get(country, 'type'), 'host': proxy_config.get(country, 'host'), 'port': int(proxy_config.get(country, 'port')), 'user': proxy_config.get(country, 'user'), 'password': proxy_config.get(country, 'password')}

