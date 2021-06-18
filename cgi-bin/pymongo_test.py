#!python
from pymongo import MongoClient

client = MongoClient()

db = client.cwm_database

rides = db.rides_collection

ride = {
    "ride_id": "EXAMPLEIDWILLBERANDOM",
    "admin_id": "IMANADMIN",   
    "name": "BCC Sunday Club Ride",
    "date": "2021-05-23",
    "routes" : [
        {
            "number": "1",
            "name": "Club ride to Tuddenham",
            "description" : "A mostly flat route taken at a steady pace",
            "start_time": "09:00",
            "departs": "Burwell Primary School",
            "distance" : "30",
            "pace": "Steady (~15mph)",
            "stop": "Wilde and Greene",
            "leader": "Judy",
            "spaces": "10",
            "lat": "52.27722117837096",
            "lon": "0.4428597805954155",
            "joined" : []
        },
        {
            "number": "2",
            "name": "Longer ride to Saffron Walden",
            "description" : "A more challenging route with distance and elevation",
            "start_time": "09:00",
            "departs": "Burwell Primary School",
            "distance" : "50",
            "pace": "Pushing on (~17mph)",
            "stop": "Saffron Walden Market Place",
            "leader": "Simon",
            "spaces": "10",
            "lat": "52.15231006196024",
            "lon": "0.2618071877055751",
            "joined" : []
        }
    ]
}

for route in ride["routes"]:
    with open("c:/Users/andrewss/git/cyclewithme/rides/"+ride["ride_id"]+"/route"+route["number"]+".gpx") as gpxf:
        route["gpx"] = gpxf.read()

# rides.remove({})
# rides.insert_one(ride)

retrieved = rides.find_one({"ride_id":"EXAMPLEIDWILLBERANDOM"})

for route in retrieved["routes"]:
    for key in route.keys():
        print(key)

