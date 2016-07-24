# -*- coding: UTF-8 -*-
from flask import jsonify, request, url_for, redirect, abort, g, session, current_app
from flask import Blueprint, render_template, abort
import app.query as query
import app.models as models
from datetime import datetime
from app.database import db
from sqlalchemy.inspection import inspect
import json
import math
import requests

api = Blueprint('api',__name__,template_folder='templates')


def item_not_found(e):
    return jsonify({"Error": str(e)}), 404

def invalid_parameters(e):
    return jsonify({"Error": "Invalid parameter: {}".format(e)}), 400


def missing_params(e):
    return jsonify({"Error": str(e)}), 400


def out_of_date_error():
    message = "Conflict detected. Object has been changed. Please refresh data and update."
    return jsonify({message}), 409


def internal_error(e):
    return jsonify({"Error": str(e)}), 500


def already_exists(e):
    return jsonify({"Error": "Item already exists: {}".format(e)}), 409


def item_deleted(message):
    return jsonify({
        "Success": True,
        "Message": str(message),
        "Dependencies" : []
        })


##############
# Seed with data
##############
def populate_db():
    user1 = models.User(
        username = "apulverizer",
        firstName = "Aaron",
        lastName = "Pulver",
        email = "apulverizer@gmail.com",
        phone = "123456789",
        password= "12345"
    )
    user2 = models.User(
        username = "bobthecooluser",
        firstName = "Bob",
        lastName = "Cool",
        email = "bobthecooluser@gmail.com",
        phone = "987654321",
        password = "12345",
    )
    user3 = models.User(
        username="jill123",
        firstName="Jill",
        lastName="Smith",
        email="jill123@gmail.com",
        phone="987123456",
        password="12345",
    )
    user4 = models.User(
        username="joethecooluser",
        firstName="Joe",
        lastName="Cool",
        email="joethecooluser@gmail.com",
        phone="321456987",
        password="12345",
    )
    user5 = models.User(
        username="gregg123",
        firstName="Bob",
        lastName="Cool",
        email="gregg123@gmail.com",
        phone="098712345",
        password="12345",
    )

    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)
    db.session.add(user4)
    db.session.add(user5)
    campsite1 = models.Campsite(
        availablePersons = 3,
        parkID = 5,
        hostID = 1,
        startDate = datetime(2016,8,15),
        endDate = datetime(2016,8,31),
        status = "open"
    )
    campsite2 = models.Campsite(
        availablePersons = 2,
        parkID = 28,
        hostID = 2,
        startDate = datetime(2016,7,26),
        endDate = datetime(2016,8,31),
        status = "open"
    )
    campsite3 = models.Campsite(
        availablePersons=2,
        parkID=30,
        hostID=3,
        startDate=datetime(2016, 7, 30),
        endDate=datetime(2016, 8, 1),
        status="open"
    )
    campsite4 = models.Campsite(
        availablePersons=2,
        parkID=31,
        hostID=4,
        startDate=datetime(2016, 9, 15),
        endDate=datetime(2016, 9, 17),
        status="open"
    )
    campsite5 = models.Campsite(
        availablePersons=2,
        parkID=51,
        hostID=5,
        startDate=datetime(2016, 8, 28),
        endDate=datetime(2016, 8, 31),
        status="open"
    )
    campsite6 = models.Campsite(
        availablePersons=2,
        parkID=51,
        hostID=4,
        startDate=datetime(2016, 8, 28),
        endDate=datetime(2016, 8, 31),
        status="open"
    )
    db.session.add(campsite1)
    db.session.add(campsite2)
    db.session.add(campsite3)
    db.session.add(campsite4)
    db.session.add(campsite5)
    db.session.add(campsite6)
    db.session.commit()

@api.route('/createData')
def create_data():
    db.create_all()
    populate_db()
    return "Added Data"

