# # -*- coding: utf-8 -*-
#
# import json
# from datetime import datetime
# from stackoverflow.spiders.items import StackoverflowItem
# from stackoverflow.spiders.comments import StackoverflowComment
#
#
# class QuestionPipeline:
#     def __init__(self):
#         file_path = "output/question/" + str(datetime.now().date()) + "-" + str(datetime.now().time().hour) + "-" + str(
#             datetime.now().time().minute) + "-" + str(datetime.now().time().second) + "-question.json"
#         self.file = open(file_path, 'w')
#
#     def process_item(self, item, spider):
#         if isinstance(item, StackoverflowItem):
#             line = json.dumps(dict(item)) + ",\n"
#             self.file.write(line)
#             return item
#
#     def close_spider(self, spider):
#         self.file.close()
#
#
# class CommentPipeline:
#     def __init__(self):
#         file_path = "output/comment/" + str(datetime.now().date()) + "-" + str(datetime.now().time().hour) + "-" + str(
#             datetime.now().time().minute) + "-" + str(datetime.now().time().second) + "-comment.json"
#         self.file = open(file_path, 'w')
#
#     def process_item(self, item, spider):
#         if isinstance(item, StackoverflowComment):
#             line = json.dumps(dict(item)) + "\n"
#             self.file.write(line)
#             return item
#
#     def close_spider(self, spider):
#         self.file.close()
