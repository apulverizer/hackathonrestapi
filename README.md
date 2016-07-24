# hackathonrestapi

## A simple Flask API to connect the mapservices features with the SQLite Db that stores the campsites and users

## Requirements

* Python 3.4+
* Flask
* Requests
* SQLAlchemy
* Flask_sqlalchemy


Recommend installing Anaconda3 as this will have all dependencies other than Flask_sqlalchemy which you can install with "pip install flask_sqlalchemy"

## How to use to?

First change the path to the database in the config.py to point to a location on your machine; you don't have to make the database, just point to where you want it to be created and give it a name.
```python
SQLALCHEMY_DATABASE_URI = r"sqlite:///C:\Users\aaro8157\Documents\SourceCode\hackathonrestapi\database.db"
```
If you are running it locally, you will need to first hit the localhost:5000/api/createData. This will create the sqlite db and seed it with a bunch of sample data.

```python
python runserver.py
```

----

**Endpoints**

* \<host\>:\<port\>/api/campsites/ GET
  * No params will return all campsites in the following format
  * hostID=1 - this gets all campsites hosted by the provided userID
  * parkID=1 - this gets all campsites in the provided parkID
  * startDate=8/1/2016 - this gets all campsites that have a startDate before or equal to this
  * endDate=8/2/2016 - this gets all campsites that have an endDate after or equal to this
    You should use these together (e.g startDate=8/1/2016&endDate=8/3/2016) this would return sites that have openings in that range
  * availablePersons=3 -this gets all campsites that have at least 3 open spots
  * status=open -this gets campsites that are open, can also query for closed
  ```json
  {
  "campsites": [
    {
      "availablePersons": 3,
      "createdDate": "2016-07-24T02:38:44",
      "endDate": "2016-08-31T00:00:00",
      "hostID": 1,
      "id": 1,
      "modifiedDate": "2016-07-24T02:38:44",
      "parkID": 1,
      "startDate": "2016-08-02T00:00:00",
      "status": "open",
      "versionID": 1
    },
    {
      "availablePersons": 2,
      "createdDate": "2016-07-24T02:38:44",
      "endDate": "2016-08-31T00:00:00",
      "hostID": 2,
      "id": 2,
      "modifiedDate": "2016-07-24T02:38:44",
      "parkID": 1,
      "startDate": "2016-08-02T00:00:00",
      "status": "closed",
      "versionID": 1
    }
    ]
  }
  ```
  
 ---- 
  
  * startingLoc=x,y&fids=1,2,3 will compute the distance between the starting point and the locations of the parks using fids
  You can use the other optional parameters (except for parkID as that uses the FIDS) to filter campsites
  ```json
  {
  "parks": [
    {
      "attributes": {...},
      "geometry": {...},
      "campsites": [
        {
          "availablePersons": 3,
          "createdDate": "2016-07-24T02:38:44",
          "endDate": "2016-08-31T00:00:00",
          "hostID": 1,
          "id": 1,
          "modifiedDate": "2016-07-24T02:38:44",
          "parkID": 1,
          "startDate": "2016-08-02T00:00:00",
          "status": "open",
          "versionID": 1
        },
        {
          "availablePersons": 2,
          "createdDate": "2016-07-24T02:38:44",
          "endDate": "2016-08-31T00:00:00",
          "hostID": 2,
          "id": 2,
          "modifiedDate": "2016-07-24T02:38:44",
          "parkID": 1,
          "startDate": "2016-08-02T00:00:00",
          "status": "closed",
          "versionID": 1
        },
        {
          "availablePersons": 2,
          "createdDate": "2016-07-24T02:38:44",
          "endDate": "2016-07-01T00:00:00",
          "hostID": 2,
          "id": 3,
          "modifiedDate": "2016-07-24T02:38:44",
          "parkID": 1,
          "startDate": "2016-06-28T00:00:00",
          "status": "closed",
          "versionID": 1
        }
      ],
      "distance": 14673361.770712454,
      "parkID": 1
    }
    ]
  }
  ```
  
 ---- 
  
* \<host\>:\<port\>/api/campsites/\<campsiteID\>/ GET
```json
{
  "availablePersons": 3,
  "createdDate": "2016-07-24T02:38:44",
  "endDate": "2016-08-31T00:00:00",
  "hostID": 1,
  "id": 1,
  "modifiedDate": "2016-07-24T02:38:44",
  "parkID": 1,
  "startDate": "2016-08-02T00:00:00",
  "status": "open",
  "versionID": 1
}
```

----

* \<host\>:\<port\>/api/campsites/\<campsiteID\>/update/ POST
This will update the provided campsite.
Required form parameters:
  - availablePersons (Integer)
  - startDate (String)
  - endDate (String)
  - status (String ["open", "closed"]
  
Returns the campsite info as shown above
  
----
  
 *\<host\>:\<port\>/api/campsites/\<campsiteID\>/delete/ POST
 This deletes a campsite based on ID
 
 ----
 
* \<host\>:\<port\>/api/campsites/\<campsiteID\>/add/ POST
This will update the provided campsite.
Required form parameters:
  - availablePersons (Integer)
  - startDate (String)
  - endDate (String)
  - parkID (FID of the park)
  - hostID (ID of the user who is hosting the site)
  
Returns the campsite info as shown above

----

* \<host\>:\<port\>/api/users/\<userID\>/
This returns the users information

```json
{
  "createdDate": "2016-07-24T02:38:44",
  "email": "apulverizer@gmail.com",
  "firstName": "Aaron",
  "id": 1,
  "lastName": "Pulver",
  "modifiedDate": "2016-07-24T02:38:44",
  "password": "12345",
  "phone": "123456789",
  "username": "apulverizer",
  "versionID": 1
}
```

* \<host\>:\<port\>/api/users/\<userID\>/add/ POST
This adds a user (checks for unique username and email)
Required form parameters:
  - username (string)
  - firstName(string)
  - lastName (string)
  - email (string)
  - phone (string)
  - password (string)
  
Returns the users json as above.

----

* \<host\>:\<port\>/api/users/\<userID\>/update/ POST
This adds a user (checks for unique username and email)
Required form parameters:
  - firstName(string)
  - lastName (string)
  - email (string)
  - phone (string)
  
Returns the users json as above.





  
  

