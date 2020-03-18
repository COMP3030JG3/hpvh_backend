from core import db
from datetime import datetime


# Reference code 5-14 from lecture 11
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(120), index=True, unique=True)
    phone_number = db.Column(db.String(11),index=True,unique=True)
    address = db.Column(db.String(120))

    appointments = db.relationship('Appointment', backref='customer', lazy='dynamic')
    questions = db.relationship('Question',backref='questioner',lazy='dynamic')
    operations = db.relationship('Operation',backref='owner',lazy='dynamic')

    def __repr__(self):
        return '<Customer {}>'.format(self.username)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    answers = db.relationship('Answer',backref='answerer',lazy='dynamic')

    def __repr__(self):
        return '<Employee {}>'.format(self.username)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    pet_name = db.Column(db.String(64))
    pet_gender = db.Column(db.String(10),index=True)
    species = db.Column(db.String(10),index=True)
    address = db.Column(db.String(15),index=True)
    description = db.Column(db.String(5000))
    image_Path = db.Column(db.String(500))
    surgery_time = db.Column(db.DateTime, index=True)

    def __repr__(self):
        return '<Appointment {}>'.format(self.id)

class Question(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    content = db.Column(db.String(500))
    questioner_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    date = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    answers = db.relationship('Answer',backref='question',lazy='dynamic')

    def __repr__(self):
        return '<Question: {}>'.format(self.content)

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500))
    answerer_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    unread = db.Column(db.Boolean,default = False)

    def __repr__(self):
        return '<Answer: {}>'.format(self.content)

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






