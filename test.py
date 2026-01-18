from pyproj import CRS, Transformer


WGS84 = CRS.from_epsg(4326)

# ----------------------------------------------------
# MUTM (Central Meridian = 84°)
# Projected CRS
# ----------------------------------------------------
MUTM84 = CRS.from_proj4("""
+proj=tmerc
+lat_0=0
+lon_0=84
+k=0.9999
+x_0=500000
+y_0=0
+a=6377276.345
+rf=300.8017
+towgs84=295.5330,763.9930,270.3525
+no_defs
""")


# ----------------------------------------------------
# Geographic CRS (lat/lon) with SAME datum as MUTM84
# ----------------------------------------------------
MUTM84_GEO = CRS.from_proj4("""
+proj=longlat
+a=6377276.345
+rf=300.8017
+towgs84=295, 736, 257
+no_defs
""")


# ----------------------------------------------------
# Transformer: Easting/Northing -> Lat/Lon
# ----------------------------------------------------
_transformer = Transformer.from_crs(
    MUTM84,
    MUTM84_GEO,
    always_xy=True
)


def mutm84_to_latlon(easting: float, northing: float):
    """
    Convert MUTM (CM=84) Easting/Northing
    to Latitude/Longitude in the SAME coordinate system.
    """
    lon, lat = _transformer.transform(easting, northing)
    return lat, lon


# ----------------------------------------------------
# Example usage
# ----------------------------------------------------
if __name__ == "__main__":
    E = 27.4131359
    N = 85.21195417

    lat, lon = mutm84_to_latlon(E, N)

    print(f"Latitude : {lat:.8f}")
    print(f"Longitude: {lon:.8f}")
