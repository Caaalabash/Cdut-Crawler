#!/usr/bin/python
from flask import Flask,request,jsonify
from server.spider import crawler as Crawler
import server.db as DB
from server.rediss import RedisQueue
app = Flask(__name__)

userCollection = DB.getCollection("cdut","user")

#路由
@app.route("/",methods=["GET"])
def hello_world():
  return "hello world from flask"

#存储订阅信息
#code 2 :已经订阅过
#code 1 :用户名/密码错误
#code 0 :订阅成功
#code -1 :连接服务器失败
@app.route("/api/cdut/subscribe",methods=["POST"])
def save():
  username = request.form.get('user')
  password = request.form.get('pwd')
  email = request.form.get('email')
  needCheck = request.form.get('check')
  global resp

  # 检查是否已经订阅过
  check = userCollection.find_one({"user":username})
  if(check != None):
    resp = jsonify({'code': "2"})
  else :
    # 检查是否可以登录
    result = Crawler.login(username, password)
    # 无法连接到服务器
    if (result == False):
      resp = jsonify({'code': "-1"})
    # 账号/密码错误
    elif(result ==True):
      resp = jsonify({"code": "1"})
    else:
      # 如果用户想要立即检查: 就push进redis队列
      queue = RedisQueue("taskQueue")
      if (needCheck == "true"):
        str = " ".join((username,password,email,"true"))
      # 用户选择只接受最新的成绩:这将不发送目前的成绩
      else :
        str = " ".join((username, password, email, "false"))
      queue.put(str)
      obj = {
        "user": username,
        "pwd": password,
        "email": email
      }
      # 写入数据
      userCollection.insert_one(obj)
      resp = jsonify({'code': "0"})

  resp.headers['Access-Control-Allow-Origin'] = '*'
  return resp

#退订
#code 1 :并没有订阅
#code 0 :退订成功
@app.route("/api/cdut/unsubscribe",methods=["POST"])
def unsubscribe():
  username = request.form.get('user')
  global resp

  check = userCollection.find_one({"user": username})
  # 订阅过
  if (check != None):
    userCollection.delete_one({"user": username})
    resp = jsonify({'code': "0"})
  else:
    resp = jsonify({'code': "1"})

  resp.headers['Access-Control-Allow-Origin'] = '*'
  return resp

#更改邮箱
@app.route("/api/cdut/changeEmail",methods=["POST"])
def changeEmail():
  email = request.form.get('email')
  username = request.form.get('user')
  global resp
  # 查找用户是否存在
  check = userCollection.find_one({"user": username})
  if (check != None) :
    userCollection.update({"user": username},{"$set":{"email":email}})
    resp = jsonify({'code': "0"})
  else :
    resp = jsonify({'code': "1"})

  resp.headers['Access-Control-Allow-Origin'] = '*'
  return resp

if __name__ == '__main__':
  app.run(port=3003)