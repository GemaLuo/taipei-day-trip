from flask import *
app=Flask(__name__, static_folder="static", static_url_path="/")
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True
app.config["JSON_SORT_KEYS"]=False #固定

from flask import Flask, jsonify
import mysql.connector, math
import jwt
import time
from flask_cors import CORS 
from mysql.connector.pooling import MySQLConnectionPool
CORS(app, resources={r"/api/*": {"origins": "*"}})
mydb_pool=mysql.connector.pooling.MySQLConnectionPool(
		pool_name="mypool",
		pool_size=5,
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

#註冊新的會員
@app.route("/api/user", methods=["POST"]) 
def signup():
	json_data=request.json
	email=json_data["email"]
	db=mydb_pool.get_connection()
	cur=db.cursor(dictionary=True, buffered=True)
	myresult={}
	try:
		cur.execute("SELECT email FROM member WHERE email=%s;", [email])
		find_email=cur.fetchone()
		if find_email is not None:
			return {
				"error": True,
				"message": "此email已被註冊過"
			}
		name=json_data["name"]
		password=json_data["password"]
		insert_member_data=(name, email, password)
		sql="INSERT INTO member(name, email, password) VALUES(%s, %s, %s);"
		cur.execute(sql, insert_member_data)
		db.commit()
		myresult["ok"]=True
	except Exception as e:
		myresult["error"]=True
		myresult["message"]=e.__class__.__name__+str(e)
	finally:
		cur.close()
		db.close()
	return myresult

@app.route("/api/user/auth", methods=["GET", "PUT", "DELETE"])
def auth():
	if request.method=="GET": #取得當前登入的會員資訊
		myresult={}
		cookies=request.cookies
		try:
			if cookies:
				token=cookies["token"]
				jwt_key="TaipeiDayTrip"
				data=jwt.decode(token, jwt_key, algorithms='HS256')
				myresult["data"]=data
				return myresult
			return {"data": None}
		except Exception as e:
			return {"data": None}
	
	if request.method=="PUT": #登入會員帳戶
		myresult={}
		data=request.json
		member_data=(data["email"], data["password"])
		db=mydb_pool.get_connection()
		cur=db.cursor(dictionary=True, buffered=True)
		sql="SELECT member_id, name, email FROM member WHERE email=%s AND password=%s;"
		try:
			cur.execute(sql, member_data)
			search_data=cur.fetchone()
			if search_data==None:
				myresult["error"]=True
				return myresult
			payloads={
				"id":search_data["member_id"],
				"name":search_data["name"],
				"email":search_data["email"]
			}
			jwt_key="TaipeiDayTrip"
			token=jwt.encode(payloads, jwt_key, algorithm='HS256')
			myresult["ok"]=True
			myresult=make_response(myresult)
			myresult.set_cookie(key="token", value=token, expires=time.time()+60*60*24*7)
		except Exception as e:
			myresult["error"]=True
			myresult["message"]=e.__class__.__name__+str(e)
		finally:
			cur.close()
			db.close()
		return myresult
	if request.method=="DELETE":
		myresult={}
		myresult["ok"]=True
		response=make_response(myresult)
		response.set_cookie(key="token", value="", expires=0)
		return response

#預定行程
@app.route("/api/booking", methods=["GET"])
def check_booking():
	try:
	#取得尚未確認下單的預定行程
		token=request.cookies.get("token")
		if token==None:
			return jsonify({
				"error": True,
				"message": "尚未登入系統"
			}), 403
		jwt_key="TaipeiDayTrip"
		payloads=jwt.decode(token, jwt_key, algorithms='HS256')
		member_id=payloads["id"]

		db=mydb_pool.get_connection()
		cur=db.cursor(dictionary=True, buffered=True)
		sql="SELECT * FROM booking WHERE member_id=%s;"
		cur.execute(sql, (member_id,))
		booking_data=cur.fetchone()
		cur.close()
		if booking_data==None:
			return jsonify({
				"data": None
		}),200	
		attraction_id=booking_data["attractionId"]
		date=booking_data["date"]
		time=booking_data["time"]
		price=booking_data["price"]
	except Exception as e:
		return jsonify({
			"error": True,
			"message": "SYSTEM ERROR"
		})
	finally:
		cur.close()
		db.close()
		
	try:
		db=mydb_pool.get_connection()
		cur=db.cursor(dictionary=True, buffered=True)
		sql="SELECT name, address, images FROM attractions WHERE attractions.id=%s;"
		cur.execute(sql, (attraction_id,))
		attraction_data=cur.fetchone()
		cur.close()
		image_data=attraction_data["images"].replace("[","").replace("]","").replace("'","").split(",")
		image=json.loads(json.dumps(image_data))
		res={
			"data":{
				"attraction":{
					"id": attraction_id,
					"name": attraction_data["name"],
					"address": attraction_data["address"],
					"image": image[0]
				},
				"date": date,
				"time": time,
				"price": price
			}
		}
		return jsonify(res), 200
	except Exception as e:
		return jsonify({
			"error":True,
			"message": e.__class__.__name__+str(e)
		})
	finally:
		db.close()

@app.route("/api/booking", methods=["POST"])
def new_booking():
	#建立新的預定行程
	token=request.cookies.get("token")
	if token==None:
		return jsonify({
			"error": True,
			"message": "尚未登入系統"
		}), 403
	jwt_key="TaipeiDayTrip"
	payloads=jwt.decode(token, jwt_key, algorithms='HS256')
	member_id=payloads["id"]

	data=request.get_json()
	attractionId=data["attractionId"]
	date=data["date"]
	time=data["time"]
	price=data["price"]
	if date=="":
		return jsonify({
			"error": True,
			"message": "select date is needed."
		}), 400
	try: 
		db=mydb_pool.get_connection()
		cur=db.cursor(dictionary=True, buffered=True)
		sql="SELECT * FROM booking WHERE member_id=%s;"
		cur.execute(sql, (member_id,))
		get_data=cur.fetchone()
		if get_data==None:
			sql_data="INSERT INTO booking (member_id, attractionId, date, time, price) VALUES(%s, %s, %s, %s, %s);"
			val=(member_id, attractionId, date, time, price)
		else:
			sql_data="UPDATE booking SET member_id=%s, attractionId=%s, date=%s, time=%s, price=%s WHERE member_id=%s;"
			val=(member_id, attractionId, date, time, price, member_id)
		cur.execute(sql_data, val)
		db.commit()
		cur.close()
		return jsonify({
			"ok": True
		})
	except Exception as e:
		print(e)
		return jsonify({
			"error": True,
			"message": e.__class__.__name__+str(e)
		})
	finally:
		db.close()
@app.route("/api/booking", methods=["DELETE"])
def delete_booking():
	#刪除目前的預定行程
		token=request.cookies.get("token")
		if token==None:
			return jsonify({
				"error": True,
				"message": "尚未登入系統"
			}), 403
		jwt_key="TaipeiDayTrip"
		payloads=jwt.decode(token, jwt_key, algorithms='HS256')
		member_id=payloads["id"]
		try:
			db=mydb_pool.get_connection()
			cur=db.cursor(dictionary=True, buffered=True)
			sql="DELETE FROM booking WHERE member_id= %s;"
			cur.execute(sql, (member_id,))
			db.commit()
			cur.close()
			return jsonify({
				"ok": True
			})
		except Exception as e:
			print(e)
			return jsonify({
				"error": True,
				"message": e.__class__.__name__+str(e)
			})
		finally:
			db.close()

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=3000)