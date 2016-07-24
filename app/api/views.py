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
    db.session.add(user1)
    db.session.add(user2)
    for i in range(1,1301):
        campsite1 = models.Campsite(
            availablePersons = 3,
            parkID = i,
            hostID = 1,
            startDate = datetime(2016,8,i%31+1),
            endDate = datetime(2016,8,31),
            status = "open"
        )
        campsite2 = models.Campsite(
            availablePersons = 2,
            parkID = i,
            hostID = 2,
            startDate = datetime(2016,8,i%31+1),
            endDate = datetime(2016,8,31),
            status = "closed"
        )
        campsite3 = models.Campsite(
            availablePersons=2,
            parkID=i,
            hostID=2,
            startDate=datetime(2016, 6, 28),
            endDate=datetime(2016, 7, 1),
            status="closed"
        )
        db.session.add(campsite1)
        db.session.add(campsite2)
        db.session.add(campsite3)
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
    # query params = hostID, parkID, starting location, fids
    try:
        if campsiteId is None:
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
                        "campsites": [i.dict() for i in query.get_campsites(park_id=park_id)]
                    })
                return jsonify({"parks":sites})
            if 'hostID' in request.args and 'parkID' in request.args:
                return jsonify(campsites = [i.dict() for i in query.get_campsites(host_id=request.args.get('hostID'), park_id=request.args.get('parkID'))])
            elif 'hostID' in request.args:
                return jsonify(campsites=[i.dict() for i in query.get_campsites(host_id=request.args.get('hostID'))])
            elif 'parkID' in request.args:
                return jsonify(campsites=[i.dict() for i in query.get_campsites(park_id=request.args.get('parkID'))])
            else:
                return jsonify(campsites=[i.dict() for i in query.get_campsites()])
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
        campsite = query.get_campsite(campsiteId)
        campsite.availablePersons = int(request.form['availablePersons'])
        campsite.startDate = request.form['startDate']
        campsite.endDate = request.form['endDate']
        campsite.status = request.form['status']
        query.commit()
        return campsite.json()
    except Exception as e:
        return internal_error(e)


@api.route('/campsites/<int:campsiteId>/delete', methods = ['POST'])
def delete_campsite(campsiteId = None):
    campsite = query.get_campsite(campsiteId)
    query.delete(campsite)
    return item_deleted("campsiteId {} deleted".format(campsiteId))


@api.route('/campsites/add/', methods = ['POST'])
def add_campsite():
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
            return jsonify(users=[i.dict() for i in query.get_users()])
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
    if username_exists(request.form['username']):
        return already_exists(request.form['username'])
    if email_exists(request.form['email']):
        return already_exists(request.form['email'])
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
    url = "http://dev002023.esri.com/arcgis/rest/services/Parks/Parks/MapServer/0/query"
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

