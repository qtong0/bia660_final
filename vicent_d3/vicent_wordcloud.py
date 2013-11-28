import pymysql
import json

def wcloud():
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='biafinal_db')
    cur = conn.cursor()
    cmd = "SELECT category.cate_name ,count(*) "\
          "  FROM biafinal_db.dish,biafinal_db.rest_category as rc ,restaurant_info as ri,biafinal_db.category"\
          "  where category.cate_id=dish.cate_id and dish.cate_id = rc.cate_id and ri.rest_id = rc.rest_id"\
          "  group by category.cate_name order by count(*) desc limit 50"
    print cmd
    cur.execute(cmd)
    print(cur.description)

    words = []
    for r in cur:
        words.append({"text": r[0], "value": float(r[1])/100})

    data = {}
    data[ "name"]= "wordcloud"
    data[ "width"]=  400
    data[ "height"]= 400
    data["padding"] =  {"top":0, "bottom":0, "left":0, "right":0}
    data["data"] = []
    
    data1 = {}
    data1["name"] = "table";
    data1["values"] = words
    data1["transform"] = [{        
          "type": "wordcloud",
          "text": "data.text",
          "font": "Helvetica Neue",
          "fontSize": "data.value",
          "rotate": {"random": [-60,-30,0,30,60]}
    }];
    data["data"].append(data1)

    data["marks"] = [
        {
          "type": "text",
          "from": {"data": "table"},
          "properties": {
            "enter": {
              "x": {"field": "x"},
              "y": {"field": "y"},
              "angle": {"field": "angle"},
              "align": {"value": "center"},
              "baseline": {"value": "alphabetic"},
              "font": {"field": "font"},
              "fontSize": {"field": "fontSize"},
              "text": {"field": "data.text"}
            },
            "update": {
              "fill": {"value": "steelblue"}
            },
            "hover": {
              "fill": {"value": "#f00"}
            }
          }
        }
      ];

    with open('./vega.json', 'w') as outfile:
        json.dump(data, outfile)

if __name__ == "__main__":
    wcloud()


