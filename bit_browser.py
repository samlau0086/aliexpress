# coding=utf-8
from HttpClass import *
from RandomClass import *


def get_config_dir():
    config_dir = os.path.join(os.environ['USERPROFILE'], 'AppData\\Roaming\\bitbrowser\\config.json')
    if not os.path.exists(config_dir):
        print('ERROR: No Config Dir Found')
        return None
    with open(config_dir, encoding='utf8') as f:
        bt_config = eval(f.read())
        return bt_config['localServerAddress']

class BitBrowser(object):
    def __init__(self, profile_name='', country='United States', proxy=0, group_name='default', device='PC'):
        self.api_host = get_config_dir()
        self.http = Http()
        self.profile_name = profile_name
        self.proxy = proxy
        self.country = country#全名
        self.group_id = None
        self.group_name = group_name if group_name else 'default'
        self.device = device

    def get_group_list(self, page=0, page_size=100):
        result = self.post_json('/group/list', {"page": page, "pageSize": page_size})
        if result['status'] != 'success':
            return []
        elif not result['data']['success']:
            return []
        '''
        #返回值
        [{'id': '2c996b3780e12b140180eb0c7bb0708c', 'groupCode': '20220522171505520', 'groupName': 'abc', 'sortNum': 1,
          'mainUserId': '2c996b377fd93bff017ff82f5fce52c2', 'isDelete': 0,
          'createdBy': '2c996b377fd93bff017ff82f5fce52c2', 'belongUserId': '2c996b377fd93bff017ff82f5fce52c2',
          'createdTime': '2022-05-22 17:15:06', 'updateBy': '2c996b377fd93bff017ff82f5fce52c2',
          'updateTime': '2022-05-22 17:15:06', 'browserCount': 0, 'ids': None, 'browserGroupUserRelList': None,
          'createdName': 'samlau0086', 'belongName': 'samlau0086'},
         {'id': '2c996b378044f18b018046c6d54e0cde', 'groupCode': '20220420194117518', 'groupName': 'AE', 'sortNum': 0,
          'parentCode': '0', 'mainUserId': '2c996b377fd93bff017ff82f5fce52c2', 'isDelete': 0,
          'createdBy': '2c996b377fd93bff017ff82f5fce52c2', 'belongUserId': '2c996b377fd93bff017ff82f5fce52c2',
          'createdTime': '2022-04-20 19:41:18', 'updateBy': '2c996b377fd93bff017ff82f5fce52c2',
          'updateTime': '2022-04-20 19:41:18', 'browserCount': 1, 'ids': None, 'browserGroupUserRelList': None,
          'createdName': 'samlau0086', 'belongName': 'samlau0086'}]
        {'id': '2c996b3780e12b140180eb197bae757d', 'groupCode': '20220522172917486', 'groupName': 'abc', 'sortNum': 1,
         'mainUserId': '2c996b377fd93bff017ff82f5fce52c2', 'isDelete': 0,
         'createdBy': '2c996b377fd93bff017ff82f5fce52c2', 'belongUserId': '2c996b377fd93bff017ff82f5fce52c2',
         'createdTime': '2022-05-22 17:29:17', 'updateBy': '2c996b377fd93bff017ff82f5fce52c2',
         'updateTime': '2022-05-22 17:29:17', 'ids': None, 'browserGroupUserRelList': None, 'createdName': None,
         'belongName': None}
        '''
        return result['data']['data']['list']

    def get_group_detail(self, group_id='', group_name=''):
        if not group_id and group_name:
            return self.get_group_by_name(group_name)
        self.group_id = group_id if group_id else self.group_id
        result = self.post_json('/group/detail', {"id": self.group_id})
        if result['status'] != 'success':
            return None
        if not result['data']['success']:
            return None
        return result['data']['data']

    def get_group_by_name(self, name):  # 未找到指定名称的就直接创建
        group_list = self.get_group_list(0, 1000)
        for group in group_list:
            if group['groupName'] == name:
                return group
        return self.add_group(name, 0)

    def add_group(self, name='未命名', sort=0):
        result = self.post_json('/group/add', {"groupName": name, "sortNum": sort})
        if result['data'] != 'success':
            return None
        if not result['data']['success']:
            return None
        #返回值
        '''
        {'id': '2c996b3780e12b140180eb0c7bb0708c', 'groupCode': '20220522171505520', 'groupName': 'abc', 'sortNum': 1,
         'mainUserId': '2c996b377fd93bff017ff82f5fce52c2', 'isDelete': 0,
         'createdBy': '2c996b377fd93bff017ff82f5fce52c2', 'belongUserId': '2c996b377fd93bff017ff82f5fce52c2',
         'createdTime': '2022-05-22 17:15:05', 'updateBy': '2c996b377fd93bff017ff82f5fce52c2',
         'updateTime': '2022-05-22 17:15:05', 'ids': None, 'browserGroupUserRelList': None, 'createdName': None,
         'belongName': None}
        '''
        return result['data']['data']

    def edit_group(self, group_id='', group_name='', sort=None):
        if not(group_id and group_name) or sort is None:
            return False
        result = self.post_json('/group/edit',  {'id': group_id, "groupName": group_name, "sortNum": sort})
        '''
        {'status': 'success', 'data': {'success': False, 'msg': 'sortNum为整数必传'}}
        '''
        if result['status'] != 'success':
            return False
        return result['data']['success']

    def drop_group(self, group_id=''):
        if not group_id:
            return False
        result = self.post_json('/group/delete', {'id': group_id})
        if result['status'] != 'success':
            return False
        return result['status']['success']

    def post_json(self, url, params):
        return self.http.bodyPost(self.api_host+url, params)

    def act(self, act='', id=0):
        if not id:
            id = self.profile_id
        result = self.post_json('/browser/%s' % act, {"id": id})
        if result['status'] != 'success':
            return None
        elif result['data']['success'] == True:
            return result['data']['data']
        return None

    def open(self, id):
        result = self.act('open', id)
        if not(result):
            return result
        return result['http']

    def close(self, id):
        return self.act('close', id) == '关闭成功'

    def remove_profile_(self, id):
        return self.act('delete', id) == '删除成功'

    def remove_profile(self, profile_id=None):
        if not profile_id:
            profile_id = self.profile_id
        return self.remove_profile_(profile_id)

    def gen_fingerprint(self):
        ip_decide = False
        if self.country == 'United States':
            lang = 'en-US'
            lat = float(random.randint(33582871, 47877342)/1000000)
            lng = -float(random.randint(91940357, 117679100)/1000000)
            time_zone = randChoice(['GMT-08:00', 'GMT-07:00', 'GMT-06:00', 'GMT-05:00'])
        elif self.country == 'United Kingdom':
            lang = 'en-GB'
            lat = float(random.randint(51806272, 54019790)/1000000)
            lng = -float(random.randint(370299, 2675790)/1000000)
            time_zone = 'GMT+00:00'
        elif self.country == 'Japan':
            lang = 'ja-JP'
            lat = float(random.randint(35198744, 36503735)/1000000)
            lng = float(random.randint(136638201, 139097580)/1000000)
            time_zone = 'GMT+09:00'
        elif self.country == 'Germany':
            lang = 'de-DE'
            lat = float(random.randint(47932368, 54085451) / 1000000)
            lng = float(random.randint(8336821, 11880445) / 1000000)
            time_zone = 'GMT+01:00'
        elif self.country == 'Brazil':
            lang = 'pt-BR'
            lat = -float(random.randint(2605628, 13753083) / 1000000)
            lng = -float(random.randint(43193859, 60511901) / 1000000)
            time_zone = 'GMT-03:00'
        elif self.country == 'Israel':
            lang = 'is-IS'
            lat = float(random.randint(30709019, 31386704) / 1000000)
            lng = float(random.randint(34529191, 35210343) / 1000000)
            time_zone = 'GMT+02:00'
        elif self.country == 'South Korea' or self.country == 'Korea':
            lang = 'ko-KR'
            lat = float(random.randint(35426137, 37586137) / 1000000)
            lng = float(random.randint(126837316, 128996848) / 1000000)
            time_zone = 'GMT+09:00'
        elif self.country == 'Portugal':
            lang = 'pt-PT'
            lat = float(random.randint(37231108, 41739770)/1000000)
            lng = -float(random.randint(7403393, 8773226) / 1000000)
            time_zone = 'GMT+00:00'
        elif self.country == 'Vietnam':
            lang = 'vi-VN'
            lat = float(random.randint(10800372, 11608829) / 1000000)
            lng = -float(random.randint(106246283, 107933262) / 1000000)
            time_zone = 'GMT+07:00'
        elif self.country == 'Russian Federation':
            lang = 'ru-RU'
            lat = float(random.randint(54971659, 66648865) / 1000000)
            lng = float(random.randint(42332202, 116863447) / 1000000)
            time_zone = randChoice(['GMT+03:00', 'GMT+04:00', 'GMT+05:00', 'GMT+06:00',
                                    'GMT+07:00', 'GMT+08:00', 'GMT+09:00'])
        else:
            lang = 'en-US'
            lat = random.randint(35, 47) + float(random.randint(0, 999999) / 1000000)
            lng = -(random.randint(94, 117) + float(random.randint(0, 999999) / 1000000))
            time_zone = randChoice(['GMT-08:00', 'GMT-07:00', 'GMT-06:00', 'GMT-05:00'])
            ip_decide = True

        finger_print = {
            'coreVersion': '104',  # 92内核版本，默认104，可选92
            "ostype": self.device,  # 操作系统平台 PC|Android|IOS
            "os": "Win32" if self.device == 'PC' else ("Linux armv7l" if self.device == 'Android' else 'MacIntel'),  # Win64|Win32|Linux i686|Linux armv7l|MacIntel
            "version": "",  # 浏览器版本，建议92以上，不填则会从92以上版本随机
            "userAgent": "",  # 不填的话会自动生成
            "isIpCreateTimeZone": ip_decide,  # 基于IP生成对应的时区
            "timeZone": "" if ip_decide else time_zone,  # isIpCreateTimeZone为false的时候，从提供的时区列表中随机一个
            "webRTC": "0",  # webrtc 0(替换)|1(允许)|2(禁止)
            "position": randChoice(["0", "1", "2"]),  # 地理位置 0(询问)|1(允许)|2(禁止)
            "isIpCreatePosition": True,  # 基于IP生成对应的地理位置 # ip_decide
            "lat": "" if ip_decide else str(lat),  # 经度 isIpCreatePosition为false时填写
            "lng": "" if ip_decide else str(lng),  # 纬度 isIpCreatePosition为false时填写
            "precisionData": "" if ip_decide else str(random.randint(1, 1000)),  # 精度米 isIpCreatePosition为false时填写
            "isIpCreateLanguage": ip_decide,  # 基于IP生成对应的国家语言
            "displayLanguages": "" if ip_decide else lang,
            'openWidth': 1280,  # 窗口宽度
            'openHeight': 720,  # 窗口高度
            "languages": "" if ip_decide else lang,  # isIpCreateLanguage为false，则需要填写语言，从提供的语言列表中选一个值
            "isIpCreateDisplayLanguage": False,
            "resolutionType": 0,  # random.choice(["0", "1"]),  # 分辨率 0(跟随电脑)|1(自定义)
            "resolution": random.choice(["1920 x 1080", "800 x 600"]),  # 自定义时分辨率值 1920 x 1080 | 1920 x 1080 | 800 x 600 | ...
            "fontType": "2",  # 字体 0(系统默认) | 1(自定义) | 2(随机匹配)
            "font": "",  # fontType非系统默认时，可以随机从字体列表中随机取一些，逗号分隔传入
            "canvas": "0",  # 0(随机) | 1(关闭)
            "webGL": "0",  # webGL图像 0(随机) | 1(关闭)
            "webGLMeta": "0",  # webGL元数据 0(自定义) | 1(关闭)
            "webGLManufacturer": "",  # webGL厂商，从提供的厂商列表中随机选一个
            "webGLRender": "",  # webGL渲染，从提供的渲染数据list中随机选一个
            "audioContext": "0",  # Audio 0(随机) | 1(关闭)
            "mediaDevice": "0",  # Media 0(随机) | 1(关闭)
            "hardwareConcurrency": random.choice(["2", "3", "4", "6", "8"]),  # CPU核心数
            "deviceMemory": random.choice(["8", "4", "2", "6"]),  # 设备内存
            "doNotTrack": "1",  # 0(开启) | 1(关闭)
            "colorDepth": random.choice(["32", "48", "32", "30", "24", "18", "16"]),  # 颜色深度 [48,32, 30, 24, 18, 16, ...] 随机一个颜色深度值
            "ignoreHttpsErrors": random.choice([False, True]),
            "isIpNoChange": False,
            "abortImage": False,
            "stopWhileNetError": False
        }

        return finger_print

    def change_proxys(self, profile_ids=[], proxy_type='socks5', host='', port='', proxy_user='', proxy_pass='', ck_service='ip-api', method=2):
        # ipCheckService: 'ip-api'
        # proxyMethod: 2
        # proxyType: socks5
        # host
        # port
        # proxyUserName
        # proxyPassword
        # self.act('proxy/update', )
        response = self.post_json('/browser/proxy/update', {'ids': profile_ids, 'ipCheckService': ck_service, 'proxyMethod': method, 'proxyType': proxy_type, 'host': host, 'port': port, 'proxyUserName': proxy_user, 'proxyPassword': proxy_pass})
        if response['status'] == 'success':
            print(response['data'])
            return True
        else:
            print(response['data'])
            return False

    def create_profile(self, profile_id='', profile_name='', proxy=0, group_name='', platform="https://www.aliexpress.com/", platformIcon="other"):
        if self.group_id:
            group_id = self.group_id
        else:
            print(group_name if group_name else self.group_name)
            group_id = self.get_group_by_name(group_name if group_name else self.group_name)['id']
        self.group_id = group_id
        if proxy and proxy['type'] != 'noproxy':
            proxy_type = str(proxy['type']).lower()
            proxy_host = proxy['host']
            proxy_port = proxy['port']
            try:
                proxy_user = proxy['username']
                proxy_pass = proxy['password']
            except:
                proxy_user = ''
                proxy_pass = ''
        else:
            proxy_type = 'noproxy'
            proxy_host = ''
            proxy_port = ''
            proxy_user = ''
            proxy_pass = ''
        if profile_id == '':
            result = self.post_json('/browser/update',
                                        {
                                            "groupId": group_id,
                                        "platform": platform,
                                        "platformIcon": platformIcon,
                                        "name": profile_name if profile_name else self.profile_name,
                                        "remark": "",
                                        "userName": "",
                                        "password": "",
                                        "cookie": "",
                                        "proxyMethod": 2,
                                        "proxyType": proxy_type,
                                        "host": proxy_host,
                                        "port": proxy_port,
                                        "proxyUserName": proxy_user if proxy_user else '',
                                        "proxyPassword": proxy_pass if proxy_user else '',
                                        "browserFingerPrint":
                                        self.gen_fingerprint()
                                        })

        else:
            result = self.post_json(self.api_host + '/browser/update',
                                        {"id": profile_id,
                                         "groupId": group_id,
                                         "platform": platform,
                                         "platformIcon": platformIcon,
                                         "name": profile_name if profile_name else self.profile_name,
                                         "remark": "",
                                         "userName": "",
                                         "password": "",
                                         "cookie": "",
                                         "proxyMethod": 2,
                                         "proxyType": proxy_type,
                                         "host": proxy_host,
                                         "port": proxy_port,
                                         "proxyUserName": proxy_user if proxy_user else '',
                                        "proxyPassword": proxy_pass if proxy_user else '',
                                         "browserFingerPrint":
                                             self.gen_fingerprint()
                                         })
        if result['status'] == 'failed':
            print('连接失败')
            return None
        elif result['data']['success']:
            self.profile_id = result['data']['data']['id']
            return result['data']['data']
        else:
            print('Profile创建/获取失败')
            print(result['data'])
            return None

    def get_profile_by_id(self, id=''):
        result = self.post_json('/browser/detail', {"id": id})
        if result['status'] == 'failed':
            return None
        elif result['data']['success'] == True:
            self.profile_id = result['data']['data']['id']
            return result['data']['data']
        return None

    def get_or_create_profile(self, profile_name='', proxy=0):
        profile_name = profile_name if profile_name else self.profile_name
        result = self.get_profile_list(name=profile_name)
        if result:
            self.profile_name = profile_name
            self.profile_id = result[0]['id']
            return result[0]

        if not proxy:
            proxy = self.proxy

        if result:
            return result
        return self.create_profile(profile_name=profile_name, proxy=proxy)

    def get_profile_list(self, page=0, page_size=10000, group_id='', name='', sort_by='seq', order='asc'):
        result = self.post_json('/browser/list', {"page": page, "pageSize": page_size, "groupId": group_id if group_id else self.group_id, "name": name, "sortProperties": sort_by, "sortDirection": order})
        if result['status'] != 'success':
            return []
        elif not result['data']['success']:
            return []
        return result['data']['data']['list']

#bitB = BitBrowser(profile_name='abc@def.com', country='Russian Federation')
#bitB.create_profile(profile_name='33333333')
#print(bitB.get_group_list())
#print(bitB.get_profile_list(name='tiktoasdasdfk'))
#print(bitB.get_group_detail(group_id='2c996b3780e12b140180eba2b61b23d8'))
'2c996b3780e12b140180eba2b61b23d8'
'''
from BitBrowserClass import *
bit_B = BitBrowser(profile_name='abc@def.com', group_id='2c996b378044f18b018046c6d54e0cde', api_host='http://127.0.0.1:13037', profile_id='')
print(bit_B.get_or_create_profile())
#print(bit_B.create_profile())#2c996b378044f18b018047e7518316b9
#print(bit_B.open('2c996b378044f18b018047e7518316b9'))
#print(bit_B.close('2c996b378044f18b018047e7518316b9'))
#print(bit_B.get_profile_by_id('2c996b378044f18b018047e7518316b9'))
#print(bit_B.remove_profile('2c996b378044f18b018047e7518316b9'))
exit()
'''