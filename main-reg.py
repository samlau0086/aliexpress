from common import time, get_account_info, element, solve_slider, get_email_code, get_bot, os


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
            process(email=user_info['email'], password=user_info['password'], country=user_info['country'], stp='开始', bot=get_bot(profile_name=user_info['email'], country=user_info['country'], proxy=user_info['proxy']))


def pick_country(bot, country='United States'):
    for i in range(10):
        if bot.element(element('注册国家选成功标志', country)).until_here(2):
            break
        if not bot.element(*element('注册国家弹出框')).show():
            bot.element(*element('注册国家弹出框触发按钮')).click()
            time.sleep(0.5)
        if bot.element(*element('注册国家弹出框')).until_show(1):
            bot.element(element('注册国家弹出框目标国家项', country)).click()
        if bot.element(*element('注册国家弹出框为空')).until_show(1):
            print('国家选择框为空')
            return False
    return bot.element(element('注册国家选择框成功标志', country)).exists()


def process(email, password, country, stp='', bot=None):
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
            # print('在此步骤卡住超过30秒, 重新开始')
            # bot.refresh()
            # stp = '开始'
        if time.time()-time_spent['total_spent'] > 240:
            pass
            # print('此账号注册超过240秒，销毁窗口重新开始')
            # stp = '失败结束'
        if stp == '开始':
            # enter mark
            if not bot.tab(tab={'loc': 'U', 'val': 'campaign.aliexpress.com'}):
                bot.get('https://campaign.aliexpress.com/wow/gcp/new-user-channel/index?wh_weex=true&wx_navbar_hidden=true&wx_navbar_transparent=true&ignoreNavigationBar=true&wx_statusbar_hidden=true&_immersiveMode=true&preDownLoad=true&tabType=coupon&benefitType=coupon&spm=a2g0o.home.houyi_aipl.0&preGetCoupon=true')
            # exit mark
            print('仅保留此标签')
            bot.keep()
            if bot.element(*element('领券页面标志')).until_here(30):
                stp = '领券'
            elif bot.element(*element('注册页面标志')).until_here(10):
                stp = '切换到注册'
        elif stp == '领券':
            if not bot.element(*element('领券按钮')).exists():
                bot.refresh()
                stp = '开始'
                time.sleep(2)
                continue
            bot.element(*element('领券按钮')).click()
            bot.element(*element('注册页面标志')).until_here(10)
            stp = '切换到注册'
        elif stp == '切换到注册':
            if not bot.element(*element('注册标签')).exists():
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
            bot.element(*element('注册标签')).click()
            if bot.element(*element('注册国家选择框标志')).until_here(3):
                stp = '选国家'
        elif stp == '选国家':
            if not pick_country(bot, country):
                bot.refresh()
                stp = '开始'
                time.sleep(2)
                continue
            if bot.element(*element('注册邮箱')).until_show(30):
                stp = '填写邮箱密码'
            else:
                bot.refresh()
                time.sleep(2)
                stp = '开始'
                continue
        elif stp == '填写邮箱密码':
            if not bot.element(*element('注册邮箱')).exists():
                # 需要判断是否已经进入到一下页
                if bot.element(*element('邮件验证码输入框1')).exists():
                    stp = '收邮件验证码'
                    continue
                bot.refresh()
                stp = '开始'
                time.sleep(2)
                continue
            if not (bot.element(*element('注册邮箱')).attr('value') == email):
                if bot.element(*element('注册邮箱清除按钮')).show():
                    bot.element(*element('注册邮箱清除按钮')).click()
                    bot.element(*element('注册邮箱清除按钮')).until_hide(3)
                bot.element(*element('注册邮箱')).text(email)
                time.sleep(2)
                continue
            if not (bot.element(*element('注册邮箱')).attr('value') == email):
                bot.refresh()
                stp = '开始'
                time.sleep(2)
                continue
            time.sleep(0.3)
            if not bot.element(*element('注册密码清除按钮')).show():
                bot.element(*element('注册密码')).click()
                bot.element(*element('注册密码')).text(password)
                time.sleep(1.9)
            if bot.element(*element('注册提交按钮')).exists():
                bot.element(*element('注册提交按钮')).focus()
                bot.element(*element('注册提交按钮')).click()
                # bot.element(*element('注册提交按钮')).press('enter')
                if bot.element(*element('注册loading')).until_show(3):
                    bot.element(*element('注册loading')).until_hide(5)
                    if not bot.element(*element('滑动提示')).until_show(3):
                        if not bot.element(*element('注册loading')).until_hide(20):
                            # 原来的 //div[contains(@class,"fm-join")]//div[contains(@class,"fm-loading-overlay")]
                            print('长时间未消失')
                            bot.refresh()
                            time.sleep(3)
                            stp = '开始'
                            continue
                time.sleep(3)
            # bot.element(*element('注册错误提示')).until_show(5)
            if bot.element(*element('滑动提示')).until_show(3):
                if not solve_slider(bot):
                    print('滑动提示仍在')
                    stp = '失败结束'
                    continue
            if bot.element(*element('注册邮箱网络问题提示')).until_show(3):
                print('网络/环境有问题，删除档案并更换代理,然后重新启动')
                stp = '失败结束'
                continue
            if bot.element(*element('接收邮件验证码界面标志')).until_here(10):
                stp = '收邮件验证码'
                continue
        elif stp == '收邮件验证码':
            if not bot.element(*element('邮件验证码输入框1')).exists():
                # 判断是否已经成功跳转至下一页
                if bot.element(*element('注册成功标志')).until_here(5):
                    stp = '成功结束'
                    continue
                if 'www.aliexpress' in bot.url():
                    stp = '成功结束'
                    continue

            if not bot.element(*element('邮件验证码输入框1')).attr('value'):
                print('获取验证码')
                email_code = get_email_code(email, password)
                if bot.element(*element('注册成功标志')).exists():
                    stp = '成功结束'
                    continue
                if email_code:
                    print('填入验证码', email_code)
                    bot.element(*element('邮件验证码输入框1')).click()
                    bot.element(*element('邮件验证码输入框1')).text(email_code)
                    time.sleep(0.3)
                    print('提交验证')
                    # bot.element(*element('验证提交按钮')).click()
                    bot.element(*element('验证提交按钮')).focus()
                    bot.element(*element('验证提交按钮')).press('enter')
                    bot.element(*element('验证提交按钮')).until_gone(25)

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
