from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from GoodHouse.spiders.anjuke import Anjuke
from GoodHouse.spiders.souhujiaodian import Souhujiaodian
from GoodHouse.spiders.soufang import Soufang


process = CrawlerProcess(get_project_settings())
process.crawl(Anjuke)
process.crawl(Souhujiaodian)
process.crawl(Soufang)
process.start()