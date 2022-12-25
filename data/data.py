import mysql.connector
import json


mydb=mysql.connector.connect(
    host="localhost",
    user="root",
    password="password", #passwordforec
    auth_plugin='mysql_native_password',
    db="taipeitrip",
    charset="utf8",
    pool_name="mypool",
    pool_size=5, 
)
connectionPool=mysql.connector.pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    pool_reset_session=True,
    auth_plugin='mysql_native_password',
    host="localhost",
    db="taipeitrip",
    user="root",
    password="password"
)
mydb=connectionPool.get_connection()
cur=mydb.cursor()

file=open("D:\\taipei-day-trip\\data\\taipei-attractions.json", 'r', encoding='utf-8').read()
json_obj=json.loads(file)
data=json_obj["result"]["results"]

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
    img=item["file"]
    img=img.split("https")
    images=[]
    for i in img:
        if i.endswith(".jpg") or i.endswith(".JPG"):
            images.append("https"+i)
    images=str(images)
    sql="INSERT INTO attractions (id, name, category, description, address, transport, mrt, lat, lng, images) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val=(id, name, category, description, address, transport, mrt, lat, lng, images)
    cur.execute(sql, val)
    mydb.commit()
mydb.close()

    
    
    
    