#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import json
import logging
import os

import scrapy
from pydispatch import dispatcher
from scrapy import signals

from stackoverflow.spiders.items import StackoverflowItem
from stackoverflow.spiders.comments import StackoverflowComment
from stackoverflow.spiders.answers import StackoverflowAnswer
from stackoverflow.spiders.users import StackoverflowUser


#
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger = logging.getLogger('monitor')
# logger.setLevel(logging.INFO)
#
# fh = logging.FileHandler('monitor.log')
# fh.setLevel(logging.INFO)
#
# fh.setFormatter(formatter)
# logger.addHandler(fh)


class StackoverflowSpider(scrapy.Spider):
    name = "stackoverflow"
    crawl_page = 200
    per_page_num = 50
    skip_question_num_wiki = 0
    skip_question_num_no_user = 0
    skip_answer_num = 0
    skip_comment_num = 0
    question_index = 0
    comment_index = 0
    answer_index = 0
    user_index = 0
    users_list = []
    question_file_path = "stackoverflow/output/question/" + str(datetime.now().date()) + "-" + str(
        datetime.now().time().hour) + "-" + str(
        datetime.now().time().minute) + "-" + str(datetime.now().time().second) + "-questions.json"
    comment_file_path = "stackoverflow/output/comment/" + str(datetime.now().date()) + "-" + str(
        datetime.now().time().hour) + "-" + str(
        datetime.now().time().minute) + "-" + str(datetime.now().time().second) + "-comments.json"
    answer_file_path = "stackoverflow/output/answer/" + str(datetime.now().date()) + "-" + str(
        datetime.now().time().hour) + "-" + str(
        datetime.now().time().minute) + "-" + str(datetime.now().time().second) + "-answers.json"
    user_file_path = "stackoverflow/output/user/" + str(datetime.now().date()) + "-" + str(
        datetime.now().time().hour) + "-" + str(
        datetime.now().time().minute) + "-" + str(datetime.now().time().second) + "-users.json"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        self.count = 1

    def start_requests(self):
        with open(self.question_file_path, 'a') as f:
            f.write('[\n')
        with open(self.comment_file_path, 'a') as f:
            f.write('[\n')
        with open(self.answer_file_path, 'a') as f:
            f.write('[\n')
        with open(self.user_file_path, 'a') as f:
            f.write('[\n')

        _url = 'https://stackoverflow.com/questions?page={}&sort=votes&pagesize=50'
        urls = [_url.format(page) for page in range(1, self.crawl_page + 1)]
        # urls = [_url.format(page) for page in range(8, 9)]
        for index, url in enumerate(urls):
            yield scrapy.Request(url=url, callback=self.parse_questions_list, meta={"page": index + 1},
                                 priority=1000000000000000 - index)

    def parse_questions_list(self, response):
        page = response.meta["page"]
        request_index = 0

        for index in range(1, self.per_page_num + 1):
            self.count += 1
            # if self.count % 100 == 0:
            #     logger.info(self.count)
            sel = response.xpath('//*[@id="questions"]/div[{}]'.format(index))
            item = StackoverflowItem()

            skip = "".join(sel.xpath('div[2]/div[2]/div[2]/div[1]/div[1]/text()').extract())
            question_uid = "".join(sel.xpath('div[2]/div[2]/div[2]/div[1]/div[1]/a/@href').extract())

            if skip == 'Community wiki':
                self.skip_question_num_wiki += 1
                continue
            if question_uid == "":
                self.skip_question_num_no_user += 1
                continue

            self.question_index += 1
            request_index += 1
            item['index'] = str(self.question_index)
            item['qid'] = "".join(sel.xpath('div[2]/h3/a/@href').extract()).split("/")[2]
            item['question_votes'] = "".join(sel.xpath('div[1]/div[1]/span[1]/text()').extract())
            item['answers_num'] = "".join(sel.xpath('div[1]/div[2]/span[1]/text()').extract())
            item['question_views'] = "".join(sel.xpath('div[1]/div[3]/@title').extract()).split()[0].replace(",", "")
            item['question_title'] = "".join(sel.xpath('div[2]/h3/a/text()').extract())
            half_url = "".join(sel.xpath('div[2]/h3/a/@href').extract())

            item['question_links_url'] = "https://stackoverflow.com" + half_url
            tags = sel.xpath('div[2]/div[2]/div[1]/ul/li/a/text()').extract()
            item_tags = []
            for i, tag in enumerate(tags):
                item_tags.append(str(tag) + "::" + str(i + 1))
            item['question_tags'] = " ".join(item_tags)

            print("发送第{}页第{}个问题页面".format(page, request_index))
            yield scrapy.Request(url=item['question_links_url'], callback=self.parse_questions_detail,
                                 meta={"item": item, "page": page, "request_index": request_index},
                                 priority=(1000000000000000 - 100000 * page - index))

    def parse_questions_detail(self, response):
        page = response.meta["page"]
        item = response.meta["item"]
        request_index = response.meta["request_index"]
        print("接受第{}页第{}个问题页面".format(page, request_index))
        sel = response.xpath('//*[@class="inner-content clearfix"]')
        item['question_asked_time'] = "".join(
            sel.xpath('div[3]/div[1]/div[2]/div[2]/div[3]/div[1]/div[3]/div[1]/div[1]/span/@title').extract())[:-1]
        uid_sel=response.xpath('//div[@class="post-signature owner flex--item"]')
        item['question_asked_uid'] = "".join(
            uid_sel.xpath('div[1]/div[3]/a/@href').extract()).split('/')[2]
        # item['question_asked_uid'] = "".join(
        #     sel.xpath('div[3]/div[1]/div[2]/div[2]/div[3]/div[1]/div[3]/div[1]/div[2]/a/@href').extract()).split('/')[2]

        ############################################
        #                   user
        ############################################
        # question_uname = "".join(
        #     sel.xpath('div[3]/div[1]/div[2]/div[2]/div[3]/div[1]/div[3]/div[1]/div[2]/a/@href').extract()).split('/')[3]
        question_uname = "".join(
            uid_sel.xpath('div[1]/div[3]/a/@href').extract()).split('/')[3]
        # print(item['question_asked_uid']+' <-----> '+question_uname)
        question_user_url = 'https://stackoverflow.com/users/' + item['question_asked_uid'] + '/' + question_uname
        # print(question_user_url)
        if item['question_asked_uid'] not in self.users_list:
            yield scrapy.Request(question_user_url, callback=self.parse_users_detail,
                                 meta={"uid": item['question_asked_uid'], "uname": question_uname})
        else:
            print('本question的用户{}---{}已存在！跳过'.format(item['question_asked_uid'],question_uname))

        comment_count = "".join(sel.xpath('div[3]/div[1]/div[2]/span/text()').extract())
        if comment_count == "":
            comment_count = "0"
        item['comment_count'] = comment_count
        item['question_body'] = "".join(
            sel.xpath(
                'div[3]/div[1]/div[2]/div[2]/div[1]//p//text() | div[3]/div[1]/div[2]/div[2]/div[1]//ul//text()').extract())

        self.process_data(dict(item), self.question_file_path)
        print('问题 +++ 增加{}---{}问题，目前共爬取{}个问题'.format(item['qid'], item['question_title'], item['index']))
        # yield item

        remain_count = "".join(
            sel.xpath('div[3]/div[1]/div[2]/div[3]/div[1]/ul/@data-remaining-comments-count').extract())
        num = int(item['comment_count']) + 1 - int(remain_count)

        for index in range(1, num):
            comment = StackoverflowComment()
            com = response.xpath(
                '//*[@class="inner-content clearfix"]/div[3]/div[1]/div[2]/div[3]/div[1]/ul/li[{index}]'.format(
                    index=index))
            if "".join(com.xpath('@data-comment-owner-id').extract()) == "-1":
                self.skip_comment_num += 1
                continue
            self.comment_index += 1
            comment['index'] = str(self.comment_index)
            comment['cid'] = "".join(com.xpath('@data-comment-id').extract())
            comment['comment_qid'] = "".join(sel.xpath('div[3]/div[1]/div[2]/div[3]/div[1]/@data-post-id').extract())
            comment['comment_aid'] = "not this type"
            comment['comment_uid'] = "".join(com.xpath('@data-comment-owner-id').extract())

            ############################################
            #                   user
            ############################################
            comment_uname = "".join(com.xpath('div[2]/div[1]/div[1]/a/@href').extract()).split('/')[3]
            comment_user_url = 'https://stackoverflow.com/users/' + comment['comment_uid'] + '/' + comment_uname
            # print(comment_user_url)
            if comment['comment_uid'] not in self.users_list:
                yield scrapy.Request(comment_user_url, callback=self.parse_users_detail,
                                     meta={"uid": comment['comment_uid'], "uname": comment_uname})
            else:
                print('本comment1的用户{}---{}已存在！跳过'.format(comment['comment_uid'],comment_uname))

            comment['comment_votes'] = "".join(com.xpath('@data-comment-score').extract())
            comment['comment_date'] = "".join(
                com.xpath('div[2]/div[1]/span[2]/span/@title').extract()).split(',')[0][:-1]
            comment['comment_body'] = "".join(com.xpath('div[2]/div[1]/span[1]//text()').extract())

            self.process_data(dict(comment), self.comment_file_path)
            print('评论1 +++ 增加{}，这是{}问题下的评论，目前共爬取{}个评论'.format(comment['cid'], comment['comment_qid'], comment['index']))
            # yield comment

        # answer
        an = response.xpath("//div[contains(@id, 'answer-')]")
        for index, data in enumerate(an):
            answer = StackoverflowAnswer()
            self.answer_index += 1
            answer['index'] = str(self.answer_index)
            answer['aid'] = "".join(data.xpath('@data-answerid').extract())
            answer['answer_qid'] = "".join(data.xpath('@data-parentid').extract())
            uid = "".join(data.xpath('div[1]/div[2]/div[2]/div[1]/div[3]/div[1]/div[2]/a/@href').extract())
            if uid == "" or uid.split('/')[1] != "users":
                self.skip_answer_num += 1
                continue

            answer['answer_uid'] = "".join(
                data.xpath('div[1]/div[2]/div[2]/div[1]/div[3]/div[1]/div[2]/a/@href').extract()).split('/')[2]
            answer['answer_votes'] = "".join(data.xpath('@data-score').extract())
            answer['answer_body'] = "".join(
                data.xpath('div[1]/div[2]/div[1]//p//text() ' +
                           '| div[1]/div[2]/div[1]//ul//text()' +
                           '| div[1]/div[2]/div[1]//ol//text()').extract())
            answer['answer_date'] = "".join(
                data.xpath('div[1]/div[2]/div[2]/div[1]/div[3]/div[1]/div[1]/span/@title').extract())[:-1]
            self.process_data(dict(answer), self.answer_file_path)
            print('回答 +++ 增加{}，这是{}问题的回答，目前共爬取{}个回答'.format(answer['aid'], answer['answer_qid'], answer['index']))

            ############################################
            #                   user
            ############################################
            answer_uname = "".join(
                data.xpath('div[1]/div[2]/div[2]/div[1]/div[3]/div[1]/div[2]/a/@href').extract()).split('/')[3]
            answer_user_url = 'https://stackoverflow.com/users/' + answer['answer_uid'] + '/' + answer_uname
            # print(answer_user_url)
            if answer['answer_uid'] not in self.users_list:
                yield scrapy.Request(answer_user_url, callback=self.parse_users_detail,
                                     meta={"uid": answer['answer_uid'], "uname": answer_uname})
            else:
                print('本answer的用户{}---{}已存在！跳过'.format(answer['answer_uid'],answer_uname))

            com2 = data.xpath('div[1]/div[3]/div[1]/ul/li')
            comment2_aid = "".join(data.xpath('div[1]/div[3]/div[1]/@data-post-id').extract())

            for index2, data2 in enumerate(com2):
                comment2 = StackoverflowComment()
                if "".join(data2.xpath('@data-comment-owner-id').extract()) == "-1":
                    self.skip_comment_num += 1
                    continue
                self.comment_index += 1
                comment2['index'] = str(self.comment_index)
                comment2['cid'] = "".join(data2.xpath('@data-comment-id').extract())
                comment2['comment_qid'] = "not this type"
                comment2['comment_aid'] = str(comment2_aid)
                comment2['comment_uid'] = "".join(data2.xpath('@data-comment-owner-id').extract())
                comment2['comment_votes'] = "".join(data2.xpath('@data-comment-score').extract())
                comment2['comment_date'] = "".join(
                    data2.xpath('div[2]/div[1]/span[2]/span/@title').extract()).split(',')[0][:-1]
                comment2['comment_body'] = "".join(data2.xpath('div[2]/div[1]/span[1]//text()').extract())
                self.process_data(dict(comment2), self.comment_file_path)
                print('评论2 +++ 增加{}，这是{}回答下的评论，目前共爬取{}个评论'.format(comment2['cid'], comment2['comment_aid'], comment2['index']))

                ############################################
                #                   user
                ############################################
                comment2_uname = "".join(
                    data2.xpath('div[2]/div[1]/div[1]/a/@href').extract()).split('/')[3]
                comment2_user_url = 'https://stackoverflow.com/users/' + comment2['comment_uid'] + '/' + comment2_uname
                # print(comment2_user_url)
                if comment2['comment_uid'] not in self.users_list:
                    yield scrapy.Request(comment2_user_url, callback=self.parse_users_detail,
                                         meta={"uid": comment2['comment_uid'], "uname": comment2_uname})
                else:
                    print('本comment2的用户{}---{}已存在！跳过'.format(comment2['comment_uid'],comment2_uname))

    def parse_users_detail(self, response):
        uid = response.meta["uid"]
        uname = response.meta["uname"]
        if uid in self.users_list:
            return

        user = StackoverflowUser()
        self.user_index += 1
        user['index'] = str(self.user_index)
        user['uid'] = str(uid)
        user['uname'] = str(uname)
        top_tags = response.xpath('//div[@id="top-tags"]/div[2]/div')
        top_tags_str = ""
        for index, data in enumerate(top_tags):
            tag_str = "".join(data.xpath('div[1]/div[1]/a/text()').extract())
            top_tags_str = top_tags_str + tag_str + "::" + str(index + 1) + " "
        top_tags_str = top_tags_str[:-1]
        user['u_tag'] = top_tags_str

        self.users_list.append(uid)
        print('用户 +++ 增加{}---{}用户，目前共爬取{}名用户'.format(user['uid'],user['uname'],user['index']))
        self.process_data(dict(user), self.user_file_path)

    def spider_closed(self, spider):
        self.logger.info("Spider is closed. Do something here.")
        print('skip_question_num_wiki ---> {}'.format(self.skip_question_num_wiki))
        print('skip_question_num_no_user ---> {}'.format(self.skip_question_num_no_user))
        print('skip_answer_num ---> {}'.format(self.skip_answer_num))
        print('skip_comment_num ---> {}'.format(self.skip_comment_num))
        print('users_list_len ---> {}'.format(len(self.users_list)))
        # print('users_list ---> {}'.format(self.users_list))
        with open(self.question_file_path, 'a') as f:
            f.seek(f.tell() - 2)  # 移动文件指针到倒数第二个字符
            f.truncate()
            f.write('\n]')
        with open(self.comment_file_path, 'a') as f:
            f.seek(f.tell() - 2)  # 移动文件指针到倒数第二个字符
            f.truncate()
            f.write('\n]')
        with open(self.answer_file_path, 'a') as f:
            f.seek(f.tell() - 2)  # 移动文件指针到倒数第二个字符
            f.truncate()
            f.write('\n]')
        with open(self.user_file_path, 'a') as f:
            f.seek(f.tell() - 2)  # 移动文件指针到倒数第二个字符
            f.truncate()
            f.write('\n]')

    def process_data(self, data, filename):
        with open(filename, 'a') as f:
            item_json_str = json.dumps(data)
            f.write(item_json_str + ',\n')
