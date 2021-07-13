#!python
from xml.dom.minidom import parse
import xml.dom.minidom
from math import cos, asin, sqrt, pi

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
    elevation = 0

    last_elevation = None

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
                print(f"This {this_elevation:.2f} last {last_elevation:.2f} total {elevation:.2f}")


        last_lat = this_lat
        last_lon = this_lon
        last_elevation = this_elevation



    mid_lat = (lat_min+lat_max)/2
    mid_lon = (lon_min+lon_max)/2

    # Convert distance from km to miles
    # distance *= 0.621


    return(mid_lat,mid_lon,distance, elevation)


with open("E:/GPX/Tempo Tearaway route Barrow 34m.gpx") as gpxf:
    gpx_data = gpxf.read()
    stats = get_stats_from_gpx(gpx_data)
    print(stats)
