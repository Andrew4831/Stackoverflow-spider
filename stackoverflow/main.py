from scrapy import cmdline
from datetime import datetime

file_path = "output/" + str(datetime.now().date()) + "-" + str(datetime.now().time().hour) + "-" + str(
    datetime.now().time().minute) + "-" + str(datetime.now().time().second) + "-stackoverflow.json"
command = "scrapy crawl stackoverflow -o " + file_path
command1 = "scrapy crawl stackoverflow"
cmdline.execute(command1.split())
