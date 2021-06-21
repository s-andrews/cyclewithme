#!/usr/bin/env python3
import json
import random
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

    if not "action" in form:
        print("Content-type: text/plain; charset=utf-8\n\nNo action")
        return

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

    elif form["action"].value == "new_route":
        add_new_route(form)

    elif form["action"].value == "delete_route":
        delete_route(form["ride"].value,form["admin"].value, form["route"].value)

    elif form["action"].value == "newevent":
        new_event(form["title"].value,form["date"].value)

    else:
        print("Didn't understand action "+form["action"].value)



def new_event(title,date):
     ride = {
         "ride_id": generate_id(10),
         "admin_id": generate_id(10),   
         "name": title,
         "date": date,
         "routes" : []
     }

     rides.insert_one(ride)

     print("Content-type: text/plain; charset=utf-8\n\n"+ride['ride_id']+" "+ride['admin_id'], end="")


def generate_id(size):
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    code = ""

    for _ in range(size):
        code += random.choice(letters)

    return code


def delete_route(ride_id,admin_id,route_number):
    ride = rides.find_one({"ride_id":ride_id})

    if ride["admin_id"] != admin_id:
        raise Exception("Invalid admin id for ride")

    seen_routes = []
    for i,route in enumerate(ride["routes"]):
        seen_routes.append(str(route["number"]))
        if str(route["number"]) == route_number:
            ride["routes"].pop(i)
            rides.update({"ride_id":ride_id},ride)

            print("Content-type: text/plain; charset=utf-8\n\nTrue")
            return

    raise Exception(f"Couldn't find route to remove matching {route_number} checked {seen_routes}")
   



def add_new_route(form):

    ride = rides.find_one({"ride_id":form["ride_id"].value})

    if ride["admin_id"] != form["admin_id"].value:
        raise Exception("Invalid admin id for ride")

    highest_route = 0

    for route in ride["routes"]:
        number = int(route["number"])
        if number > highest_route:
            highest_route = number

    
    highest_route += 1

    gpx_file = form["gpx"]
    gpx = gpx_file.file.read().decode("UTF-8")

    lat,lon = get_average_lon_lat_from_gpx(gpx)

    new_route = {
            "number": str(highest_route),
            "name": form["title"].value,
            "description" : form["description"].value,
            "start_time": form["start"].value,
            "departs": form["departs"].value,
            "distance" : form["distance"].value,
            "pace": form["pace"].value,
            "stop": form["stop"].value,
            "leader": form["leader"].value,
            "spaces": form["spaces"].value,
            "gpx": gpx,
            "lat": str(lat),
            "lon": str(lon),
            "joined" : []
        }

    ride["routes"].append(new_route)

    rides.update({"ride_id":form["ride_id"].value},ride)

    print("Content-type: text/plain; charset=utf-8\n\nTrue")




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

    print(f"Content-type: text/plain; charset=utf-8\n\n{route_number}", end="")

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

    print(f"Content-type: text/plain; charset=utf-8\n\n{route_number}", end="")


def validate_admin(ride, admin):
    
    if rides.find_one({"ride_id":ride, "admin_id":admin}):
        print("Content-type: text/plain; charset=utf-8\n\nTrue")

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



def get_average_lon_lat_from_gpx(gpx_data):

    # Open XML document using minidom parser
    DOMTree = xml.dom.minidom.parseString(gpx_data)
    collection = DOMTree.documentElement

    points = collection.getElementsByTagName("trkpt")

    lat = 0
    lon = 0

    for point in points:
        lat += float(point.getAttribute("lat"))
        lon += float(point.getAttribute("lon"))

    lat /= len(points)
    lon /= len(points)

    return(lat,lon)



if __name__ == "__main__":
    main()