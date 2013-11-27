#!/usr/bin/env python
#

import MySQLdb
import os
import webapp2
import jinja2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
MAIN_HTML = '''
<!DOCTYPE HTML>
<HTML>
<HEAD>
    <TITLE>Temporary Main Page</TITLE>
</HEAD>

<BODY>
    <H1>
        <a href="/maps">Map</a>
    </H1>
    <H1>
        <a href="/list">List</a>
    </H1>
</BODY>
</HTML>
'''

class IndexPage(webapp2.RequestHandler):
    def get(self):
        self.response.write(MAIN_HTML)

class myMap(webapp2.RequestHandler):
    def get(self):
        tpl_vars = {"testVal": ""}
        template = JINJA_ENVIRONMENT.get_template('/maps/maps.html')
        self.response.out.write(template.render(tpl_vars))
    def post(self):
        search_cont = self.request.get("search_cont")
        str_opt_num = self.request.get("opt_num")
        db = MySQLdb.connect(host='localhost', user='bia_user',
            passwd = 'biabiabia', db = 'biafinal_db')
        cursor = db.cursor()
        str_sql_getaddress = '''
        select distinct restaurant_info.address, restaurant_info.rest_name, rest_latlong.lat, rest_latlong.lng
        from restaurant_info, dish, rest_category, rest_latlong
        where restaurant_info.rest_id = rest_category.rest_id and rest_category.cate_id = dish.cate_id and rest_latlong.rest_id = restaurant_info.rest_id\n'''
        str_sql_getaddress += "and dish.dish_name like '%"+search_cont+"%' limit "+str_opt_num+";"

        cursor.execute(str_sql_getaddress)
        str_restnames = ""
        str_latlng = ''
        arr_addresses = []
        arr_names = []
        arr_latlongs = []
        for r in cursor.fetchall():
            dic_latlong = {'lat': '', 'lng': ''}
            str_restnames = str_restnames + str(r[1]) + '#'
            arr_addresses.append(str(r[0]))
            arr_names.append(str(r[1]))
            dic_latlong['lat'] = str(r[2])
            dic_latlong['lng'] = str(r[3])
            arr_latlongs.append(dic_latlong)
            tmp_str_latlng = dic_latlong['lat']+' '+dic_latlong['lng']
            str_latlng += tmp_str_latlng + '#'

        str_restnames = str_restnames[:-1]
        str_latlng = str_latlng[:-1]

        tmp_html = search_cont
        tpl_vars = {"testVal": str_restnames, 'str_latlng': str_latlng}
        template = JINJA_ENVIRONMENT.get_template('/maps/maps.html')
        self.response.out.write(template.render(tpl_vars))
        self.response.write("Result:<br>\n"+str(len(arr_addresses))+"<br>\n")
        for i in range(len(arr_addresses)):
            self.response.write(arr_addresses[i]+": "+arr_names[i]+" "+arr_latlongs[i]['lat']+" "+arr_latlongs[i]['lng']+"<br>\n")
        db.close()

class myList(webapp2.RequestHandler):
    def get(self):
        orderby = self.request.get("order")
        search_cont = self.request.get("s_cont")
        if orderby == "rating" and search_cont != '':
            db = MySQLdb.connect(host='localhost', user='bia_user',
                passwd = 'biabiabia', db = 'biafinal_db')
            cursor = db.cursor()
            str_sql_getrestinfo = '''
                select restaurant_info.rest_name, restaurant_info.address, restaurant_info.telephone, rating, restaurant_info.rest_id, count(restaurant_info.rest_name)
                from restaurant_info, dish, rest_category
                where restaurant_info.rest_id = rest_category.rest_id and rest_category.cate_id = dish.cate_id\n'''
            str_sql_getrestinfo += "and dish.dish_name like '%"+search_cont+"%'\n"
            str_sql_getrestinfo += '''group by restaurant_info.rest_name, restaurant_info.address, restaurant_info.telephone, rating, restaurant_info.rest_id
                order by restaurant_info.rating desc;'''
            cursor.execute(str_sql_getrestinfo)

            arr_mytable = []
            for r in cursor.fetchall():
                dic_item = {"name":'', "address":'', "telephone":'', "rating":''}
                dic_item['name'] = r[0]
                dic_item['address'] = r[1]
                dic_item['telephone'] = r[2]
                dic_item['rating'] = str(r[3])
                arr_mytable.append(dic_item)

            tpl_vars = {"links_display": "display: inline-block;", "arr_mytable": arr_mytable, "search_cont": search_cont}
            template = JINJA_ENVIRONMENT.get_template('/list/list.html')
            self.response.out.write(template.render(tpl_vars))

            db.close()
        else:
            tpl_vars = {"links_display": "display:none;"}
            template = JINJA_ENVIRONMENT.get_template('/list/list.html')
            self.response.out.write(template.render(tpl_vars))

    def post(self):
        search_cont = self.request.get("search_cont")

        db = MySQLdb.connect(host='localhost', user='bia_user',
            passwd = 'biabiabia', db = 'biafinal_db')
        cursor = db.cursor()
        str_sql_getrestinfo = '''
            select restaurant_info.rest_name, restaurant_info.address, restaurant_info.telephone, rating, restaurant_info.rest_id, count(restaurant_info.rest_name)
            from restaurant_info, dish, rest_category
            where restaurant_info.rest_id = rest_category.rest_id and rest_category.cate_id = dish.cate_id\n'''
        str_sql_getrestinfo += "and dish.dish_name like '%"+search_cont+"%'\n"
        str_sql_getrestinfo += '''group by restaurant_info.rest_name, restaurant_info.address, restaurant_info.telephone, rating, restaurant_info.rest_id
            order by rest_id;'''
        cursor.execute(str_sql_getrestinfo)

        arr_mytable = []
        for r in cursor.fetchall():
            dic_item = {"name":'', "address":'', "telephone":'', "rating":''}
            dic_item['name'] = r[0]
            dic_item['address'] = r[1]
            dic_item['telephone'] = r[2]
            dic_item['rating'] = str(r[3])
            arr_mytable.append(dic_item)

        tpl_vars = {"links_display": "display: inline-block;", "arr_mytable": arr_mytable, "search_cont": search_cont}
        template = JINJA_ENVIRONMENT.get_template('/list/list.html')
        self.response.out.write(template.render(tpl_vars))

        db.close()


app = webapp2.WSGIApplication([
    ('/', IndexPage),
    ('/maps', myMap),
    ('/list', myList)
    ])