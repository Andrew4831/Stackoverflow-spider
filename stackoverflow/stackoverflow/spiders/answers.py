#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy


class StackoverflowAnswer(scrapy.Item):
    index = scrapy.Field()
    aid = scrapy.Field()
    answer_qid = scrapy.Field()
    answer_uid = scrapy.Field()
    answer_votes = scrapy.Field()
    answer_body = scrapy.Field()
    answer_date = scrapy.Field()
