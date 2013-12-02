# -*- coding: utf-8 -*-
"""

Vincent Bar Chart Example

"""

#Build a Bar Chart from scratch

from vincent import *
import pandas as pd
import pymysql

dbuser = 'bia_user'
dbpsw = 'biabiabia'
dbname = 'biafinal_db'
l_host = '127.0.0.1'
l_port = 3306

vega_width = 500
vega_height = 300

def ratioBar(cate,getwhat,w_price,w_allmenu_ratio,w_allmenu_review,w_yelp_ratio,w_yelp_review):
    conn = pymysql.connect(host=l_host, port=l_port, user=dbuser, passwd=dbpsw, db=dbname)
    cur_p = conn.cursor()
    cur_a = conn.cursor()
    cur_y = conn.cursor()

    cmd_price = "SELECT ri.rest_id,ri.rest_name,avg(dish_price)" \
        " FROM biafinal_db.dish,biafinal_db.rest_category as rc ,restaurant_info as ri,biafinal_db.category" \
        " where category.cate_id=dish.cate_id and dish.cate_id = rc.cate_id and ri.rest_id = rc.rest_id "\
        " and category.cate_name like '{0}%'" \
        " group by ri.rest_id order by ri.rest_id".format(cate)
    cmd_allmenu = "select distinct rest_name,rating,review_count,ri.rest_id "\
            " from restaurant_info ri,rest_category rc, biafinal_db.category c "\
            " where ri.rest_id = rc.rest_id and c.cate_id = rc.cate_id "\
            " and c.cate_name like '{0}%' order by ri.rest_id ".format(cate)

    cmd_yelp =      "select aaa.name,IFNULL(aaa.rating,0),IFNULL(aaa.review_count,0),aaa.id from (select id,name,rating,review_count,id_allmenu from"\
          "        restaurant_yelp y, id_map where y.id = id_map.id_yelp) as aaa "\
          "  right outer join ( "\
          "         select rest_id from restaurant_info "\
          "          where rest_id in(select rest_id from rest_category where cate_id in  "\
          "              (SELECT cate_id FROM biafinal_db.category where cate_name like '{0}%')) "\
          " order by rest_id         ) as ccc on ccc.rest_id = aaa.id_allmenu "\
          " order by aaa.id".format(cate)

    #print cmd
    cur_p.execute(cmd_price)
    cur_a.execute(cmd_allmenu)
    cur_y.execute(cmd_yelp)
    #print(cur.description)
    #r = cur.fetchall()

    ratios = []
    titles = []
    names = []
    c = 1
    for p,a,y in zip(cur_p,cur_a,cur_y):
        names.append(a[0])
        ratios.append({"recommend":(float(p[2])*w_price+\
                                    float(a[1])*w_allmenu_ratio+\
                                    float(a[2])*w_allmenu_review+\
                                    float(y[1])*w_yelp_ratio+\
                                    float(y[2])*w_yelp_review)})
        titles.append("T{0}".format(c))
        c += 1 

    print ratios ,titles
    cur_p.close()
    cur_a.close()
    cur_y.close()
    conn.close()
    #self.redirect("/vicent")


    df = pd.DataFrame(ratios, index=titles)

    vis = Visualization(width=vega_width, height=vega_height)
    vis.scales['x'] = Scale(name='x', type='ordinal', range='width',
                            domain=DataRef(data='table', field="data.idx"))
    vis.scales['y'] = Scale(name='y', range='height', nice=True,
                            domain=DataRef(data='table', field="data.val"))
    vis.axes.extend([Axis(type='x', scale='x'),
                     Axis(type='y', scale='y')])

    #Marks
    enter_props = PropertySet(x=ValueRef(scale='x', field="data.idx"),
                              y=ValueRef(scale='y', field="data.val"),
                              width=ValueRef(scale='x', band=True, offset=-1),
                              y2=ValueRef(scale='y', value=0))

    update_props = PropertySet(fill=ValueRef(value='steelblue'))

    mark = Mark(type='rect', from_=MarkRef(data='table'),
                properties=MarkProperties(enter=enter_props,
                                          update=update_props))
    vis.marks.append(mark)

    data = Data.from_pandas(df[getwhat])

    #Using a Vincent KeyedList here
    vis.data['table'] = data
    vis.axis_titles(x='restaurant', y=getwhat)
    vis.to_json('vega_bc_pro.json')
    print names;
    return names;

if __name__ == "__main__":
    #ratioBar("Burgers","recommend",w_price,w_allmenu_ratio,w_allmenu_review,w_yelp_ratio,w_yelp_review);
    ratioBar("Burgers","recommend",0.8,0.9,0.5,0.9,1);
