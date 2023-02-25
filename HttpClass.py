# coding=utf-8
import requests
from commonFunc import *
from lxml import etree
import os.path
import json

class ELEMENT(object):
    def __init__(self, html, xpath):
        self.html = html
        self.xpath = xpath

    def getAttr(self,attrName = ""):
        if attrName == "":
            return []
        return self.html.xpath(self.xpath+"/@"+attrName)

    def getAttrList(self,attrName = ""):
        if attrName == "":
            return []
        if self.html is None:
            return []
        return self.html.xpath(self.xpath+"//@"+attrName)


    def getText(self):
        return self.html.xpath(self.xpath+"/text()")

    def getTextList(self):
        return self.html.xpath(self.xpath+"//text()")

def cookiestr2dict(cookie = ""):
    if cookie=="":
        return {}
    return {i.split("=")[0]:i.split("=")[-1] for i in cookie.split("; ")}

class Http(object):
    def __init__(self):
        self.UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
        self.cookies = None
        self.session = None
        self.response = None
        self.proxies = {}
        self.timeout = None#未设置
    def setUA(self,ua):
        if ua == "":
            pass
        elif ua == "":
            pass

    def setProxies(self, proxies = {}):
        self.proxies = proxies

    def getProxies(self):
        return self.proxies

    def setCookies(self,cookies = ""):
        self.cookies = cookies

    def getCookies(self,isDict = False):
        if not isDict:#返回字符串形式cookie
            return self.cookies
        #返回dict形式cookie
        if typeof(self.cookies)=="dict":
            return self.cookies
        else:
            return cookiestr2dict(self.cookies)

    def bodyPost(self, url="",  parameters={}):
        response = requests.post(url, data=json.dumps(parameters), headers={'content-type': "application/json"})
        try:
            return {"status": "success", "data": response.json()}
        except:
            return {"status": "failed", "data": response.text}

    def get(self,url="", parameters={}, cookieInHeaders = True):#默认在header中
        if self.timeout:
            time_out = self.timeout
        else:
            time_out = (5, 15)
        if cookieInHeaders:
            try:
                self.response = requests.get(url, headers=self.getHeaders(1), params=parameters, proxies = self.getProxies(), timeout=time_out)
            except:
                return None
        elif self.session:#如果有session了就不用cookies,直接用session来请求
            try:
                self.response = self.session.get(url, headers=self.getHeaders(1), params=parameters, proxies = self.getProxies(), timeout=time_out)
            except:
                return None
        else:
            try:
                self.response = requests.get(url, headers = self.getHeaders(0), params=parameters, cookies = self.getCookies(1), proxies = self.getProxies(), timeout=time_out)
            except:
                return None
        return self.response

    def getJSON(self, url="", parameters={}, cookieInHeaders = True):
        response = self.get(url, parameters, cookieInHeaders)
        try:
            return response.json()
        except:
            print(response.text)

    def sessionGet(self,url = "", parameters = {}):
        if self.timeout:
            time_out = self.timeout
        else:
            time_out = (5,15)
        if not self.session:
            self.session = requests.session()
        try:
            self.response = self.session.get(url, headers=self.getHeaders(1), params=parameters, proxies = self.getProxies(), timeout=time_out)
        except:
            return None
        return self.response
    def getHeaders(self, withCookie = False):#header中带cookie时需要将withCookie设置为True
        if self.cookies=="" or not withCookie:
            return {"user-agent":self.UA}
        return {"user-agent":self.UA,"Cookie":self.getCookies(0)}

    def post(self,url = "", postdata = {}, session = False):#cookie必须要用session来实现#https://blog.csdn.net/williamgavin/article/details/81390014
        if session and self.session:
            self.response = self.session.post(url,headers=self.getHeaders(),data = postdata)
        else:
            self.response = requests.post(url,headers=self.getHeaders(),data = postdata)
        return self.response
    def postJSON(self, url = "", postdata = {}, session = False):
        if session and self.session:
            self.response = self.session.post(url,headers={'Content-Type': 'application/json'},data=postdata)
        else:
            self.response = requests.post(url,headers={'Content-Type': 'application/json'}, data=postdata)
        return self.response


    def clearSession(self):
        self.session = None

    def sessionPost(self,url="",postdata = {}):
        if not(self.session):
            self.session = requests.session()
        return self.post(url,postdata,1)
    def element(self, xpath):
        try:
            return ELEMENT(etree.HTML(self.response.text),xpath)
        except:
            print('元素未找到,返回None')
            return None
    def download(self,url = "", path = "" ,stream = False):#stream为True时适合大文件,为False时适合小文件
        r = requests.get(url, stream=stream)
        if stream:
            with open(path, "wb") as f:
                for chunk in r.iter_content(chunk_size=512):
                    f.write(chunk)
        else:
            with open(path, "wb") as f:
                f.write(r.content)
        return os.path.isfile(path)