from flask import *
app=Flask(__name__)
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True
app.config["JSON_SORT_KEYS"]=False #固定

from flask import Flask, jsonify
import mysql.connector, math
from mysql.connector.pooling import MySQLConnectionPool

mydb_pool=mysql.connector.pooling.MySQLConnectionPool(
		pool_name="mypool",
		pool_size=3,
    	host="localhost",
    	user="root",
    	password="password",
		auth_plugin='mysql_native_password',
    	db="taipeitrip",
    	charset="utf8")
# print(mydb_pool.pool_name)
# print(mydb_pool.pool_size)

# Pages
@app.route("/")
def index():
	return render_template("index.html")
@app.route("/attraction/<id>")
def attraction(id):
	return render_template("attraction.html")
@app.route("/booking")
def booking():
	return render_template("booking.html")
@app.route("/thankyou")
def thankyou():
	return render_template("thankyou.html")

#旅遊景點
#1st API 取得景點資料列表
@app.route("/api/attractions")
def attractions():
	page=int(request.args.get("page"))
	pages=page*12
	keyword=request.args.get("keyword")
	db=mydb_pool.get_connection()
	cur=db.cursor(buffered=True)

	#1-1(有keyword)搜尋category or name的資料，完全比對景點分類&模糊比對景點名稱
	sql1="SELECT * FROM attractions WHERE category = %s OR LOCATE(%s, name)>0 LIMIT %s,%s"
	val1=(keyword, keyword, pages, 12)
	
	#1-2(有keyword)category or name的資料筆數
	count1="SELECT COUNT(*) FROM attractions WHERE category = %s OR LOCATE(%s, name)>0"
	val2=(keyword, keyword)

	#2-1(no keyword)all pages
	sql2="SELECT * FROM attractions LIMIT %s,%s"
	val3=(pages, 12)

	#2-2(no keyword)all pages的資料筆數
	count3="SELECT count(*) FROM attractions"
	
	if keyword != None:
		#1-1
		cur.execute(sql1, val1)
		result=cur.fetchall()
		#1-2
		cur.execute(count1, val2)
		num=cur.fetchone()[0]
	else:
		#2-1
		cur.execute(sql2, val3)
		result=cur.fetchall()
		#2-2
		cur.execute(count3)
		num=cur.fetchone()[0]
	#算最後一頁:用math.ceil(x)取大於or等於x值的整數
	last=math.ceil(num/12)
	next=page+1
	if next>=last:
		next=None
	i=0 
	mylist=[]
	try:
		while i<len(result): 
			myresult = {				
				"id" : result[i][0],
				"name" : result[i][1],
				"category" : result[i][2],
				"description" : result[i][3],
				"address" : result[i][4],
				"transport" : result[i][5],
				"mrt" : result[i][6],
				"lat" : result[i][7],
				"lng" : result[i][8],
				"images" : eval(result[i][9]) 
			}
			mylist.append(myresult)
			i=i+1
		return jsonify({
			"nextPage" : next, 
			"data" : mylist
		})
	except ValueError:
		return jsonify({
			"error": True,
			"message": "Error!"
		}), 400
	except Exception:
		return jsonify({
			"error": True,
			"message": "伺服器內部錯誤"
		}), 500
	finally:
		db.close()
	# page=int(request.args.get("page"))
	# pages=page*12
	# keyword=request.args.get("keyword")
	# db=mydb_pool.get_connection()
	# cur=db.cursor(buffered=True)
	# if keyword:
	# 	#
	# 	sql="SELECT * FROM attractions WHERE category=%s OR LOCATE(%s, name)>0 LIMIT %s,%s"
	# 	val=(keyword, keyword, pages, 12)
	# 	cur.execute(sql, val)
	# 	result=cur.fetchall()

	# 	count="SELECT COUNT(*) FROM attractions WHERE category=%s OR LOCATE(%s, name)>0"
	# 	val=(keyword, keyword)
	# 	cur.execute(count, val)
	# 	num=cur.fetchone()[0]
		
	# else:
	# 	sql="SELECT * FROM attractions LIMIT %s,%s"
	# 	val=(pages, 12)
	# 	cur.execute(sql,val)
	# 	result=cur.fetchall()

	# 	count="SELECT count(*) FROM attractions"
	# 	cur.execute(count)
	# 	num=cur.fetchone()[0]
		
	# last=math.ceil(num/12)
	# next=page+1
	# if next>=last:
	# 	next=None
	# i=0 
	# mylist=[]
	# try:
	# 	while i<len(result): 
	# 		myresult = {				
	# 			"id" : result[i][0],
	# 			"name" : result[i][1],
	# 			"category" : result[i][2],
	# 			"description" : result[i][3],
	# 			"address" : result[i][4],
	# 			"transport" : result[i][5],
	# 			"mrt" : result[i][6],
	# 			"lat" : result[i][7],
	# 			"lng" : result[i][8],
	# 			"images" : eval(result[i][9])
	# 		}
			
	# 		mylist.append(myresult)
	# 		i = i + 1
	# 	return jsonify({"nextPage" : next, 
	# 				"data" : mylist})
	# except:
	# 	return jsonify({"error": True,
	# 			"message": "Internal Server Error"}), 500
	# finally:
	# 	db.close()

#2nd API 根據景點編號取得景點資料
@app.route("/api/attraction/<id>")
def attraction_id(id):
	try:
		db=mydb_pool.get_connection()
		cur=db.cursor(dictionary=True,buffered=True)
		id_sql="SELECT * FROM attractions WHERE id=%s ;" % (id,)
		cur.execute(id_sql)
		result=cur.fetchall()
		img_list=result[0]["images"].replace("[","").replace("]","").replace("'","").split(",")
		img_list=img_list[0:-1]
		x=["images"]
		y=[img_list]
		img2list=dict(zip(x,y))
		result[0].update(img2list)
		z=["data"]
		k=result
		listplus=dict(zip(z,k))
		return listplus
	except TypeError:
		return jsonify({
			"error":True,
			"message":"景點編號不正確"
		}), 400
	except Exception:
		return jsonify({
			"error":True,
			"message":"伺服器錯誤"
		}), 500
	finally:
		db.close()

#3rd API 取得景點分類名稱列表
@app.route("/api/categories")
def category():
	try:
		db=mydb_pool.get_connection()
		cur=db.cursor()
		sql="SELECT category FROM attractions"
		cur.execute(sql)
		myresult=set(cur.fetchall())
		categories=[]
		for result in myresult:
			obj=result[0].replace(u'\u3000', u'') #去除空格:https://www.cnblogs.com/zqifa/p/python-9.html
			categories.append(obj)
		get_data={"data":categories}
		return get_data
	except Exception:
		return jsonify({
			"error":True,
			"message":"伺服器內部錯誤"
		}), 500
	finally:
		db.close()

	
if __name__ == "__main__":
	app.run(host="0.0.0.0", port=3000)