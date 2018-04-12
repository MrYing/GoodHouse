from scrapy import Spider, Request
from utils.useful_functions import find
from xpath import qq as q
from utils.qq_houses_id import qq_houses_id
from settings import CITY, base_info_dict


class QQ(Spider):

    name = 'qq'

    custom_settings = {'DOWNLOAD_DELAY': 3}

    urls = [
        'http://db.house.qq.com/xian',
    ]

    def start_requests(self):
        for url in self.urls:
            city, housses_ids = qq_houses_id(url)
            for house_id in housses_ids:
                info = f'http://db.house.qq.com/{city}_{house_id}/info.html'
                photo = f'http://photo.house.qq.com/{city}_{house_id}/photo/'
                news = f'http://db.house.qq.com/{city}_{house_id}/news/'
                yield Request(info, callback=self.parse_xiangqing,
                              meta={'house_id': house_id, 'city': city})

                yield Request(photo, callback=self.parse_xiangce,
                              meta={'house_id': house_id})

                yield Request(news, callback=self.parse_news,
                              meta={'house_id': house_id})

    def parse_xiangqing(self, response):
        house = {
            'new_data': True,
            'table': self.name,
            'house_id': response.meta['house_id'],
            'city': CITY[response.meta['city']],
            'building_name': find(response, q.NAME),
            'alias_name': find(response, q.ALIAS),
            'description': ''.join(find(response, q.DESCRIPTION, False))
        }
        for div_id in ['basics', 'saleIntro', 'building', 'property']:
            xp = f'//div[@id="{div_id}"]/div[2]/ul/li'
            for item in response.xpath(xp):
                name = find(item, './span/text()')
                if not name:
                    continue
                if name not in base_info_dict:
                    self.logger.warning('name %s not in dict %s', name, response.url)
                    continue
                house[base_info_dict[name]] = find(item, './p/text()')
        try:
            other_info = ' '.join(find(response, q.OTHER_INFO_MORE, False))
        except:
            other_info = ' '.join(find(response, q.OTHER_INFO, False))
        house.update({'transportation': other_info})

        yield house

    def parse_xiangce(self, response):
        """TODO: 如果超过８张，拿不全图片"""
        pics = response.xpath(q.PICS)
        if not pics:
            self.logger.error('pic not found %s', response.url)
            return
        pictures = {
            'house_id': response.meta['house_id'],
            'table': self.name,
        }
        album = []
        # 房型
        if find(pics[0], './@id') == '_apartment':
            yield {
                'new_data': True,
                'house_id': response.meta['house_id'],
                'table': self.name + '_room',
                'room_album': [
                    {
                        'room_label': find(item, './div[2]/a/text()'), 
                        'room_url': find(item, q.IMG)
                    }
                    for item in pics[0].xpath('.//ul/li')
                ]
            }

        # 所有类型图片
        for pic in pics:
            title = find(pic, q.TITLE)
            for src in find(pic, q.IMG, False):
                album.append({
                    'picture_title': title,
                    'picture_url': src
                })
        pictures.update({'item': ('album', album)})
        yield pictures

    def parse_news(self, response):
        # TODO: 只获取了第一页
        story_list = response.xpath('//div[@class="bd"]')
        if not story_list:
            self.logger.warning('no story %s', response.url)
            return

        news = [
            {
                'update_at': find(story, './div/span/text()'),
                'news_content': {
                    'news_link': find(story, './/h3/a/@href'),
                    'news_title': find(story, './/h3/a/text()')
                }
            }
            for story in story_list
        ]

        yield {
            'house_id': response.meta['house_id'],
            'table': self.name,
            'item': ('news', news)
        }