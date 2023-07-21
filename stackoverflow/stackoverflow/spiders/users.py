#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy


class StackoverflowUser(scrapy.Item):
    index = scrapy.Field()
    uid = scrapy.Field()
    uname = scrapy.Field()
    u_tag = scrapy.Field()