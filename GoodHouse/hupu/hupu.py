import time
import logging
from selenium import webdriver

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
    # datefmt='%a, %d %b %Y %H:%M:%S',
    # filename='myapp.log',
    # filemode='w'
)


class HuPu:
    """
    虎扑网刷回复
    提供登录、评论功能
    需要人为滑动验证登录
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.driver = webdriver.Firefox()
        self.driver.set_page_load_timeout(10)

    def login(self, username, password):
        """
        人为滑动验证，时间为１０秒
        """
        if self.request('https://passport.hupu.com/pc/login') == 110:
            return
        try:
            self.driver.find_element_by_id('J_username').send_keys(username)
            self.driver.find_element_by_id('J_pwd').send_keys(password)
            time.sleep(10)
            self.driver.find_element_by_id('J_submit').click()
            time.sleep(1)
        except:
            self.logger.error('login error!')
            self.driver.close()

    def comment(self, url, commentary):
        """
        添加评论
        """
        if self.request(url) == 110:
            return
        try:
            self.driver.find_element_by_id('atc_content').send_keys(commentary)
            self.driver.find_element_by_id('fastbtn').click()
            time.sleep(2)
        except:
            self.logger.error('find element error!')
        time.sleep(2)

    def request(self, url):
        """
        对driver.get()的封装
        １１０仅用做判断是否成功访问，本身并无意义
        """
        try:
            self.driver.get(url)
            time.sleep(1)
        except:
            try:
                self.driver.execute_script('window.stop()')
            except:
                self.logger.error('request %s error!', url)
                return 110


if __name__ == '__main__':
    hupu = HuPu()
    hupu.login('', '')
    url = 'https://bbs.hupu.com/21155004.html'
    commentary = '之前爬过，太惊险了！'
    hupu.comment(url, commentary)
    hupu.driver.close()
