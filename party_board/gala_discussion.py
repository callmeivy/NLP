#coding:UTF-8
'''
Created on 2016年3月28日
@author: Ivy
晚会总讨论量
微博春晚讨论量分析
4月5日补充，
加上日期这一维度
'''
import sys,os
import MySQLdb
from collections import Counter
reload(sys)
sys.setdefaultencoding('utf8')
from sys import path
path.append('tools/')
path.append(path[0]+'/tools')
import datetime
import time
from emtionProcess import emotionProcess
# 工具类
from remove import removeIrrelevant
import json
import base64
from requests_kerberos import HTTPKerberosAuth, OPTIONAL
import requests

def issuccessful(request):
    if 200 <= request.status_code and request.status_code <= 299:
        return True
    else:
        return False


def mentioned_trend(baseurl,mysqlhostIP, mysqlUserName = 'root', mysqlPassword = '', dbname = 'btv_v2'):
    # 连接数据库
    sqlConn=MySQLdb.connect(host=mysqlhostIP, user=mysqlUserName, passwd=mysqlPassword, db = dbname, charset='utf8')
    sqlcursor = sqlConn.cursor()
    sqlcursor.execute('''CREATE TABLE IF NOT EXISTS gala_discussion(pk bigint NOT NULL PRIMARY KEY AUTO_INCREMENT, disscussion bigint(50), specific_time datetime, neutral double, positive double, program_id varchar(50), program varchar(50)) DEFAULT CHARSET=utf8;''')
    print '新建库成功'
    emProcess = emotionProcess()
    rmIrr = removeIrrelevant()

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


    tempData = []
    positive_count = 0
    neutral_count = 0
    total_count = 0
    # 时间属性
    # inter为0，即为当日
    inter = 88
    # for inter in range(88,89):
    now = int(time.time())-86400*inter
    timeArray = time.localtime(now)
    otherStyleTime = time.strftime("%Y-%m-%d", timeArray)
    print otherStyleTime

    # bleats is json file
    for row in bleats['Row']:
        flag = True
        for cell in row['Cell']:
            columnname = base64.b64decode(cell['column'])
            value = cell['$']
            if value == None:
                print 'none'
                continue
            if columnname == "base_info:match":
                column = base64.b64decode(value)
                if ("北京卫视春晚"  not in column) and ("北京台的春晚" not in column) and ("BTV春晚" not in column) and ("BTV春晚" not in column) and ("bTV春晚" not in column):
                    flag = False
                    break
            if columnname == "base_info:text":
                content = base64.b64decode(value)
            if columnname == "base_info:cdate":
                cdate = base64.b64decode(value)
                cdate = cdate.split('T')[0]
                if cdate != otherStyleTime:
                    flag = False
                    break
        if flag:
            total_count += 1
            (emotionsWord,emotionsScore) = emProcess.processSentence(rmIrr.removeEverythingButEmotion(content))
    #     倾向性判断flag:1是正面，0是中性，-1是负面
    #     情感极性判断，这里我限制了更严格的条件
            if emotionsScore>0:
                positive_count += 1
            elif emotionsScore==0:
                neutral_count += 1
    positive_count = round(float(positive_count)/float(total_count)*100,2)
    neutral_count = round(float(neutral_count)/float(total_count)*100,2)
    print
    # disscussion
    tempData.append(total_count)
    # specific_time???需要修改
    tempData.append(otherStyleTime)
    # neutral
    tempData.append(neutral_count)
    # positive
    tempData.append(positive_count)
    # program_id
    tempData.append('100')
    # program
    tempData.append('2016年北京卫视春节联欢晚会')
    sqlcursor.execute('''insert into gala_discussion(disscussion, specific_time, neutral, positive, program_id, program) values (%s, %s, %s, %s, %s, %s)''',tempData)
    sqlConn.commit()
    tempData = []
    sqlConn.close()


if __name__=='__main__':
    commentTest = mentioned_trend(baseurl = "http://172.28.12.34:8080", mysqlhostIP = '172.28.34.16', dbname = 'btv_v2')


