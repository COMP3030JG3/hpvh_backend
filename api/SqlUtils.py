import json

from core import db
from models.models import Customer, Employee, Appointment, Answer, Operation, Question


# def search(key,table):
    # table = table.lower()
    # if table == "customer":
    #
    # elif table == "employee":
    #
    # elif table == "appointment":
    #
    # elif table == "answer":
    #
    # elif table == "question":
    #
    # elif table == "answer":
    #
    # elif table == "operation":

def insert(data,table):
    try:
        data=json.load(data)
        table=table.lower()
        if table=="customer":
            db.session.add(Customer(**data))
        elif table=="employee":
            db.session.add(Employee(**data))
        elif table == "appointment":
            db.session.add(Appointment(**data))
        elif table == "answer":
            db.session.add(Answer(**data))
        elif table == "question":
            db.session.add(Question(**data))
        elif table == "answer":
            db.session.add(Answer(**data))
        elif table == "operation":
            db.session.add(Operation(**data))
        db.session.commit()
        return 1
    except BaseException:
        return 0