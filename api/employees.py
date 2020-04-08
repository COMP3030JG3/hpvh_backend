from core import app, db
from models.models import Employee
from flask import Flask, session, request 
from api.utils import status, auth, getEmployee
import time
import api.SqlUtils as DBUtil


###--------------------已完成---------------------------####
# 雇员不能随便注册,

@app.route('/api/employee/register', methods=['POST'])
def employee_register():
    
    register_res = request.get_json()     # 获得前端来的json数据,格式应该是 {username：,password：,email:, phone_num:, address:, }

    # password = register_res.pop('password')
    # register_res[password_hash] = password
    # 名称转换     或者前后统一名字

    username = {"username":register_res.get("username")}   #提取有用信息(username)
    
    if DBUtil.search(username,"employee"):
        return status(4103,'exist username')
    else:
        return_status = DBUtil.insert(register_res,"employee")    
        if return_status == 0:                     #插入失败
            return status(4103,'data insertion failure')
    return status(201,'register success')


@app.route('/api/employee/login', methods=['POST'])
def employee_login():

    login_res = request.get_json()                #get_json获得字典  格式{username：,password：}       名字尚未统一, password还是password_hash

    username = login_res.get('username')
    password = login_res.get('password_hash')

    employee = {"username":username, "password_hash":password}

    # if username == None or password == None:             #情况不存在吧,前端应该要先判断了是否非空
    #     return status(4103,"Error parament")

    user = DBUtil.search(customer,'employee')[0]       #返回的是一个数组, [0] 获得第一个

    if not user:
        return status(4103,'error username or password')
    else:
        user_id = user.get('id')
        return generate_token(user_id,"employee")
                # {
                #     "code": 200,
                #     "msg": "Login success",
                #     "token": {"user_id":user_id,"identify":"employee"}
                # }

@app.route('/api/employee/logout', methods=['GET'])
@auth.login_required
def employee_logout():
    # 前端的数据不再带有 token ,舍弃那个header即可
    return status(200,'logout success')


@app.route('/api/employee/appointment/<int:id>',methods = ['GET'])
@auth.login_required
def employee_appointment_get(id):
    
    if id == 0:   #0 表示获得所有
        appointments = DBUtil.searchAll('appointment')        
    else:         #非0  获得某个appointment
        appointments = DBUtil.search({'id':id},'appointment')
    
    if appointments:
        return status(200,'get appointment successfully',appointments)
    else:      
        return status(404)  #如果没有该appointment   或   搜索出错


@app.route('/api/employee/appointment/modify/<int:id>',methods = ['POST'])             #  update 传过来的数据是什么样的
@auth.login_required
def employee_appointment_modify(id):
    
    appointment = DBUtil.search({'id':id},'appointment')
    
    appointment_res = request.get_json()

    print(appointment_res)
    print('----------')
    print(id)

    if not appointment:
        return status(404)
    else:
        success = DBUtil.modify({'id':id},appointment_res,'appointment')       # key / data / table
        if not success:
            return status(403,'update fails')

    return status(201,'update successfully')



@app.route('/api/employee/profile/<int:id>',methods = ['GET'])
@auth.login_required
def employee_profile_get(id):

    #获取用户信息
    current_employee = getEmployee()
    if current_employee['id'] != id:             #避免获得别人的信息
        return status(401)

    profile = DBUtil.search({'id':current_employee['id']},'employee')
    
    if profile:
        return status(200,'get profile successfully',profile)
    else:
        return status(404)

@app.route('/api/employee/profile/modify/<int:id>',methods = ['POST'])
@auth.login_required
def employee_profile_modify(id):

    #获取用户信息
    current_employee = getEmployee()
    if current_employee['id'] != id:             #避免获得别人的信息
        return status(401)

    profile_res = request.get_json()

    profile = DBUtil.search({'id':current_employee['id']},'employee')
    
    if profile:
        success = DBUtil.modify({'id':id},profile_res,'employee')
        if success:
            return status(201,'update profile successfully')
        else:
            return status(403,'update profile fails')
    else:
        return status(404)