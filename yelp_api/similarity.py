import nltk
import pymysql

word_to_replace  = {}
word_to_replace["'s"]=""  
word_to_replace["and"]="&"



db_host = '127.0.0.1'
db_name = 'biafinal_db'
db_user = "root"
db_password = "123456"

def addNewResterant(id_yelp,id_allmenu):
    conn = pymysql.connect(host=db_host, port=3306, user=db_user, passwd=db_password, db=db_name)
    cur = conn.cursor()
    cur.execute("INSERT INTO id_map(`id_yelp`,`id_allmenu`)" \
            " VALUES (%s,%s)" \
            , (id_yelp,id_allmenu))
    cur.close()
    conn.commit()
    conn.close()


def distance(info1,info2):
    info1 = info1.replace("'s"," ").replace("and","&").replace(","," ").replace("\\s+"," ")
    info1 = info1.replace("(","").replace(") ","").replace("-","");
    info2 = info2.replace("'s"," ").replace("and","&").replace(","," ").replace("\\s+"," ")
    info2 = info2.replace("(","").replace(") ","").replace("-","");
    if info1 == info2 or info1 in info2 or info2 in info1:
        return 0
    else:
        return nltk.metrics.edit_distance(info1, info2)

def find_most_simi(info1,info2list):
    min_dist = 999999999
    best = "None"
    for info2 in info2list:
        dist1  = distance(info1[0], info2[0]) #name
        dist2 = distance(info1[1], info2[1])  #address
        #dist3 = distance(info1[2], info2[2])  #phone
        dist = min(dist1,dist2)
        #print info1, info,dist
        if dist < min_dist:
            best = info2
            min_dist = dist
    return [best,min_dist]
    

def similarity():
    conn_yelp = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='biafinal_db')
    cur_yelp = conn_yelp.cursor()
    cur_yelp.execute("SELECT name,location,phone,id FROM restaurant_yelp where location like '%Hoboken%'")
    infos_of_yelp = []
    for row in cur_yelp:
        infos_of_yelp.append(row)
    cur_yelp.close()
    conn_yelp.close()
        
    conn_allmenu = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='biafinal_db')
    cur_allmenu = conn_allmenu.cursor()
    cur_allmenu.execute("SELECT rest_name,address,telephone,rest_id as id FROM restaurant_info")
    infos_of_allmenu = []
    for row in cur_allmenu:
        infos_of_allmenu.append(row)
    cur_allmenu.close()
    conn_allmenu.close()

    result = []
    for info in infos_of_allmenu:
        simi  = find_most_simi(info,infos_of_yelp)
        if simi[1]<2:
            #print "======",simi[0][3],info[3],"--------";
            addNewResterant(simi[0][3],info[3])
            #print info,simi
            result.append(info)
    print len(result)
