from core import db
from datetime import datetime


# Reference code 5-14 from lecture 11
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    fullname = db.Column(db.String(64), index=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(120), index=True, unique=True)
    phone_number = db.Column(db.String(11),index=True,unique=True)
    address = db.Column(db.String(120))

    appointments = db.relationship('Appointment', backref='customer', lazy='dynamic')
    questions = db.relationship('Question',backref='questioner',lazy='dynamic')
    answers = db.relationship('Answer', backref='answerer', lazy='dynamic')
    operations = db.relationship('Operation',backref='owner',lazy='dynamic')

    def __repr__(self):
        return '<Customer {}>'.format(self.username)

    def to_dict(self):
        return self.__dict__
        # return {"id":self.id,
        #         "username":self.username,
        #         "fullname":self.fullname,
        #         "password_hash":self.password_hash,
        #         "email":self.email,
        #         "phone_number":self.phone_number,
        #         "address":self.address}

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    answers = db.relationship('Answer',backref='answerer',lazy='dynamic')

    def __repr__(self):
        return '<Employee {}>'.format(self.username)

    def to_dict(self):
        return self.__dict__
        # return {"id":self.id,
        #         "username":self.username,
        #         "password_hash":self.password_hash}


class Appointment(db.Model):#id is not primary key, do not have primary key in this table
    id = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    pet_name = db.Column(db.String(64))
    pet_gender = db.Column(db.String(10),index=True)
    pet_image_path = db.Column(db.String(500))
    species = db.Column(db.String(10),index=True)
    address = db.Column(db.String(15),index=True)
    description = db.Column(db.String(5000))
    appointment_type = db.Column(db.String(30))
    appointment_status = db.Column(db.String(30))
    diagnosis = db.Column(db.String(5000))
    needOperation = db.Column(db.Boolean)
    appointment_date=db.Column(db.DateTime, index=True)
    date = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    operation = db.relationship('Operation', backref='appointment', lazy='dynamic')

    __table_args__=(db.PrimaryKeyConstraint("id","appointment_date",name="appointment_registration"),)

    def __repr__(self):
        return '<Appointment {}>'.format(self.id)

    def to_dict(self):
        return self.__dict__
        # return {"id":self.id,
        #         "customer_id":self.customer_id,
        #         "pet_name":self.pet_name,
        #         "pet_gender":self.pet_gender,
        #         "pet_image_Path":self.pet_image_Path,
        #         "species":self.species,
        #         "address":self.address,
        #         "description":self.description,
        #         "appointment_type":self.appointment_type,
        #         "appointment_status":self.appointment_status,
        #         "diagnosis":self.diagnosis,
        #         "needOperation":self.needOperation,
        #         "appointment_date":self.appointment_date,
        #         "date":self.date}

class Question(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    content = db.Column(db.String(500))
    questioner_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    date = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    answers = db.relationship('Answer',backref='question',lazy='dynamic')

    def __repr__(self):
        return '<Question: {}>'.format(self.content)

    def to_dict(self):
        return self.__dict__
        # return {"id":self.id,
        #         "content":self.content,
        #         "questioner_id":self.questioner_id,
        #         "date":self.date}

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    unread = db.Column(db.Boolean,default = False)

    def __repr__(self):
        return '<Answer: {}>'.format(self.content)

    def to_dict(self):
        return self.__dict__
        # return {"id":self.id,
        #         "content":self.content,
        #         "answerer_id":self.answerer_id,
        #         "date":self.date,
        #         "question_id":self.question_id,
        #         "unread":self.unread}

class Operation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    pet_name = db.Column(db.String(64))
    pet_detail =  db.Column(db.String(500))
    operation_plan_path = db.Column(db.String(500))
    surgery_cost = db.Column(db.Integer)
    surgery_begin_time = db.Column(db.DateTime, index=True)
    livin_duration = db.Column(db.Integer)
    release_time = db.Column(db.DateTime, index=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'))

    def to_dict(self):
        return self.__dict__
        # return {"id":self.id,
        #         "customer_id":self.customer_id,
        #         "pet_name":self.pet_name,
        #         "pet_detail":self.pet_detail,
        #         "operation_plan_path":self.operation_plan_path,
        #         "surgery_cost":self.surgery_cost,
        #         "surgery_begin_time": self.surgery_begin_time,
        #         "livin_duration": self.livin_duration,
        #         "release_time": self.release_time}




