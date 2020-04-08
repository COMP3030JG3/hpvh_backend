from core import app, db
from models.models import Customer
from flask import Flask, session, request 
from api.utils import status, auth , generate_token , getCustomer
import time
import api.SqlUtils as DBUtil

#在每个需要判断token的函数下面调用 login_required

@app.route('/api/customer/register', methods=['POST']) 
def user_register():
    
    register_res = request.get_json()     # 获得前端来的json数据,格式应该是 {username：,password：,email:, phone_num:, address:, }

    # password = register_res.pop('password')
    # register_res[password_hash] = password
    # 名称转换     或者前后统一名字

    username = {"username":register_res.get("username")}   #提取有用信息(username)
    
    if DBUtil.search(username,"customer"):
        return status(4103,'exist username')
    else:
        return_status = DBUtil.insert(register_res,"customer")    
        if return_status == 0:                     #插入失败
            return status(4103,'data insertion failure')
    return status(200,'register success')


@app.route('/api/customer/login', methods=['POST'])
def user_login():

    login_res = request.get_json()                #get_json获得字典  格式{username：,password：}       名字尚未统一, password还是password_hash

    username = login_res.get('username')
    password = login_res.get('password_hash')

    customer = {"username":username, "password_hash":password}

    # if username == None or password == None:             #情况不存在吧,前端应该要先判断了是否非空
    #     return status(4103,"Error parament")

    user = DBUtil.search(customer,'customer')[0]       #返回的是一个数组, [0] 获得第一个

    if not user:
        return status(4103,'error username or password')
    else:
        user_id = user.get('id')
        return generate_token(user_id,"customer")
                # {
                #     "code": 200,
                #     "msg": "Login success",
                #     "token": {"user_id":user_id,"identify":"customer"}
                # }

@app.route('/api/customer/appointment/create',methods=['POST'])
@auth.login_required
def appointment_create():

    # # 获得预约信息
    appointment_res = request.get_json()

    # 获得 customer 信息
    current_customer = getCustomer()

    # 将customer_id 加入到 字典中
    customer_id = current_customer.get('id')
    appointment_res["customer_id"] = customer_id

    if DBUtil.insert(appointment_res,'appointment'):
        return status(200,'create appointment success')
    else:
        return status(4103,'failed to create appointment')

@app.route('/api/customer/logout', methods=['GET'])
@auth.login_required
def user_logout():
    # 前端的数据不再带有 token ,舍弃那个header即可
    return status(200,'logout success')

@app.route('/api/customer/appointment/<int:id>',methods = ['GET'])
@auth.login_required
def user_appointment_get(id):
    
    # 获得用户信息
    current_customer = getCustomer()

    if id == 0:   #0 表示获得所有 该用户的appointment
        appointments = DBUtil.search({'customer_id':current_customer['id']},'appointment')        
    else:         #非0  获得该用户的某个appointment
        appointments = DBUtil.search({'customer_id':current_customer['id'],'id':id},'appointment')
    
    if appointments:
        return status(200,'get appointment successfully',appointments)
    else:      
        return status(404)  #如果没有该appointment   或   搜索出错

@app.route('/api/customer/profile/<int:id>',methods = ['GET'])
@auth.login_required
def user_profile_get(id):

    #获取用户信息
    current_customer = getCustomer()
    if current_customer['id'] != id:             #避免获得别人的信息
        return status(401)

    profile = DBUtil.search({'id':current_customer['id']},'customer')
    
    if profile:
        return status(200,'get profile successfully',profile)
    else:
        return status(404)

@app.route('/api/customer/profile/modify/<int:id>',methods = ['POST'])
@auth.login_required
def user_profile_modify(id):

    #获取用户信息
    current_customer = getCustomer()
    if current_customer['id'] != id:             #避免获得别人的信息
        return status(401)

    profile_res = request.get_json()

    profile = DBUtil.search({'id':current_customer['id']},'customer')
    
    if profile:
        success = DBUtil.modify({'id':id},profile_res,'customer')
        if success:
            return status(201,'update profile successfully')
        else:
            return status(403,'update profile fails')
    else:
        return status(404)
