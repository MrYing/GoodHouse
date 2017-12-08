"""
顺序返回
"""

import grequests

sites = [
        'http://www.firefox.com.cn/',
        'http://www.asus.com.cn/',
        'http://www.sina.com.cn/',
        'http://www.qq.com/',
        'http://news.163.com/',
        'http://yule.sohu.com/',
        'http://ent.163.com/',
        'http://news.qq.com/',
        'http://www.toutiao.com/',
        'http://www.csdn.net/',
        'http://www.7c.com/',
        'http://www.9ku.com/',
        'http://www.9553.com/',
        'http://www.eeyy.com/',
        'http://www.cr173.com/',
        'http://www.ddooo.com/',
        'http://iphone.tgbus.com/',
        'http://soft.hao123.com/',
        'http://www.xitongzhijia.net/',
        'http://www.xdowns.com/',
        'http://www.xinhuanet.com/',
        'http://weego-hotel.oss-cn-beijing.aliyuncs.com/'
]

requests = (grequests.get(url) for url in sites)

results = grequests.map(requests)

urls = [result.url for result in results]
for i in range(len(sites)):
    if sites[i] == urls[i]:
        print(1)
    else:
        print(sites[i])
        print(urls[i])