##############################################################################
# Campsites
##############################################################################
@api.route('/campsites/', methods = ['GET'])
@api.route('/campsites/<int:campsiteId>/', methods = ['GET'])
def get_campsites(campsiteId = None):
    try:
        if campsiteId is None:
            for arg in request.args:
                if arg not in ['startDate', 'endDate', 'hostID', 'parkID', 'startingLoc', 'fids', 'status', 'availablePersons']:
                    return invalid_parameters(arg)
            hostID = None
            parkID = None
            startDate = None
            endDate = None
            status = None
            availablePersons = None
            # Handle the non-spatial query
            if 'hostID' in request.args:
                hostID = request.args.get('hostID')
            if 'parkID' in request.args:
                parkID = request.args.get('parkID')
            if 'startDate' in request.args:
                startDate = request.args.get('startDate')
            if 'endDate' in request.args:
                endDate = request.args.get('endDate')
            if 'status' in request.args:
                status = request.args.get('status')
            if 'availablePersons' in request.args:
                availablePersons = int(request.args.get('availablePersons'))
            # Handle the spatial query
            if 'startingLoc' in request.args and 'fids' in request.args:
                x = float(request.args.get('startingLoc').split(',')[0].strip().rstrip())
                y = float(request.args.get('startingLoc').split(',')[1].strip().rstrip())
                query_result = query_parks(objectIds=request.args.get('fids').split(","))
                sites = []
                for feature in query_result['features']:
                    park_id = feature["attributes"]["OBJECTID"]
                    feature_x = feature["geometry"]["x"]
                    feature_y = feature["geometry"]["y"]
                    distance = get_simple_distance((x,y),(feature_x,feature_y))
                    sites.append({
                        "parkID": park_id,
                        "distance": distance,
                        "campsites": [i.dict() for i in query.get_campsites(park_id=park_id, host_id=hostID, startDate=startDate, endDate=endDate, status=status, availablePersons=availablePersons)],
                        "attributes": feature["attributes"],
                        "geometry": feature["geometry"]
                    })
                return jsonify({"parks":sites})
            else:
                return jsonify(campsites=[i.dict() for i in query.get_campsites(host_id=hostID, park_id=parkID, startDate=startDate, endDate=endDate, status=status, availablePersons=availablePersons)])
        else:
            campsite = query.get_campsites(campsiteId).first()
            if campsite is not None:
                return campsite.json()
            else:
                return item_not_found("Campsite {} not found".format(campsiteId))
    except Exception as e:
        return internal_error(e)


@api.route('/campsites/<int:campsiteId>/update/', methods = ['POST'])
def update_campsite(campsiteId = None):
    try:
        if 'availablePersons' not in request.form: return missing_params('availablePersons')
        if 'startDate' not in request.form: return missing_params('startDate')
        if 'endDate' not in request.form: return missing_params('endDate')
        if 'status' not in request.form: return missing_params('status')
        campsite = query.get_campsite(campsiteId)
        campsite.availablePersons = int(request.form['availablePersons'])
        campsite.startDate = request.form['startDate']
        campsite.endDate = request.form['endDate']
        campsite.status = request.form['status']
        query.commit()
        return campsite.json()
    except Exception as e:
        return internal_error(e)


@api.route('/campsites/<int:campsiteId>/delete/', methods = ['POST'])
def delete_campsite(campsiteId = None):
    campsite = query.get_campsite(campsiteId)
    query.delete(campsite)
    return item_deleted("campsiteId {} deleted".format(campsiteId))


@api.route('/campsites/add/', methods = ['POST'])
def add_campsite():
    if 'availablePersons' not in request.form: return missing_params('availablePersons')
    if 'startDate' not in request.form: return missing_params('startDate')
    if 'endDate' not in request.form: return missing_params('endDate')
    if 'status' not in request.form: return missing_params('status')
    if 'hostID' not in request.form: return missing_params('hostID')
    if 'parkID' not in request.form: return missing_params('parkID')
    if not park_exists(request.form['parkID']):
        item_not_found("Park was not found.")
    campsite = models.Campsite(
        availablePersons=request.form['availablePersons'],
        parkID=request.form['parkID'],
        hostID=request.form['hostID'],
        startDate=datetime.strptime(request.form['startDate'], "%Y-%m-%d"),
        endDate=datetime.strptime(request.form['endDate'], "%Y-%m-%d"),
        status="open"
    )
    query.add(campsite)
    return campsite.json()

