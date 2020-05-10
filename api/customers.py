from core import app, db
from models.models import Customer
from flask import Flask, session, request 
from api.utils import status, auth , generate_token , getCustomer
import time
import api.SqlUtils as DBUtil
import re

# ------------------------------------------------------------------------------------------------------------------------------------#

# @app.route('/api/customer/getinfo',methods=['GET'])
# @auth.login_required
# def user_info():
#     customer = getCustomer()
#     info = {"id":customer.get("id")}
#     return status(200,data = info)

@app.route('/api/customer/register', methods=['POST']) 
def user_register():
    
    # 避免瞎注册  正则表达式
    register_res = request.get_json()     # 获得前端来的json数据,格式应该是 {username：,password：,email:, phone_num:, address:, }
    username = {"username":register_res.get("username")}   #提取有用信息(username)
    
    if DBUtil.search(username,"customer")[0]:
        return status(4103,'exist username')
    else:
        return_status = DBUtil.insert(register_res,"customer")    
        if return_status == 0:                     #插入失败
            return status(4103,'data insertion failure')
    return status(201,'register success')


@app.route('/api/customer/login', methods=['POST'])
def user_login():

    login_res = request.get_json()                #get_json获得字典  格式{username：,password：}       名字尚未统一, password还是password_hash

    username = login_res.get('username')
    password = login_res.get('password_hash')

    customer = {"username":username, "password_hash":password}

    user = DBUtil.search(customer,'customer')       #返回的是一个数组, [0] 获得第一个

    if not user:
        return status(4103,'error username or password')
    else:
        user_id = user[0][0].get('id')                               #咋回事啊   变成两个[0][0] 了
        return generate_token(user_id,"customer")
        

@app.route('/api/customer/appointment/create',methods=['POST'])
@auth.login_required
def appointment_create():

    # # 获得预约信息
    appointment_res = request.get_json()

    # 获得 customer 信息
    current_customer = getCustomer()
    customer_id = current_customer.get('id')

    pets = {}
    pets["owner_id"] = customer_id

    pets["pet_name"] = appointment_res.get("pet_name")
    pets["pet_gender"] = appointment_res.get("pet_gender")
    pets["pet_species"] = appointment_res.get("species")

    succusse = DBUtil.search(pets,"pet")              #没找到才插入
    print(succusse)
    if not succusse:
        DBUtil.insert(pets,"pet")
    
    # 将customer_id 加入到 字典中
    appointment_res["customer_id"] = customer_id

    if DBUtil.insert(appointment_res,'appointment'):
        return status(201,'create appointment success')
    else:
        return status(4103,'failed to create appointment')

@app.route('/api/customer/logout', methods=['GET'])
@auth.login_required
def user_logout():
    return status(201,'logout success')

@app.route('/api/customer/pet/<int:id>',methods=['GET'])
@auth.login_required
def get_pets(id):
    
    current_customer = getCustomer()
    query = {"owner_id":current_customer.get('id'),'index':id}
    pets ,length = DBUtil.search(query,"pet")

    if pets:
        for p in pets:
            p.pop('_sa_instance_state')
        return_data = {}
        return_data["count"] = len(pets)
        return_data['index'] = id
        return_data["item"] = pets
        return_data['total'] = length
        return status(200,'get pet successfully',return_data)
    else:
        return status(4103,'fail to get pets')

@app.route('/api/customer/appointment/<int:id>',methods = ['GET']) 
@auth.login_required
def user_appointment_get(id):      #id是appointment的id
    
    url  = request.url      # request.url: 返回带?，request.base_url返回不带?的

    current_customer = getCustomer()      # 获得用户信息

    para = re.findall(r'([^?&]*?)=',url)
    value = re.findall(r'=([^?&]*)',url)

    inpu = {}
    inpu['index'] = id
    inpu['customer_id'] = current_customer['id']
    inpu['appointment_date'] = '2020-02-05 00:00:00'
    for i in range(0,len(para)):
        inpu[para[i]] = value[i]

    print(inpu)
    print("-------------------------------------")
    appointments,length = DBUtil.search(inpu,"appointment")

    for a in appointments:
        a.pop('_sa_instance_state')
    return_appointment = {}
    return_appointment["total"] = length
    return_appointment["count"] = 0 if appointments==0 else len(appointments)
    return_appointment["index"] = id
    return_appointment["item"] = appointments

    if appointments:
        return status(200,'get appointment successfully',return_appointment)       # appointment 是一个数组
    else:      
        return status(404)  #如果没有该appointment   或   搜索出错

@app.route('/api/customer/profile',methods = ['GET'])       
@auth.login_required
def user_profile_get():

    #获取用户信息
    current_customer = getCustomer()

    profile = DBUtil.search({'id':current_customer['id']},'customer')[0]
    profile[0].pop("_sa_instance_state")
    profile[0].pop("password_hash")
    if profile:
        print(profile)
        return status(200,'get profile successfully',profile)
    else:
        return status(404)

@app.route('/api/customer/profile/modify',methods = ['POST'])               
@auth.login_required
def user_profile_modify():
    #获取用户信息
    current_customer = getCustomer()

    profile_res = request.get_json()

    profile = DBUtil.search({'id':current_customer['id']},'customer')[0]
    
    if profile:
        success = DBUtil.modify({'id':id},profile_res,'customer')
        if success:
            return status(201,'update profile successfully')
        else:
            return status(403,'update profile fails')
    else:
        return status(404)

@app.route('/api/customer/password/modify',methods = ['POST'])               
@auth.login_required
def user_password_modify():

    # 获取用户信息
    current_customer = getCustomer()

    password_res = request.get_json()

    key = {'id':current_customer.get('id'),'old_password':password_res.get('old_password')}
    pa = {'password_hash':password_res.get('new_passowrd')}
    success = DBUtil.modify(key,pa,'customer')
    if success:
        return status(201,'update password sucessfully')
    else:
        return status(403,'update password fails')

@app.route('/api/customer/operation/<int:id>',methods = ['GET'])     
@auth.login_required
def user_operation_get(id):
    
    url  = request.url      # request.url: 返回带?，request.base_url返回不带?的

    # 获得用户信息
    current_customer = getCustomer()

    para = re.findall(r'([^?&]*?)=',url)
    value = re.findall(r'=([^?&]*)',url)

    inpu = {}
    inpu['index'] = id
    inpu['customer_id'] = current_customer.get('id')
    for i in range(0,len(para)):
        inpu[para[i]] = value[i]

    operations, length = DBUtil.search(inpu,'operation')

    for o in operations:
        o.pop("_sa_instance_state")
        
    return_operation = {}
    return_operation["total"] = length
    return_operation["count"] = 0 if operations==0 else len(operations)
    return_operation["index"] = id
    return_operation["item"] = operations
    
    if operations:
        return status(200,'get operation successfully',return_operation)
    else:      
        return status(404)  