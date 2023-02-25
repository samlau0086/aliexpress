from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import pyautogui
from selenium.webdriver.common.keys import Keys
from HttpClass import *
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import time


def by_(by):
    by_ = None
    if by == 'XPATH':
        by_ = By.XPATH
    elif by == 'ID':
        by_ = By.ID
    elif by == 'CLASS':
        by_ = By.CLASS_NAME
    elif by == 'CSS':
        by_ = By.CSS_SELECTOR
    return by_


class Element:
    def __init__(self, bot, selector, by):
        self.bot = bot
        self.driver = bot.driver
        self.selector = selector
        self.by = by

    def get(self):
        try:
            e = self.driver.find_element(by_(self.by), self.selector)
        except:
            print('暂未发现元素')
            e = None
        finally:
            return e

    def click(self, cord=None):
        if not cord:
            try:
                return self.get().click()
            except:
                return False
        try:
            pyautogui.click(cord['x'], cord['y'])
        except:
            return False
        return True


    def press(self, key):  # mouse down press
        if key.lower() == 'enter':
            k = Keys.ENTER
        else:
            k = Keys.ENTER
        try:
            self.get().send_keys(k)
        except:
            pass


    def drag_to(self):
        pass

    def hard_release(self):
        pass

    def size(self):
        try:
            return self.get().size
        except:
            return {"height": -1, "width": -1}

    def hard_click(self):
        size = self.size()
        position = self.position()
        if size['height'] <= 0 or size['width'] <= 0:
            print('尺寸获取失败')
            return False
        elif position['x'] < 0 or position['y'] < 0:
            print('位置获取失败')
            return False
        cord = {'x': random.randint(position['x']+1, position['x']+size['width']-1), 'y': random.randint(position['y']+1, position['y']+size['height']-1)}
        return self.click(cord=cord)

    def position(self):  # 获取任何元素(不管是在iframe中还是在iframe外)相对屏幕的位置
        self.bot.maximize()
        to_border = self.location()
        if not to_border:
            return {"x": -1, "y": -1}
        if self.bot.in_frame:
            in_frame = self.bot.in_frame
            self.bot.to_default()
            nav_height = self.driver.execute_script('return window.outerHeight - window.innerHeight;')
            frame_to_border = in_frame.location()
            to_border = {'x': to_border['x']+frame_to_border['x'], 'y': to_border['y']+frame_to_border['y']}
            self.bot.to_frame(in_frame)
        else:
            nav_height = self.driver.execute_script('return window.outerHeight - window.innerHeight;')
        return {"x": to_border['x'], "y": nav_height+to_border['y']}

    def exists(self):
        try:
            exists = self.get().is_enabled()
        except:
            exists = False
        finally:
            return exists

    def until_here(self, timeout):
        try:
            return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by_(self.by), self.selector)))
        except:
            return False

    def until_gone(self, timeout):  # 这里可能有逻辑问题
        try:
            return WebDriverWait(self.driver, timeout).until(EC.invisibility_of_element_located((by_(self.by), self.selector)))
        except:
            return False

    def reload(self):
        self.__init__(self.bot, self.selector, self.by)

    def show(self):
        try:
            return self.get().is_displayed()
        except:
            return False

    def until_show(self, timeout):
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by_(self.by), self.selector)))
        except:
            return False

    def until_hide(self, timeout):
        try:
            e = WebDriverWait(self.driver, timeout).until(EC.invisibility_of_element((by_(self.by), self.selector)))
            if type(e) == bool:
                return e
            else:
                return False
        except:
            return True

    def attr(self, name=None, value=None):
        if value is None:
            try:
                return self.get().get_attribute(name)
            except:
                return None
        try:
            self.driver.execute_script("return arguments[0].%s = '%s';" % (name, value), self.get())
            return value in self.get().get_attribute(name)
        except:
            return None

    def text(self, text=None):  # 获取文本或者输入文本
        if text is None:
            try:
                return self.get().text
            except:
                return None
        try:
            self.get().send_keys(text)
        except:
            return False
        return True

    def clear(self):
        try:
            self.get().clear()
        except:
            return False
        return True

    def location(self):
        try:
            location = self.get().location
        except:
            return None
        return location

    def focus(self):  # 焦点移动到元素
        try:
            ActionChains(self.driver).move_to_element(self.get()).perform()
        except:
            return False
        return True

    def hold(self):
        try:
            ActionChains(self.driver).click_and_hold(self.get()).perform()
        except:
            return False
        return True

    def move_by_tracks(self, tracks):
        for track in tracks:
            ActionChains(self.driver).move_by_offset(xoffset=track[0], yoffset=track[1]).perform()

    def release(self):
        try:
            ActionChains(self.driver).release(self.get()).perform()
        except:
            try:
                ActionChains(self.driver).release().perform()
            except:
                print('释放失败')

    def to(self):  # 滚动到元素
        try:
            self.driver.execute_script("arguments[0].scrollIntoView();", self.get())
        except:
            return False
        return True


