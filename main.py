from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bit_browser import BitBrowser
from bot import Bot
import time
from email_class import Email
import re


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
    if bot.element(*elements['注册loading']).show():
        print('在loading')
        if not bot.element(*elements['注册loading']).until_hide(10):
            print('仍在loading，刷新页面')
            bot.refresh()
            time.sleep(3)
            return True
    if not bot.element(*elements['滑动>Iframe']).exists():
        return True
    bot.to_frame(*elements['滑动>Iframe'])
    for i in range(3):
        tracks = [
            (bot.element(*elements['滑动>容器']).size()['width'] - bot.element(*elements['滑动>滑块']).size()['width'] / 2, 0)]
        print('开始滑动')
        bot.element(*elements['滑动>滑块']).hold()
        bot.element(*elements['滑动>滑块']).move_by_tracks(tracks)
        time.sleep(0.3)
        bot.element(*elements['滑动>滑块']).release()
        print('滑动完成，看是否有刷新按钮出现')
        if not bot.element(*elements['滑动>刷新提示']).until_show(3):
            break
        else:
            print('刷新按钮仍存在')
    bot.to_default()
    return bot.element(*elements['滑动提示']).until_hide(3)

def get_account_info(row):
    row = re.sub('\n', '', row)
    temp = row.split('----')
    proxy_ = temp[3].split(':')
    return {"email": temp[0], "password": temp[1], "country": temp[2], "proxy": {"type": proxy_[0], "host": proxy_[1], "port": proxy_[2], "username": proxy_[3], "password": proxy_[4]}}


def main():
    with open('history.txt', 'r', encoding='utf-8') as f:
        history = f.read()
    with open('账号导入.txt', 'r', encoding='utf-8') as f:
        rows = f.readlines()

    for row in rows:
        user_info = get_account_info(row)
        if ('[%s]' % user_info['email']) in history:
            print('%s已注册过, 跳过' % user_info['email'])
        else:
            print('开始注册流程')
            print(user_info)
            process(email=user_info['email'], password=user_info['password'], stp='开始', bot=get_bot(profile_name=user_info['email'], country=user_info['country'], proxy=user_info['proxy']))


def pick_country(bot, country='United States'):
    for i in range(10):
        if bot.element(elements['注册国家选成功标志'] % country,).until_here(2):
            break
        if not bot.element(*elements['注册国家弹出框']).show():
            bot.element(*elements['注册国家弹出框触发按钮']).click()
            time.sleep(0.5)
        if bot.element(*elements['注册国家弹出框']).until_show(1):
            bot.element(elements['注册国家弹出框目标国家项'] % country,).click()
        if bot.element(*elements['注册国家弹出框为空']).until_show(1):
            print('国家选择框为空')
            return False
    return bot.element(elements['注册国家选择框成功标志'] % country,).exists()


