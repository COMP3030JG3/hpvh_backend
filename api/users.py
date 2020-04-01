from core import app, db
from models.models import User
from flask import Flask, session, request
from api.utils import status, user_login_required
import time


@app.route('/api/user/login', methods=['POST'])
def user_login():
    login_res = request.get_json()

    username = login_res.get('username')
    password = login_res.get('password')

    if username == None or password == None:
        return status(4103,"Error parament")

    user = User.query.filter_by(username=username).first()
    if user.validate_password(password):
        session["user_session"] = username
    else:
        return status(4103,'error username or password')
    
    return status(200,'login success',user.to_dict())


@app.route('/api/user/logout', methods=['GET'])
@user_login_required
def user_logout():
    session.pop('user_session')
    return status(200,'logout success')

@app.route('/api/users/getinfo', methods=['GET'])
@user_login_required
def user_getinfo():

    user = User.query.filter_by(username=session.get('user_session')).first()
    return status(200,'get user data success',user.to_dict())

@app.route('/api/users/register', methods=['POST'])
def user_register():
    
    register_res = request.get_json()

    if User.query.filter_by(username=register_res['username']).first():
        return status(4103,'exist username')
    else:
        register_res['created_time'] = int(time.time())

        user = User(register_res)
        db.session.add(user)
        db.session.commit()
    return status(200,'register success',user.to_dict())