# !/usr/bin/python
# -*-coding:utf-8-*-
import smtplib;
from email.mime.text import MIMEText

# 常量部分 服务器 端口 发送方账户及口令
host = 'smtp.qq.com'
port = 465
username = '发件人邮箱'
passwd = '授权码'

def send_email(send_to, subject, content):

    msg = MIMEText(content.encode('utf8'), _subtype='html', _charset='utf8')
    msg['From'] = username
    msg['Subject'] = u'%s' % subject
    msg['To'] = ",".join(send_to)

    try:
        s = smtplib.SMTP_SSL(host, port)
        s.login(username, passwd)
        s.sendmail(username, send_to, msg.as_string())
        s.close()
        print("发送成功")
        return True

    except Exception as e:

        print('Exception: send email failed', e)
        return False
