import poplib
import re
import time


def dec_to_hex(str1):  # 十转十六
    a = str(hex(eval(str1)))
    b = a.replace("0x", '')
    return b.upper()


class Email(object):
    def __init__(self, email = "", password = ""):
        self.email = email
        self.password = password
        self.msg_count = 0
        self.total_size = 0
        self.pop = None

    def get_pop(self):
        if "@rambler.ru" in self.email or "@rambler.ua" in self.email or "@ro.ru" in self.email or "@autorambler.ru" in self.email or "@lenta.ru" in self.email:
            return {"server": "pop.rambler.ru", "port": "995", "ssl": 1}  # mail.rambler.ru
        elif "@inbox.ru" in self.email:  # pop.inbox.ru
            return {"server": "pop.inbox.ru", "port": "995", "ssl": 1}
        elif "@yandex.ru" in self.email:
            return {"server": "pop.yandex.ru", "port": "995", "ssl": 1}
        elif "@list.ru" in self.email:  # pop.list.ru
            return {"server": "pop.list.ru", "port": "995", "ssl": 1}
        elif "@mail.ru" in self.email:
            return {"server": "pop.mail.ru", "port": "995", "ssl": 1}
        elif "@bigmir.net" in self.email:
            return {"server": "pop.bigmir.net", "port": "995", "ssl": 1}
        elif "@bk.ru" in self.email:  # pop3.bk.ru
            return {"server": "pop3.bk.ru", "port": "995", "ssl": 1}
        elif "@web.de" in self.email:#pop3.bk.ru
            return {"server": "pop3.web.de", "port": "995", "ssl": 1}
        elif "@yahoo.com"  in self.email:
            return {"server": "pop.mail.yahoo.com", "port": "995", "ssl": 1}
        elif "@mail.com"  in self.email:
            return {"server": "pop3.mail.com", "port": "995", "ssl": 1}
        elif "@onet.pl" in self.email:
            return {"server": "pop3.onet.pl", "port": "995", "ssl": 1}
        elif "@gmail.com" in self.email:
            return {"server": "pop.gmail.com", "port": "995", "ssl": 1}
        elif "@qq.com" in self.email:
            return {"server": "pop.qq.com", "port": "995", "ssl": 1}
        elif "@outlook." in self.email:
            return {"server": "outlook.office365.com", "port": "995", "ssl": 1}
        domain_pos = re.search(r"@", self.email).span()

        if not domain_pos:
            return None

        domain_pos = re.search(r"@", self.email).span()
        return {"server": "pop.%s" % (self.email[domain_pos[0] + 1:len(self.email)]), "port": "995", "ssl": 1}

    def get_smtp(self):
        pass

    def connect(self):
        pop_server = self.get_pop()
        if pop_server['ssl']:
            for i in range(3):
                try:
                    self.pop = poplib.POP3_SSL(pop_server['server'], int(pop_server['port']), timeout=60)
                    if self.pop:
                        print("Connected")
                        break
                    else:
                        self.pop = None
                        print("Connecting Failed")
                except:
                    time.sleep(3)
                    self.pop = None
                    print("Connection Error")
        else:
            self.pop = poplib.POP3(pop_server['server'], int(pop_server['port']), timeout=60)

    def login(self):
        self.connect()
        if self.pop is None:
            print("Connecting Failed")
            return False
        self.pop.user(self.email)
        try:
            self.pop.pass_(self.password)
        except:
            print('邮件服务器连接失败')
            return False
        if not ('OK' in str(self.pop.getwelcome())):
            print('登录失败')
            return False
        self.msg_count, self.total_size = self.pop.stat()
        return True

    def fetch_one(self):
        pass

    def get_count(self):#获取邮件列表
        return self.msg_count

    def find_email2(self,sender = "", subject = "", n = 0):  # 从最新的n封邮件中查找
        i = 0
        email_counts = self.get_count()
        n = n if n<=self.get_count() else email_counts
        while i < n:
            try:
                resp, lines, octets = self.pop.retr(email_counts - i)  # 最新的一封邮件
                msg_content = self.strip_email(' '.join(lines))
                if (sender in msg_content) and not (
                        re.search(r'%s' % subject.replace(' ', '\s+'), msg_content, re.I).group() is None):
                    return msg_content
                i = i + 1
            except:
                return False

    def find_email(self, sender="", subject="", n=1):
        i = 0
        target_msg = ""
        while i < n:
            msg = self.get_email(i)
            if msg is None:
                print('未获取到邮件,邮件为None')
                continue
            i = i + 1
            if re.search(subject, msg, re.I) is None:
                print('检索邮件主题失败')
                print(msg)
                continue
            if not(re.search(sender, msg, re.I).group() is None or re.search(subject, msg, re.I).group() is None):
                target_msg = msg
                break
        if target_msg != '':
            print('target_msg found')
        return target_msg

    def get_email(self, n=0):
        total = self.get_count()
        print('Total Message Count: %d' % total)
        if total<n:
            n = total-1
        if n < 0:
            return None
        try:
            resp, lines, octets = self.pop.retr(total - n)  # 最新的一封邮件#resp: +OK 1464, octets:1466
        except:
            print('Failed to retrieve message %d' % (total - n))
            try:
                resp, lines, octets = self.pop.retr(total - n + 1)  # 最新的一封邮件#resp: +OK 1464, octets:1466
            except:
                print('Again, failed to retrieve message %d' % (total - n + 1))
        msg_content = None
        try:
            msg_content = self.strip_email(' '.join(lines))
        except:
            print('failed to retrieve str message directly, convert bytes to str')
            try:
                msg_content = self.strip_email(b' '.join(lines).decode())
            except:
                print('failed to retrieve btyes message again')
        if not(msg_content is None):
            return msg_content
        else:
            print('Email message %d is None, retry' % n)
        if msg_content is None:
            print('Email message %d is None' % n)
        return msg_content

    def strip_email(self,msg):  # 将邮件解析为正常HTML内容
        schars = ['=', '\t', ' ', '\xe2', '\x80', '\x99', '\xe9', '\x98', '\xbf', '\x87', '\x8c', '\xe5', '\xb7',
                  '\xb4', '\xa6', '\xb8', '\xaf', '\xe6', '\x9c', '\x89', '\x90', '\x85', '\xac', '\x8f', '\xef',
                  '\xbc', '\x8a', '\x91', '\xe7', '\x81', '\xa3', '\x8b', '\xb0', '\xe8', '\xa1', '\x9f', '\x82',
                  '\xe4', '\xbb', '\xba', '\xa8', '\x93']
        for c in schars:
            msg = msg.replace(self.memi_c(c), c)
        return msg.replace('= ', '')

    def memi_c(self, special_char):  # 特殊字符转成16进制memi转义字符
        if dec_to_hex(str(ord(special_char))).__len__() < 2:
            return '=0' + dec_to_hex(str(ord(special_char)))
        return '=' + dec_to_hex(str(ord(special_char)))

'''
# email = Email(email='hcajwyjktqb@outlook.kr', password='j6ruTBmvk')
email = Email(email='rfqmrc@outlook.kr', password='8CdsWVY5')
email.login()
print(email.get_email(0))
'''
'''
#print email.get_email(0)#获取最新的邮件
print email.get_email(2)#获取最新的邮件
#email.get_email(1)#获取第二封邮件

#email.find_email("member@notice.alibaba.com","Verification Code From Alibaba Group",10)#获取特定邮件内容
#print email.get_email(1)
msg = email_client.find_email('account@notice.aliexpress.com', 'AliExpress')
re.sub(r'[^\d]', '', re.search(r'>(\d{4})<\/', msg).group())
'''