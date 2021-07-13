#!/usr/bin/env python3
import json
import random
from pymongo import MongoClient
from xml.dom.minidom import parse
import xml.dom.minidom
from icalendar import Calendar, Event
from datetime import datetime
import cgi
import cgitb
from math import cos, asin, sqrt, pi
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

    elif form["action"].value == "ics":
        get_ics(form["ride_id"].value,form["route"].value)

    elif form["action"].value == "json":
        get_json(form["ride"].value, form["guid"].value)

    elif form["action"].value == "signup":
        signup(form["ride"].value,form["route"].value, form["name"].value, form["guid"].value)

    elif form["action"].value == "getroute":
        get_route(form["ride"].value,form["route"].value)

    elif form["action"].value == "withdraw":
        withdraw(form["ride"].value,form["route"].value, form["guid"].value)

    elif form["action"].value == "withdrawadmin":
        withdraw(form["ride"].value,form["route"].value, form["name"].value, form["guid"].value, form["admin"].value)

    elif form["action"].value == "validate_admin":
        validate_admin(form["ride"].value,form["admin"].value)

    elif form["action"].value == "new_route":
        add_edit_route(form)

    elif form["action"].value == "delete_route":
        delete_route(form["ride"].value,form["admin"].value, form["route"].value)

    elif form["action"].value == "newevent":
        new_event(form["title"].value,form["date"].value)

    else:
        print("Didn't understand action "+form["action"].value)



def new_event(title,date):
    """
    Creates a new event and puts it into the database
    """

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
    """
    Generic function used for creating IDs for both
    events and admin authentication
    """
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    code = ""

    for _ in range(size):
        code += random.choice(letters)

    return code


def delete_route(ride_id,admin_id,route_number):
    """
    Completely removes a route from an event including
    the gpx and the signup information.
    """
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
   

