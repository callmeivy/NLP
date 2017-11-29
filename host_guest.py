#coding:UTF-8
'''
Created on

@author:
主持嘉宾热度
'''
import sys,os
from sys import path
path.append('tools/')
path.append(path[0]+'/tools')
import MySQLdb
# 工具类
import jieba
from datetime import *
import time
import json
import base64
from requests_kerberos import HTTPKerberosAuth, OPTIONAL

reload(sys)
sys.setdefaultencoding('utf8')

def issuccessful(request):
    if 200 <= request.status_code and request.status_code <= 299:
        return True
    else:
        return False


def addhost_guest(baseurl,mysqlhostIP, fan_number_weight, weibo_number_weight, repost_number_weight, comment_number_weight, like_number_weight, mysqlUserName = 'root', mysqlPassword = '', dbname = 'btv'):

    # 连接数据库
    sqlConn=MySQLdb.connect(host=mysqlhostIP, user=mysqlUserName, passwd=mysqlPassword, db = dbname, charset='utf8')
    sqlcursor = sqlConn.cursor()

    sqlcursor.execute('''CREATE TABLE IF NOT EXISTS host_popularity(pk bigint NOT NULL PRIMARY KEY AUTO_INCREMENT, host varchar(20), date date, popularity bigint(20), rank bigint(20),
                    pic varchar(1000), created_date datetime, weibo varchar(200), description varchar(300)) DEFAULT CHARSET=utf8;''')
    sqlcursor.execute('''CREATE TABLE IF NOT EXISTS top_host_trend(pk bigint NOT NULL PRIMARY KEY AUTO_INCREMENT, host varchar(20), date date, popularity bigint(20), created_date datetime, program_id varchar(50)) DEFAULT CHARSET=utf8;''')
    print '新建库成功'
    program = '军情解码'
    sqlcursor.execute('''SELECT program_id from competition_analysis where program = %s''', (program,))
    bufferTemp = sqlcursor.fetchone()
    program_id = bufferTemp[0]
    # 时间属性
    # inter为0，即为当日
    inter = 0
    now = int(time.time())-86400*inter
    timeArray = time.localtime(now)
    otherStyleTime = time.strftime("%Y-%m-%d", timeArray)
    print otherStyleTime
    # 连接hbase数据库

    os.popen('kinit -k -t ctvit.keytab ctvit')
    kerberos_auth = HTTPKerberosAuth(mutual_authentication=OPTIONAL)
    # 表名
    tablename = "DATA:WEIBO_POST_Keywords"
    r = requests.get(baseurl + "/" + tablename + "/*",  auth=kerberos_auth, headers = {"Accept" : "application/json"})
    if issuccessful(r) == False:
        print "Could not get messages from HBase. Text was:\n" + r.text
    # quit()
    bleats = json.loads(r.text)

    # 存储评论数据
    commentsData = []
    tempData = []
    # 处理情感
    # table=conn.table('WEIBO_USER')
    # customerEvaluation_informal需要有program标识
    count = 0
    printCount = 0
    # row_prefix, limit可以限定次数
    # 加入userid判断机制？？？？
    # bleats is json file
    for row in bleats['Row']:
        for cell in row['Cell']:
            columnname = base64.b64decode(cell['column'])
            value = cell['$']
            if value == None:
                print 'none'
                continue
            if columnname == "'base_info:cdate'":
                cdate = base64.b64decode(value)
        # 日期
            if cdate == otherStyleTime:
                # 主持人
                if columnname == "'base_info:screen_name'":
                    host = base64.b64decode(value)
                # pic
                if columnname == "'base_info:pic'":
                    pic = base64.b64decode(value)
                # 插表的时间
                now = datetime.datetime.now()
                # 主持人基本介绍
                if columnname == "'base_info:description'":
                    profile = base64.b64decode(value)
                # 主持人微博？
                if columnname == "'base_info:domain'":
                    weibo = base64.b64decode(value)
                # 粉丝数
                if columnname == "'base_info:followers_count'":
                    fan_number = base64.b64decode(value)
                # 微博数
                if columnname == "'base_info:statuses_count'":
                    weibo_number = base64.b64decode(value)
                # 关注数
                if columnname == "'base_info:friends_count'":
                    repost_number = base64.b64decode(value)
                # 用户收藏数
                if columnname == "'base_info:facourites_count'":
                    comment_number = base64.b64decode(value)
                # 用户互粉数
                if columnname == "'base_info:bi_followers_count'":
                    like_number = base64.b64decode(value)
                # 暂时没有主持人微博的评论数、转发数、点赞数

                popularity = float(fan_number)/float(10000)*float(fan_number_weight) + float(weibo_number)/float(100)*float(weibo_number_weight)\
                + float(repost_number)/float(100000)*float(repost_number_weight) + float(comment_number)/float(10000)*float(comment_number_weight)\
                + float(like_number)/float(10000)*float(like_number_weight)
                print "Hallelujah",popularity
                count += 1
                printCount+=1
            # 处理每一条
            #
                tempData.append(host)
                tempData.append(otherStyleTime)
                # popularity
                tempData.append(popularity)
                # 插表的时间
                tempData.append(now)
                # program_id
                tempData.append(program_id)
            #     转换为元组
                commentsData.append(tuple(tempData))
                tempData = []
                sqlcursor.executemany('''insert into top_host_trend(host, date, popularity, created_date, program_id)
                            values (%s, %s, %s, %s, %s)''',commentsData)
                sqlcursor.execute('''UPDATE host_popularity set date = '%s' and popularity = '%s' where name = '%s';'''(otherStyleTime, popularity,host))
                sqlConn.commit()
                commentsData = []
    sqlConn.close()




if __name__=='__main__':
    commentTest = addhost_guest(baseurl = "http://172.28.12.34:8080", mysqlhostIP = '10.3.3.182', fan_number_weight = '0.3', weibo_number_weight = '0.05', repost_number_weight = '0.25', comment_number_weight = '0.3', like_number_weight = '0.1', dbname = 'btv')