#####################
# Users
#####################

@api.route('/users/', methods = ['GET'])
@api.route('/users/<int:userID>/', methods = ['GET'])
def get_users(userID=None):
    try:
        if userID is None:
            for arg in request.args:
                if arg not in ['email', 'username', 'firstName', 'lastName', 'phone']:
                    return invalid_parameters(arg)
            email = None
            username = None
            firstName = None
            lastName = None
            phone = None
            if 'email' in request.args:
                email = request.args.get('email')
            if 'username' in request.args:
                username = request.args.get('username')
            if 'firstName' in request.args:
                firstName = request.args.get('firstName')
            if 'lastName' in request.args:
                lastName = request.args.get('lastName')
            if 'phone' in request.args:
                phone = request.args.get('phone')
            return jsonify(users=[i.dict() for i in query.get_users(email=email, username=username, firstName=firstName, lastName=lastName, phone=phone)])
        else:
            user = query.get_user(userID)
            if user is not None:
                return user.json()
            else:
                return item_not_found("User {} not found".format(userID))
    except Exception as e:
        return internal_error(e)


@api.route('/users/<int:userID>/update/', methods = ['POST'])
def update_user(userID):
    try:
        if 'email' not in request.form: return missing_params('email')
        if 'phone' not in request.form: return missing_params('phone')
        if 'firstName' not in request.form: return missing_params('firstName')
        if 'lastName' not in request.form: return missing_params('lastName')
        user = query.get_user(userID)
        user.email = request.args.get('email')
        user.phone = request.args.get('phone')
        user.firstName = request.args.get('firstName')
        user.lastName = request.args.get('lastName')
        query.commit()
        return user.json()
    except Exception as e:
        return internal_error(e)


@api.route('/users/add/', methods = ['POST'])
def add_user():
    if 'email' not in request.form: return missing_params('email')
    if 'phone' not in request.form: return missing_params('phone')
    if 'firstName' not in request.form: return missing_params('firstName')
    if 'lastName' not in request.form: return missing_params('lastName')
    if 'username' not in request.form: return missing_params('username')
    if 'password' not in request.form: return missing_params('password')
    if username_exists(request.form['username']):
        return already_exists(request.form['username'])
    if email_exists(request.form['email']):
        return already_exists(request.form['email'])
    #TODO make this not plain text
    user = models.User(
        username=request.form['username'],
        firstName=request.form['firstName'],
        lastName=request.form['lastName'],
        email=request.form['email'],
        phone=request.form['phone'],
        password=request.form['password']
    )
    query.add(user)
    return user.json()


def park_exists(parkID):
    url="http://dev002023.esri.com/arcgis/rest/services/Parks/Parks/MapServer/0/query"
    params = {'f': 'json','where': 'OBJECTID={}'.format(parkID)}
    res = requests.get(url, params = params).json()
    return len(res['features'])>=1 # number of parks should be bigger than one


def username_exists(username):
    return len(query.get_users(username=username).all())>0


def email_exists(email):
    return len(query.get_users(email=email).all())>0


def query_parks(objectIds=None):
    #url = "http://dev002023.esri.com/arcgis/rest/services/Parks/Parks/MapServer/0/query"
    url = "http://services.arcgis.com/dkFz166a8Pp3vBsS/arcgis/rest/services/SurveyParks2Me/FeatureServer/0/query"
    params = {'f': 'json',
              'outFields': '*'
              }
    if objectIds:
        params['objectIds'] = ",".join(objectIds)
    return requests.get(url, params=params).json()


def get_simple_distance(coords1, coords2):
    """
    Calculates the simple distance between two x,y points
    :param coords1: (Tuple) of x and y coordinates
    :param coords2: (Tuple) of x and y coordinates
    :return: (float) The distance between the two points
    """
    return math.sqrt((coords1[0]-coords2[0])**2 + (coords1[1]-coords2[1])**2)


