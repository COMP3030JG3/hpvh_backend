import os
import matplotlib.image as mp
import traceback
from core import db
from models.models import Customer, Employee, Appointment, Answer, Operation, Question
from werkzeug.security import generate_password_hash,check_password_hash

APPOINTMENT_LIMIT=3

# get path config
temp=os.path.dirname(__file__).split("/")
temp.pop()
IMAGE_DIR="/".join(temp) + "/uploaded_image"

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
        # preprocessing
        table = table.lower()
        if key.get("index") is not None:
            index = key.pop("index")
        else:
            index = None
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
            appointments = Appointment.query.filter_by(**key).all()
            r=[]
            for appointment in appointments:
                temp = appointment.__dict__
                if temp.get("pet_image_path") is not None:
                    temp["pet_image_path"]=mp.imread(temp["pet_image_path"])
                r.append(temp)
            if index is None:
                return r,len(r)
            else:
                return r[(index-1)*15:index*15],len(r)
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
            appointments = Appointment.query.all()
            for appointment in appointments:
                temp = appointment.__dict__
                temp["pet_image_path"] = mp.imread(temp["pet_image_path"])
                r.append(temp)
            return r
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

def insert(data,table):#data is a dict object,
    # constraints:appointment must be insert with appointment_date
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
            appointments=Appointment.query.filter_by(**d).all()
            if len(appointments) != 0:
                maxId=len(appointments)
                # print(maxId)
                if maxId < APPOINTMENT_LIMIT:
                    data["id"] = maxId + 1
                    if data.get("pet_image_path") is not None:
                        data["pet_image_path"].save(IMAGE_DIR + "/pet_image_path/" + str(data["id"]) + ".jpg")
                        # mp.imsave(IMAGE_DIR + "/pet_image_path/" + str(data["id"]) + ".jpg",data["pet_image_path"])
                        data["pet_image_path"] = IMAGE_DIR + "/pet_image_path/" + str(data["id"]) + ".jpg"
                    db.session.add(Appointment(**data))
                else:
                    return 0
            else:
                db.session.add(Appointment(id=1,**data))
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
            for appointment in items:
                os.remove(appointment.pet_image_path)
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

def searchTimeSpan(key,table):#The key format should be {"column":"...","start":datetime.datetime(yaer,month,day),"end":datetime.datetime(yaer,month,day)}
    try:
        table = table.lower()
        r=[]
        if table == "customer":
            r=Customer.query.filter(getattr(Customer,key["column"]) >= key["start"]).filter(getattr(Customer,key["column"]) <= key["end"])
        elif table == "employee":
            r=Employee.query.filter(getattr(Employee,key["column"]) >= key["start"]).filter(getattr(Employee,key["column"]) <= key["end"])
        elif table == "appointment":
            r=Appointment.query.filter(getattr(Appointment,key["column"]) >= key["start"]).filter(getattr(Appointment,key["column"]) <= key["end"])
        elif table == "answer":
            r=Answer.query.filter(getattr(Answer,key["column"]) >= key["start"]).filter(getattr(Answer,key["column"]) <= key["end"])
        elif table == "question":
            r=Question.query.filter(getattr(Question,key["column"]) >= key["start"]).filter(getattr(Question,key["column"]) <= key["end"])
        elif table == "operation":
            r=Operation.query.filter(getattr(Operation,key["column"]) >= key["start"]).filter(getattr(Operation,key["column"]) <= key["end"])
        else:
            return 0
        return to_dict(r)
    except BaseException:
        traceback.print_exc()
        return 0

if __name__ == '__main__':
    print(IMAGE_DIR)