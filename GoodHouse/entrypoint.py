from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from spiders.anjuke import Anjuke
from spiders.souhujiaodian import Souhujiaodian
from spiders.soufang import Soufang
from spiders.qq import QQ


process = CrawlerProcess(get_project_settings())
process.crawl(Anjuke)
process.crawl(Souhujiaodian)
process.crawl(Soufang)
process.crawl(QQ)
process.start()