elements = {'注册邮箱': ('//div[contains(@class,"fm-join")]//div[contains(@class,"fm-field")]//input',),
            '注册邮箱网络问题提示': ('//span[contains(@class,"fm-error-tip") and contains(.,"Service is unavailable")]',),
            '注册邮箱清除按钮': (
            '//div[contains(@class,"fm-join")]//div[contains(@class,"fm-field")]//span[contains(@class,"comet-input-clear-icon")]',),
            '注册密码': ('//div[contains(@class,"fm-join")]//span[contains(@class,"comet-input-password")]//input',),
            '注册密码清除按钮': (
            '//div[contains(@class,"fm-join")]//span[contains(@class,"comet-input-password")]//span[contains(@class,"comet-input-clear-icon")]',),
            '注册提交按钮': ('//div[contains(@class,"fm-join")]//button[@type="submit"]',),
            '注册loading': ('//div[contains(@class,"fm-join")]/div[contains(@class,"fm-loading")]',),
            '注册页面标志': ('//*[contains(@class,"login-container")]',),
            '注册标签': ('//div[contains(@class,"comet-tabs-nav")]/div[1]',),
            '注册国家选择框标志': ('//div[contains(@class,"fm-join")]//input',),
            '注册国家弹出框': ('//div[contains(@class,"comet-select-popup-body")]/ul[contains(@class,"comet-menu")]',),
            '注册国家选成功标志': '//span[contains(@class,"comet-select-selection")]/span[contains(.,"%s")]',
            '注册国家弹出框触发按钮': ('//div[contains(@class,"batman-address")]/span[contains(@class,"comet-select")]',),
            '注册国家弹出框目标国家项': '//div[contains(@class,"comet-select-popup-body")]/ul[contains(@class,"comet-menu")]//span[contains(@class,"comet-menu-item-content") and contains(.,"%s")]',
            '注册国家弹出框为空': ('//div[contains(@class,"comet-select-empty")]',),
            '注册国家选择框成功标志': '//span[contains(@class,"comet-select-selection")]/span[contains(.,"%s")]',
            '滑动': ('//div[@id="baxia-join-check-code"]',),
            '注册错误提示': ('//span[contains(@class,"error-text")]',),
            '滑动失败提示': ('//div[contains(@class,"errloading")]',),
            '滑动提示': ('//div[contains(@class,"fm-baxia-container")]/span[contains(@class,"error-text") and contains(.,"slide")]',),
            '滑动>滑块': ('nc_1_n1z', 'ID'),
            '滑动>容器': ('nc_1_wrapper', 'ID'),
            '滑动>Iframe': ('baxia-dialog-content', 'ID'),
            '滑动>刷新提示': ('nc_1_refresh1', 'ID'),
            '接收邮件验证码界面标志': ('//p[contains(@class,"batman-verify-desc")]/span[contains(.,"@")]',),
            '验证码重发按钮': ('//p[contains(@class,"batman-verify-resend")]/span',),
            '验证提交按钮': ('//button[@type="submit" and not(@disabled) and contains(.,"Verify")]',),
            '验证提交按钮loading': ('//button[@type="submit" and not(@disabled) and contains(.,"Verify") and contains(@class,"comet-btn-loading")]'),
            '验证码服务不可用提示': ('//span[contains(@class,"fm-error-tip") and contains(.,"unavailable")]',),
            '邮件验证码输入框1': ('//div[contains(@class,"batman-verify")]/input[1]',),
            '邮件验证码输入框2': ('//div[contains(@class,"batman-verify")]/input[2]',),
            '邮件验证码输入框3': ('//div[contains(@class,"batman-verify")]/input[3]',),
            '邮件验证码输入框4': ('//div[contains(@class,"batman-verify")]/input[4]',),
            '注册成功标志': ('//a[contains(@href,"account/index.html")]/div',),
            }


