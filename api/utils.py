from core import app,db
from flask import Flask, send_file, jsonify, session, g,request
import api.SqlUtils as DBUtil
from core.config import Config
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from flask_httpauth import HTTPTokenAuth   #要pip install flask_httpauth
auth = HTTPTokenAuth()

from models.models import Employee
import time
import api.SqlUtils as DBUtil
import re

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
            g.employee = DBUtil.search({"id":user_id},identify)[0][0]
        return True
    return False
    
def generate_token(user_id,identify):
    expiration = 360000           #  3600s = 一小时
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


@app.route('/api/question/create',methods=['POST'])
@auth.login_required
def question_create():
    question_res = request.get_json()
    question_res['questioner_id'] = g.customer.get('id')
    # {
    #     content:"this is a question",
    # }
    print(question_res)
    success = DBUtil.insert(question_res,"question")
    if success:
        return status(201,"insert question successfully")
    else:
        return status(404)


@app.route('/api/question/<int:id>',methods=['GET'])               
def question_get(id):

    url  = request.url      # request.url: 返回带?，request.base_url返回不带?的

    para = re.findall(r'([^?&]*?)=',url)
    value = re.findall(r'=([^?&]*)',url)

    inpu = {}
    inpu['index'] = id
    for i in range(0,len(para)):
        inpu[para[i]] = value[i]

    questions, length = DBUtil.search(inpu,"question")

    for q in questions:
        q.pop("_sa_instance_state")
        q.pop('questioner')
    print(questions)

    return_data = {}
    return_data["total"] = length
    return_data["count"] = 0 if questions==0 else len(questions)
    return_data["index"] = id
    return_data["item"] = questions


    return status(200,'get operation successfully',return_data)



@app.route('/api/answer/create',methods=['POST'])
@auth.login_required
def answer_create():

    answer_res = request.get_json()
    
    if g.customer:
        answer_res['user_id'] = g.customer.get('id')
        answer_res['user_type'] = 'customer'
    else:
        answer_res['user_type'] = 'employee'
        answer_res['user_id'] = g.employee.get('id')

    # if answer_res.get('user_type') == 'customer':
    #     answer_res['user_id'] = g.customer.get('id')
    # else:
    #     answer_res['user_id'] = g.employee.get('id')

    # {	
    # 	"content":"this is a answer",
    # 	"user_type":"customer",
    # 	"question_id":1
    # }

    success = DBUtil.insert(answer_res,"answer")
    if success:
        return status(201,"insert answer successfully")
    else:
        return status(404)

@app.route('/api/answer/<int:id>',methods=['GET'])      #  question 的 id          返回的格式
def answer_get(id):
    
    url  = request.url      # request.url: 返回带?，request.base_url返回不带?的

    para = re.findall(r'([^?&]*?)=',url)
    value = re.findall(r'=([^?&]*)',url)

    inpu = {}
    inpu['index'] = id
    for i in range(0,len(para)):
        inpu[para[i]] = value[i]

    answers ,length = DBUtil.search(inpu,"answer")

    for a in answers:
        a.pop("_sa_instance_state")
        if "employee_id" in a:
            a.pop("employee_id")
            a.pop('customer_answerer')
        elif "customer_id" in a:
            a.pop("customer_id")
            a.pop("employee_answerer")

    if answers:
        return_answers = {}
        return_answers["total"] = length
        return_answers["count"] = len(answers)
        return_answers["index"] = id
        return_answers['item'] = answers
        
        return status(200,"get answers successfully",return_answers)
    else:
        return status(404)
