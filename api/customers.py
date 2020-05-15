from core import app, db
from models.models import Customer
from flask import Flask, session, request
from api.utils import status, auth, generate_token, getCustomer
import time
import api.SqlUtils as DBUtil
import re
from flask import make_response

import io
from PIL import Image, ImageFont, ImageDraw, ImageFilter
import random


@app.route('/api/customer/register', methods=['POST'])
def user_register():

    # 避免瞎注册  正则表达式
    # 获得前端来的json数据,格式应该是 {username：,password：,email:, phone_num:, address:, }
    register_res = request.get_json()
    username = {"username": register_res.get("username")}  # 提取有用信息(username)

    # 验证码测试
    if 'captcha' not in register_res:
        return status(4103, 'No verification code')

    test = register_res.pop('captcha')
    if test.lower() != session['image'].lower():
        return status(4103, 'Incorrect verification code')

    if DBUtil.search(username, "customer"):
        return status(4103, 'exist username')
    else:
        return_status = DBUtil.insert(register_res, "customer")
        if return_status == 0:  # 插入失败
            return status(4103, 'data insertion failure')
    return status(201, 'register success')


@app.route('/api/customer/login', methods=['POST'])
def user_login():

    # get_json获得字典  格式{username：,password：}       名字尚未统一, password还是password_hash
    login_res = request.get_json()

    username = login_res.get('username')
    password = login_res.get('password_hash')

    customer = {"username": username, "password_hash": password}

    user = DBUtil.search(customer, 'customer')  # 返回的是一个数组, [0] 获得第一个

    if not user:
        return status(4103, 'error username or password')
    else:
        user_id = user[0].get('id')
        return generate_token(user_id, "customer")


@app.route('/api/customer/appointment/create', methods=['POST'])
@auth.login_required
def appointment_create():

    # # 获得预约信息
    appointment_res = request.get_json()

    # 获得 customer 信息
    current_customer = getCustomer()
    customer_id = current_customer.get('id')

    pets = {}
    pets["owner_id"] = customer_id

    pets["pet_name"] = appointment_res.get("pet_name")
    pets["pet_gender"] = appointment_res.get("pet_gender")
    pets["pet_species"] = appointment_res.get("species")

    succusse = DBUtil.search(pets, "pet")  # 没找到才插入

    if not succusse:
        DBUtil.insert(pets, "pet")

    # 将customer_id 加入到 字典中
    appointment_res["customer_id"] = customer_id

    if DBUtil.insert(appointment_res, 'appointment'):
        return status(201, 'create appointment success')
    else:
        return status(4103, 'failed to create appointment')


@app.route('/api/customer/logout', methods=['GET'])
@auth.login_required
def user_logout():
    return status(201, 'logout success')


@app.route('/api/customer/pet/<int:id>', methods=['GET'])
@auth.login_required
def get_pets(id):

    current_customer = getCustomer()
    query = {"owner_id": current_customer.get('id'), 'index': id}
    pets, length = DBUtil.search(query, "pet")

    if pets:
        for p in pets:
            p.pop('_sa_instance_state')
        return_data = {}
        return_data["count"] = len(pets)
        return_data['index'] = id
        return_data["item"] = pets
        return_data['total'] = length
        return status(200, 'get pet successfully', return_data)
    else:
        return status(4103, 'fail to get pets')


@app.route('/api/customer/appointment/<int:id>', methods=['GET'])
@auth.login_required
def user_appointment_get(id):  # id是appointment的id

    url = request.url      # request.url: 返回带?，request.base_url返回不带?的

    current_customer = getCustomer()      # 获得用户信息

    para = re.findall(r'([^?&]*?)=', url)
    value = re.findall(r'=([^?&]*)', url)

    inpu = {}
    inpu['index'] = id
    inpu['customer_id'] = current_customer['id']
    # inpu['appointment_date'] = 109821017
    for i in range(0, len(para)):
        inpu[para[i]] = value[i]

    # print(inpu)
    # print("-------------------------------------")
    appointments, length = DBUtil.search(inpu, "appointment")

    if appointments:
        for a in appointments:
            a.pop('_sa_instance_state')
        return_appointment = {}
        return_appointment["total"] = length
        return_appointment["count"] = 0 if appointments == 0 else len(
            appointments)
        return_appointment["index"] = id
        return_appointment["item"] = appointments
        # appointment 是一个数组
        return status(200, 'get appointment successfully', return_appointment)
    else:
        return status(404)  # 如果没有该appointment   或   搜索出错


@app.route('/api/customer/profile', methods=['GET'])
@auth.login_required
def user_profile_get():

    # 获取用户信息
    current_customer = getCustomer()
    profile = DBUtil.search({'id': current_customer['id']}, 'customer')

    if profile:
        profile[0].pop("_sa_instance_state")
        profile[0].pop("password_hash")
        return status(200, 'get profile successfully', profile[0])
    else:
        return status(404)


