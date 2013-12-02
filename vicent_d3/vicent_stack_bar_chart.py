import pymysql
import json

dbuser = 'bia_user'
dbpsw = 'biabiabia'
dbname = 'biafinal_db'
l_host = '127.0.0.1'
l_port = 3306

vega_width = 500
vega_height = 300
def stackChart(cate,getwhat):
    conn = pymysql.connect(host=l_host, port=l_port, user=dbuser, passwd=dbpsw, db=dbname)
    cur1 = conn.cursor()
    cur2 = conn.cursor()

    cmd = "select distinct rest_name,rating,review_count "\
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
    print cmd
    print cmd_yelp
    cur1.execute(cmd)
    cur2.execute(cmd_yelp)
    #print(cur.description)

    values= []
    if getwhat=="ratio":
        wflag=1
    else:
        wflag=2
    idx = 1
    names = []
    for r1,r2 in zip(cur1,cur2):
        names.append(r1[0])
        print r1[wflag],r2[wflag]
        values.append({"x": idx, "y": int(r1[wflag]),"c":0})
        values.append({"x": idx, "y": int(r2[wflag]),"c":1})
        idx +=1

    stackchart = {}
    stackchart[ "name"]= "stack chart"
    stackchart[ "width"]=  vega_width
    stackchart[ "height"]= vega_height
    stackchart["padding"] =  {"top":10, "bottom":30, "left":30, "right":10}
    stackchart["data"] = []
    
    stackchart1 = {}
    stackchart1["name"] = "table";
    stackchart1["values"] = values
    stackchart2 = {}
    stackchart2["name"] = "stats"
    stackchart2["source"] = "table"
    stackchart2["transform"] = [        
        {"type": "facet", "keys": ["data.x"]},
        {"type": "stats", "value": "data.y"}];
    stackchart["data"].append(stackchart1)
    stackchart["data"].append(stackchart2)

    stackchart["scales"]= [
    {
      "name": "x",
      "type": "ordinal",
      "range": "width",
      "domain": {"data": "table", "field": "data.x"}
    },
    {
      "name": "y",
      "type": "linear",
      "range": "height",
      "nice": True,
      "domain": {"data": "stats", "field": "sum"}
    },
    {
      "name": "color",
      "type": "ordinal",
      "range": "category10"
    }
    ]

    stackchart["axes"] = [
        {"type": "x", "scale": "x"},
        {"type": "y", "scale": "y"}
    ]

    stackchart["marks"] = [
    {
      "type": "group",
      "from": {
        "data": "table",
        "transform": [
          {"type": "facet", "keys": ["data.c"]},
          {"type": "stack", "point": "data.x", "height": "data.y"}
        ]
      },
     "marks": [
        {
          "type": "rect",
          "properties": {
            "enter": {
              "x": {"scale": "x", "field": "data.x"},
              "width": {"scale": "x", "band": True, "offset": -1},
              "y": {"scale": "y", "field": "y"},
              "y2": {"scale": "y", "field": "y2"},
              "fill": {"scale": "color", "field": "data.c"}
            },
            "update": {
              "fillOpacity": {"value": 1}
            },
            "hover": {
              "fillOpacity": {"value": 0.5}
            }
          }
        }
      ]
    }    
    ]

    print stackchart
    with open('./vega_stack_bc_{0}.json'.format(getwhat), 'w') as outfile:
        json.dump(stackchart, outfile)

    print names;
    return names;

if __name__ == "__main__":
    #stackChart("Burgers","ratio")
    stackChart("Burgers","review")

