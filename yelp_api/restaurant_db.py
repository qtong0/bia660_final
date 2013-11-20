#!/usr/bin/env python

import pymysql

db_host = '127.0.0.1'
db_name = 'biafinal_db'
db_user = "root"
db_password = "123456"

def addNewResterant(na,ra,re,ph,lo):
    #conn = pymysql.connect(host='127.0.0.1', unix_socket='/tmp/mysql.sock', user='root', passwd=None, db='mysql')
    conn = pymysql.connect(host=db_host, port=3306, user=db_user, passwd=db_password, db=db_name)
    cur = conn.cursor()
    #cur.execute("SELECT * FROM restaurant_yelp")
    #print(cur.description)
    #for row in cur:
    #   print(row)
    cur.execute("INSERT INTO restaurant_yelp(`name`,`rating`,`review_count`,`phone`,`location`)" \
            " VALUES (%s,%s,%s,%s,%s)" \
            , (na,ra,re,ph,lo))
    # print cur.description
    # r = cur.fetchall()
    # print r
    # ...or...
    #for r in cur:
    #       print r
    rid = conn.insert_id()
    cur.close()
    conn.commit()
    conn.close()
    return rid

def addNewComment(rid,comm):
    conn = pymysql.connect(host=db_host, port=3306, user=db_user, passwd=db_password, db=db_name)
    cur = conn.cursor()
    cur.execute("INSERT INTO comments(`id_restaurant`,`comment`)" \
            " VALUES (%s,%s)" \
            , (rid,comm))
    # print cur.description
    # r = cur.fetchall()
    # print r
    # ...or...
    #for r in cur:
    #       print r
    cur.close()
    conn.commit()
    conn.close()

