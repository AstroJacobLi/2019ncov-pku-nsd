from baidu.items import BaiduNewsItem
import scrapy
import logging
import datetime
import pandas as pd

def parse_time(time_str):
    if "分钟" in time_str:
        delta = int(time_str.strip('前').strip('分钟'))
        delta = datetime.timedelta(minutes=delta)
        now = datetime.datetime.now().replace(second=0, microsecond=0)
        pub_time = pd.to_datetime(now - delta)
    elif "小时" in time_str:
        delta = int(time_str.strip('前').strip('小时'))
        delta = datetime.timedelta(hours=delta)
        now = datetime.datetime.now().replace(second=0, microsecond=0)
        pub_time = pd.to_datetime(now - delta)
    else:
        pub_time = datetime.datetime.strptime(time_str, '%Y年%m月%d日 %H:%M')
        pub_time = pd.to_datetime(pub_time)
    return pub_time

# spider class
class BaiduNews(scrapy.Spider):
    name = 'baidu_news'
    '''
    start_urls = ["https://www.baidu.com/s?ie=utf-8&cl=2&medium=0&rtt=1&bsst=1&rsv_dl=news_t_sk&tn=news&word=疫情+企业&rsv_sug3=1&rsv_sug2=0&inputT=14"]
    '''
    def __init__(self, keywords):
        self.keywords = keywords.split(' ')
        print('Keywords are: {}'.format(' '.join(self.keywords)))
        self.start_urls = ['https://www.baidu.com/s?ie=utf-8&cl=2&medium=0&rtt=1&bsst=1&rsv_dl=news_t_sk&tn=news&wd={}&tfflag=0'.format('+'.join(self.keywords))]
        super().__init__()
    
    custom_settings = {
            'LOG_LEVEL': logging.DEBUG,
            'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
        }
    
    def parse(self, response):
        item = BaiduNewsItem()
        page = response.css("div#content_left div.result")
        for news in page:
            item['title'] = "".join(news.css('h3.c-title a ::text').getall()).strip()
            item['url'] = news.css('h3.c-title a').attrib['href']
            author_time = "".join(news.css('div.c-summary p.c-author ::text').getall()).strip().split('\xa0\xa0')
            item['author'] = author_time[0].strip()
            item['time'] = parse_time(author_time[1].strip())
            if len(news.css('div.c-summary div.c-span18')) == 0: 
                item['abstract'] = "".join(news.css('div.c-summary::text').getall()).strip().replace('\xa0', '')
                
            else:
                abs_str = "".join(news.css('div.c-summary div.c-span18 ::text').getall()[3:]).split('...')
                item['abstract'] = abs_str[0].strip() + '...'

            if len(news.css('div.c-summary span.c-info a')) == 1:
                screenshot_pos = 0
            else:
                screenshot_pos = 1
            item['screenshot'] = news.css('div.c-summary span.c-info a')[screenshot_pos].attrib['href']

            #if item['time'] 
            #pd.to_datetime('2018年12月15日'.replace("年", "").replace("月", "").replace("日", "").strip())
            yield item
        
        next_page =  response.css("p#page a::attr(href)")[-1].get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
            