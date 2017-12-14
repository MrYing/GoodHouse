from fake_useragent import UserAgent
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware


class RandomUserAgent(UserAgentMiddleware):

    def process_request(self, request, spider):
        # TODO: NO mobile browser
        request.headers.setdefault('User-Agent', UserAgent().random)