def add_edit_route(form):
    """
    This same function is used to either edit an existing
    route or add a new one.  If they supply a route_number
    then they're editing rather than adding.
    """

    ride = rides.find_one({"ride_id":form["ride_id"].value})

    if ride["admin_id"] != form["admin_id"].value:
        raise Exception("Invalid admin id for ride")

    # See if they supplied an existing route number
    if form["route_number"].value:
        existing_number = int(form["route_number"].value)
        # We're editing an existing route
        for route in ride["routes"]:
            number = int(route["number"])
            if number == existing_number:
                # This is the route we're editing
                route = route
                route["name"] = form["title"].value
                route["description"] = form["description"].value
                route["start_time"] = form["start"].value
                route["departs"] = form["departs"].value
                route["pace"] = form["pace"].value
                route["stop"] = form["stop"].value
                route["leader"] =  form["leader"].value
                route["spaces"] = form["spaces"].value

                # If they supplied a gpx file we need to add 
                # the data from that too.
                # If there's no file then it will just be a 
                # string here
                # raise Exception(f"gpx is {type(form['gpx'].value)}")
                if not isinstance(form['gpx'].value,str):
                    gpx_file = form["gpx"]
                    gpx = gpx_file.file.read().decode("UTF-8")
                    lat,lon,distance, elevation = get_stats_from_gpx(gpx)
                    route["gpx"] = gpx
                    route["lat"] = str(lat)
                    route["lon"] = str(lon)
                    route["distance"] = round(distance,3)
                    route["elevation"] = round(elevation,3)
                
                break

    else:
        highest_route = 0
        for route in ride["routes"]:
            number = int(route["number"])
            if number > highest_route:
                highest_route = number

        
        highest_route += 1

        gpx_file = form["gpx"]
        gpx = gpx_file.file.read().decode("UTF-8")

        lat,lon,distance,elevation = get_stats_from_gpx(gpx)

        new_route = {
                "number": str(highest_route),
                "name": form["title"].value,
                "description" : form["description"].value,
                "start_time": form["start"].value,
                "departs": form["departs"].value,
                "distance": round(distance,3),
                "elevation": round(elevation,3),
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


def get_json(ride_id,guid):
    """
    Gets the main JSON document covering the whole event
    and all routes.  We ask for the guid so we can show the
    rider whether they are signed up for anything, but we 
    remove all of the other guids so they don't see other
    people's data.
    """
    # We need the user's guid so we can only
    # return their guids in the answer
    json_content = rides.find_one({"ride_id":ride_id})

    json_content.pop("_id")
    json_content.pop("admin_id")

    for route in json_content["routes"]:
        # Hide all guids but the users own
        for joined in route["joined"]:
            if joined["guid"] != guid:
                joined["guid"] = ""

        route.pop("gpx")

    print("Content-type: application/json\n")

    print(json.dumps(json_content))


def get_route(ride, route_number):
    """
    Used for populating the edit route dialog.  Gets
    the JSON for a single route, but removes the signup
    information (including guids)
    """
    json_data = rides.find_one({"ride_id":ride})

    found_route = False
    for route in json_data["routes"]:
        if route["number"] == route_number:
            route.pop("joined")
            print("Content-type: application/json\n")
            print(json.dumps(route))
            return

    raise Exception(f"Couldn't find route '{route_number}'")


def signup(ride, route_number, name, guid):
    """
    Adds a new signup to a ride.  The guid must be present
    unless this is being instigated by an admin
    """

    if guid.strip() == "":
        raise Exception(f"Only admins can sign up riders without a guid")

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

            if not already_signed and len(route["joined"]) < int(route["spaces"]):
                route["joined"].append({"guid":guid, "name":name})
            else:
                raise Exception("Already signed or route full")
            
            break

    if not found_route:
        raise Exception(f"Couldn't find route '{route_number}'")

    rides.update({"ride_id":ride},json_data)

    print(f"Content-type: text/plain; charset=utf-8\n\n{route_number}", end="")

def withdraw(ride, route_number, guid):
    """
    Processes a user-initiated withdrawl.  The guid must
    be present and correct.  Admins can bypass this with
    the withdrawadmin function which is less picky
    """

    if guid.strip() == "":
        raise Exception(f"Won't withdraw a blank guid")

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


def withdrawadmin(ride, route_number, guid, name, admin_id):
    """
    Processes a withdrawl but here we can allow this for another
    user because they will authenticate as admins.  This also 
    allows removing registrations without a guid (ie those made)
    by an admin
    """

    json_data = rides.find_one({"ride_id":ride})

    if ride["admin_id"] != admin_id:
        raise Exception("Invalid admin id for ride")

    found_route = False
    for route in json_data["routes"]:
        if route["number"] == route_number:
            new_joined = []
            found_route = True
            for joined in route["joined"]:
                if joined["guid"] == guid and joined["name"] == name:
                    continue

                new_joined.append(joined)

            route["joined"] = new_joined            
            break

    if not found_route:
        raise Exception(f"Couldn't find route '{route_number}'")

    rides.update({"ride_id":ride},json_data)

    print(f"Content-type: text/plain; charset=utf-8\n\n{route_number}", end="")


def list_joined_admin(ride,route,admin_id):
    """
    Gets the json for the signups for a specific
    route.  Doesn't redact the guids, but we may
    want to rethink this as it does expose guids
    to any admin of an event you've signed up for
    """
    json_data = rides.find_one({"ride_id":ride})

    if ride["admin_id"] != admin_id:
        raise Exception("Invalid admin id for ride")

    for route in json_data["routes"]:
        if route["number"] == route:
            print("Content-type: application/json\n")
            print(json.dumps(route["joined"]))
            return

    raise Exception(f"Couldn't find route '{route}'")

def validate_admin(ride, admin):
    
    if rides.find_one({"ride_id":ride, "admin_id":admin}):
        print("Content-type: text/plain; charset=utf-8\n\nTrue")

    else:
        raise Exception(f"Admin IDs didn't match")



def get_gpx(ride_id, route_number):
    ride = rides.find_one({"ride_id":ride_id})

    for route in ride["routes"]:
        if (route["number"] == route_number):
            print("Content-Disposition:attachment;filename=route.gpx")
            print("Content-type: application/gpx+xml\n")
            print(route["gpx"])
            return

    raise Exception(f"Couldn't find gpx for ride={ride_id} route={route_number}")


def get_ics(ride_id, route_number):
    ride = rides.find_one({"ride_id":ride_id})

    for route in ride["routes"]:
        if (route["number"] == route_number):
            # Create a calendar object
            cal = Calendar()
            event = Event()


            # We need a datetime string with the 
            # year month day hour minute in it
            ymd = [int(x) for x in ride["date"].split("-")]
            hm = [int(x) for x in route["start_time"].split(":")]

            event.add('dtstart', datetime(ymd[0],ymd[1],ymd[2],hm[0],hm[1],0))
            event.add('dtend', datetime(ymd[0],ymd[1],ymd[2],hm[0]+1,hm[1],0))
            event.add('summary',ride["name"])
            event.add('description',f"{route['name']} : {route['description']}\nDeparting {route['departs']}")

            cal.add_component(event)

            print("Content-type: text/calendar; charset=utf-8\n")
            print(cal.to_ical().decode("utf-8"))
            return

    raise Exception(f"Couldn't find ics for ride={ride_id} route={route_number}")




def get_stats_from_gpx(gpx_data):

    # Open XML document using minidom parser
    DOMTree = xml.dom.minidom.parseString(gpx_data)
    collection = DOMTree.documentElement

    points = collection.getElementsByTagName("trkpt")

    lat_max = 0
    lat_min = 0
    lon_max = 0
    lon_min = 0

    last_lat = 0
    last_lon = 0

    distance = 0

    # Our elevation calculation is pretty crude.  We're just
    # using the elevation markers in the GPS file, which isn't 
    # ideal but is the best we can do without additional external
    # information.
    elevation = 0

    last_elevation = 0

    for i,point in enumerate(points):
        this_lat = float(point.getAttribute("lat"))
        this_lon = float(point.getAttribute("lon"))
        this_elevation = float(point.getElementsByTagName("ele")[0].firstChild.data)


        if i==0:
            lat_max = this_lat
            lat_min = this_lat
            lon_max = this_lon
            lon_min = this_lon

        else:
            if this_lat > lat_max:
                lat_max = this_lat
            if this_lat < lat_min:
                lat_min = this_lat
            if this_lon > lon_max:
                lon_max = this_lon
            if this_lon < lon_min:
                lon_min = this_lon

            # Calculate the distance from the last
            # point to this one
            p = pi/180
            a = 0.5 - cos((this_lat-last_lat)*p)/2 + cos(last_lat*p) * cos(this_lat*p) * (1-cos((this_lon-last_lon)*p))/2
            distance += 12742 * asin(sqrt(a))

            
            # Add any elevation change
            if this_elevation > last_elevation:
                elevation += this_elevation - last_elevation


        last_lat = this_lat
        last_lon = this_lon
        last_elevation = this_elevation


    mid_lat = (lat_min+lat_max)/2
    mid_lon = (lon_min+lon_max)/2


    return(mid_lat,mid_lon,distance, elevation)



if __name__ == "__main__":
    main()