def process(email, password, stp='', bot=None):
    bot.maximize()
    time_spent = {'total_spent': time.time(), 'stp_spent': time.time(), 'current': stp}
    repeats = {}
    stp_limit = 10
    while 1:
        if stp not in repeats:
            repeats[stp] = 0
        elif repeats[stp] > stp_limit:
            print('同一骤超过10次执行，销毁窗口重新开始')
            stp = '失败结束'
        else:
            repeats[stp] += 1
        print(stp)
        if time_spent['current'] != stp:
            time_spent['stp_spent'] = time.time()
            time_spent['current'] = stp
        elif time.time()-time_spent['stp_spent'] > 30:
            time_spent['stp_spent'] = time.time()
            time_spent['current'] = stp
            print('在此步骤卡住超过30秒, 重新开始')
            bot.refresh()
            stp = '开始'
        if time.time()-time_spent['total_spent'] > 240:
            print('此账号注册超过240秒，销毁窗口重新开始')
            stp = '失败结束'
        if stp == '开始':
            # enter mark
            if not bot.tab(tab={'loc': 'U', 'val': 'login.aliexpress'}):
                bot.get('https://login.aliexpress.com/')
            # exit mark
            print('仅保留此标签')
            bot.keep()
            if bot.element(*elements['注册页面标志']).until_here(10):
                stp = '切换到注册'
        elif stp == '切换到注册':
            if not bot.element(*elements['注册标签']).exists():
                bot.refresh()
                stp = '开始'
                time.sleep(2)
                continue
            print('等待页面直到加载完成')
            for i in range(30):
                if bot.status == 'complete':
                    print('页面已加载完成')
                    break
                time.sleep(1)
            bot.element(*elements['注册标签']).click()
            if bot.element(*elements['注册国家选择框标志']).until_here(3):
                stp = '选国家'
        elif stp == '选国家':
            if not pick_country(bot, 'Korea'):
                bot.refresh()
                stp = '开始'
                time.sleep(2)
                continue
            if bot.element(*elements['注册邮箱']).until_show(30):
                stp = '填写邮箱密码'
            else:
                bot.refresh()
                time.sleep(2)
                stp = '开始'
                continue
        elif stp == '填写邮箱密码':
            if not bot.element(*elements['注册邮箱']).exists():
                # 需要判断是否已经进入到一下页
                if bot.element(*elements['邮件验证码输入框1']).exists():
                    stp = '收邮件验证码'
                    continue
                bot.refresh()
                stp = '开始'
                time.sleep(2)
                continue
            if not (bot.element(*elements['注册邮箱']).attr('value') == email):
                if bot.element(*elements['注册邮箱清除按钮']).show():
                    bot.element(*elements['注册邮箱清除按钮']).click()
                    bot.element(*elements['注册邮箱清除按钮']).until_hide(3)
                bot.element(*elements['注册邮箱']).text(email)
                time.sleep(2)
                continue
            if not (bot.element(*elements['注册邮箱']).attr('value') == email):
                bot.refresh()
                stp = '开始'
                time.sleep(2)
                continue
            time.sleep(0.3)
            if not bot.element(*elements['注册密码清除按钮']).show():
                bot.element(*elements['注册密码']).click()
                bot.element(*elements['注册密码']).text(password)
                time.sleep(1.9)
            if bot.element(*elements['注册提交按钮']).exists():
                bot.element(*elements['注册提交按钮']).focus()
                bot.element(*elements['注册提交按钮']).press('enter')
                if bot.element(*elements['注册loading']).until_show(3):
                    if not bot.element(*elements['注册loading']).until_hide(20):
                        print('长时间未消失')
                        bot.refresh()
                        time.sleep(3)
                        stp = '开始'
                        continue
                time.sleep(3)
            # bot.element(*elements['注册错误提示']).until_show(5)
            if bot.element(*elements['滑动提示']).until_show(3):
                if not solve_slider(bot):
                    print('滑动提示仍在')
                    stp = '失败结束'
                    continue
            if bot.element(*elements['注册邮箱网络问题提示']).until_show(3):
                print('网络/环境有问题，删除档案并更换代理,然后重新启动')
                stp = '失败结束'
                continue
            if bot.element(*elements['接收邮件验证码界面标志']).until_here(10):
                stp = '收邮件验证码'
                continue
        elif stp == '收邮件验证码':
            if not bot.element(*elements['邮件验证码输入框1']).exists():
                # 判断是否已经成功跳转至下一页
                if bot.element(*elements['注册成功标志']).until_here(5):
                    stp = '成功结束'
                    continue
                if 'www.aliexpress' in bot.url():
                    stp = '成功结束'
                    continue

            if not bot.element(*elements['邮件验证码输入框1']).attr('value'):
                print('获取验证码')
                email_code = get_email_code(email, password)
                if email_code:
                    print('填入验证码', email_code)
                    bot.element(*elements['邮件验证码输入框1']).click()
                    bot.element(*elements['邮件验证码输入框1']).text(email_code)
                    time.sleep(0.3)
                    print('提交验证')
                    # bot.element(*elements['验证提交按钮']).click()
                    bot.element(*elements['验证提交按钮']).focus()
                    bot.element(*elements['验证提交按钮']).press('enter')

        elif stp == '成功结束':
            print('将结果写入文件并关闭窗口')
            with open(r'aliexpress.txt', 'a', encoding='utf-8') as f:  # 写入账号文件
                f.write(email+':'+password+'\n')
            with open(r'history.txt', 'a', encoding='utf-8') as f:  # 写入历史文件，防止重新注册
                f.write('[%s]' % email)
            bot.shut()  # 断开selenium
            bot.console.close(None)  # 关闭窗口
            time.sleep(2)
            bot.console.remove_profile()
            return True

        elif stp == '失败结束':
            bot.shut()  # 断开selenium
            bot.console.close(None)  # 关闭窗口
            time.sleep(2)
            bot.console.remove_profile()
            return False

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
