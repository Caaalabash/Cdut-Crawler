#!/usr/bin/python
from flask import Flask,request,jsonify
from server.tool import validation as Validation
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
  # 参数校验
  form = Validation.SubscriptionForm(request.form)
  if not form.validate():
    return jsonify({"msg":"Invalid Request"})

  username = request.form.get('user')
  password = request.form.get('pwd')
  email = request.form.get('email')
  needCheck = request.form.get('check')

  # 检查是否已经订阅过
  check = userCollection.find_one({"user":username})
  if(check != None):
    return jsonify({'code': "2"})
  # 检查是否可以登录
  result = Crawler.login(username, password)
  # 无法连接到服务器
  if (result == False):
    return jsonify({'code': "-1"})
  # 账号/密码错误
  elif (result == True):
    return jsonify({"code": "1"})
  else:
    # 如果用户想要立即检查: 就push进redis队列
    queue = RedisQueue("taskQueue")
    if (needCheck == "true"):
      str = " ".join((username, password, email, "true"))
    # 用户选择只接受最新的成绩:这将不发送目前的成绩
    else:
      str = " ".join((username, password, email, "false"))
    # 写入任务队列
    queue.put(str)
    obj = {
      "user": username,
      "pwd": password,
      "email": email
    }
    # 写入数据
    userCollection.insert_one(obj)
    return jsonify({'code': "0"})

#退订
#code 1 :并没有订阅
#code 0 :退订成功
@app.route("/api/cdut/unsubscribe",methods=["POST"])
def unsubscribe():
  # 参数校验
  form = Validation.UnsubscriptionForm(request.form)
  if not form.validate():
    return jsonify({"msg": "Invalid Request"})
  username = request.form.get('user')
  # 检查是否订阅过
  check = userCollection.find_one({"user": username})
  # 订阅过
  if (check != None):
    userCollection.delete_one({"user": username})
    return jsonify({'code': "0"})
  else:
    return jsonify({'code': "1"})


#更改邮箱
#code 1 :并没有订阅
#code 0 :修改成功
@app.route("/api/cdut/changeEmail",methods=["POST"])
def changeEmail():
  #参数校验
  form = Validation.ChangeEmailForm(request.form)
  if not form.validate():
    return jsonify({"msg": "Invalid Request"})

  email = request.form.get('email')
  username = request.form.get('user')

  # 查找用户是否存在
  check = userCollection.find_one({"user": username})
  if (check != None) :
    userCollection.update({"user": username},{"$set":{"email":email}})
    return jsonify({'code': "0"})
  else :
    return jsonify({'code': "1"})


#resp.headers['Access-Control-Allow-Origin'] = '*'

if __name__ == '__main__':
  app.run(port=3003)