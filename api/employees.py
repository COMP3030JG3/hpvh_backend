from core import app, db
from models.models import Employee
from flask import Flask, session, request 
from api.utils import status, auth, getEmployee, generate_token
import time
import api.SqlUtils as DBUtil


###--------------------已完成---------------------------####
# 雇员不能随便注册,      所有的modify似乎不需要提供id

@app.route('/api/employee/getinfo',methods=['GET'])
@auth.login_required
def employee_info():
    employee = getEmployee()
    info = {"id":employee.get("id")}
    return status(200,data = info)

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

    user = DBUtil.search(employee,'employee')     #返回的是一个数组, [0] 获得第一个

    if not user:
        return status(4103,'error username or password')
    else:
        user_id = user[0].get('id')
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

    appointments = DBUtil.search(inpu,'appointment')   

    all_appoint = DBUtil.searchAll('appointment')   
    return_appointment = {}
    return_appointment["total"] = 0 if all_appoint==0 else len(all_appoint)
    return_appointment["count"] = 0 if appointments==0 else len(appointments)
    return_appointment["index"] = id
    return_appointment["item"] = appointments
    if appointments:
        return status(200,'get appointment successfully',return_appointment)
    else:      
        return status(404)  #如果没有该appointment   或   搜索出错


# @app.route('/api/employee/appointment/modify/<int:id>',methods = ['POST'])             #  update    (好像不需要id),  POST过来的自动有id,  只传修改的项,还是全部重传？
@app.route('/api/employee/appointment/modify',methods = ['POST']) 
@auth.login_required
# def employee_appointment_modify(id):
def employee_appointment_modify():

    # appointment = DBUtil.search({'id':id},'appointment')
    
    appointment_res = request.get_json()

    # if not appointment:
    #     return status(404)
    # else:
    #     success = DBUtil.modify({'id':id},appointment_res,'appointment')       # key / data / table
    #     if not success:
    #         return status(403,'update fails')

    if not DBUtil.modify({'id':id},appointment_res,'appointment'):                                            # modify是只修改传入的参数,还是全部替换？
        return status(403,'update fails')
    return status(201,'update successfully')


# @app.route('/api/employee/profile/<int:id>',methods = ['GET'])
@app.route('/api/employee/profile',methods = ['GET'])                 #需要查看customer的profile？
@auth.login_required
# def employee_profile_get(id):
def employee_profile_get():

    #获取用户信息
    current_employee = getEmployee()

    profile = DBUtil.search({'id':current_employee['id']},'employee')
    
    if profile:
        return status(200,'get profile successfully',profile)
    else:
        return status(404)

# @app.route('/api/employee/profile/modify/<int:id>',methods = ['POST'])
@app.route('/api/employee/profile/modify',methods = ['POST'])             #需要修改customer的profile？
@auth.login_required
# def employee_profile_modify(id):
def employee_profile_modify():
    #获取用户信息
    # current_employee = getEmployee()

    profile_res = request.get_json()

    # profile = DBUtil.search({'id':current_employee['id']},'employee')
    
    # if profile:
        # success = DBUtil.modify({'id':id},profile_res,'employee')
        # if success:
            # return status(201,'update profile successfully')
        # else:
            # return status(403,'update profile fails')
    # else:
        # return status(404)

    if not DBUtil.modify({'id':id},profile_res,'employee'):
        return status(201,'update profile fails')
    return status(201,'update profile successfully')

#创建 
@app.route('/api/employee/operation/create',methods = ['POST'])                 #传进来的operation的格式？？？？？？
@auth.login_required
def employee_operation_create():
    
        # # 获得预约信息
    operation_res = request.get_json()

    # 对operation的操作

    if DBUtil.insert(operation_res,'operation'):
        return status(200,'create operation success')
    else:
        return status(4103,'failed to create operation')


@app.route('/api/employee/operation/<int:id>',methods = ['GET'])
@auth.login_required
def employee_operation_get(id):
    
    if id == 0:   #0 表示获得所有
        operations = DBUtil.searchAll('operation')        
    else:         #非0  获得某个operation
        operations = DBUtil.search({'id':id},'operation')
    if operations:
        return status(200,'get operations successfully',operations)
    else:      
        return status(404)  #如果没有该operations   或   搜索出错


# @app.route('/api/employee/operation/modify/<int:id>',methods = ['POST'])             #  update  (好像不需要id)
@app.route('/api/employee/operation/modify',methods = ['POST']) 
@auth.login_required
# def employee_operation_modify(id):
def employee_operation_modify():

    # operation = DBUtil.search({'id':id},'operation')
    
    operation_res = request.get_json()

    # if not operation:
    #     return status(404)
    # else:
    #     # success = DBUtil.modify({'id':operation_res['id']},operation_res,'appointment')   # key / data / table
    #     if not success:
    #         return status(403,'update fails')

    if not DBUtil.modify({'id':operation_res['id']},operation_res,'appointment'):
        return status(403,'update fails')
    return status(201,'update successfully')