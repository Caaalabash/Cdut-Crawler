#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from pymongo import MongoClient
import server.config as Config


def getCollection(dbName,collectionName):
  # 建立数据库链接
  client = MongoClient(host=Config.host, port=Config.port)
  # 选择数据库/集合
  db = client[dbName]
  userCollection = db[collectionName]
  # 配置日志选项
  logging.basicConfig(filename=Config.RootPath+"/cdut.log", level=logging.DEBUG, format=Config.LOG_FORMAT, datefmt=Config.DATE_FORMAT)
  # 返回集合
  logging.info("Connect Mongodb Success")
  return userCollection