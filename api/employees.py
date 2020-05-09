from core import app, db
from models.models import Employee
from flask import Flask, session, request 
from api.utils import status, auth, getEmployee, generate_token
import time
import api.SqlUtils as DBUtil
import re

###--------------------已完成---------------------------####

@app.route('/api/employee/getinfo',methods=['GET'])
@auth.login_required
def employee_info():
    employee = getEmployee()
    info = {"id":employee.get("id")}
    return status(200,data = info)

@app.route('/api/employee/register', methods=['POST'])
def employee_register():
    
    register_res = request.get_json()     # 获得前端来的json数据,格式应该是 {username：,password：,email:, phone_num:, address:, }

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

    user = DBUtil.search(login_res,'employee')     #返回的是一个数组, [0] 获得第一个

    if not user:
        return status(4103,'error username or password')
    else:
        user_id = user[0].get('id')
        return generate_token(user_id,"employee")


@app.route('/api/employee/logout', methods=['GET'])
@auth.login_required
def employee_logout():
    return status(201,'logout success')


@app.route('/api/employee/appointment/<int:id>',methods = ['GET'])
@auth.login_required
def employee_appointment_get(id):
    
    url = request.url
    para = re.findall(r'([^?&]*?)=',url)
    value = re.findall(r'=([^?&]*)',url)

    inpu = {}
    inpu['index'] = id
    for i in range(0,len(para)):
        inpu[para[i]] = value[i]

    appointments, length  = DBUtil.search(inpu,'appointment')   

    for a in appointments:
        a.pop('_sa_instance_state')

    return_appointment = {}
    return_appointment["total"] = length
    return_appointment["count"] = 0 if appointments==0 else len(appointments)
    return_appointment["index"] = id
    return_appointment["item"] = appointments

    if appointments:
        return status(200,'get appointment successfully',return_appointment)
    else:      
        return status(404)  #如果没有该appointment   或   搜索出错



@app.route('/api/employee/appointment/modify',methods = ['POST']) 
@auth.login_required
def employee_appointment_modify():
    
    appointment_res = request.get_json()

    if not DBUtil.modify({'id':id},appointment_res,'appointment'):                                        
        return status(403,'update fails')
    return status(201,'update successfully')


@app.route('/api/employee/profile',methods = ['GET'])                 #需要查看customer的profile？
@auth.login_required
def employee_profile_get():

    #获取用户信息
    current_employee = getEmployee()

    profile = DBUtil.search({'id':current_employee['id']},'employee')
    profile[0].pop("_sa_instance_state")
    profile[0].pop("password_hash")

    if profile:
        return status(200,'get profile successfully',profile)
    else:
        return status(404)


@app.route('/api/employee/profile/modify',methods = ['POST'])             #需要修改customer的profile？
@auth.login_required
def employee_profile_modify():

    current_employee = getEmployee()

    profile_res = request.get_json()

    profile = DBUtil.search({'id':current_employee['id']},'employee')
    
    if profile:
        success = DBUtil.modify({'id':id},profile_res,'customer')
        if success:
            return status(201,'update profile successfully')
        else:
            return status(403,'update profile fails')
    else:
        return status(404)

@app.route('/api/employee/password/modify',methods = ['POST'])               
@auth.login_required
def employee_password_modify():

    # 获取用户信息
    current_employee = getEmployee()

    password_res = request.get_json()

    key = {'id':current_employee.get('id'),'old_password':password_res.get('old_password')}
    pa = {'password_hash':password_res.get('new_passowrd')}
    success = DBUtil.modify(key,pa,'employee')
    if success:
        return status(201,'update password sucessfully')
    else:
        return status(403,'update password fails')

#创建 
@app.route('/api/employee/operation/create',methods = ['POST'])             
@auth.login_required
def employee_operation_create():
    
    operation_res = request.get_json()

    if DBUtil.insert(operation_res,'operation'):
        return status(201,'create operation success')
    else:
        return status(4103,'failed to create operation')


@app.route('/api/employee/operation/<int:id>',methods = ['GET'])
@auth.login_required
def employee_operation_get(id):
    
    url  = request.url      # request.url: 返回带?，request.base_url返回不带?的

    para = re.findall(r'([^?&]*?)=',url)
    value = re.findall(r'=([^?&]*)',url)

    inpu = {}
    inpu['index'] = id
    for i in range(0,len(para)):
        inpu[para[i]] = value[i]

    operations,length = DBUtil.search(inpu,'operation') 

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
        return status(404)  #如果没有该operation   或   搜索出错

@app.route('/api/employee/operation/modify',methods = ['POST']) 
@auth.login_required
def employee_operation_modify():
    
    operation_res = request.get_json()

    if not DBUtil.modify({'id':operation_res['id']},operation_res,'appointment'):
        return status(403,'update fails')
    return status(201,'update successfully')

# @app.route('api/employee/search/<int:id>',methods=['GET'])
# @auth.login_required
# def employee_search():
#     current_employee = g.employee
#     level = g.employee.get('level')
#     if level = "administrator":
#         return status(404,'you have no rights')
#     else:
#         employees = DBUtil.search({'index':id},'employee')
#         e = {}
