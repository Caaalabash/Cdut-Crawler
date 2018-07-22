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
    str = doc.decode('utf-8')
    i = str.split(" ")
    global flag
    if(i[3]=="true"):
      flag = True
    else:
      flag =False
    Worker.init(userCollection, i[0], i[1], i[2],flag)


# 每分钟运行一次
schedule.every(1).minutes.do(job)


while True:
    schedule.run_pending()
    time.sleep(1)
