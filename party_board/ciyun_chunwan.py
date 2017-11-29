#coding: UTF-8
'''
by Ivy
created on 2016年3月26日

'''
import sys
reload(sys)
import MySQLdb
import os
import time
from sys import path
sys.setdefaultencoding('utf8')
from collections import Counter
import datetime
import json
import base64
from requests_kerberos import HTTPKerberosAuth, OPTIONAL
import requests
import jieba


def issuccessful(request):
    if 200 <= request.status_code and request.status_code <= 299:
        return True
    else:
        return False


# number是限定词云个数
def addhighFreqencyWords(baseurl,mysqlhostIP, programid, number,mysqlUserName = 'root', mysqlPassword = '', dbname = 'btv_v2'):
    # 晚会名称
    program = '2016年北京卫视春节联欢晚会'
# 读停用词
    path = os.path.abspath(os.path.dirname(sys.argv[0]))
    dicFile = open(path+'/tools/NTUSD_simplified/stopwords.txt','r')
    stopwords = dicFile.readlines()
    stopwordList = []
    stopwordList.append(' ')
    for stopword in stopwords:
        temp = stopword.strip().replace('\r\n','').decode('utf8')
        stopwordList.append(temp)
    dicFile.close()

    # 连接数据库
    sqlConn=MySQLdb.connect(host=mysqlhostIP,user=mysqlUserName,passwd=mysqlPassword,db = dbname,charset='utf8')
    sqlcursor = sqlConn.cursor()
    sqlcursor.execute('''CREATE TABLE IF NOT EXISTS gala_ci_yun_chunwan(pk bigint NOT NULL PRIMARY KEY AUTO_INCREMENT, word varchar(50), freqency bigint(50), date Date,
                    program_id varchar(200), program varchar(200)) DEFAULT CHARSET=utf8;''')
    print '新建库成功'


    # 读取微博正文内容

    # 存储评论数据
    commentsData = []
    tempData = []
    # 
    os.popen('kinit -k -t ctvit.keytab ctvit')
    kerberos_auth = HTTPKerberosAuth(mutual_authentication=OPTIONAL)
    # 表名
    tablename = "DATA:WEIBO_POST_Keywords"
    r = requests.get(baseurl + "/" + tablename + "/*",  auth=kerberos_auth, headers = {"Accept" : "application/json"})
    if issuccessful(r) == False:
        print "Could not get messages from HBase. Text was:\n" + r.text
    bleats = json.loads(r.text)

    sqlcursor.execute("SELECT DISTINCT(program) from hbase_info;")
    bufferTemp = sqlcursor.fetchall()

    count = 0
    printCount = 0
    Corpus_cut = list()
    body_content_box = list()
    # 时间属性
    # inter为0，即为当日,与2016.4.18相差18天,与2016.2.8相差87天
    inter = 87
    now = int(time.time())-86400*inter
    timeArray = time.localtime(now)
    otherStyleTime = time.strftime("%Y-%m-%d", timeArray)
    print otherStyleTime

    Corpus_cut_box = list()

    # bleats is json file
    for row in bleats['Row']:
        flag = True
        for cell in row['Cell']:
            columnname = base64.b64decode(cell['column'])
            value = cell['$']
            if value == None:
                print 'none'
                continue
                # 如果以下这段不要，就是全部的内容，没有时间限制
            if columnname == "base_info:cdate":
                date_created = base64.b64decode(value)
                date_created = date_created.split('T')[0]
                # print 'hh',date_created
                if date_created != otherStyleTime:
                    flag = False
                    break
            if columnname == "base_info:match":
                column = base64.b64decode(value)
                if ("北京卫视春晚"  not in column) and ("北京台的春晚" not in column) and ("BTV春晚" not in column) and ("BTV春晚" not in column) and ("bTV春晚" not in column):
                    flag = False
                    break
            if columnname == "base_info:text":
                body_content = base64.b64decode(value)
        if flag:
            print "oo",body_content
            Corpus_cut_box.append(body_content)
            Corpus_cut = Corpus_cut + list(jieba.cut(body_content,cut_all = False))

    # 将空格以及停用词去除
    Corpus_cut_new = list()
    for i in Corpus_cut:
        if i !=' ':
            if i not in stopwordList:
                if len(i) > 1:
        #         print 111
                    Corpus_cut_new.append(i)
    Corpus_cut = Corpus_cut_new

    # 词频及排序
    kandian_listcount = dict(Counter(Corpus_cut))
    kandian_listcount = sorted(kandian_listcount.iteritems(), key=lambda e:e[1], reverse=True)
    ind = 0
    rank = 0
    for item in kandian_listcount:
        count += 1
        printCount+=1

        ind += 1
        if ind > int(number):
            break
        rank += 1
        try:
            word = item[0].strip().encode('utf-8')
            # print 'word',word
            how_many = item[1]
            # print 'how_many',how_many
        except:
            pass
        # 高频词
        tempData.append(str(word))
        # 词频
        tempData.append(int(how_many))
        # 数据指向的日期
        tempData.append(str(otherStyleTime))
        # 栏目id
        tempData.append('100')
        # 栏目名称
        tempData.append('2016年北京卫视春节联欢晚会')
        # commentsData.append(tuple(tempData))
        # tempData = []
        sqlcursor.execute('''insert into gala_ci_yun_chunwan(word, freqency, date, program_id, program) values (%s, %s, %s, %s, %s)''',tempData)
        sqlConn.commit()
        tempData = []
    sqlConn.close()



if __name__=='__main__':
    commentTest = addhighFreqencyWords(baseurl = "http://172.28.12.34:8080", mysqlhostIP = '172.28.34.16', programid = '100', number = '10')
    # number：展示多少个热词