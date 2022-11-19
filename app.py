from flask import *
app=Flask(__name__)
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True
from flask import Flask, request, abort, jsonify

import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool

mydb_pool=MySQLConnectionPool(
	pool_name="",
	pool_size=3,
    host="localhost",
    user="root",
    password="password",
    #auth-plugin='mysql_native_password',
    db="taipeitrip",
    charset="utf8"
)


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
	#讀取頁數
	page=request.args.get("page", 0) 
	page=int(page)
	page_num=page*12
	next_pagenum=(page+1)*12
	#關鍵字搜尋
	try:
		db=mydb_pool.get_connection() 
		cur=db.cursor(dictionary=True)

		keyword=request.args.get("keyword")
		sql_key="SELECT id, name, category, description, address, transport, mrt, latitude, longitude, images FROM attractions WHERE name LIKE '%%%s%%' LIMIT %s, 12; " % (keyword, page_num,)
		sql="SELECT id, name, category, description, address, transport, mrt, latitude, longitude, images FROM attractions LIMIT %s, 12; " % (page_num,)
		sql_next="SELECT name FROM attractions LIMIT %s, 12; " % (next_pagenum,)
		sql_next_key="SELECT name FROM attractions WHERE name LIKE '%%%s%%' LIMIT %s, 12; " % (keyword, next_pagenum,)

		#判斷keyword
		if keyword != None:
			cur.execute(sql_key)
			result=cur.fetchall() #dict=true become dict

			#圖片處理-迴圈
			for i in range(len(result)):
				cur.execute(sql_key)
				img_result=cur.fetchall()
				img_list=img_result[i]["images"].split(",") #list
				img_list=img_list[0:-1] #cuz last one is null
				x=["images"]
				y=[img_list]
				img2list=dict(zip(x,y))
				result[i].update(img2list)
			z=["nextPage", "data"]
			k=[page+1, result]
			listplus=dict(zip(z,k))

			#nextPage keyword
			cur.execute(sql_next_key)
			next_result=cur.fetchall()

			if next_result==[]:  #fetch next page,if list is []/nothing,null
				x=["nextPage", "data"]
				y=[None, result]
				result_next_null=dict(zip(x,y))
				return result_next_null
			return listplus

		cur.execute(sql)
		result=cur.fetchall()

		for i in range(len(result)):
			cur.execute(sql)
			img_result=cur.fetchall()
			img_list=img_result[i]["images"].split(",")
			img_list=img_list[0:-1]
			x=["images"]
			y=[img_list]
			img2list=dict(zip(x,y))
			result[i].update(img2list)

		#combined "nextPage" & "data" with database
		z=["nextPage", "data"]
		k=[page+1, result]
		listplus=dict(zip(z,k))

		#make sure nextpage
		cur.execute(sql_next)
		next_result=cur.fetchall()

		if next_result==[]:
			z=["nextPage", "data"]
			k=[None,result]
			result_next_null=dict(zip(z,k))

			return result_next_null
		return listplus
	except:
		return abort(500)
	finally:
		mydb_pool.close()


#2nd API 根據景點編號取得景點資料
@app.route("/api/attraction/<attractionId>")
def attraction_id(attractionId):
	try:
		db=mydb_pool.get_connection()
		cur=db.cursor(dictionary=True)
		id_sql="SELECT id, name, category, description, address, transport, mrt, latitude, longitude, images FROM attractions WHERE id=%s ;" % (id,)
		cur.execute(id_sql)
		result=cur.fetchall()
		db.close()

		if result==None or result=="" or id=="" or id=="id" or id==None:
			return jsonify({"error":True, "message":"景點編號不正確"}), 400

		img_list=result[0]["images"].split(",")
		img_list=img_list[0:-1]
		x=["images"]
		y=[img_list]
		img2list=dict(zip(x,y))
		result[0].update(img2list)

		z=["data"]
		k=result
		listplus=dict(zip(z,k))
		
		return listplus
	except:
		return abort(500)

@app.errorhandler(400)
def request_failed(e):
	return jsonify({"error":True, "message":"景點編號不正確"}),400

@app.errorhandler(500)
def request_failed(e):
	return jsonify({"error":True,"message":"伺服器內部錯誤"}),500


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
			obj=result[0].replace(u'\u3000', u'')
			categories.append(obj)
		res_data={"data":categories}
		return res_data
	except:
		return jsonify({"error":True,"message":"伺服器內部錯誤"})

	

app.run(port=3000)