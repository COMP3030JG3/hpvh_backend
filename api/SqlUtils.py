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
            key["appointment_date"] = datetime.datetime.fromtimestamp(key["appointment_date"])
            if key.get("date") is not None:
                key["date"] = datetime.datetime.fromtimestamp(key["date"])

            d = {}
            d["appointment_date"] = key["appointment_date"]
            appointments = Appointment.query.filter_by(**key).all()
            r=[]
            for appointment in appointments:
                temp = appointment.__dict__

                temp["appointment_date"] = temp["appointment_date"].timestamp()
                temp["date"] = temp["date"].timestamp()
                if temp.get("pet_image_path") is not None:
                    temp["pet_image_path"]=mp.imread(temp["pet_image_path"])

                r.append(temp)
            # if index is None:
            #     return sorted(r,key=lambda item:item[orderBy],reverse=True),len(r)
            # else:
            return sorted(r[(index-1)*15:index*15],key=lambda item:item[orderBy],reverse=True),len(r)
        elif table == "answer":
            # preprocessing
            if key.get("content") is not None:
                content = key.pop("content")
            else:
                content = None
            if key.get("date") is not None:
                key["date"] = datetime.datetime.fromtimestamp(key["date"])

            if content is not None:
                answers = Answer.query.filter_by(**key).filter(Answer.content.like("%" + content + "%")).all()
            else:
                answers = Answer.query.filter_by(**key).all()
            for answer in answers:
                answer_dict = answer.__dict__
                answer_dict["date"] = answer_dict["date"].timestamp()
                if answer.customer_id is not None:
                    answer_dict.update({"user_type":"customer"})
                    answer_dict.update({"username":answer.customer_answerer.__dict__.get("username")})
                    answer_dict.update({"user_id":answer_dict.pop("customer_id")})
                elif answer.employee_id is not None:
                    answer_dict.update({"user_type": "employee"})
                    answer_dict.update({"username":answer.employee_answerer.__dict__.get("username")})
                    answer_dict.update({"user_id": answer_dict.pop("employee_id")})
                r.append(answer_dict)
            return r[(index-1)*15:index*15],len(r)
        elif table == "question":
            # preprocessing
            if key.get("content") is not None:
                content = key.pop("content")
            else:
                content = None
            if key.get("date") is not None:
                key["date"] = datetime.datetime.fromtimestamp(key["date"])

            if content is not None:
                questions = Question.query.filter_by(**key).filter(Question.content.like("%" + content + "%")).all()
            else:
                questions = Question.query.filter_by(**key).all()
            for question in questions:
                question_dict = question.__dict__

                question_dict["date"] = question_dict["date"].timestamp()
                question_dict.update({"user_type":"customer"})
                question_dict.update({"username":question.questioner.__dict__.get("username")})
                question_dict.update({"user_id":question_dict.get("questioner_id")})

                r.append(question_dict)
            return r[(index-1)*15:index*15],len(r)
        elif table == "operation":
            # preprocessing
            if key.get("surgery_begin_time") is not None:
                key["surgery_begin_time"] = datetime.datetime.fromtimestamp(key["surgery_begin_time"])
            if key.get("release_time") is not None:
                key["release_time"] = datetime.datetime.fromtimestamp(key["release_time"])
            operations = Operation.query.filter_by(**key).all()

            for operation in operations:
                operation_dict = operation.__dict__
                operation_dict["surgery_begin_time"] = operation_dict["surgery_begin_time"].timestamp()
                operation_dict["release_time"] = operation_dict["release_time"].timestamp()
                r.append(operation_dict)
            return r
        elif table == "pet":
            r = Pet.query.filter_by(**key).all()
        else:
            return 0
        return to_dict(r)[(index-1)*15:index*15],len(r)
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
                temp["appointment_date"] = temp["appointment_date"].timestamp()
                temp["date"] = temp["date"].timestamp()
                temp["pet_image_path"] = mp.imread(temp["pet_image_path"])
                r.append(temp)
            return r
        elif table == "answer":
            answers = Answer.query.all()
            for answer in answers:
                answer_dict = answer.__dict__
                answer_dict["date"] = answer_dict["date"].timestamp()
                if answer.customer_id is not None:
                    answer_dict.update({"user_type": "customer"})
                    answer_dict.update({"username": answer.customer_answerer.__dict__.get("username")})
                    answer_dict.update({"user_id": answer_dict.pop("customer_id")})
                elif answer.employee_id is not None:
                    answer_dict.update({"user_type": "employee"})
                    answer_dict.update({"username": answer.employee_answerer.__dict__.get("username")})
                    answer_dict.update({"user_id": answer_dict.pop("employee_id")})
                r.append(answer_dict)
            return r
        elif table == "question":
            questions = Question.query.all()
            for question in questions:
                question_dict = question.__dict__
                question_dict["date"] = question_dict["date"].timestamp()
                question_dict.update({"user_type": "customer"})
                question_dict.update({"username": question.questioner.__dict__.get("username")})
                question_dict.update({"user_id": question_dict.get("questioner_id")})
                r.append(question_dict)
            return r
        elif table == "operation":
            operations = Operation.query.all()
            for operation in operations:
                operation_dict = operation.__dict__
                operation_dict["surgery_begin_time"] = operation_dict["surgery_begin_time"].timestamp()
                operation_dict["release_time"] = operation_dict["release_time"].timestamp()
                r.append(operation_dict)
            return r
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
            # preprocessing
            data["appointment_date"] = datetime.datetime.fromtimestamp(data["appointment_date"])
            if data.get("date") is not None:
                data["date"] = datetime.datetime.fromtimestamp(data["date"])

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
            # preprocessing
            user_id = data.pop("user_id")
            user_type = data.pop("user_type")
            if user_type.lower() == "customer":
                data.update({"customer_id":user_id})
            else:
                data.update({"employee_id": user_id})
            if data.get("date") is not None:
                data["date"] = datetime.datetime.fromtimestamp(data["date"])

            db.session.add(Answer(**data))
        elif table == "question":
            # preprocessing
            if data.get("date") is not None:
                data["date"] = datetime.datetime.fromtimestamp(data["date"])

            db.session.add(Question(**data))
        elif table == "operation":
            data["surgery_begin_time"] = datetime.datetime.fromtimestamp(data["surgery_begin_time"])
            data["release_time"] = datetime.datetime.fromtimestamp(data["release_time"])
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
            # preprocessing key
            if key.get("appointment_date") is not None:
                key["appointment_date"] = datetime.datetime.fromtimestamp(key["appointment_date"])
            if key.get("date") is not None:
                key["date"] = datetime.datetime.fromtimestamp(key["date"])

            # preprocessing data
            if data.get("appointment_date") is not None:
                data["appointment_date"] = datetime.datetime.fromtimestamp(data["appointment_date"])
            if data.get("date") is not None:
                data["date"] = datetime.datetime.fromtimestamp(data["date"])
            if data.get("pet_image_path") is not None:
                pet_image_path = Appointment.query.filter_by(**key).first().pet_image_path
                os.remove(pet_image_path)
                data["pet_image_path"].save(pet_image_path)
                data.pop("pet_image_path")

            Appointment.query.filter_by(**key).update(data)
        elif table == "answer":
            # preprocessing key
            if key.get("date") is not None:
                key["date"] = datetime.datetime.fromtimestamp(key["date"])

            # preprocessing data
            if data.get("date") is not None:
                data["date"] = datetime.datetime.fromtimestamp(data["date"])

            Answer.query.filter_by(**key).update(data)
        elif table == "question":
            # preprocessing key
            if key.get("date") is not None:
                key["date"] = datetime.datetime.fromtimestamp(key["date"])

            # preprocessing data
            if data.get("date") is not None:
                data["date"] = datetime.datetime.fromtimestamp(data["date"])

            Question.query.filter_by(**key).update(data)
        elif table == "operation":
            # preprocessing key
            if key.get("surgery_begin_time") is not None:
                key["surgery_begin_time"] = datetime.datetime.fromtimestamp(key["surgery_begin_time"])
            if key.get("release_time") is not None:
                key["release_time"] = datetime.datetime.fromtimestamp(key["release_time"])

            # preprocessing data
            if data.get("surgery_begin_time") is not None:
                data["surgery_begin_time"] = datetime.datetime.fromtimestamp(data["surgery_begin_time"])
            if data.get("release_time") is not None:
                data["release_time"] = datetime.datetime.fromtimestamp(data["release_time"])

            Operation.query.filter_by(**key).update(data)
        else:
            return 0
        db.session.commit()
        return 1
    except BaseException:
        traceback.print_exc()
        return 0