class Bot:

    def __init__(self, driver, console):
        self.in_frame = None
        self.driver = driver
        self.maximized = False
        self.http = Http()
        self.console = console  # 中控台(比特)

    def get(self, url, timeout=10):
        self.driver.get(url)
        self.driver.implicitly_wait(timeout)

    def maximize(self, force=False):
        if (not self.maximized) or force:
            try:
                self.driver.maximize_window()
            except:
                print('maximized already')
        self.maximized = True

    def is_tab(self, tab):  # 是否为目标标签
        if type(tab) != dict:
            self.driver.switch_to(tab)
            return self.driver.current_window_handle

        if tab['loc'] == 'U':  # 网址定位
            if self.url() and tab['val'] in self.url():
                return True
        elif tab['loc'] == 'E':
            if type(tab['val']) == str:  # 未指明定位 方式，则默认xpath
                if self.element(tab['val']).is_enabled():
                    return True
            elif type(tab['val']) == dict:  # 指明定位 方式
                if self.element(tab['val']['value'], tab['val']['type']).is_enabled():
                    return True
            elif tab['val'].is_enabled():  # 直接传递element
                return True
        return False

    def tab(self, tab=None):  # 获取当前tab，或者切换到指定tab, tab可以为dict或者handle或者None
        if tab:
            if type(tab) == dict:
                if not self.is_tab(tab):
                    for tab_ in self.tabs():
                        self.driver.switch_to.window(tab_)
                        time.sleep(1)  # 等待1秒以使driver反应过来
                        if self.is_tab(tab):
                            break
                if not self.is_tab(tab):
                    return None
            else:  # tab为handle对象
                self.driver.switch_to.window(tab)
        return self.driver.current_window_handle

    def tabs(self):  # 获取全部tab
        return self.driver.window_handles

    def close(self, tab=None):  # 关闭某个标签
        self.tab(tab)
        self.driver.close()

    def url(self):
        try:
            return self.driver.current_url
        except:
            return ''

    def keep(self, tab=None):  # 仅保留此tab
        keep = self.tab(tab)
        for tab_ in self.tabs():
            if tab_ != keep:
                self.close(tab_)
        return keep

    def to_default(self):
        self.driver.switch_to.default_content()
        self.in_frame = None
        return True

    def to_frame(self, value=None, type_="xpath"):
        self.to_default()
        if type(value) == Element:
            self.in_frame = value
            self.driver.switch_to.frame(value.get())
        elif type_.lower() == "id":
            try:
                self.in_frame = self.element(value, 'ID')
                self.driver.switch_to.frame(value)
            except:
                return False
        else:  # 只有ID或者xpath
            try:
                self.in_frame = self.element(value)
                self.driver.switch_to.frame(self.element(value).get())
            except:
                return False
        return True

    def element(self, selector='', by=None):
        if selector[0] == '(' and selector[-1] == ')' and (not by):
            return Element(self, *eval(selector))
        return Element(self, selector, by if by else 'XPATH')

    def elements(self, selector='', by='XPATH'):
        if by == 'XPATH':
            by_ = By.XPATH
        elif by == 'ID':
            by_ = By.ID
        elif by == 'CLASS':
            by_ = By.CLASS_NAME
        elif by == 'CSS':
            by_ = By.CSS_SELECTOR

        return self.driver.find_elements(by_, selector)

    def stop(self):
        self.driver.service.stop()

    def start(self):
        self.driver.service.start()

    def shut(self):
        self.driver.close()

    def refresh(self):
        self.driver.refresh()

    def status(self):  # complete, interactive
        try:
            status = self.driver.execute_script('return document.readyState')
        except:
            status = 'unknown'
        finally:
            return status