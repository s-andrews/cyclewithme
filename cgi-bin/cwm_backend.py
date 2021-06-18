#!/usr/bin/env python3
import json
from pymongo import MongoClient
from xml.dom.minidom import parse
import xml.dom.minidom
import cgi
import cgitb
cgitb.enable()

def main():
    # Set up the database connection
    client = MongoClient()
    db = client.cwm_database
    global rides 
    rides = db.rides_collection
    
    # get_average_lon_lat_from_gpx("EXAMPLEIDWILLBERANDOM",2)
    form = cgi.FieldStorage()
    if form["action"].value == "gpx":
        get_gpx(form["ride_id"].value,form["route"].value)

    elif form["action"].value == "json":
        get_json(form["ride"].value)

    elif form["action"].value == "signup":
        signup(form["ride"].value,form["route"].value, form["name"].value, form["guid"].value)

    elif form["action"].value == "withdraw":
        withdraw(form["ride"].value,form["route"].value, form["guid"].value)

    elif form["action"].value == "validate_admin":
        validate_admin(form["ride"].value,form["admin"].value)


    else:
        print("Didn't understand action "+form["action"].value)


def get_json(ride_id):
    json_content = rides.find_one({"ride_id":ride_id})

    json_content.pop("_id")
    json_content.pop("admin_id")

    for route in json_content["routes"]:
        route.pop("gpx")

    print("Content-type: application/json\n")

    print(json.dumps(json_content))


def signup(ride, route_number, name, guid):
    json_data = rides.find_one({"ride_id":ride})

    found_route = False
    for route in json_data["routes"]:
        if route["number"] == route_number:
            found_route = True
            already_signed = False
            for joined in route["joined"]:
                if joined["guid"] == guid:
                    # They're already signed up
                    already_signed = True
                    break

            if not already_signed:
                route["joined"].append({"guid":guid, "name":name})
            else:
                raise Exception("Already signed")
            
            break

    if not found_route:
        raise Exception(f"Couldn't find route '{route_number}'")

    rides.update({"ride_id":ride},json_data)

    print("Content-type: text/plain\n\nTrue")

def withdraw(ride, route_number, guid):
    json_data = rides.find_one({"ride_id":ride})

    found_route = False
    for route in json_data["routes"]:
        if route["number"] == route_number:
            new_joined = []
            found_route = True
            for joined in route["joined"]:
                if joined["guid"] != guid:
                    new_joined.append(joined)

            route["joined"] = new_joined            
            break

    if not found_route:
        raise Exception(f"Couldn't find route '{route_number}'")

    rides.update({"ride_id":ride},json_data)

    print("Content-type: text/plain\n\nTrue")


def validate_admin(ride, admin):
    
    if rides.find_one({"ride_id":ride, "admin_id":admin}):
        print("Content-type: text/plain\n\nTrue")

    else:
        raise Exception(f"Admin IDs didn't match")



def get_gpx(ride_id, route_number):
    ride = rides.find_one({"ride_id":ride_id})

    for route in ride["routes"]:
        if (route["number"] == route_number):
            print("Content-type: text/xml\n")
            print(route["gpx"])
            return

    raise Exception(f"Couldn't find gpx for ride={ride_id} route={route_number}")



def get_average_lon_lat_from_gpx(ride_id, route_number):
    gpx_file = os.path.join(
        os.path.dirname(__file__),
        "..",
        "rides",
        ride_id,
        f"route{route_number}.gpx"
    )


    # Open XML document using minidom parser
    DOMTree = xml.dom.minidom.parse(gpx_file)
    collection = DOMTree.documentElement

    points = collection.getElementsByTagName("trkpt")

    lat = 0
    lon = 0

    for point in points:
        lat += float(point.getAttribute("lat"))
        lon += float(point.getAttribute("lon"))

    lat /= len(points)
    lon /= len(points)

    print(f"Average position is lat={lat} lon={lon}")


    print(f"Found {len(points)} points")







if __name__ == "__main__":
    main()