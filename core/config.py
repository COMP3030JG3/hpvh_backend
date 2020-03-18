import os
basedir = os.path.abspath(os.path.dirname(__file__))
print(basedir)
class Config(object):
	# Session encrypt
	SECRET_KEY = 'UCD-2020-COMP3030J-GROUP3'

	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, '../models/database.db')

	SQLALCHEMY_TRACK_MODIFICATIONS = False

	RESOURCE = {
        'AVATAR': os.path.join(basedir, '../res/img/avatar'),
        'PET_PHOTO': os.path.join(basedir, '../res/img/petphoto')
        }

