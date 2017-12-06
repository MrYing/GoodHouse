from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from GoodHouse.spiders.anjuke import Anjuke


process = CrawlerProcess(get_project_settings())
process.crawl(Anjuke)
process.start()