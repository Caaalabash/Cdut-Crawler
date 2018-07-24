import redis
import logging
import random
import server.config as Config

r = redis.Redis()

class RedisQueue(object):
  def __init__(self, name, namespace='queue'):
    self.__db = redis.Redis(Config.redis_host,Config.redis_port,0)
    if(namespace==''):
      self.key = '%s' % (name)
    else:
      self.key = '%s:%s' % (namespace, name)
    logging.info("Connect Redis Success")

  def qsize(self):
    return self.__db.llen(self.key)  # 返回队列里面list内元素的数量

  def put(self, item):
    self.__db.rpush(self.key, item)  # 添加新元素到队列最右方
  def get_nowait(self):
    # 直接返回队列第一个元素，如果队列为空返回的是None
    item = self.__db.lpop(self.key)
    return item
  def get_random_item(self):
    length = self.__db.llen(self.key)
    index = random.random(0,length)
    return self.__db.lindex(self.key,index)