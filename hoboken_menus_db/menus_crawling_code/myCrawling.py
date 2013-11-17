# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import BeautifulSoup as bs4
import urllib

import pymysql
import re

import time

# <codecell>

dbuser = 'bia_user'
dbpsw = 'biabiabia'
dbname = 'biafinal_db'
tbl_name = 'restaurant_info'

# <codecell>

def isFloat(str_num):
    try:
        float(str_num)
        return True
    except ValueError:
        return False

# <codecell>

url_str = "http://www.allmenus.com/nj/hoboken/-/?sort=popular"
#################################
#url_str = "/users/michaelt/downloads/first.html"
#################################
f = urllib.urlopen(url_str)

sss_html = f.read()
sssoup = bs4.BeautifulSoup(sss_html)

list_restaurants = []

arr_p = sssoup.findAll('p')
for elem in arr_p:
    if(elem.get('class') == u'restaurant_name'):
        dic_restinfo = {'name': None, 'url': None, 'address': None, 'tel': None, 
                'ratingValue': None, 'reviewCount': None}
        tmp_str = elem.getText()
        tmp_str = tmp_str.replace('&amp;', '&')
        rest_name = tmp_str
        dic_restinfo['name'] = rest_name
        print rest_name
        
        rest_url = elem.findAll('a')[0]['href']
        rest_url = 'http://www.allmenus.com'+rest_url
        dic_restinfo['url'] = rest_url
        #################################
        #rest_url = '/users/michaelt/downloads/satay.html'
        #################################
        print rest_url
        
        f_rest = urllib.urlopen(rest_url)
        rest_html = f_rest.read()
        rest_soup = bs4.BeautifulSoup(rest_html)
        arr_div = rest_soup.findAll('div')
        for elem2 in arr_div:
            if elem2.get('id') == 'restaurant':
                arr_primary = elem2.findAll('div')
                for elem3 in arr_primary:
                    if elem3.get('id') == 'review_teaser':
                        span_ratingicon = elem3.find('span', {'id': 'overall_rating'})
                        ratingValue = span_ratingicon.find('meta', 
                                                           {'itemprop': 'ratingValue'}).get('content')
                        reviewCount = span_ratingicon.find('meta', 
                                                           {'itemprop': 'reviewCount'}).get('content')
                        dic_restinfo['ratingValue'] = ratingValue
                        dic_restinfo['reviewCount'] = reviewCount
                        print ratingValue
                        print reviewCount
                        print '\n'
                    if(elem3.get('id') == 'primary_info'):
                        arr_span_address = elem3.findAll('span')
                        for elem4 in arr_span_address:
                            if elem4.get('id') == 'address':
                                address = elem4.getText(separator = ' ')
                                address = address.replace(' ,', ',').strip()
                                dic_restinfo['address'] = address
                                print address
                            if elem4.get('id') == 'phone_number':
                                phone_num = elem4.getText()
                                dic_restinfo['tel'] = phone_num
                                print phone_num
                        list_restaurants.append(dic_restinfo)
                        time.sleep(3)

# <codecell>

def getMenusInfo(str_url, str_url_tosearch):
    conn = pymysql.connect(host = '127.0.0.1', port = 3306, user = dbuser,
                       passwd = dbpsw, db = dbname)
    cur = conn.cursor()
    
    f = urllib.urlopen(str_url)
    sss_html = f.read()
    sssoup = bs4.BeautifulSoup(sss_html)
    menu_soup = sssoup.find('div', {'id': 'menu'})
    if menu_soup == None:
        str_sql = ('DELETE IGNORE FROM RESTAURANT_INFO WHERE REST_URL = \''
                   ''+re.escape(str_url_tosearch)+'\';')
        print '\"' + str_url_tosearch + '\" has been deleted from DB.'
        cur.execute(str_sql)
        cur.fetchall()
        cur.connection.commit()
        return
    arr_category_soup = menu_soup.findAll('div', {'class': 'category'})
    for elem in arr_category_soup:
        category_name = elem.find('div', {'class': 'category_head'}).find('h3').getText()
        category_name = category_name.replace('&amp;', '&')
        
        str_sql = ('SELECT REST_ID FROM RESTAURANT_INFO WHERE REST_URL = \''
                   ''+re.escape(str_url_tosearch)+'\';')
        cur.execute(str_sql)
        restaurant_id = None
        for row in cur:
            restaurant_id = row[0]
        cur.fetchall()
        cur.connection.commit()
        str_sql = 'INSERT IGNORE INTO CATEGORY(CATE_NAME) VALUES(\''+re.escape(category_name)+'\');'
        cur.execute(str_sql)
        cur.fetchall()
        cur.connection.commit()
        str_sql = ('SELECT CATE_ID FROM CATEGORY WHERE CATE_NAME = '
                   '\''+re.escape(category_name)+'\';')
        cur.execute(str_sql)
        cate_id = None
        for row in cur:
            cate_id = row[0]
        if cate_id == None:
            print '\"'+category_name+'\" fail to uploaded to Database.'
            continue
        cur.fetchall()
        cur.connection.commit()
        str_sql = ('INSERT IGNORE INTO REST_CATEGORY VALUES'
                   '(\''+str(restaurant_id)+'\', \''+str(cate_id)+'\');')
        cur.execute(str_sql)
        cur.fetchall()
        cur.connection.commit()
        arr_dish_soup = elem.findAll('li')
        for elem1 in arr_dish_soup:
            dish_name = elem1.find('span', {'class': 'name'})
            dish_price = elem1.find('span', {'class': 'price'})
            if dish_name != None and dish_price != None:
                dish_name = dish_name.getText()
                dish_price = dish_price.getText().replace('$', '')
                dish_price = dish_price.strip()
                if isFloat(dish_price) == True:
                    str_sql = ('INSERT IGNORE INTO DISH(DISH_NAME, DISH_PRICE, CATE_ID) VALUE(\''
                               ''+re.escape(dish_name)+'\', '+dish_price+''
                               ', '+str(cate_id)+');')
                    cur.execute(str_sql)
    cur.fetchall()
    cur.connection.commit()
    cur.close()
    conn.close()