@app.route('/api/customer/profile/modify', methods=['POST'])
@auth.login_required
def user_profile_modify():
    # 获取用户信息
    current_customer = getCustomer()

    profile_res = request.get_json()

    profile = DBUtil.search({'id': current_customer['id']}, 'customer')

    if profile:
        success = DBUtil.modify(
            {'id': current_customer['id']}, profile_res, 'customer')
        if success:
            return status(201, 'update profile successfully')
        else:
            return status(403, 'update profile fails')
    else:
        return status(404)


@app.route('/api/customer/password/modify', methods=['POST'])
@auth.login_required
def user_password_modify():

    # 获取用户信息
    current_customer = getCustomer()

    password_res = request.get_json()

    key = {'id': current_customer.get(
        'id'), 'old_password': password_res.get('old_password')}
    pa = {'password_hash': password_res.get('new_passowrd')}
    success = DBUtil.modify(key, pa, 'customer')
    if success:
        return status(201, 'update password sucessfully')
    else:
        return status(403, 'update password fails')


@app.route('/api/customer/operation/<int:id>', methods=['GET'])
@auth.login_required
def user_operation_get(id):

    url = request.url      # request.url: 返回带?，request.base_url返回不带?的

    # 获得用户信息
    current_customer = getCustomer()

    para = re.findall(r'([^?&]*?)=', url)
    value = re.findall(r'=([^?&]*)', url)

    inpu = {}
    inpu['index'] = id
    inpu['customer_id'] = current_customer.get('id')
    for i in range(0, len(para)):
        inpu[para[i]] = value[i]

    operations, length = DBUtil.search(inpu, 'operation')

    if operations:
        for o in operations:
            o.pop("_sa_instance_state")
        return_operation = {}
        return_operation["total"] = length
        return_operation["count"] = 0 if operations == 0 else len(operations)
        return_operation["index"] = id
        return_operation["item"] = operations

        return status(200, 'get operation successfully', return_operation)
    else:
        return status(404)


# references :  https://blog.51cto.com/12080420/2400408
def validate_picture():
    total = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ012345789'
    # 图片大小 130 x 50
    width = 130
    height = 50
    # 生成一个新图片对象
    im = Image.new('RGB', (width, height), 'white')
    # 设置字体
    font = ImageFont.truetype('CALIFB.TTF', 40)
    # font = ImageFont.load_default().font
    # 创建draw对象
    draw = ImageDraw.Draw(im)
    str1 = ''
    # 输入每一个文字
    for item in range(5):
        text = random.choice(total)
        str1 += text
        draw.text((5+random.randint(4, 7)+20*item, 5 +
                   random.randint(3, 7)), text=text, fill='blue', font=font)
    # 划几根干扰线
    for num in range(8):
        x1 = random.randint(0, width/2)
        y1 = random.randint(0, height/2)
        x2 = random.randint(0, width)
        y2 = random.randint(height/2, height)
        draw.line(((x1, y1), (x2, y2)), fill='black', width=1)

    # 模糊下，加个滤镜
    im = im.filter(ImageFilter.FIND_EDGES)
    return im, str1


@app.route('/api/customer/code', methods=['GET'])
def get_code():
    image, str1 = validate_picture()
    # 讲验证码图片以二进制形式写入内存，防止图片都放在文件夹中，占用磁盘空间
    buf = io.BytesIO()
    image.save(buf, 'jpeg')
    buf_str = buf.getvalue()
    # 把二进制作为response发回前端，并设置头部字段
    response = make_response(buf_str)
    response.headers['Content-Type'] = 'image/gif'
    # 验证码字符串存储在seesion中
    session['image'] = str1
    return response


# appointment 的id
@app.route('/api/appointment/image/<int:id>', methods=['GET'])
def pet_image(id):

    # with open('13690.html1.jpg',"rb") as image:
    #     b=bytes(image.read())
    # print(type(b))
    # response = make_response(b)
    # response.headers['Content-Type'] = 'image/gif'
    # 测试

    # 传给你  appointment  的 primary key id， 返回二进制
    byte = DBUtil.searchImage({"app_primary_key": id}, 'appointment')
    if byte is None:
        return status('403', 'no photos')
    response = make_response(byte)
    response.headers['Content-Type'] = 'image/gif'
    return response


@app.route('/api/customer/image/<int:id>', methods=['GET'])  # customer自己的
def customer_image(id):

    # 传给你  customer id，  返回二进制
    byte = DBUtil.searchImage({"id": id}, 'customer')
    if byte is None:
        return status('403', 'no photos')
    response = make_response(byte)
    response.headers['Content-Type'] = 'image/gif'
    return response

# @app.route('/api/customer/test',methods=['GET'])
# def test():
#     print(session['image'])
#     print(session['image'].lower())
#     return "0"

