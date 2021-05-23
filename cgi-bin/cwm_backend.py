#!/usr/bin/env python3
import os.path
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

    else:
        print("Didn't understand action "+form["action"].value)

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