#!/usr/bin/env python3
import os.path
import json
from xml.dom.minidom import parse
import xml.dom.minidom
import cgi
import cgitb
cgitb.enable()

def main():
    # get_average_lon_lat_from_gpx("EXAMPLEIDWILLBERANDOM",2)
    form = cgi.FieldStorage()
    if form["action"].value == "gpx":
        get_gpx(form["ride_id"].value,form["route"].value)

    elif form["action"].value == "json":
        get_json(form["ride"].value)

    elif form["action"].value == "signup":
        signup(form["ride"].value,form["route"].value, form["name"].value, form["guid"].value)

    else:
        print("Didn't understand action "+form["action"].value)


def get_json(ride_id):
    json_file = json_file_location(ride_id)

    print("Content-type: application/json\n")

    with open(json_file) as f:
        print(f.read())

def json_file_location (ride_id):
    json_file = os.path.join(
        os.path.dirname(__file__),
        "..",
        "rides",
        ride_id,
        "ride.json"
    )

    return json_file

def signup(ride, route_number, name, guid):
    json_file = json_file_location(ride)

    with open(json_file) as jf:
        json_data = json.load(jf)

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


    with open(json_file,"w") as jf:
        json.dump(json_data,jf)

    print("Content-type: text/plain\n\nTrue")




def get_gpx(ride_id, route_number):
    gpx_file = os.path.join(
        os.path.dirname(__file__),
        "..",
        "rides",
        ride_id,
        f"route{route_number}.gpx"
    )

    print("Content-type: text/xml\n")
    with open(gpx_file) as gpx:
        for line in gpx:
            print (line)




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