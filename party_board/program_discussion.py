#coding:UTF-8
'''
Created on 2016年3月27日
@author: Ivy
晚会节目讨论量
'''
import sys,os
import MySQLdb
import time
from collections import Counter
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
    sqlcursor.execute('''CREATE TABLE IF NOT EXISTS gala_program_discussion(pk bigint NOT NULL PRIMARY KEY AUTO_INCREMENT, item varchar(50), disscussion bigint(50), specific_time datetime, program_id varchar(50), program varchar(50)) DEFAULT CHARSET=utf8;''')
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

    inter = 88
    date_mentioned_dict = dict()
    now = int(time.time())-86400*inter
    timeArray = time.localtime(now)
    otherStyleTime = time.strftime("%Y-%m-%d", timeArray)
    print 'otherStyleTime', otherStyleTime
    # 节目内容
    sqlcursor.execute('''SELECT item from gala_epg;''')
    bufferTemp = sqlcursor.fetchall()

    for one_item in bufferTemp:
        one_item = one_item[0]
        count = 0
        weibo_interaction = dict()
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
                if columnname == "base_info:match":
                    column = base64.b64decode(value)
                    if ("北京卫视春晚"  not in column) and ("北京台的春晚" not in column) and ("BTV春晚" not in column) and ("BTV春晚" not in column) and ("bTV春晚" not in column):
                        flag = False
                        break
                if columnname == "base_info:text":
                    content = base64.b64decode(value)
                    if one_item not in content:
                        flag = False
                        break
                if columnname == "base_info:cdate":
                    cdate = base64.b64decode(value)
                    cdate = cdate.split('T')[0]
                    if cdate != otherStyleTime:
                        flag = False
                        break
            if flag:
                count += 1
            # 互动量
        weibo_interaction[str(one_item)] = count
        weibo_interaction = sorted(weibo_interaction.iteritems(), key=lambda e:e[1], reverse=True)
        ind = 0
        tempData = list()
        for i in weibo_interaction:
            ind += 1
            # 这里取多少个，就写多少，比如取3个，就写>3
            if ind > 10:
                break
            item_name = i[0]
            interaction_value = i[1]
            print item_name,interaction_value
            # type
            # tempData.append('节目内容')
            # content
            tempData.append(item_name)
            # attention_degree
            tempData.append(interaction_value)
            # date
            tempData.append(otherStyleTime)
            # program_id
            tempData.append('100')
            # program
            tempData.append('2016年北京卫视春节联欢晚会')
            sqlcursor.execute('''insert into gala_program_discussion(item, disscussion, specific_time, program_id, program) values (%s, %s, %s, %s, %s)''',tempData)
            sqlConn.commit()
            tempData = []
    sqlConn.close()


if __name__=='__main__':
    commentTest = mentioned_trend(baseurl = "http://172.28.12.34:8080", mysqlhostIP = '172.28.34.16', dbname = 'btv_v2')


