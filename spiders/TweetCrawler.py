from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.conf import settings
from scrapy import http
from scrapy.shell import inspect_response  # for debugging
import re
import io
import json
import time
import logging
import pkgutil
import pandas as pd
try:
    from urllib import quote  # Python 2.X
except ImportError:
    from urllib.parse import quote  # Python 3+

from datetime import datetime

from TweetScraper.items import Tweet

logger = logging.getLogger(__name__)
pkdata = pkgutil.get_data("TweetScraper", "v1_mul_2.csv")
df = pd.read_csv(io.BytesIO(pkdata))
# df = pd.read_csv('v1_mul_2.csv')
company_name = df['Company_name'].tolist()
Tickers = df['Ticker'].tolist()


class TweetScraper(CrawlSpider):
    name = 'TweetScraper'
    allowed_domains = ['twitter.com']

    def __init__(self, query='', lang='en', crawl_user=False, top_tweet=False):
        self.query = []
        for i in range(200):
            self.query.append(company_name[i]+' '+Tickers[i])
        self.url = "https://twitter.com/i/search/timeline?f=tweets&vertical=default&l={}".format(lang)
        # https://twitter.com/i/search/timeline?vertical=default&l=en&q=ali%20BABA&src=typed
        # if not top_tweet:
        #     self.url = self.url + "&f=tweets"

        self.url = self.url + "&q=%s&src=typed"#&max_position=%s

        # self.crawl_user = crawl_user

    def start_requests(self):
        for index, query in enumerate(self.query):
            url = self.url % (quote(query))
            yield http.Request(url, callback=lambda response, i=index: self.parse_page(response, i))

    def parse_page(self, response, index):
        # inspect_response(response, self)
        # handle current page
        data = json.loads(response.body.decode("utf-8"))
        for item in self.parse_tweets_block(data['items_html'],index):
            yield item

        # # get next page
        # min_position = data['min_position']
        # min_position = min_position.replace("+","%2B")
        # url = self.url % (quote(self.query), min_position)
        # yield http.Request(url, callback=self.parse_page)

    def parse_tweets_block(self, html_page,index):
        page = Selector(text=html_page)

        ### for text only tweets
        items = page.xpath('//li[@data-item-type="tweet"]/div')
        for item in self.parse_tweet_item(items,index):
            yield item

    def parse_tweet_item(self, items, index):
        tweet = Tweet()

        tweet['post_content'] = []
        tweet['user_name'] = []
        tweet['URL'] = []
        tweet['num_retweets'] = []
        tweet['num_likes'] = []
        tweet['num_comments'] = []
        tweet['timestamp'] = []
        tweet['symbols'] = []
        tweet['user_account'] = []

        for item in items:
            try:
                # ID = item.xpath('.//@data-tweet-id').extract()
                # if not ID:
                #     continue
                # tweet['ID'] = ID[0]

                ### get text content
                timestamp = datetime.fromtimestamp(int(
                    item.xpath('.//div[@class="stream-item-header"]/small[@class="time"]/a/span/@data-time').extract()[
                        0])).strftime('%Y-%m-%d %H:%M:%S')
                # if timestamp
                text = ''.join(
                    item.xpath('.//div[@class="js-tweet-text-container"]/p//text()').extract()).replace(' # ','#').replace(' @ ','@')
                if text == '':
                    continue
                tweet['post_content'].append(text)
                tweet['user_name'].append(
                    item.xpath('.//span[@class="username u-dir u-textTruncate"]/b/text()').extract()[0])
                ### get meta data
                tweet['URL'].append(item.xpath('.//@data-permalink-path').extract()[0])

                nbr_retweet = item.css('span.ProfileTweet-action--retweet > span.ProfileTweet-actionCount').xpath(
                    '@data-tweet-stat-count').extract()
                if nbr_retweet:
                    tweet['num_retweets'].append(int(nbr_retweet[0]))
                else:
                    tweet['num_retweets'].append(0)

                nbr_favorite = item.css('span.ProfileTweet-action--favorite > span.ProfileTweet-actionCount').xpath(
                    '@data-tweet-stat-count').extract()
                if nbr_favorite:
                    tweet['num_likes'].append(int(nbr_favorite[0]))
                else:
                    tweet['num_likes'].append(0)

                nbr_reply = item.css('span.ProfileTweet-action--reply > span.ProfileTweet-actionCount').xpath(
                    '@data-tweet-stat-count').extract()
                if nbr_reply:
                    tweet['num_comments'].append(int(nbr_reply[0]))
                else:
                    tweet['num_comments'].append(0)

                tweet['timestamp'].append(timestamp)
                tweet['symbols'].append(Tickers[index])
                ### get photo
                # has_cards = item.xpath('.//@data-card-type').extract()
                # if has_cards and has_cards[0] == 'photo':
                #     tweet['has_image'] = True
                #     tweet['images'] = item.xpath('.//*/div/@data-image-url').extract()
                # elif has_cards:
                #     logger.debug('Not handle "data-card-type":\n%s' % item.xpath('.').extract()[0])

                ### get animated_gif
                # has_cards = item.xpath('.//@data-card2-type').extract()
                # if has_cards:
                #     if has_cards[0] == 'animated_gif':
                #         tweet['has_video'] = True
                #         tweet['videos'] = item.xpath('.//*/source/@video-src').extract()
                #     elif has_cards[0] == 'player':
                #         tweet['has_media'] = True
                #         tweet['medias'] = item.xpath('.//*/div/@data-card-url').extract()
                #     elif has_cards[0] == 'summary_large_image':
                #         tweet['has_media'] = True
                #         tweet['medias'] = item.xpath('.//*/div/@data-card-url').extract()
                #     elif has_cards[0] == 'amplify':
                #         tweet['has_media'] = True
                #         tweet['medias'] = item.xpath('.//*/div/@data-card-url').extract()
                #     elif has_cards[0] == 'summary':
                #         tweet['has_media'] = True
                #         tweet['medias'] = item.xpath('.//*/div/@data-card-url').extract()
                #     elif has_cards[0] == '__entity_video':
                #         pass  # TODO
                #         # tweet['has_media'] = True
                #         # tweet['medias'] = item.xpath('.//*/div/@data-src').extract()
                #     else:  # there are many other types of card2 !!!!
                #         logger.debug('Not handle "data-card2-type":\n%s' % item.xpath('.').extract()[0])
                #
                # is_reply = item.xpath('.//div[@class="ReplyingToContextBelowAuthor"]').extract()
                # tweet['is_reply'] = is_reply != []
                #
                # is_retweet = item.xpath('.//span[@class="js-retweet-text"]').extract()
                # tweet['is_retweet'] = is_retweet != []

                tweet['user_account'].append(item.xpath('.//@data-user-id').extract()[0])


                # if self.crawl_user:
                #     ### get user info
                #     user = User()
                #     user['ID'] = tweet['user_id']
                #     user['name'] = item.xpath('.//@data-name').extract()[0]
                #     user['screen_name'] = item.xpath('.//@data-screen-name').extract()[0]
                #     user['avatar'] = \
                #         item.xpath('.//div[@class="content"]/div[@class="stream-item-header"]/a/img/@src').extract()[0]
                #     yield user
            except:
                logger.error("Error tweet:\n%s" % item.xpath('.').extract()[0])
                # raise
        yield tweet

    def extract_one(self, selector, xpath, default=None):
        extracted = selector.xpath(xpath).extract()
        if extracted:
            return extracted[0]
        return default
