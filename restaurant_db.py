#!/usr/bin/env python

import pymysql

def addNewResterant(na,ra,re,ph,lo):
    #conn = pymysql.connect(host='127.0.0.1', unix_socket='/tmp/mysql.sock', user='root', passwd=None, db='mysql')
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='test')
    cur = conn.cursor()
    #cur.execute("SELECT * FROM restaurant")
    #print(cur.description)
    #for row in cur:
    #   print(row)
    cur.execute("INSERT INTO restaurant(`name`,`rating`,`review_count`,`phone`,`location`)" \
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
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='test')
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

