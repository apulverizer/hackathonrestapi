import json
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.database import db
from app.models import *


def create_all():
    db.create_all()


def flush():
    db.session.flush()


def commit():
    return db.session.commit()


def add(obj):
    db.session.add(obj)
    return db.session.commit()


def delete(obj):
    db.session.delete(obj)
    return db.session.commit()


def get_campsite(campsite_id):
    return db.session.query(Campsite).filter_by(id=campsite_id).first()


def get_campsites(park_id=None, host_id=None, startDate=None, endDate=None, status=None, availablePersons=None):
    filters = []
    if park_id:
        filters.append(Campsite.parkID == park_id)
    if host_id:
        filters.append(Campsite.hostID == host_id)
    if status:
        filters.append(Campsite.status == status)
    if availablePersons:
        filters.append(Campsite.availablePersons >= availablePersons)
    if startDate:
        filters.append(Campsite.startDate <= datetime.datetime.strptime(startDate,"%m/%d/%Y"))
    if endDate:
        filters.append(Campsite.endDate >= datetime.datetime.strptime(endDate,"%m/%d/%Y"))
    if filters:
        return db.session.query(Campsite).filter(*filters)
    else:
        return db.session.query(Campsite).all()


def get_user(userID):
    return db.session.query(User).filter_by(id=userID).first()


def get_users(username=None, email=None):
    if username and email:
        return db.session.query(User).filter_by(username=username, email=email)
    elif username:
        return db.session.query(User).filter_by(username=username)
    elif email:
        return db.session.query(User).filter_by(email=email)
    else:
        return db.session.query(User).all()


