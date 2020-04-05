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
    return status(200,'register success')


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