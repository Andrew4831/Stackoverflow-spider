#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy


class StackoverflowItem(scrapy.Item):
    index = scrapy.Field()
    qid = scrapy.Field()
    question_votes = scrapy.Field()
    question_views = scrapy.Field()
    question_title = scrapy.Field()
    question_links_url = scrapy.Field()
    question_tags = scrapy.Field()
    question_asked_time = scrapy.Field()
    question_asked_uid = scrapy.Field()
    comment_count = scrapy.Field()
    answers_num = scrapy.Field()
    question_body = scrapy.Field()
