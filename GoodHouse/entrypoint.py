from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from GoodHouse.spiders.anjuke import Anjuke
from GoodHouse.spiders.souhujiaodian import Souhujiaodian


process = CrawlerProcess(get_project_settings())
# process.crawl(Anjuke)
process.crawl(Souhujiaodian)
process.start()

