import mysql.connector
import json
import os

file=os.path.abspath('D:\taipei-day-trip\data\taipei-attractions.json')
json_data=open(file).read()
json_obj=json.loads(json_data)
data=json_obj["result"]["results"]

mydb=mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="passwordforec",
    #auth-plugin='mysql_native_password',
    db="taipeitrip",
    charset="utf8",
)
cur=mydb.cursor()
for item in data:
    id=item["_id"]
    name=item["name"]
    category=item["CAT"]
    description=item["description"]
    address=item["address"][0:3]+item["address"][5:]
    transport=item["direction"]
    mrt=item["MRT"]
    lat=item["latitude"]
    lng=item["longitude"]
    img=item["file"] #抓取file第一個網址，若第一個網址是非jpg檔案，就往後抓
    img=img.split("https")
    images=[]
    for i in img:
        if i.endswith(".jpg") or i.endswith(".JPG"):
            img.append("https"+i)
    images=str(images)
    sql="INSERT INTO data (id, name, category, description, address, transport, mrt, lat, lng, images) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val=(id, name, category, description, address, transport, mrt, lat, lng, images)
    cur.execute(sql, val)
    mydb.commit()
    
file.close()
    
    
    
    