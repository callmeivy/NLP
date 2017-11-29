#coding:UTF-8
'''
Created on 2016年3月27日
@author: Ivy

'''
import sys,os
import MySQLdb
import time
from collections import Counter
reload(sys)
sys.setdefaultencoding('utf8')
import datetime
import requests
import json
import base64
from requests_kerberos import HTTPKerberosAuth, OPTIONAL

def issuccessful(request):
    if 200 <= request.status_code and request.status_code <= 299:
        return True
    else:
        return False
def mentioned_trend(baseurl,mysqlhostIP, mysqlUserName = 'root', mysqlPassword = '', dbname = 'btv_v2'):
    # 连接数据库
    sqlConn=MySQLdb.connect(host=mysqlhostIP, user=mysqlUserName, passwd=mysqlPassword, db = dbname, charset='utf8')
    sqlcursor = sqlConn.cursor()
    sqlcursor.execute('''CREATE TABLE IF NOT EXISTS gala_brand_echo(pk bigint NOT NULL PRIMARY KEY AUTO_INCREMENT, sponsor varchar(20), echo double, date date, program_id varchar(50), program varchar(50)) DEFAULT CHARSET=utf8;''')
    print '新建库成功'
    # 存储评论数据

    os.popen('kinit -k -t ctvit.keytab ctvit')
    kerberos_auth = HTTPKerberosAuth(mutual_authentication=OPTIONAL)
    tablename = "DATA:WEIBO_POST_Keywords"
    r = requests.get(baseurl + "/" + tablename + "/*",  auth=kerberos_auth, headers = {"Accept" : "application/json"})
    if issuccessful(r) == False:
        print "Could not get messages from HBase. Text was:\n" + r.text
    bleats = json.loads(r.text)


    # 时间属性
    # inter = 17
    # inter = 2
    # 2016.6.23与2016.2.8相差136天
    # for inter in range(135,137):
    inter = 136
    date_mentioned_dict = dict()
    now = int(time.time())-86400*inter
    timeArray = time.localtime(now)
    otherStyleTime = time.strftime("%Y-%m-%d", timeArray)
    print otherStyleTime
    sqlcursor.execute("""SELECT mentioned from gala_mentioned_trend where date = %s """, (otherStyleTime,))
    bufferTemp = sqlcursor.fetchone()
    # “春晚”总共被提及的次数
    chunwan_times = bufferTemp[0]
    sqlcursor.execute('''SELECT DISTINCT(sponsor) from gala_sponsor''')
    bufferTemp = sqlcursor.fetchone()
    sponsor_name = bufferTemp[0].encode('utf8')
    # print 'sponsor_name',sponsor_name
    count = 0
    count_sposor = 0
    tempData = list()
    for row in bleats['Row']:
        message = ''
        lineNumber = ''
        username = ''
        flag = True
        flag_0 = True
        for cell in row['Cell']:
            columnname = base64.b64decode(cell['column'])
            value = cell['$']
            if value == None:
                print 'none'
                continue
            if columnname == "base_info:cdate":
                cdate = base64.b64decode(value)
                # print 'hh',cdate
                cdate = cdate.split('T')[0]
                # 日期筛选
                # print '222',cdate
                if cdate != otherStyleTime:
                    flag = False
                    flag_0 = False
                    break
            if columnname == "base_info:match":
                column = base64.b64decode(value)
                if ("北京卫视春晚"  not in column) and ("北京台的春晚" not in column) and ("BTV春晚" not in column) and ("BTV春晚" not in column) and ("bTV春晚" not in column):
                    flag = False
                    break
            if columnname == "base_info:text":
                content = base64.b64decode(value)
                # print 'ff',sponsor_name
                if sponsor_name not in content:
                    flag = False
                    flag_0 = False
                    break
        if flag:
                # print 'lal',sponsor_name
                # print 't',content
                # count代表“春晚”与“赞助商名字”共同被提及的次数
                count += 1
        if flag_0:
                count_sposor += 1
    date_mentioned_dict[otherStyleTime] = str(count)+","+str(count_sposor)
    both_mentioned_probability = 0
    for i,j in date_mentioned_dict.iteritems():
        print i,j
        # 赞助商及春晚同时被提及的次数
        times_both = j.split(',')[0]
        times_sponsor = j.split(',')[1]
        if chunwan_times != 0:
            if chunwan_times >times_sponsor:
                both_mentioned_probability = round(float(times_both)/float(times_sponsor)*100,3)
            else:
                both_mentioned_probability = round(float(times_both)/float(chunwan_times)*100,3)
        else:
            both_mentioned_probability = 0

        print "here", times_both, times_sponsor, chunwan_times,both_mentioned_probability
        # sponsor
        tempData.append(sponsor_name)
        # echo
        tempData.append(both_mentioned_probability)
        # date
        tempData.append(i)
        # program_id
        tempData.append('100')
        # program
        tempData.append('2016年北京卫视春节联欢晚会')
        sqlcursor.execute('''insert into gala_brand_echo(sponsor, echo, date, program_id, program) values (%s, %s, %s, %s, %s)''',tempData)
        sqlConn.commit()
        tempData = []


    sqlConn.close()


if __name__=='__main__':
    commentTest = mentioned_trend(baseurl = "http://172.28.12.34:8080", mysqlhostIP = '172.28.34.16', dbname = 'btv_v2')


