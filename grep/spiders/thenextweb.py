__author__ = 'ahmed'
import traceback
import sys
import scrapy
import logging
from grep.items import GrepItem
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class ThenextwebSpider(CrawlSpider):

    #####################
    # # scrappy own vars
    ######################
    name = "thenextweb"
    allowed_domains = ["thenextweb.com"]
    start_urls = (
        'http://thenextweb.com/',
    )

    rules = (
        # # Rules should allow only pages will be craweled
        Rule(LinkExtractor(allow=('[\-0-9a-zA-Z]+/\d+/\d+/\d+/[\-0-9a-zA-Z]+/?$'), unique=True),
             callback='parse_article'),
        # # rules to allow categories only
        Rule(LinkExtractor(allow=('section/[\-0-9a-zA-Z]+$'), unique=True))
    )


    #######################
    # # my own variables
    #######################
    xpaths = {
        'title': '//article/header/h1//text()',
        'image': '//div[@class="lazy post-featuredImage-image"]//@data-src-set',
        'content': '//article/div[contains(@class,"post-body")]/p//text()',
        'time': '//header//time[contains(@class,"timeago")]//@datetime'
    }

    response = None

    def parse_article(self, response):
        self.response = response

        try:
            item = GrepItem()
            item['url'] = self.response.url
            item['title'] = self.getxPath(self.xpaths['title'])[0]
            lastImageSize = 0
            for imageCollection in self.getxPath(self.xpaths['image'])[0].split(','):
                imageDesc = imageCollection.split(' ')
                if lastImageSize < imageDesc[1]:
                    lastImageSize = imageDesc[1]
                    item['image'] = imageDesc[1]

            item['time'] = self.getxPath(self.xpaths['time'])[0]
            content = ''
            for singleContent in self.getxPath(self.xpaths['content']):
                content += singleContent
            item['raw_content'] = item['content'] = content
            return [item]
        except Exception, e:
            traceback.print_exc(file=sys.stderr)
            self.log(" Url " + self.response.url + " failed ", logging.ERROR)

    def getxPath(self, selectXpath):
        return self.response.xpath(selectXpath).extract()