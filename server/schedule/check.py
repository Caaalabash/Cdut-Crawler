#!/usr/bin/python
import time
import schedule
from server.rediss import RedisQueue
import server.db as DB
from server.spider import crawler as Worker


def job():
  queue = RedisQueue("taskQueue")
  # 遍历所有user
  doc = queue.get_nowait()
  if(doc != None):
    userCollection = DB.getCollection("cdut", "user")
    # 从redis中取出一个任务
    str = doc.decode('utf-8')
    i = str.split(" ")
    global flag
    # 这里只是把字符串变成布尔值,判断这个任务是否需要发送邮件
    if(i[3]=="true"):
      flag = True
    else:
      flag =False
    Worker.init(userCollection, i[0], i[1], i[2],flag)


# 每分钟运行一次
schedule.every(1).minutes.do(job)


while True:
    schedule.run_pending()
    # 为了避免过高的CPU占用,让出5秒,否则CPU会一直是100%状态
    time.sleep(5)
