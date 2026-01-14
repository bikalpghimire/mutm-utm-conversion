import pandas as pd
import numpy as np
from pyproj import CRS, Transformer

# ============================================================
# FILES
# ============================================================
INPUT_FILE = "survey_points_MUTM.xlsx"     # Easting, Northing
OUTPUT_FILE = "output_wgs84_utm45.xlsx"

# ============================================================
# CRS DEFINITIONS
# ============================================================

# MUTM (as per project note)
crs_mutm = CRS.from_proj4(
    "+proj=tmerc +lat_0=0 +lon_0=84 +k=0.9999 "
    "+x_0=500000 +y_0=0 +ellps=WGS84 +units=m +no_defs"
)

# Geographic WGS84
crs_wgs84 = CRS.from_epsg(4326)

# UTM Zone 45N (true UTM)
crs_utm45 = CRS.from_epsg(32645)

# Transformers
mutm_to_geo = Transformer.from_crs(crs_mutm, crs_wgs84, always_xy=True)
geo_to_utm45 = Transformer.from_crs(crs_wgs84, crs_utm45, always_xy=True)

# ============================================================
# CONTROL POINTS (FROM FINAL CONTROL TABLE)
# ============================================================
control = pd.DataFrame({
    "E": [634413.7394, 634027.2585, 634483.1774, 634785.476],
    "N": [3064905.402, 3065117.858, 3065239.617, 3066440.749],
    "Lat": [27.6959917, 27.69794782, 27.69900009, 27.70980646],
    "Lon": [85.36060931, 85.35671598, 85.36135136, 85.36455331],
})

# Raw inverse projection
lon_r, lat_r = mutm_to_geo.transform(control["E"], control["N"])

# Fit affine correction
A = np.column_stack([lon_r, lat_r, np.ones(len(lon_r))])
Cx, *_ = np.linalg.lstsq(A, control["Lon"], rcond=None)
Cy, *_ = np.linalg.lstsq(A, control["Lat"], rcond=None)

def corrected_geo(E, N):
    lon0, lat0 = mutm_to_geo.transform(E, N)
    lon = Cx[0]*lon0 + Cx[1]*lat0 + Cx[2]
    lat = Cy[0]*lon0 + Cy[1]*lat0 + Cy[2]
    return lat, lon

# ============================================================
# LOAD INPUT MUTM POINTS
# ============================================================
df = pd.read_excel(INPUT_FILE)

df["Easting"] = pd.to_numeric(df["Easting"])
df["Northing"] = pd.to_numeric(df["Northing"])

# ============================================================
# MUTM → WGS84 (CORRECTED)
# ============================================================
lat_list, lon_list = [], []

for e, n in zip(df["Easting"], df["Northing"]):
    lat, lon = corrected_geo(e, n)
    lat_list.append(lat)
    lon_list.append(lon)

df["Latitude"] = lat_list
df["Longitude"] = lon_list

# ============================================================
# WGS84 → UTM 45N
# ============================================================
utm_e, utm_n = geo_to_utm45.transform(df["Longitude"], df["Latitude"])
df["UTM45_Easting"] = utm_e
df["UTM45_Northing"] = utm_n

# ============================================================
# SAVE OUTPUT
# ============================================================
df.to_excel(OUTPUT_FILE, index=False)

print("✔ MUTM → WGS84 → UTM45 conversion completed")
print(f"✔ Output saved as: {OUTPUT_FILE}")
