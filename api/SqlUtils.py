import datetime
import os
import matplotlib.image as mp
import traceback
from core import db
from models.models import Customer, Employee, Appointment, Answer, Operation, Question, Pet
from werkzeug.security import generate_password_hash,check_password_hash

APPOINTMENT_LIMIT=20

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
    # when search for the data in answer and question table, it will return the data with the user binded
    try:
        # preprocessing
        table = table.lower()
        if key.get("index") is not None:
            index = key.pop("index")
        else:
            index = 1
        if key.get("orderBy") is not None:
            orderBy = key.pop("orderBy")
        else:
            orderBy = "appointment_date"

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
            # preprocessing
            key["appointment_date"] = datetime.datetime.strptime(key["appointment_date"], '%Y-%m-%d %H:%M:%S')
            # if key.get("date") is not None:
            #     key["date"] = datetime.datetime.strptime(key["date"], '%Y-%m-%d %H:%M:%S')

            d = {}
            d["appointment_date"] = key["appointment_date"]
            appointments = Appointment.query.filter_by(**key).all()
            r=[]
            for appointment in appointments:
                temp = appointment.__dict__
                if temp.get("pet_image_path") is not None:
                    temp["pet_image_path"]=mp.imread(temp["pet_image_path"])
                r.append(temp)
            # if index is None:
            #     return sorted(r,key=lambda item:item[orderBy],reverse=True),len(r)
            # else:
            return sorted(r[(index-1)*15:index*15],key=lambda item:item[orderBy],reverse=True),len(r)
        elif table == "answer":
            answers = Answer.query.filter_by(**key).all()
            for answer in answers:
                answer_dict = answer.__dict__
                if answer.customer_id is not None:
                    answer_dict.update({"user_type":"customer"})
                    answer_dict.update({"username":answer.customer_answerer.__dict__.get("username")})
                    answer_dict.update({"user_id":answer_dict.pop("customer_id")})
                else:
                    answer_dict.update({"user_type": "employee"})
                    answer_dict.update({"username":answer.employee_answerer.__dict__.get("username")})
                    answer_dict.update({"user_id": answer_dict.pop("employee_id")})
                r.append(answer_dict)
            return r[(index-1)*15:index*15]
        elif table == "question":
            questions = Question.query.filter_by(**key).all()
            for question in questions:
                question_dict = question.__dict__
                question_dict.update({"user_type":"customer"})
                question_dict.update({"username":question.questioner.__dict__.get("username")})
                question_dict.update({"user_id":question_dict.get("questioner_id")})
                r.append(question_dict)
            return r[(index-1)*15:index*15]
        elif table == "operation":
            r = Operation.query.filter_by(**key).all()
        elif table == "pet":
            r = Pet.query.filter_by(**key).all()
        else:
            return 0
        return to_dict(r)[(index-1)*15:index*15]
    except BaseException:
        traceback.print_exc()
        return 0

def searchAll(table):#select * from table
    # when search for the data in answer and question table, it will return the data with the user binded
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
            answers = Answer.query.all()
            for answer in answers:
                answer_dict = answer.__dict__
                if answer.customer_id is not None:
                    answer_dict.update({"user_type": "customer"})
                    answer_dict.update({"username": answer.customer_answerer.__dict__.get("username")})
                    answer_dict.update({"user_id": answer_dict.pop("customer_id")})
                else:
                    answer_dict.update({"user_type": "employee"})
                    answer_dict.update({"username": answer.employee_answerer.__dict__.get("username")})
                    answer_dict.update({"user_id": answer_dict.pop("employee_id")})
                r.append(answer_dict)
            return r
        elif table == "question":
            questions = Question.query.all()
            for question in questions:
                question_dict = question.__dict__
                question_dict.update({"user_type": "customer"})
                question_dict.update({"username": question.questioner.__dict__.get("username")})
                question_dict.update({"user_id": question_dict.get("questioner_id")})
                r.append(question_dict)
            return r
        elif table == "operation":
            r = Operation.query.all()
        elif table == "pet":
            r = Pet.query.all()
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
            # preprocessing, the data application logic passed is not standard
            data["appointment_date"] = datetime.datetime.strptime(data["appointment_date"],'%Y-%m-%d %H:%M:%S')

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
                    db.session.add(Pet(owner_id=data.get("customer_id"),pet_name=data.get("pet_name"),pet_gender=data.get("pet_gender"),pet_species=data.get("species")))
                    db.session.add(Appointment(**data))
                else:
                    return 0
            else:
                db.session.add(
                    Pet(owner_id=data.get("customer_id"), pet_name=data.get("pet_name"), pet_gender=data.get("pet_gender"),
                        pet_species=data.get("species")))
                db.session.add(Appointment(id=1,**data))
        elif table == "answer":
            user_id = data.pop("user_id")
            user_type = data.pop("user_type")
            if user_type.lower() == "customer":
                data.update({"customer_id":user_id})
            else:
                data.update({"employee_id": user_id})
            db.session.add(Answer(**data))
        elif table == "question":
            db.session.add(Question(**data))
        elif table == "operation":
            data["surgery_begin_time"] = datetime.datetime.strptime(data["surgery_begin_time"], '%Y-%m-%d %H:%M:%S')
            data["release_time"] = datetime.datetime.strptime(data["release_time"], '%Y-%m-%d %H:%M:%S')
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
    # only support modify one row at a time
    try:
        # key = json.loads(key)
        # data = json.loads(data)
        table = table.lower()
        if table == "customer":
            if key.get("old_password") is not None:
                old_password = key.pop("old_password")
                if "password_hash" in data:
                    new_password = data.pop("password_hash")
                    if check_password_hash(Customer.query.filter_by(**key).first().password_hash,old_password):
                        data["password_hash"]= generate_password_hash(str(new_password))
            Customer.query.filter_by(**key).update(data)
        elif table == "employee":
            if key.get("old_password") is not None:
                old_password = key.pop("old_password")
                if "password_hash" in data:
                    new_password = data.pop("password_hash")
                    if check_password_hash(Employee.query.filter_by(**key).first().password_hash, old_password):
                        data["password_hash"] = generate_password_hash(str(new_password))
            Employee.query.filter_by(**key).update(data)
        elif table == "appointment":
            if data.get("pet_image_path") is not None:
                pet_image_path = Appointment.query.filter_by(**key).first().pet_image_path
                os.remove(pet_image_path)
                data["pet_image_path"].save(pet_image_path)
                data.pop("pet_image_path")
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