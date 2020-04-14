import json
import traceback
from core import db
from models.models import Customer, Employee, Appointment, Answer, Operation, Question
from werkzeug.security import generate_password_hash,check_password_hash

APPOINTMENT_LIMIT=3

def to_dict(list1):#util function
    r = []
    for item in list1:
        r.append(item.to_dict())

    if len(r)==0:
        return None
    else:
        return r

def search(key,table):#key is a dict variable used to search required row in target table
    try:
        # key = json.loads(key)
        table = table.lower()
        # if (table == "customer" or table == "employee") and ("password_hash" in key):
        #     if check_password_hash(,key["password_hash"])
        r=[]
        if table == "customer":
            if "password_hash" in key:
                password=key.pop("password_hash")
                r = Customer.query.filter_by(**key).first()
                if not check_password_hash(r.password_hash, password):
                    return 0
            r=Customer.query.filter_by(**key).all()
        elif table == "employee":
            if "password_hash" in key:
                password=key.pop("password_hash")
                r = Employee.query.filter_by(**key).first()
                if not check_password_hash(r.password_hash, password):
                    return 0
            r = Employee.query.filter_by(**key).all()
        elif table == "appointment":
            r = Appointment.query.filter_by(**key).all()
        elif table == "answer":
            r = Answer.query.filter_by(**key).all()
        elif table == "question":
            r = Question.query.filter_by(**key).all()
        elif table == "operation":
            r = Operation.query.filter_by(**key).all()
        else:
            return 0
        return to_dict(r)
    except BaseException:
        traceback.print_exc()
        return 0

def searchAll(table):#select * from table
    try:
        table = table.lower()
        r=[]
        if table == "customer":
            r=Customer.query.all()
        elif table == "employee":
            r = Employee.query.all()
        elif table == "appointment":
            r = Appointment.query.all()
        elif table == "answer":
            r = Answer.query.all()
        elif table == "question":
            r = Question.query.all()
        elif table == "operation":
            r = Operation.query.all()
        else:
            return 0
        return to_dict(r)
    except BaseException:
        traceback.print_exc()
        return 0

def insert(data,table):#data is a dict object
    try:
        # data=json.loads(data)
        table=table.lower()
        if table=="customer":
            if "password_hash" in data:
                password_hash = generate_password_hash(str(data["password_hash"]))
                data["password_hash"]= password_hash
            db.session.add(Customer(**data))
        elif table=="employee":
            if "password_hash" in data:
                password_hash = generate_password_hash(str(data["password_hash"]))
                data["password_hash"]= password_hash
            db.session.add(Employee(**data))
        elif table == "appointment":
            d={}
            d["appointment_date"]=data["appointment_date"]
            appointments=search(d,"appointment")
            if appointments is not None:
                maxId=len(appointments)
                # print(maxId)
                if maxId < APPOINTMENT_LIMIT:
                    data["id"] = maxId + 1
                    db.session.add(Appointment(**data))
                else:
                    return 0
            else:
                db.session.add(Appointment(**data))
        elif table == "answer":
            db.session.add(Answer(**data))
        elif table == "question":
            db.session.add(Question(**data))
        elif table == "operation":
            db.session.add(Operation(**data))
        else:
            return 0
        db.session.commit()
        return 1
    except BaseException:
        traceback.print_exc()
        return 0

def delete(key,table):#key is a dict variable used to search required row in target table
    try:
        # key = json.loads(key)
        table = table.lower()
        items=[]
        if table == "customer":
            items=Customer.query.filter_by(**key).all()
        elif table == "employee":
            items = Employee.query.filter_by(**key).all()
        elif table == "appointment":
            items = Appointment.query.filter_by(**key).all()
        elif table == "answer":
            items = Answer.query.filter_by(**key).all()
        elif table == "question":
            items = Question.query.filter_by(**key).all()
        elif table == "operation":
            items = Operation.query.filter_by(**key).all()
        else:
            return 0
        for item in items:
            db.session.delete(item)
        db.session.commit()
        return 1
    except BaseException:
        traceback.print_exc()
        return 0

def modify(key,data,table):#key is a dict variable used to search required row in target table,data is the modifed data
    try:
        # key = json.loads(key)
        # data = json.loads(data)
        table = table.lower()
        if table == "customer":
            Customer.query.filter_by(**key).update(data)
        elif table == "employee":
            Employee.query.filter_by(**key).update(data)
        elif table == "appointment":
            Appointment.query.filter_by(**key).update(data)
        elif table == "answer":
            Answer.query.filter_by(**key).update(data)
        elif table == "question":
            Question.query.filter_by(**key).update(data)
        elif table == "operation":
            Operation.query.filter_by(**key).update(data)
        else:
            return 0
        db.session.commit()
        return 1
    except BaseException:
        traceback.print_exc()
        return 0