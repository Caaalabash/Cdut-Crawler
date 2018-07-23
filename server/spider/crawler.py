import time
import logging
import requests
import execjs
from pyquery import PyQuery as pq
from server.tool import sendemail as Worker
import server.config as Config

# 登录接口
loginService = "http://202.115.133.173:805/Common/Handler/UserLogin.ashx"
# 成绩接口
scoreService = "http://202.115.133.173:805/SearchInfo/Score/ScoreList.aspx"
# 当前学期
currentTerm = "201702"

# 定制header方法,接收一个cookie,返回一个key-value对
def getHeaders(cookie):
  return {
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36",
    "Host" : "202.115.133.173:805",
    "Origin": "http://202.115.133.173:805",
    "Referer": "http://202.115.133.173:805/Default.aspx",
    "X-Requested-With": "XMLHttpRequest",
    "Upgrade-Insecure-Requests": "1",
    "Cookie" : cookie
  }

# 解析js代码获得经过md5加密后的密码
def getMd5pwd(pwd):
  return execjs.compile(open(r"{0}/spider/md5.js".format(Config.RootPath)).read()).call('hex_md5', pwd)

# 根据用户名/密码发送登录请求
# 登录成功返回 cookie
# 登录失败返回 True
# 连接服务器失败返回 False
def login(username,password):
  t = round(time.time() * 1000)
  tstr = str(t)
  action = "Login"
  pwd = getMd5pwd(username + tstr + getMd5pwd(password))

  try:
    r = requests.post(loginService, data={
      "Action": action,
      "userName": username,
      "pwd": pwd,
      "sign": t
    })
    if (r.text == "0"):
      return r.headers["Set-Cookie"]
    else :
      return True

  except Exception as err:
    return False

# 请求成绩页面 返回Dom树
def getList(cookie):
  r = requests.get(scoreService,headers=getHeaders(cookie))
  return r.text

# 解析DOM树提取需要的内容
def getScore(dom):
  list = []
  doc = pq(dom)
  its = doc(".listUl > .item").items()
  for it in its:
    # 如果是本学期的成绩
    if(it(".floatDiv20").text() == currentTerm):
      # 提取 课程编号/课程名称/成绩
      id = it(".floatDiv10:nth-child(2)").text()
      className = it(".floatDiv10:nth-child(3)").text()
      score = it(".floatDiv10:nth-child(6)").text()
      list.append({
        "id":id,
        "className":className,
        "score":score
      })
  return list

# 比较
def compare(dataFromDB,crawlerData):
  list = []
  storeId = []
  # 如果数据库中没有数据,返回爬去的数据
  if(len(dataFromDB)==0):
    return crawlerData
  # 如果爬取的数据长度<= 数据库存储的数据,说明没有更新
  if(len(crawlerData) <= len(dataFromDB)):
    return []
  for i in dataFromDB:
    storeId.append(i['id'])
  for i in crawlerData:
    if i['id'] not in storeId:
      list.append(i)
  return list


# 最终滴劳动力
def init(collection,user,pwd,email,wannaSend):
  res = login(user, pwd)
  try:
    # 如果返回了Cookie
    if (res != False and res != True):
      # 处理cookie 这里也许要改一下
      list = res.split(";")
      cookie = list[0] + ";" + list[2].split(",")[1]
      # 提取本学期成绩
      dom = getList(cookie)
      list = getScore(dom)
      # 提取数据库数据
      doc = collection.find_one({"user": user})
      global dataFromDB
      if ("classList" in doc):
        dataFromDB = doc["classList"]
      else:
        dataFromDB = []
      diff = compare(dataFromDB, list)
      for i in diff:
        collection.update({"user": user}, {"$push": {"classList": i}})
        if(wannaSend==True):
          Worker.send_email(email, "成绩更新啦!", i['className'] + ":" + i['score'] + "分")
    else:
      logging.ERROR("handle [User]" + user + "LOGGIN ERROR")
  except Exception as err:
    logging.ERROR("handle [User]"+ user + "ERROR")