def searchTimeSpan(key,table):#The key format should be {"column":"...","start":datetime.datetime(yaer,month,day),"end":datetime.datetime(yaer,month,day)}
    # only support search time span for appointment, question ,answer ,operation
    try:
        # preprocessing
        if key.get("index") is not None:
            index = key.pop("index")
        else:
            index = 1
        if key.get("orderBy") is not None:
            orderBy = key.pop("orderBy")
        else:
            orderBy = "appointment_date"
        key["start"]=datetime.datetime.fromtimestamp(key["start"])
        key["end"] = datetime.datetime.fromtimestamp(key["end"])

        table = table.lower()
        r=[]
        if table == "appointment":
            appointments=Appointment.query.filter(getattr(Appointment,key["column"]) >= key["start"]).filter(getattr(Appointment,key["column"]) <= key["end"])
            for appointment in appointments:
                temp = appointment.__dict__

                temp["appointment_date"] = temp["appointment_date"].timestamp()
                temp["date"] = temp["date"].timestamp()
                if temp.get("pet_image_path") is not None:
                    temp["pet_image_path"]=mp.imread(temp["pet_image_path"])

                r.append(temp)
            return sorted(r[(index - 1) * 15:index * 15], key=lambda item: item[orderBy], reverse=True)
        elif table == "answer":
            answers=Answer.query.filter(getattr(Answer,key["column"]) >= key["start"]).filter(getattr(Answer,key["column"]) <= key["end"])
            for answer in answers:
                answer_dict = answer.__dict__
                answer_dict["date"] = answer_dict["date"].timestamp()
                if answer.customer_id is not None:
                    answer_dict.update({"user_type":"customer"})
                    answer_dict.update({"username":answer.customer_answerer.__dict__.get("username")})
                    answer_dict.update({"user_id":answer_dict.pop("customer_id")})
                elif answer.employee_id is not None:
                    answer_dict.update({"user_type": "employee"})
                    answer_dict.update({"username":answer.employee_answerer.__dict__.get("username")})
                    answer_dict.update({"user_id": answer_dict.pop("employee_id")})
                r.append(answer_dict)
        elif table == "question":
            questions=Question.query.filter(getattr(Question,key["column"]) >= key["start"]).filter(getattr(Question,key["column"]) <= key["end"])
            for question in questions:
                question_dict = question.__dict__

                question_dict["date"] = question_dict["date"].timestamp()
                question_dict.update({"user_type":"customer"})
                question_dict.update({"username":question.questioner.__dict__.get("username")})
                question_dict.update({"user_id":question_dict.get("questioner_id")})

                r.append(question_dict)
        elif table == "operation":
            operations=Operation.query.filter(getattr(Operation,key["column"]) >= key["start"]).filter(getattr(Operation,key["column"]) <= key["end"])
            for operation in operations:
                operation_dict = operation.__dict__
                operation_dict["surgery_begin_time"] = operation_dict["surgery_begin_time"].timestamp()
                operation_dict["release_time"] = operation_dict["release_time"].timestamp()
                r.append(operation_dict)
        else:
            return 0
        return r[(index-1)*15:index*15]
    except BaseException:
        traceback.print_exc()
        return 0



if __name__ == '__main__':
    print(IMAGE_DIR)