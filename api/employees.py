from core import app, db
from models.models import Employee
from flask import Flask, session, request
from api.utils import status, user_login_required
import time


@app.route('/api/employee/login', methods=['POST'])
def employee_login():
    login_res = request.get_json()

    username = login_res.get('username')
    password = login_res.get('password')

    if username == None or password == None:
        return status(4103,"Error parament")

    employee = Employee.query.filter_by(username=username).first()
    if employee.validate_password(password):
        session["user_session"] = username
    else:
        return status(4103,'error username or password')
    
    return status(200,'login success',employee.to_dict())


@app.route('/api/employee/logout', methods=['GET'])
@user_login_required
def employee_logout():
    session.pop('employee_session')
    return status(200,'logout success')

@app.route('/api/employee/getinfo', methods=['GET'])
@user_login_required
def employee_getinfo():

    employee = Employee.query.filter_by(username=session.get('employee_session')).first()
    return status(200,'get employee data success',employee.to_dict())

@app.route('/api/employee/register', methods=['POST'])
def employee_register():
    
    register_res = request.get_json()

    if employee.query.filter_by(username=register_res['username']).first():
        return status(4103,'exist username')
    else:
        register_res['created_time'] = int(time.time())

        employee = Employee(register_res)
        db.session.add(employee)
        db.session.commit()
    return status(200,'register success',employee.to_dict())