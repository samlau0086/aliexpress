from common import get_account_info, element, solve_slider, get_email_code, get_bot, os


def process(email, password, stp='', bot=None):
    bot.maximize()


def main():
    if not os.path.isfile('已注册账号导入.txt'):
        open('已注册账号导入.txt', 'w')
    with open('已注册账号导入.txt', 'r', encoding='utf-8') as f:
        rows = f.readlines()
    for row in rows:
        user_info = get_account_info(row)


if __name__ == '__main__':
    main()