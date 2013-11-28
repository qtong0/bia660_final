# -*- coding: utf-8 -*-
"""

Vincent Line Examples

"""

#Build a Line Chart from scratch

from vincent import *
import pandas.io.data as web
import pandas as pd
import pymysql

def line(cate):
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='biafinal_db')
    cur = conn.cursor()
    cmd = "select rest_name,rating,review_count from restaurant_info where rest_id in"\
            "(" \
            "select rest_id from rest_category where cate_id in "\
            "(SELECT cate_id FROM biafinal_db.category where cate_name like '{0}%')"\
            ")".format(cate)
    print cmd
    cur.execute(cmd)
    print(cur.description)

    ratings = []
    reviews = []
    for r in cur:
        #print (r[2])
        ratings.append(r[1])
        reviews.append(r[2])

    print ratings ,reviews
    #d3py

    df = pd.DataFrame({
        'd1': ratings,
        'd2': reviews
    })



    #Note that we're using timeseries, so x-scale type is "time". For non
    #timeseries data, use "linear"
    vis = Visualization(width=500, height=300)
    vis.scales['x'] = Scale(name='x', type='time', range='width',
                            domain=DataRef(data='table', field="data.idx"))
    vis.scales['y'] = Scale(name='y', range='height', type='linear', nice=True,
                            domain=DataRef(data='table', field="data.val"))
    vis.scales['color'] = Scale(name='color', type='ordinal',
                                domain=DataRef(data='table', field='data.col'),
                                range='category20')
    vis.axes.extend([Axis(type='x', scale='x'),
                     Axis(type='y', scale='y')])

    #Marks
    transform = MarkRef(data='table',
                        transform=[Transform(type='facet', keys=['data.col'])])
    enter_props = PropertySet(x=ValueRef(scale='x', field="data.idx"),
                              y=ValueRef(scale='y', field="data.val"),
                              stroke=ValueRef(scale="color", field='data.col'),
                              stroke_width=ValueRef(value=2))
    mark = Mark(type='group', from_=transform,
                marks=[Mark(type='line',
                properties=MarkProperties(enter=enter_props))])
    vis.marks.append(mark)

    data = Data.from_pandas(df)

    #Using a Vincent Keyed List here
    vis.data['table'] = data
    vis.axis_titles(x='ratio', y='review')
    vis.legend(title='ratio/review')
    vis.to_json('vega.json')

if __name__ == "__main__":
    #ratioBar("Burgers","ratio");
    #ratioBar("Burgers","review");
    line("Burgers");

