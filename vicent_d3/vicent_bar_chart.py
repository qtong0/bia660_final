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

def ratioBar(cate,getwhat):
    if getwhat not in ["ratio","review","price"]:
        raise AssertionError("getwhat should be ratio/review/price")
    conn = pymysql.connect(host=l_host, port=l_port, user=dbuser, passwd=dbpsw, db=dbname)
    cur = conn.cursor()

    cmd = ""
    if getwhat=="price":
        cmd = "SELECT ri.rest_id,ri.rest_name,avg(dish_price)" \
        " FROM biafinal_db.dish,biafinal_db.rest_category as rc ,restaurant_info as ri,biafinal_db.category" \
        " where category.cate_id=dish.cate_id and dish.cate_id = rc.cate_id and ri.rest_id = rc.rest_id "\
        " and category.cate_name like '{0}%'" \
        " group by ri.rest_id"\
        " order by ri.rest_id".format(cate)
    else:
        """
        cmd = "select rest_name,rating,review_count from restaurant_info where rest_id in"\
            "(" \
            "select rest_id from rest_category where cate_id in "\
            "(SELECT cate_id FROM biafinal_db.category where cate_name like '{0}%')"\
            ")".format(cate)
        """
        cmd = "select distinct rest_name,rating,review_count "\
            " from restaurant_info ri,rest_category rc, biafinal_db.category c "\
            " where ri.rest_id = rc.rest_id and c.cate_id = rc.cate_id "\
            " and c.cate_name like '{0}%' order by ri.rest_id ".format(cate)
    print cmd
    cur.execute(cmd)
    print(cur.description)
    #r = cur.fetchall()

    names = []
    ratios = []
    titles = []
    c = 1
    for r in cur:
        #print (r[2])
        if getwhat=="price":
            names.append(r[1])
            ratios.append({"price":r[2]})
        else:
            names.append(r[0])
            ratios.append({"ratio":r[1],"review":r[2]})
        titles.append("T{0}".format(c))
        c += 1 

    print ratios ,titles
    cur.close()
    conn.close()
    #self.redirect("/vicent")


    df = pd.DataFrame(ratios, index=titles)

    vis = Visualization(width=500, height=300)
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
    vis.to_json('vega_bc.json')
    print names
    return names

if __name__ == "__main__":
    #ratioBar("Burgers","ratio");
    #ratioBar("Burgers","review");
    ratioBar("Burgers","price");