# <codecell>

conn = pymysql.connect(host = '127.0.0.1', port = 3306, user = dbuser,
                       passwd = dbpsw, db = dbname)
cur = conn.cursor()
for elem in list_restaurants:
    if elem['address'] == None and elem['tel'] == None:
        continue
    str_sql = ('INSERT IGNORE INTO '+ tbl_name + '(rest_name, rest_url, address, telephone,'
               ' rating, review_count) VALUES(\''+re.escape(elem['name'])+'\''
               ',\''+re.escape(elem['url'])+'\',\''+re.escape(elem['address'])+'\','
               ' \''+re.escape(elem['tel'])+'\','
               ' '+str(elem['ratingValue'])+','+str(elem['reviewCount'])+');')
    cur.execute(str_sql)
cur.fetchall()
cur.connection.commit()
cur.close()
conn.close()

# <codecell>

list_restaurants = [{'reviewCount': u'246', 'tel': u'(201) 222-8388', 'name': u'Robongi', 'url': u'http://www.allmenus.com/nj/hoboken/12998-robongi/menu/', 'ratingValue': u'3.5', 'address': u'520 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'203', 'tel': u'(201) 386-8688', 'name': u'Satay', 'url': u'http://www.allmenus.com/nj/hoboken/22705-satay/menu/', 'ratingValue': u'3.5', 'address': u'99 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'74', 'tel': u'(201) 216-1888', 'name': u"It's Greek To Me", 'url': u'http://www.allmenus.com/nj/hoboken/12961-its-greek-to-me/menu/', 'ratingValue': u'3.5', 'address': u'538 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'97', 'tel': u'(201) 216-1766', 'name': u'Havana Cafe & Lounge', 'url': u'http://www.allmenus.com/nj/hoboken/306306-havana-cafe--lounge/menu/', 'ratingValue': u'3', 'address': u'32 Newark St, Hoboken  NJ  07030'}, {'reviewCount': u'52', 'tel': u'(201) 386-3200', 'name': u'Mr Wraps', 'url': u'http://www.allmenus.com/nj/hoboken/273651-mr-wraps/menu/', 'ratingValue': u'3.5', 'address': u'741 Garden St, Hoboken  NJ  07030'}, {'reviewCount': u'114', 'tel': u'(201) 798-8827', 'name': u'Precious Chinese Cuisine', 'url': u'http://www.allmenus.com/nj/hoboken/12978-precious-japanese--chinese/menu/', 'ratingValue': u'3.5', 'address': u'128 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'52', 'tel': u'(201) 762-2568', 'name': u"H&S Giovanni's", 'url': u'http://www.allmenus.com/nj/hoboken/12986-hs-giovannis/menu/', 'ratingValue': u'3.5', 'address': u'603 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'23', 'tel': u'(201) 610-9955', 'name': u'Uptown Pizzeria', 'url': u'http://www.allmenus.com/nj/hoboken/55421-uptown-pizzeria/menu/', 'ratingValue': u'3', 'address': u'54 14th St, Hoboken  NJ  07030'}, {'reviewCount': u'43', 'tel': u'(201) 656-2161', 'name': u'Biggies Clam Bar', 'url': u'http://www.allmenus.com/nj/hoboken/241654-biggies-clam-bar/menu/', 'ratingValue': u'4', 'address': u'318 Madison St, Hoboken  NJ  07030'}, {'reviewCount': u'20', 'tel': u'(201) 418-8717', 'name': u"Rosario's at Willow", 'url': u'http://www.allmenus.com/nj/hoboken/17083-rosarios-at-willow/menu/', 'ratingValue': u'3', 'address': u'1132 Willow Ave, Hoboken  NJ  07030'}, {'reviewCount': u'93', 'tel': u'(201) 216-0900', 'name': u"Napoli's", 'url': u'http://www.allmenus.com/nj/hoboken/243834-napolis/menu/', 'ratingValue': u'3.5', 'address': u'1118 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'14', 'tel': u'(201) 963-1767', 'name': u'No. 1 Hoboken', 'url': u'http://www.allmenus.com/nj/hoboken/12982-no-1-fine-chinese/menu/', 'ratingValue': u'2.5', 'address': u'642 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'29', 'tel': u'(201) 798-6078', 'name': u'Off the Wall', 'url': u'http://www.allmenus.com/nj/hoboken/12993-off-the-wall/menu/', 'ratingValue': u'3', 'address': u'512 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'111', 'tel': u'(201) 653-2358', 'name': u'10th & Willow', 'url': u'http://www.allmenus.com/nj/hoboken/55428-10th--willow/menu/', 'ratingValue': u'3.5', 'address': u'935 Willow Ave, Hoboken  NJ  07030'}, {'reviewCount': u'67', 'tel': u'(201) 876-5887', 'name': u'Aroma', 'url': u'http://www.allmenus.com/nj/hoboken/12988-aroma/menu/', 'ratingValue': u'2.5', 'address': u'318 Washington St, Hoboken  NJ  07030'}, {'reviewCount': None, 'tel': u'(201) 762-2567', 'name': u'Stacks Pancake House', 'url': u'http://www.allmenus.com/nj/hoboken/290572-stacks-pancake-house/menu/', 'raingValue': 0, 'ratingValue': None, 'address': u'506 Washington St, Hoboken  NJ  07030', 'reveiwCount': 0}, {'reviewCount': u'83', 'tel': u'(201) 222-8148', 'name': u'Ayame Hibachi & Sushi', 'url': u'http://www.allmenus.com/nj/hoboken/296884-ayame-hibachi--sushi/menu/', 'ratingValue': u'3.5', 'address': u'526 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'278', 'tel': u'(201) 792-4132', 'name': u"Benny Tudino's", 'url': u'http://www.allmenus.com/nj/hoboken/16334-benny-tudinos/menu/', 'ratingValue': u'4', 'address': u'622 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'85', 'tel': u'(201) 942-2888', 'name': u'Sri Thai', 'url': u'http://www.allmenus.com/nj/hoboken/12990-sri-thai/menu/', 'ratingValue': u'3', 'address': u'234 Bloomfield St, Hoboken  NJ  07030'}, {'reviewCount': u'10', 'tel': u'(201) 653-5567', 'name': u'Flamboyan Restaurant', 'url': u'http://www.allmenus.com/nj/hoboken/55426-flamboyan-restaurant/menu/', 'ratingValue': u'3.5', 'address': u'1000 Willow Ave, Hoboken  NJ  07030'}, {'reviewCount': u'12', 'tel': u'(201) 963-3112', 'name': u'Green Garden Chinese', 'url': u'http://www.allmenus.com/nj/hoboken/241672-green-garden-chinese/menu/', 'ratingValue': u'2.5', 'address': u'1202 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'48', 'tel': u'(201) 268-7918', 'name': u'Re-juice A Nation', 'url': u'http://www.allmenus.com/nj/hoboken/55455-re-juice-a-nation/menu/', 'ratingValue': u'3.5', 'address': u'64 Newark St, Hoboken  NJ  07030'}, {'reviewCount': u'54', 'tel': u'(201) 762-2563', 'name': u'Ali Baba', 'url': u'http://www.allmenus.com/nj/hoboken/23104-ali-ba-ba/menu/', 'ratingValue': u'3.5', 'address': u'912 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'23', 'tel': u'(201) 683-8554', 'name': u'Healthy For Life', 'url': u'http://www.allmenus.com/nj/hoboken/299639-healthy-for-life/menu/', 'ratingValue': u'4', 'address': u'150 14th St., Hoboken  NJ  07030'}, {'reviewCount': u'164', 'tel': u'(201) 418-8833', 'name': u'Illuzion', 'url': u'http://www.allmenus.com/nj/hoboken/22701-illuzion/menu/', 'ratingValue': u'3.5', 'address': u'337 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'23', 'tel': u'(201) 659-0808', 'name': u'Marios Classic Pizza Cafe', 'url': u'http://www.allmenus.com/nj/hoboken/55434-marios-classic-pizza-cafe/menu/', 'ratingValue': u'3', 'address': u'742 Garden St, Hoboken  NJ  07030'}, {'reviewCount': u'36', 'tel': u'(201) 222-2660', 'name': u'Backyard Bistro', 'url': u'http://www.allmenus.com/nj/hoboken/280170-backyard-bistro/menu/', 'ratingValue': u'3', 'address': u'732 Jefferson St, Hoboken  NJ  07030'}, {'reviewCount': u'107', 'tel': u'(201) 942-2301', 'name': u"Vito's Delicatessen", 'url': u'http://www.allmenus.com/nj/hoboken/271931-vitos-delicatessen/menu/', 'ratingValue': u'4.5', 'address': u'806 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'61', 'tel': u'(201) 762-2569', 'name': u'Bangkok City Thai Restaurant', 'url': u'http://www.allmenus.com/nj/hoboken/197894-bangkok-city-thai-restaurant/menu/', 'ratingValue': u'3', 'address': u'335 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'67', 'tel': u'(201) 499-1052', 'name': u'Sushi House', 'url': u'http://www.allmenus.com/nj/hoboken/12991-sushi-house/menu/', 'ratingValue': u'3', 'address': u'155 1st St, Hoboken  NJ  07030'}, {'reviewCount': u'194', 'tel': u'(201) 499-0661', 'name': u"Mamoun's Falafel Restaurant", 'url': u'http://www.allmenus.com/nj/hoboken/296669-mamouns-falafel-restaurant/menu/', 'ratingValue': u'4', 'address': u'502 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'66', 'tel': u'(201) 942-2568', 'name': u'Pizza Republic', 'url': u'http://www.allmenus.com/nj/hoboken/14953-pizza-republic/menu/', 'ratingValue': u'3', 'address': u'406 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'46', 'tel': u'(201) 499-0639', 'name': u'Bagels On The Hudson', 'url': u'http://www.allmenus.com/nj/hoboken/55419-bagels-on-the-hudson/menu/', 'ratingValue': u'2.5', 'address': u'802 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'52', 'tel': u'(201) 762-2564', 'name': u'Casual Thai', 'url': u'http://www.allmenus.com/nj/hoboken/22700-casual-thai/menu/', 'ratingValue': u'2.5', 'address': u'1006 Washington St, Hoboken  NJ  07030'}, {'reviewCount': None, 'tel': u'(201) 222-5500', 'name': u"Leo's Grandevous", 'url': u'http://www.allmenus.com/nj/hoboken/19634-leos-grandevous/menu/', 'raingValue': 0, 'ratingValue': None, 'address': u'200 Grand St, Hoboken  NJ  07030', 'reveiwCount': 0}, {'reviewCount': u'66', 'tel': u'(201) 793-2517', 'name': u"Lisa's Italian Deli", 'url': u'http://www.allmenus.com/nj/hoboken/19650-lisas-italian-deli/menu/', 'ratingValue': u'3.5', 'address': u'901 Park Ave, Hoboken  NJ  07030'}, {'reviewCount': None, 'tel': u'(201) 942-6975', 'name': u'Rice Shop', 'url': u'http://www.allmenus.com/nj/hoboken/12984-rice-shop/menu/', 'raingValue': 0, 'ratingValue': None, 'address': u'304 Washington St, Hoboken  NJ  07030', 'reveiwCount': 0}, {'reviewCount': u'121', 'tel': u'(201) 403-9784', 'name': u"Luca Brasi's", 'url': u'http://www.allmenus.com/nj/hoboken/52216-luca-brasis/menu/', 'ratingValue': u'4', 'address': u'100 Park Ave, Hoboken  NJ  07030'}, {'reviewCount': u'1', 'tel': u'(201) 792-0800', 'name': u"Grimaldi's", 'url': u'http://www.allmenus.com/nj/hoboken/52214-grimaldis/menu/', 'ratingValue': u'5', 'address': u'133 Clinton St, Hoboken  NJ  07030'}, {'reviewCount': u'21', 'tel': u'(201) 653-3700', 'name': u"Domino's Pizza", 'url': u'http://www.allmenus.com/nj/hoboken/82397-dominos-pizza/menu/', 'ratingValue': u'3', 'address': u'462 Newark St, Hoboken  NJ  07030'}, {'reviewCount': u'80', 'tel': u'(201) 268-7916', 'name': u"Imposto's Pizza & Deli Restaurant", 'url': u'http://www.allmenus.com/nj/hoboken/12973-impostos-restaurant--deli/menu/', 'ratingValue': u'2.5', 'address': u'102 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'66', 'tel': u'(201) 499-3069', 'name': u'Pita Grill', 'url': u'http://www.allmenus.com/nj/hoboken/42003-pita-grill/menu/', 'ratingValue': u'3', 'address': u'324 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'362', 'tel': u'(201) 659-8197', 'name': u'La Isla Restaurant', 'url': u'http://www.allmenus.com/nj/hoboken/12965-la-isla-restaurant/menu/', 'ratingValue': u'4', 'address': u'104 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'19', 'tel': u'(201) 403-9805', 'name': u'Fresh Tortillas Grill', 'url': u'http://www.allmenus.com/nj/hoboken/12995-fresh-tortillas-grill/menu/', 'ratingValue': u'2.5', 'address': u'514 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'43', 'tel': u'(201) 653-0011', 'name': u'Bombay West', 'url': u'http://www.allmenus.com/nj/hoboken/12966-bombay-west/menu/', 'ratingValue': u'4', 'address': u'832 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'71', 'tel': u'(201) 268-7117', 'name': u'The Chicken Factory', 'url': u'http://www.allmenus.com/nj/hoboken/293264-the-chicken-factory/menu/', 'ratingValue': u'3.5', 'address': u'529 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'51', 'tel': u'(201) 762-2557', 'name': u'Johnny Rockets', 'url': u'http://www.allmenus.com/nj/hoboken/305696-johnny-rockets-hoboken/menu/', 'ratingValue': u'3', 'address': u'134 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'22', 'tel': u'(201) 798-8873', 'name': u'Torna Pizzeria', 'url': u'http://www.allmenus.com/nj/hoboken/55430-torna-pizzeria/menu/', 'ratingValue': u'3', 'address': u'252 9th St, Hoboken  NJ  07030'}, {'reviewCount': u'174', 'tel': u'(201) 630-6443', 'name': u'Sushi Lounge', 'url': u'http://www.allmenus.com/nj/hoboken/22706-sushi-lounge/menu/', 'ratingValue': u'3.5', 'address': u'200 Hudson St, Hoboken  NJ  07030'}, {'reviewCount': u'60', 'tel': u'(201) 683-9307', 'name': u'Cluck U Chicken', 'url': u'http://www.allmenus.com/nj/hoboken/280954-cluck-u-chicken/menu/', 'ratingValue': u'2.5', 'address': u'112 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'5', 'tel': u'(201) 222-9991', 'name': u'Las Olas Sushi Bar and Grill', 'url': u'http://www.allmenus.com/nj/hoboken/308865-las-olas-sushi-bar-and-grill/menu/', 'ratingValue': u'3', 'address': u'1319 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'6', 'tel': u'(201) 706-8680', 'name': u'Chicken Galore', 'url': u'http://www.allmenus.com/nj/hoboken/303512-chicken-galore/menu/', 'ratingValue': u'2', 'address': u'363 15th St, Hoboken  NJ  07030'}, {'reviewCount': u'32', 'tel': u'(201) 798-6788', 'name': u'Hoboken Cottage', 'url': u'http://www.allmenus.com/nj/hoboken/13005-hoboken-cottage/menu/', 'ratingValue': u'3', 'address': u'516 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'71', 'tel': u'(201) 420-7197', 'name': u'Yeung II Sushi and Asian Cuisine', 'url': u'http://www.allmenus.com/nj/hoboken/305707-yeung-ii-sushi-and-asian-cuisine/menu/', 'ratingValue': u'3.5', 'address': u'1120 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'34', 'tel': u'(201) 653-0564', 'name': u"Piccolo's Clam Bar", 'url': u'http://www.allmenus.com/nj/hoboken/55437-piccolos/menu/', 'ratingValue': u'4', 'address': u'92 Clinton St, Hoboken  NJ  07030'}, {'reviewCount': u'16', 'tel': u'(201) 499-5175', 'name': u'Istana Sushi & Wok', 'url': u'http://www.allmenus.com/nj/hoboken/12967-istana-japanese-cuisine/menu/', 'ratingValue': u'3', 'address': u'936 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'21', 'tel': u'(201) 792-7457', 'name': u"Delfino's Italian Pizzeria & Restaurant", 'url': u'http://www.allmenus.com/nj/hoboken/303777-delfinos-italian-pizzeria--restaurant/menu/', 'ratingValue': u'3', 'address': u'500 Jefferson St, Hoboken  NJ  07030'}, {'reviewCount': None, 'tel': u'(201) 863-1437', 'name': u'Turning Point', 'url': u'http://www.allmenus.com/nj/hoboken/258908-turning-point/menu/', 'raingValue': 0, 'ratingValue': None, 'address': u'1440 Frank Sinatra Drive N, Hoboken  NJ  07030', 'reveiwCount': 0}, {'reviewCount': u'201', 'tel': u'(201) 762-2561', 'name': u'Karma Kafe', 'url': u'http://www.allmenus.com/nj/hoboken/12972-karma-kafe/menu/', 'ratingValue': u'4', 'address': u'505 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'77', 'tel': u'(201) 354-1135', 'name': u'Baja Mexican Cuisine', 'url': u'http://www.allmenus.com/nj/hoboken/19638-baja-hoboken/menu/', 'ratingValue': u'3', 'address': u'104 14th St, Hoboken  NJ  07030'}, {'reviewCount': u'73', 'tel': u'(201) 710-5333', 'name': u'Piri Piri Portuguese Barbeque', 'url': u'http://www.allmenus.com/nj/hoboken/285237-piri-piri-portuguese-barbeque/menu/', 'ratingValue': u'3', 'address': u'515 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'74', 'tel': u'(212) 979-2337', 'name': u'The Village Pourhouse', 'url': u'http://www.allmenus.com/nj/hoboken/293604-the-village-pourhouse/menu/', 'ratingValue': u'3', 'address': u'205 1st St, Hoboken  NJ  07030'}, {'reviewCount': None, 'tel': u'(201) 792-0999', 'name': u'Cafe Ganache', 'url': u'http://www.allmenus.com/nj/hoboken/280173-cafe-ganache/menu/', 'raingValue': 0, 'ratingValue': None, 'address': u'1500 Hudson St, Hoboken  NJ  07030', 'reveiwCount': 0}, {'reviewCount': None, 'tel': u'(201) 942-6318', 'name': u"D's Soul Full Cafe", 'url': u'http://www.allmenus.com/nj/hoboken/23106-josh--ives-toasted-subs--wraps/menu/', 'raingValue': 0, 'ratingValue': None, 'address': u'918 Willow Ave, Hoboken  NJ  07030', 'reveiwCount': 0}, {'reviewCount': u'38', 'tel': u'(201) 403-9795', 'name': u'7 Stars Pizzeria', 'url': u'http://www.allmenus.com/nj/hoboken/247614-7-stars-pizzeria/menu/', 'ratingValue': u'2', 'address': u'342 Garden St, Hoboken  NJ  07030'}, {'reviewCount': u'75', 'tel': u'(201) 499-0136', 'name': u'Biggies', 'url': u'http://www.allmenus.com/nj/hoboken/313991-biggies/menu/', 'ratingValue': u'3.5', 'address': u'42 Newark Street, Hoboken  NJ  07030'}, {'reviewCount': u'2', 'tel': u'(201) 714-9446', 'name': u"Old Lorenzo's Pizza", 'url': u'http://www.allmenus.com/nj/hoboken/12968-old-lorenzos-pizza/menu/', 'ratingValue': u'3.5', 'address': u'301 Jackson Street, Hoboken  NJ  07030'}, {'reviewCount': u'113', 'tel': u'(201) 630-6450', 'name': u"Margherita's Cafe", 'url': u'http://www.allmenus.com/nj/hoboken/14551-margheritas-cafe/menu/', 'ratingValue': u'3.5', 'address': u'740 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'62', 'tel': u'(201) 604-0120', 'name': u'Bagel Smashery', 'url': u'http://www.allmenus.com/nj/hoboken/55458-bagel-smashery/menu/', 'ratingValue': u'2.5', 'address': u'153 1st St, Hoboken  NJ  07030'}, {'reviewCount': u'22', 'tel': u'(201) 367-1366', 'name': u'Cold Stone Creamery', 'url': u'http://www.allmenus.com/nj/hoboken/36099-cold-stone-creamery/menu/', 'ratingValue': u'3', 'address': u'116 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'17', 'tel': u'(201) 403-9777', 'name': u"Ben & Jerry's", 'url': u'http://www.allmenus.com/nj/hoboken/217292-ben--jerrys/menu/', 'ratingValue': u'3.5', 'address': u'405 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'31', 'tel': u'(201) 683-9600', 'name': u'Rome Pizza', 'url': u'http://www.allmenus.com/nj/hoboken/282676-rome-pizza/menu/', 'ratingValue': u'2.5', 'address': u'20 Hudson Place, Hoboken  NJ  07030'}, {'reviewCount': u'55', 'tel': u'(201) 793-2527', 'name': u"Fran's Italian Deli", 'url': u'http://www.allmenus.com/nj/hoboken/284305-frans-italian-deli/menu/', 'ratingValue': u'4.5', 'address': u'202 Hudson St, Hoboken  NJ  07030'}, {'reviewCount': u'151', 'tel': u'(201) 942-2310', 'name': u'Madison Bar & Grill', 'url': u'http://www.allmenus.com/nj/hoboken/13004-madison-bar--grill/menu/', 'ratingValue': u'3.5', 'address': u'1316 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'29', 'tel': u'(201) 963-3236', 'name': u'Molfetta Pizzeria', 'url': u'http://www.allmenus.com/nj/hoboken/13001-molfetta-pizzeria/menu/', 'ratingValue': u'1.5', 'address': u'1122 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'16', 'tel': u'(201) 351-7991', 'name': u'Rosticeria da Gigi', 'url': u'http://www.allmenus.com/nj/hoboken/345803-rosticeria-da-gigi/menu/', 'ratingValue': u'4.5', 'address': u'916 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'24', 'tel': u'(201) 630-6067', 'name': u'Fresh U', 'url': u'http://www.allmenus.com/nj/hoboken/320449-fresh-u/menu/', 'ratingValue': u'2.5', 'address': u'70 Hudson St, Hoboken  NJ  07030'}, {'reviewCount': u'35', 'tel': u'(201) 793-2522', 'name': u'Piccolo Roma Ristorante', 'url': u'http://www.allmenus.com/nj/hoboken/247970-piccolo-roma-ristorante-/menu/', 'ratingValue': u'2', 'address': u'120 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'66', 'tel': u'(201) 659-3333', 'name': u"Filippo's on First", 'url': u'http://www.allmenus.com/nj/hoboken/14775-filippos-on-first/menu/', 'ratingValue': u'4', 'address': u'267 1st St, Hoboken  NJ  07030'}, {'reviewCount': None, 'tel': u'(201) 268-7195', 'name': u'Hoboken Burrito', 'url': u'http://www.allmenus.com/nj/hoboken/297417-hoboken-burrito/menu/', 'raingValue': 0, 'ratingValue': None, 'address': u'209 4th St, Hoboken  NJ  07030', 'reveiwCount': 0}, {'reviewCount': u'45', 'tel': u'(201) 798-3311', 'name': u'Maru Sushi', 'url': u'http://www.allmenus.com/nj/hoboken/12979-maru-sushi/menu/', 'ratingValue': u'3.5', 'address': u'219 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'60', 'tel': u'(201) 610-9220', 'name': u'The Little Grocery', 'url': u'http://www.allmenus.com/nj/hoboken/280175-the-little-grocery/menu/', 'ratingValue': u'4', 'address': u'214 Jefferson St, Hoboken  NJ  07030'}, {'reviewCount': u'22', 'tel': u'(201) 792-7373', 'name': u'Crepe Grill', 'url': u'http://www.allmenus.com/nj/hoboken/280008-crepe-grill/menu/', 'ratingValue': u'3.5', 'address': u'525 Sinatra Dr, Hoboken  NJ  07030'}, {'reviewCount': u'37', 'tel': u'(201) 963-5522', 'name': u'JP Bagel Express Cafe & Deli', 'url': u'http://www.allmenus.com/nj/hoboken/55446-jp-bagel-express-cafe--deli/menu/', 'ratingValue': u'4', 'address': u'52 Newark St, Hoboken  NJ  07030'}, {'reviewCount': u'38', 'tel': u'(201) 942-2333', 'name': u'India on the Hudson', 'url': u'http://www.allmenus.com/nj/hoboken/285307-india-on-the-hudson/menu/', 'ratingValue': u'3.5', 'address': u'1210 Washington St, Hoboken  NJ  07030'}, {'reviewCount': None, 'tel': u'(201) 885-3139', 'name': u'Sabores Restaurante Mexicano', 'url': u'http://www.allmenus.com/nj/hoboken/315269-sabores-restaurante-mexicano/menu/', 'raingValue': 0, 'ratingValue': None, 'address': u'518 Washington St, Hoboken  NJ  07030', 'reveiwCount': 0}, {'reviewCount': None, 'tel': u'(201) 942-2959', 'name': u'Cugini Kitchen', 'url': u'http://www.allmenus.com/nj/hoboken/303857-cugini-kitchen/menu/', 'raingValue': 0, 'ratingValue': None, 'address': u'918 Washington St, Hoboken  NJ  07030', 'reveiwCount': 0}, {'reviewCount': u'76', 'tel': u'(201) 793-2855', 'name': u'Hoboken Gourmet Company', 'url': u'http://www.allmenus.com/nj/hoboken/270379-hoboken-gourmet-company/menu/', 'ratingValue': u'3', 'address': u'423 Washington St, Hoboken  NJ  07030'}, {'reviewCount': None, 'tel': u'(201) 499-0188', 'name': u'Midtown Philly Steaks', 'url': u'http://www.allmenus.com/nj/hoboken/321100-midtown-philly-steaks/menu/', 'raingValue': 0, 'ratingValue': None, 'address': u'523 Washington St, Hoboken  NJ  07030', 'reveiwCount': 0}, {'reviewCount': u'34', 'tel': u'(201) 850-1882', 'name': u'Maoz Hoboken', 'url': u'http://www.allmenus.com/nj/hoboken/296828-maoz-hoboken/menu/', 'ratingValue': u'3.5', 'address': u'315 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'5', 'tel': u'(201) 942-6310', 'name': u"Sasso's Deli", 'url': u'http://www.allmenus.com/nj/hoboken/296877-sassos-deli/menu/', 'ratingValue': u'3.5', 'address': u'1038 Garden St, Hoboken  NJ  07030'}, {'reviewCount': u'46', 'tel': u'(201) 222-8499', 'name': u'Energy Kitchen', 'url': u'http://www.allmenus.com/nj/hoboken/271529-energy-kitchen/menu/', 'ratingValue': u'2.5', 'address': u'96 Hudson St, Hoboken  NJ  07030'}, {'reviewCount': u'36', 'tel': u'(201) 710-5450', 'name': u'Hoboken on Rye', 'url': u'http://www.allmenus.com/nj/hoboken/308884-hoboken-on-rye/menu/', 'ratingValue': u'4', 'address': u'164 1st St, Hoboken  NJ  07030'}, {'reviewCount': u'45', 'tel': u'(201) 403-9829', 'name': u'Liberty Bar & Grill', 'url': u'http://www.allmenus.com/nj/hoboken/55420-liberty-bar--grill/menu/', 'ratingValue': u'2', 'address': u'61 14th St, Hoboken  NJ  07030'}, {'reviewCount': u'1', 'tel': u'(201) 656-8085', 'name': u"Joe's Prime Meats", 'url': u'http://www.allmenus.com/nj/hoboken/280174-joes-prime-meats/menu/', 'ratingValue': u'4', 'address': u'918 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'12', 'tel': u'(201) 656-3450', 'name': u'Uptown Bagels Incorporated', 'url': u'http://www.allmenus.com/nj/hoboken/280172-uptown-bagels-incorporated/menu/', 'ratingValue': u'3.5', 'address': u'112 14th St, Hoboken  NJ  07030'}, {'reviewCount': u'13', 'tel': u'(201) 963-8686', 'name': u'El Barrio Burritos', 'url': u'http://www.allmenus.com/nj/hoboken/241661-el-barrio-burritos/menu/', 'ratingValue': u'2', 'address': u'89 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'24', 'tel': u'(201) 222-1414', 'name': u'Fresh U Grill + Juice Bar', 'url': u'http://www.allmenus.com/nj/hoboken/320110-fresh-u-grill-and-juice-bar/menu/', 'ratingValue': u'2.5', 'address': u'70 Hudson Street, Hoboken  NJ  07030'}, {'reviewCount': u'2', 'tel': u'(201) 714-9446', 'name': u'Alucra Pizzeria', 'url': u'http://www.allmenus.com/nj/hoboken/293118-alucra-pizzeria/menu/', 'ratingValue': u'3.5', 'address': u'301 Jackson St, Hoboken  NJ  07030'}, {'reviewCount': None, 'tel': u'(201) 710-5094', 'name': u'Hudson Pizza Company', 'url': u'http://www.allmenus.com/nj/hoboken/297314-hudson-pizza-company/menu/', 'raingValue': 0, 'ratingValue': None, 'address': u'100 Hudson St, Hoboken  NJ  07030', 'reveiwCount': 0}, {'reviewCount': u'27', 'tel': u'(201) 963-0900', 'name': u"Lucky's Famous Burgers - Hoboken", 'url': u'http://www.allmenus.com/nj/hoboken/297685-luckys-famous-burgers/menu/', 'ratingValue': u'2.5', 'address': u'79 Hudson St, Hoboken  NJ  07030'}, {'reviewCount': u'26', 'tel': u'(201) 793-2514', 'name': u'Grande Pizza & Wings To Go', 'url': u'http://www.allmenus.com/nj/hoboken/12963-grande-pizza-/menu/', 'ratingValue': u'2.5', 'address': u'400 Newark St, Hoboken  NJ  07030'}, {'reviewCount': u'26', 'tel': u'(201) 793-2514', 'name': u'Grande Pizza & Wings To Go', 'url': u'http://www.allmenus.com/nj/hoboken/12963-grande-pizza-/menu/', 'ratingValue': u'2.5', 'address': u'400 Newark St, Hoboken  NJ  07030'}, {'reviewCount': u'118', 'tel': u'(201) 792-0010', 'name': u"Grimaldi's", 'url': u'http://www.allmenus.com/nj/hoboken/296886-grimaldis/menu/', 'ratingValue': u'4', 'address': u'411 Washington St, Hoboken  NJ  07030'}, {'reviewCount': None, 'tel': u'(201) 942-6300', 'name': u'Zena Grocery and Deli', 'url': u'http://www.allmenus.com/nj/hoboken/293747-zena-grocery-and-deli/menu/', 'raingValue': 0, 'ratingValue': None, 'address': u'400 Jefferson St, Hoboken  NJ  07030', 'reveiwCount': 0}, {'reviewCount': u'14', 'tel': u'(201) 942-6387', 'name': u'Raf Deli & Cafe', 'url': u'http://www.allmenus.com/nj/hoboken/298198-raf-deli--cafe/menu/', 'ratingValue': u'2', 'address': u'552 1st St, Hoboken  NJ  07030'}, {'reviewCount': u'65', 'tel': u'(201) 630-6061', 'name': u'San Giuseppe Coal Fired Pizza & Cucina', 'url': u'http://www.allmenus.com/nj/hoboken/313631-san-giuseppe-coal-fired-pizza--cucina/menu/', 'ratingValue': u'4', 'address': u'1320 Adams St, Hoboken  NJ  07030'}, {'reviewCount': u'11', 'tel': u'(201) 683-8733', 'name': u'Sol Caribe', 'url': u'http://www.allmenus.com/nj/hoboken/305699-sol-caribe/menu/', 'ratingValue': u'2', 'address': u'518 Washington Street, Hoboken  NJ  07030'}, {'reviewCount': u'22', 'tel': u'(201) 942-8688', 'name': u'Matt & Meera', 'url': u'http://www.allmenus.com/nj/hoboken/313955-matt--meera/menu/', 'ratingValue': u'4.5', 'address': u'618 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'1', 'tel': u'(201) 942-6386', 'name': u'Hoboken Munchies', 'url': u'http://www.allmenus.com/nj/hoboken/296623-hoboken-munchies/menu/', 'ratingValue': u'1', 'address': u'1040 Grand St, Hoboken  NJ  07030'}, {'reviewCount': None, 'tel': u'(201) 942-2848', 'name': u'Eco Hoboken', 'url': u'http://www.allmenus.com/nj/hoboken/301609-eco-hoboken/menu/', 'raingValue': 0, 'ratingValue': None, 'address': u'249 11th St., Hoboken  NJ  07030', 'reveiwCount': 0}, {'reviewCount': u'27', 'tel': u'(201) 706-8308', 'name': u"Jo's Diner", 'url': u'http://www.allmenus.com/nj/hoboken/340413-jos-diner/menu/', 'ratingValue': u'3.5', 'address': u'219 Washington Street, Hoboken  NJ  07030'}, {'reviewCount': u'102', 'tel': u'(201) 792-9102', 'name': u'Tutta Pasta Restaurant and Bar', 'url': u'http://www.allmenus.com/nj/hoboken/305695-tutta-pasta-restaurant-and-bar/menu/', 'ratingValue': u'3', 'address': u'200 Washington St, Hoboken  NJ  07030'}, {'reviewCount': None, 'tel': u'(201) 625-5688', 'name': u"Chris' Curbside Cravings", 'url': u'http://www.allmenus.com/nj/hoboken/339594-chris-curbside-cravings/menu/', 'raingValue': 0, 'ratingValue': None, 'address': u'101 Washington St, Hoboken  NJ  07030', 'reveiwCount': 0}, {'reviewCount': u'37', 'tel': u'(201) 942-9797', 'name': u'Hoboken Dhaba', 'url': u'http://www.allmenus.com/nj/hoboken/341269-hoboken-dhaba/menu/', 'ratingValue': u'3.5', 'address': u'630 Washington Street, Hoboken  NJ  07030'}, {'reviewCount': u'16', 'tel': u'(201) 706-8550', 'name': u'Sammys Roadhouse', 'url': u'http://www.allmenus.com/nj/hoboken/303593-sammys-roadhouse/menu/', 'ratingValue': u'3.5', 'address': u'700 1st St, Hoboken  NJ  07030'}, {'reviewCount': None, 'tel': u'(201) 630-6073', 'name': u'Muscle Maker Grill', 'url': u'http://www.allmenus.com/nj/hoboken/318374-muscle-maker-grill/menu/', 'raingValue': 0, 'ratingValue': None, 'address': u'217 Washington St, Hoboken  NJ  07030', 'reveiwCount': 0}, {'reviewCount': u'27', 'tel': u'(201) 963-0900', 'name': u'Windmill', 'url': u'http://www.allmenus.com/nj/hoboken/308866-windmill-hot-dogs/menu/', 'ratingValue': u'2.5', 'address': u'79 Hudson St, Hoboken  NJ  07030'}, {'reviewCount': u'33', 'tel': u'(201) 459-0008', 'name': u'Harvest Cuisine', 'url': u'http://www.allmenus.com/nj/hoboken/296425-harvest-cuisine/menu/', 'ratingValue': u'3', 'address': u'518 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'3', 'tel': u'(201) 706-8333', 'name': u'La Bella Vista Pizza & Seafood', 'url': u'http://www.allmenus.com/nj/hoboken/297272-la-bella-vista-pizza--seafood/menu/', 'ratingValue': u'2.5', 'address': u'916 Washington St, Hoboken  NJ  07030'}, {'reviewCount': None, 'tel': u'(201) 706-8946', 'name': u'Park Ave Pizza and Grill', 'url': u'http://www.allmenus.com/nj/hoboken/333758-park-ave-pizza-and-grill/menu/', 'raingValue': 0, 'ratingValue': None, 'address': u'539 Park Ave, Hoboken  NJ  07030', 'reveiwCount': 0}, {'reviewCount': u'43', 'tel': u'(201) 238-2363', 'name': u'Fresh Pommes Frites', 'url': u'http://www.allmenus.com/nj/hoboken/295587-fresh-pommes-frites/menu/', 'ratingValue': u'3', 'address': u'207 Washington St, Hoboken  NJ  07030'}, {'reviewCount': None, 'tel': u'(201) 942-2875', 'name': u'Delight Deli and Grocery', 'url': u'http://www.allmenus.com/nj/hoboken/311169-delight-deli-and-grocery/menu/', 'raingValue': 0, 'ratingValue': None, 'address': u'56 Monroe St, Hoboken  NJ  07030', 'reveiwCount': 0}, {'reviewCount': None, 'tel': u'(201) 222-9662', 'name': u"Saint Mary's Pizzeria", 'url': u'http://www.allmenus.com/nj/hoboken/295841-saint-marys-pizzeria/menu/', 'raingValue': 0, 'ratingValue': None, 'address': u'131 Willow Ave, Hoboken  NJ  07030', 'reveiwCount': 0}, {'reviewCount': u'21', 'tel': u'(201) 610-1300', 'name': u"Ibby's Falafel", 'url': u'http://www.allmenus.com/nj/hoboken/298392-ibbys-falafel/menu/', 'ratingValue': u'3', 'address': u'614 Washington St, Hoboken  NJ  07030'}, {'reviewCount': None, 'tel': u'(201) 876-7950', 'name': u'Famous Pizza', 'url': u'http://www.allmenus.com/nj/hoboken/314069-famous-pizza/menu/', 'raingValue': 0, 'ratingValue': None, 'address': u'207 Washington St, Hoboken  NJ  07030', 'reveiwCount': 0}, {'reviewCount': None, 'tel': u'(201) 792-9202', 'name': u'Basic', 'url': u'http://www.allmenus.com/nj/hoboken/280171-basic/menu/', 'raingValue': 0, 'ratingValue': None, 'address': u'356 13th St, Hoboken  NJ  07030', 'reveiwCount': 0}, {'reviewCount': u'12', 'tel': u'(201) 420-8555', 'name': u'Dino Sandwich Cafe', 'url': u'http://www.allmenus.com/nj/hoboken/293265-dino-sandwich-cafe/menu/', 'ratingValue': u'3.5', 'address': u'614 Washington St, Hoboken  NJ  07030'}, {'reviewCount': None, 'tel': u'(201) 780-8912', 'name': u'Park & 11th Grocery', 'url': u'http://www.allmenus.com/nj/hoboken/281196-park--11th-grocery/menu/', 'raingValue': 0, 'ratingValue': None, 'address': u'249 11th St, Hoboken  NJ  07030', 'reveiwCount': 0}, {'reviewCount': u'43', 'tel': u'(201) 332-6889', 'name': u"Balbo's Pizzeria", 'url': u'http://www.allmenus.com/nj/hoboken/303778-balbos-pizzeria/menu/', 'ratingValue': u'3.5', 'address': u'70 Hudson St, Hoboken  NJ  07030'}, {'reviewCount': u'1', 'tel': u'(201) 653-6869', 'name': u'J & D', 'url': u'http://www.allmenus.com/nj/hoboken/295860-j--d/menu/', 'ratingValue': u'1', 'address': u'10 Paterson Ave, Hoboken  NJ  07030'}, {'reviewCount': u'36', 'tel': u'(201) 885-3149', 'name': u'Hoboken Dhaba', 'url': u'http://www.allmenus.com/nj/hoboken/342912-hoboken-dhaba/menu/', 'ratingValue': u'3.5', 'address': u'630 Washington St, Hoboken  NJ  07030'}, {'reviewCount': u'52', 'tel': u'(201) 351-7994', 'name': u"Rita's Ices Shakes & Sundaes", 'url': u'http://www.allmenus.com/nj/hoboken/345886-ritas-ices-shakes--sundaes/menu/', 'ratingValue': u'4.5', 'address': u'121 Washington St, Hoboken  NJ  07030'}]
for elem in list_restaurants:
    if elem['reviewCount'] == None:
        elem['reviewCount'] = 0
    if elem['ratingValue'] == None:
        elem['ratingValue'] = 0

# <codecell>

i = 0
for elem in list_restaurants:
    i = i+1
    str_url_tosearch = elem['url']
    str_url = '/users/michaelt/downloads/menus/'+str(i)+'.html'
    getMenusInfo(str_url, str_url_tosearch)
    print i,

# <codecell>


