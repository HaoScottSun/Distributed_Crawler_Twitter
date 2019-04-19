# -*- coding: utf-8 -*-
import pandas as pd
from sqlalchemy import create_engine
from TweetScraper.items import Tweet

API_ENDPOINT = "postgres://udhirs6827duas:pacf2c0e626ad2676436a5553e64b48b7f24e6c7863c9f149f0ff4030e3d6c6e5@ec2-18-233-145-60.compute-1.amazonaws.com:5432/d3kjpkvmh982t3"
table_name = 'twitters'
# sql_1 ="""
#                 SELECT setval(pg_get_serial_sequence('twitters', 'id'), (SELECT MAX(id) FROM twitters)+1);
#         """
# engine.execute(sql_1)

class SavetoPSQLPipeline(object):
    def process_item(self, item, spider):
        data_1 = dict(item)
        df = pd.DataFrame.from_dict(data_1)
        engine = create_engine(API_ENDPOINT)
        df.to_sql(table_name, engine, if_exists='append', index=False)
        item = []
        return item
