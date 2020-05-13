from core import app, db
from models.models import Employee
from flask import Flask, session, request 
from api.utils import status, auth, getEmployee, generate_token
import time
import api.SqlUtils as DBUtil
import re

###--------------------已完成---------------------------####

# @app.route('/api/employee/getinfo',methods=['GET'])
# @auth.login_required
# def employee_info():
#     employee = getEmployee()
#     info = {"id":employee.get("id")}
#     return status(200,data = info)

@app.route('/api/employee/register', methods=['POST'])
def employee_register():
    
    register_res = request.get_json()     # 获得前端来的json数据,格式应该是 {username：,password：,email:, phone_num:, address:, }

    username = {"username":register_res.get("username")}   #提取有用信息(username)

    if DBUtil.search(username,"employee")[0]:
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
        user_id = user[0][0].get('id')
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

    if appointments:
        for a in appointments:
            a.pop('_sa_instance_state')

        return_appointment = {}
        return_appointment["total"] = length
        return_appointment["count"] = 0 if appointments==0 else len(appointments)
        return_appointment["index"] = id
        return_appointment["item"] = appointments

        return status(200,'get appointment successfully',return_appointment)
    else:      
        return status(404)  #如果没有该appointment   或   搜索出错



@app.route('/api/employee/appointment/modify/<int:id>',methods = ['POST']) 
@auth.login_required
def employee_appointment_modify(id):
    
    appointment_res = request.get_json()

    if not DBUtil.modify({'id':id},appointment_res,'appointment'):                                        
        return status(403,'update fails')
    return status(201,'update successfully')


@app.route('/api/employee/profile',methods = ['GET'])                 #需要查看customer的profile？
@auth.login_required
def employee_profile_get():

    #获取用户信息
    current_employee = getEmployee()

    profile = DBUtil.search({'id':current_employee['id']},'employee')[0]

    if profile:
        profile[0].pop("_sa_instance_state")
        profile[0].pop("password_hash")
        return status(200,'get profile successfully',profile)
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

    if 'appointment_id' not in operation_res:
        return status(4103,'must have appointment_id')
    appointment ,length = DBUtil.search({'app_primary_key':operation_res.get('appointment_id')},'appointment')
    if not appointment:
        return status(4103,'wrong appointment_id')
    operation_res['customer_id'] = appointment[0].get('customer_id')

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
    
    if operations:
        
        for o in operations:
            o.pop("_sa_instance_state")

        return_operation = {}
        return_operation["total"] = length
        return_operation["count"] = 0 if operations==0 else len(operations)
        return_operation["index"] = id
        return_operation["item"] = operations
        return status(200,'get operation successfully',return_operation)
    else:      
        return status(404)  #如果没有该operation   或   搜索出错

@app.route('/api/employee/operation/modify/<int:id>',methods = ['POST']) 
@auth.login_required
def employee_operation_modify(id):
    
    operation_res = request.get_json()
    if not DBUtil.modify({'id':id},operation_res,'operation'):
        return status(403,'update fails')
    return status(201,'update successfully')

@app.route('/api/employee/<int:id>',methods=['GET'])
@auth.login_required
def employee_search(id):
    current_employee = getEmployee()
    level = current_employee.get('level')
    if level == "administrator":
        employees,length = DBUtil.search({'index':id},'employee')
        if employees:
            for ee in employees:
                ee.pop("_sa_instance_state")
                ee.pop("password_hash")
            e = {}
            e['total'] = length
            e['count'] =  0 if employees==0 else len(employees)
            e['index'] = id
            e['item'] = employees
            return status(200,'get employees successfully',e)
        else:
            return status(404,'no employees')
    else:
        return status(404,'you have no rights')

@app.route('/api/employee/modify/<int:id>',methods = ['POST'])             #需要修改customer的profile？
@auth.login_required
def employee_profile_modify(id):

    current_employee = getEmployee()
    level = current_employee.get('level')
    if level == "administrator":
        profile_res = request.get_json()

        profile = DBUtil.search({'id':id},'employee')[0]
        if not profile:
            return status(404,'no such employee')
        else:
            success = DBUtil.modify({'id':id},profile_res,'employee')
            if success:
                return status(201,'update profile successfully')
            else:
                return status(403,'update profile fails')
    else:
        return status(404,'you have no rights')

@app.route('/api/employee/add', methods=['POST'])
@auth.login_required
def employee_add():
    
    current_employee = getEmployee()
    level = current_employee.get('level')
    if level == "administrator":

        register_res = request.get_json()     # 获得前端来的json数据,格式应该是 {username：,password：,email:, phone_num:, address:, }
        username = {"username":register_res.get("username")}   #提取有用信息(username)
        if DBUtil.search(username,"employee")[0]:
            return status(4103,'exist username')
        else:
            return_status = DBUtil.insert(register_res,"employee")    
            if return_status == 0:                     #插入失败
                return status(4103,'data insertion failure')
            else:
                return status(201,'register success')
    else:
        return status(404,'you have no rights')





