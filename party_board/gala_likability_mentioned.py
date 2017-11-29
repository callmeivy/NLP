#coding:UTF-8
'''
Created on 2016年3月27日
@author: Ivy
各大晚会提及量及喜爱度
4月5日补充，
加上日期这一维度
'''
import sys,os
from sys import path
path.append('tools/')
path.append(path[0]+'/tools')
import MySQLdb
import time
from collections import Counter
from emtionProcess import emotionProcess
# 工具类
from remove import removeIrrelevant
reload(sys)
sys.setdefaultencoding('utf8')
import datetime
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
    sqlcursor.execute('''CREATE TABLE IF NOT EXISTS gala_likability_mentioned(pk bigint NOT NULL PRIMARY KEY AUTO_INCREMENT, channel varchar(20), mentioned bigint(50), likability bigint(50), date date, program_id varchar(50), program varchar(50)) DEFAULT CHARSET=utf8;''')
    print '新建库成功'

    # 连接hbase数据库
    os.popen('kinit -k -t ctvit.keytab ctvit')
    kerberos_auth = HTTPKerberosAuth(mutual_authentication=OPTIONAL)
    tablename = "DATA:WEIBO_POST_Keywords"
    r = requests.get(baseurl + "/" + tablename + "/*",  auth=kerberos_auth, headers = {"Accept" : "application/json"})
    if issuccessful(r) == False:
        print "Could not get messages from HBase. Text was:\n" + r.text
    # quit()
    bleats = json.loads(r.text)
    # 北京卫视 2.8
    # 时间属性
    # inter为0，即为当日
    # inter = 91
    # now = int(time.time())-86400*inter
    # timeArray = time.localtime(now)
    # otherStyleTime = time.strftime("%Y-%m-%d", timeArray)
    # print otherStyleTime
    #
    # # 存储评论数据
    # sqlcursor.execute('''SELECT mentioned from gala_mentioned_trend where date = %s and program = '2016年北京卫视春节联欢晚会';''',(otherStyleTime,))
    # bufferTemp = sqlcursor.fetchone()
    # chunwan_times = bufferTemp[0]
    # print chunwan_times
    # emProcess = emotionProcess()
    # rmIrr = removeIrrelevant()
    # tempData = []
    # sum_emotionsScore = 0
    # # bleats is json file
    # for row in bleats['Row']:
    #     flag = True
    #     for cell in row['Cell']:
    #         columnname = base64.b64decode(cell['column'])
    #         value = cell['$']
    #         if value == None:
    #             print 'none'
    #             continue
    #         if columnname == "base_info:match":
    #             column = base64.b64decode(value)
    #             if ("北京卫视春晚"  not in column) and ("北京台的春晚" not in column) and ("BTV春晚" not in column) and ("BTV春晚" not in column) and ("bTV春晚" not in column):
    #                 flag = False
    #                 break
    #         if columnname == "base_info:cdate":
    #             cdate = base64.b64decode(value)
    #             cdate = cdate.split('T')[0]
    #             if cdate != otherStyleTime:
    #                 flag = False
    #                 break
    #         if columnname == "base_info:text":
    #             content = base64.b64decode(value)
    #             # print 'q',content
    #     #     情感关键词
    #     if flag:
    #         (emotionsWord,emotionsScore) = emProcess.processSentence(rmIrr.removeEverythingButEmotion(content))
    #     #     倾向性判断flag:1是正面，0是中性，-1是负面
    #     #     情感极性判断，这里我限制了更严格的条件
    #         # channel
    #         # if emotionsScore > 0:
    #         sum_emotionsScore += emotionsScore
    # tempData.append('北京卫视')
    # # mentioned
    # tempData.append(chunwan_times)
    # # likability
    # tempData.append(sum_emotionsScore)
    # # date
    # tempData.append(otherStyleTime)
    # # program_id
    # tempData.append('100')
    # # program
    # tempData.append('2016年北京卫视春节联欢晚会')
    # sqlcursor.execute('''insert into gala_likability_mentioned(channel, mentioned, likability, date, program_id, program) values (%s, %s, %s, %s, %s, %s)''',tempData)
    # sqlConn.commit()
    # tempData = []

    # 湖南卫视 2.2
    # inter为0，即为当日
    inter_hn = 97
    now = int(time.time())-86400*inter_hn
    timeArray = time.localtime(now)
    otherStyleTime = time.strftime("%Y-%m-%d", timeArray)
    print 'bb', otherStyleTime

    # 存储评论数据
    sqlcursor.execute('''SELECT mentioned from gala_mentioned_trend where date = %s and program = '2016湖南卫视小年夜春晚';''',(otherStyleTime,))
    bufferTemp = sqlcursor.fetchone()
    chunwan_times = bufferTemp[0]
    print chunwan_times
    emProcess = emotionProcess()
    rmIrr = removeIrrelevant()
    tempData = []
    sum_emotionsScore = 0
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
                if ("湖南"  not in column) and ("芒果" not in column):
                    flag = False
                    break
            if columnname == "base_info:cdate":
                cdate = base64.b64decode(value)
                cdate = cdate.split('T')[0]
                if cdate != otherStyleTime:
                    flag = False
                    break
            if columnname == "base_info:text":
                content = base64.b64decode(value)
                # print 'q',content
        #     情感关键词
        if flag:
            (emotionsWord,emotionsScore) = emProcess.processSentence(rmIrr.removeEverythingButEmotion(content))
        #     倾向性判断flag:1是正面，0是中性，-1是负面
        #     情感极性判断，这里我限制了更严格的条件
            # channel
            # if emotionsScore > 0:
            sum_emotionsScore += emotionsScore
    tempData.append('湖南卫视')
    # mentioned
    tempData.append(chunwan_times)
    # likability
    tempData.append(sum_emotionsScore)
    # date
    tempData.append(otherStyleTime)
    # program_id
    tempData.append('100')
    # program
    tempData.append('2016湖南卫视小年夜春晚')
    sqlcursor.execute('''insert into gala_likability_mentioned(channel, mentioned, likability, date, program_id, program) values (%s, %s, %s, %s, %s, %s)''',tempData)
    sqlConn.commit()
    tempData = []


    # 辽宁卫视2.6
    # inter_ln = 93
    # now = int(time.time())-86400*inter_ln
    # timeArray = time.localtime(now)
    # otherStyleTime = time.strftime("%Y-%m-%d", timeArray)
    # print otherStyleTime
    #
    # # 存储评论数据
    # sqlcursor.execute('''SELECT mentioned from gala_mentioned_trend where date = %s and program = '2016年辽宁卫视春晚';''',(otherStyleTime,))
    # bufferTemp = sqlcursor.fetchone()
    # chunwan_times = bufferTemp[0]
    # print chunwan_times
    # emProcess = emotionProcess()
    # rmIrr = removeIrrelevant()
    # tempData = []
    # sum_emotionsScore = 0
    # # bleats is json file
    # for row in bleats['Row']:
    #     flag = True
    #     for cell in row['Cell']:
    #         columnname = base64.b64decode(cell['column'])
    #         value = cell['$']
    #         if value == None:
    #             print 'none'
    #             continue
    #         if columnname == "base_info:match":
    #             column = base64.b64decode(value)
    #             if ("辽宁"  not in column):
    #                 flag = False
    #                 break
    #         if columnname == "base_info:cdate":
    #             cdate = base64.b64decode(value)
    #             cdate = cdate.split('T')[0]
    #             if cdate != otherStyleTime:
    #                 flag = False
    #                 break
    #         if columnname == "base_info:text":
    #             content = base64.b64decode(value)
    #             # print 'q',content
    #     #     情感关键词
    #     if flag:
    #         (emotionsWord,emotionsScore) = emProcess.processSentence(rmIrr.removeEverythingButEmotion(content))
    #     #     倾向性判断flag:1是正面，0是中性，-1是负面
    #     #     情感极性判断，这里我限制了更严格的条件
    #         # channel
    #         # if emotionsScore > 0:
    #         sum_emotionsScore += emotionsScore
    # tempData.append('辽宁卫视')
    # # mentioned
    # tempData.append(chunwan_times)
    # # likability
    # tempData.append(sum_emotionsScore)
    # # date
    # tempData.append(otherStyleTime)
    # # program_id
    # tempData.append('100')
    # # program
    # tempData.append('2016年辽宁卫视春晚')
    # sqlcursor.execute('''insert into gala_likability_mentioned(channel, mentioned, likability, date, program_id, program) values (%s, %s, %s, %s, %s, %s)''',tempData)
    # sqlConn.commit()
    # tempData = []
    sqlConn.close()


if __name__=='__main__':
    commentTest = mentioned_trend(baseurl = "http://172.28.12.34:8080", mysqlhostIP = '172.28.34.16', dbname = 'btv_v2')


