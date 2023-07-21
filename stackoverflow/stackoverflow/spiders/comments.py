#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy


class StackoverflowComment(scrapy.Item):
    index = scrapy.Field()
    cid = scrapy.Field()
    comment_qid = scrapy.Field()
    comment_aid = scrapy.Field()
    comment_uid = scrapy.Field()
    comment_votes = scrapy.Field()
    comment_body = scrapy.Field()
    comment_date = scrapy.Field()
