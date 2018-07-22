#!/usr/bin/python
import schedule
import server.db as DB
import time
from server.spider import crawler as Worker

def job():
  userCollection = DB.getCollection("cdut","user")
  # 遍历所有user
  doc = userCollection.find()
  for i in doc:
    Worker.init(userCollection,i["user"],i["pwd"],i["email"],True)

# 每分钟运行一次
schedule.every(1).hour.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
