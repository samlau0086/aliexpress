from common import time, get_account_info, element, solve_slider, get_email_code, get_bot, os


def process(email, password, stp='', bot=None):
    bot.maximize()
    while 1:
        print(stp)
        if stp == '开始':
            # enter mark
            if not bot.tab(tab={'loc': 'U', 'val': 'login.aliexpress'}):
                bot.get('https://login.aliexpress.com/')
            # exit mark
            print('仅保留此标签')
            bot.keep()
            if bot.element(*element('登录页面标志')).until_here(10):
                stp = '开始登录'
        elif stp == '开始登录':
            # 加载中的步骤

            if not bot.element(*element('登录邮箱')).exists():
                if 'login' not in bot.url():
                    print('登录成功?', bot.url())

                print('没有登录邮箱出现,看是否已经跳转到下一页')
                pass
            if not (bot.element(*element('登录邮箱')).attr('value') == email):
                if bot.element(*element('登录邮箱清除按钮')).show():
                    bot.element(*element('登录邮箱清除按钮')).click()
                    bot.element(*element('登录邮箱清除按钮')).until_hide(3)
                bot.element(*element('登录邮箱')).text(email)
                time.sleep(2)
                continue
            time.sleep(0.3)
            if not bot.element(*element('登录密码清除按钮')).show():
                bot.element(*element('登录密码')).click()
                bot.element(*element('登录密码')).text(password)
                time.sleep(1.9)

            if bot.element(*element('滑动提示')).show():
                if not solve_slider(bot):
                    print('滑动提示仍在')
                    stp = '失败结束'
                    continue
            # 是否需要邮件验证

            if bot.element(*element('登录提交按钮')).exists():
                # 是否在loading
                if not bot.element(*element('登录提交按钮loading')).show():
                    bot.element(*element('登录提交按钮')).focus()
                    bot.element(*element('登录提交按钮')).press('enter')
                    if bot.element(*element('登录loading')).until_show(3):
                        if not bot.element(*element('登录loading')).until_hide(20):
                            print('长时间未消失')
                            bot.refresh()
                            time.sleep(3)
                            stp = '开始'
                            continue
                    time.sleep(3)

            if bot.element(*element('登录成功标志')).until_here(5):
                stp = '成功结束'
                continue
        elif stp == '成功结束':
            bot.shut()
            bot.console.close(None)  # 关闭窗口
            time.sleep(2)
            bot.console.remove_profile()
            return True
        elif stp == '失败结束':  # 换IP，清除profile
            bot.shut()
            bot.console.close(None)  # 关闭窗口
            time.sleep(2)
            bot.console.remove_profile()
            return False


def main():
    if not os.path.isfile('已注册账号导入.txt'):
        open('已注册账号导入.txt', 'w')
    with open('已注册账号导入.txt', 'r', encoding='utf-8') as f:
        rows = f.readlines()
    for row in rows:
        user_info = get_account_info(row)
        print('开始登录流程')
        print(user_info)
        process(email=user_info['email'], password=user_info['password'], stp='开始',
                bot=get_bot(profile_name=user_info['email'], country=user_info['country'],
                            proxy=user_info['proxy']))


if __name__ == '__main__':
    main()