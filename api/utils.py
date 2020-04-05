from core import app
from flask import Flask, send_file, jsonify, session, g
import api.SqlUtils as DBUtil
from core.config import Config
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from flask_httpauth import HTTPTokenAuth   #要pip install flask_httpauth
auth = HTTPTokenAuth()

def getCustomer():
    return g.customer

def getEmployee():
    return g.employee

@auth.verify_token        # reference ：https://blog.csdn.net/ousuixin/article/details/94053454
def verify_token(token):
    g.customer = None                          
    g.employee = None
    s = Serializer(Config.SECRET_KEY)
    try:
        data = s.loads(token)
    except SignatureExpired:
        # token正确但是过期了
        return False
    except BadSignature:
        # token错误
        return False
    user_id = data["user_id"]
    identify = data["identify"]
    if user_id:
        if identify == "customer":
            g.customer = DBUtil.search({"id":user_id},identify)[0]
        else:
            g.employee = DBUtil.search({"id":user_id},identify)[0]
        return True
    return False
    
def generate_token(user_id,identify):
    expiration = 3600           #  3600s = 一小时
    serializer = Serializer(Config.SECRET_KEY,expires_in=expiration) 
    token = serializer.dumps({"user_id":user_id,"identify":identify}).decode("utf-8")
    return jsonify({
                    "code": 200,
                    "msg": "Login success",
                    "token":token,
                })

@auth.error_handler
def error_handler():
    return jsonify({ "code":401, 
                     "msg":'Unauthorized Access' 
                })

def status(code, msg=None, data={}):
    error = str(code)[0] == '4'
    codes = {
        code: {'code': code,'error' if error else 'data': data,'error' if error else 'message': msg},
        200: {'code': 200, 'message': msg or 'success', 'data': data},
        201: {'code': 201, 'message': msg or 'created'},
        204: {'code': 204, 'message': msg or 'deleted'},
        400: {'code': 400, 'error': msg or 'invalid request'},
        401: {'code': 401, 'error': msg or 'unauthorized'},
        403: {'code': 403, 'error': msg or 'forbidden'},
        404: {'code': 404, 'error': msg or 'not found'}  
    }
    return jsonify(codes.get(code))