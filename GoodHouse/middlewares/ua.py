from fake_useragent import UserAgent
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware


class RandomUserAgent(UserAgentMiddleware):

    def process_request(self, request, spider):
        request.headers.setdefault('User-Agent', UserAgent().random)