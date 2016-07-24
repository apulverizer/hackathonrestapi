import json
import datetime
from flask import Flask
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from app.database import db
from app.helpers import DateTimeEncoder
from sqlalchemy.orm import class_mapper
from sqlalchemy.ext.declarative import declared_attr


STATUS = db.Enum("closed", "open")

"""
    A base class that all models derive from
"""


class CustomModel(db.Model):
    __abstract__ = True
    # def __init__(self):
    #    super(CustomModel,self).__init__()

    createdDate = db.Column(db.DateTime, server_default=db.func.now())
    modifiedDate = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    versionID = db.Column(db.Integer, nullable=False)

    __mapper_args__ = {
        "version_id_col": versionID
    }

    def dict(self):
        result = {}
        for prop in class_mapper(self.__class__).iterate_properties:
            if isinstance(prop, sqlalchemy.orm.ColumnProperty):
                result[prop.key] = getattr(self, prop.key)
        return result

    def json(self):
        return jsonify(self.dict())


##############################################################################
# Models
##############################################################################

class User(CustomModel):
    __tablename__ = 'user'

    id = db.Column('id', db.Integer, primary_key=True)
    username = db.Column('username', db.String)
    firstName = db.Column('firstName', db.String)
    lastName = db.Column('lastName', db.String)
    email = db.Column('email', db.String)
    phone = db.Column('phone', db.String)
    password = db.Column('password', db.String)


class Campsite(CustomModel):
    __tablename__ = 'site'

    id= db.Column('id', db.Integer, primary_key=True)
    availablePersons = db.Column('persons', db.Integer)
    parkID = db.Column('parkID', db.Integer) # link to parks FS ID
    hostID = db.Column('hostID', db.Integer, db.ForeignKey('user.id'))
    startDate = db.Column('startDate', db.DateTime)
    endDate = db.Column('endDate', db.DateTime)
    status = db.Column('status', STATUS)








