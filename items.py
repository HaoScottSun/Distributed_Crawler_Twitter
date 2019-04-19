# -*- coding: utf-8 -*-

# Define here the models for your scraped items
from scrapy import Item, Field


class Tweet(Item):
    post_content = Field()       # tweet id
    user_name = Field()      # tweet url
    URL = Field() # post time
    num_retweets = Field()     # text content
    num_likes = Field()  # user id
    num_comments = Field()  # username of tweet

    timestamp = Field()  # nbr of retweet
    symbols = Field()  # nbr of favorite
    user_account = Field()

# class User(Item):
#     ID = Field()            # user id
#     name = Field()          # user name
#     screen_name = Field()   # user screen name
#     avatar = Field()        # avator url
