## HPVH Appointment System - Frontend

This project is about the back end of the appointment system by using Flask and Sqlalchemy

## Dependencies

- Flask (overall development framework)
- Sqlalchemy (database util)
- Restful (api development norms)

## How to use

### 1.create database (for the first time)
in CMD:
python
from core import db
db.create_all()

### 2.start flask
python main.py