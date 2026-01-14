from pyproj import CRS
import math

def make_wgs84():
    return CRS.from_epsg(4326)

def make_utm(zone):
    return CRS.from_epsg(32600 + zone)

def make_mutm(cm):
    return CRS.from_proj4(f"""
    +proj=tmerc
    +lat_0=0
    +lon_0={cm}
    +k=0.9999
    +x_0=500000
    +y_0=0
    +a=6377276.345
    +rf=300.8017
    +towgs84=295,736,257
    +units=m
    +no_defs
    """)

def utm_zone_from_lon(lon):
    return int(math.floor((lon + 180) / 6) + 1)
