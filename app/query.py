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


def get_campsites(park_id=None, host_id=None):
    if park_id and host_id:
        return db.session.query(Campsite).filter_by(parkID=park_id, hostID=host_id)
    elif park_id:
        return db.session.query(Campsite).filter_by(parkID=park_id)
    elif host_id:
        return db.session.query(Campsite).filter_by(hostID=host_id)
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


