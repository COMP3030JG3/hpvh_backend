from core import app
from flask import Flask, send_file, jsonify, session
import functools


def user_login_required(func):
    @functools.wraps(func)
    def inner(*args,**kwargs):
        if session.get('user_session'):
            return func(*args,**kwargs)
        else:
            return status(401,'user not login')
    return inner


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