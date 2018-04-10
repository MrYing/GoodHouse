"""
获取某城市所有新房链接
"""
import re
from requestium import Session

ptn = re.compile('function_button_(\d+)')
s = Session(
    webdriver_path='../chromedriver',
    browser='chrome',
    webdriver_options={'arguments': ['headless']}
)


def qq_houses_id(url):
    results = []
    city = url.split('/')[-1]
    s.driver.get(url)
    s.transfer_driver_cookies_to_session()
    html = s.get(url(1)).text
    results.extend(ptn.findall(html))
    total_count = int(html.split(' = ')[-1].rstrip(';'))
    for page in range(2, int(total_count / 10) + 2):
        results.extend(ptn.findall(s.get(url(page)).text))
    return [f'http://db.house.qq.com/{city}_{result}/' for result in results]