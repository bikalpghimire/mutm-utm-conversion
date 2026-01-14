import pandas as pd
from pyproj import CRS, Transformer

# ==========================================================
# USER SETTINGS
# ==========================================================

INPUT_EXCEL = "survey_points_MUTM.xlsx"
OUTPUT_EXCEL = "output_wgs84_utm-adpi.xlsx"

MUTM_CENTRAL_MERIDIAN = 84   # 81 / 84 / 87
UTM_ZONE = 45               # 44 or 45

# ==========================================================
# DEFINE CRS (CORRECT WAY)
# ==========================================================

# MUTM Projection (Everest 1937) From ADPi Survey Report
mutm = CRS.from_proj4(f"""
+proj=tmerc
+lat_0=0
+lon_0={MUTM_CENTRAL_MERIDIAN}
+k=0.9999
+x_0=500000
+y_0=0
+a=6377276.345
+rf=300.8017
+towgs84=295, 736, 257
+units=m
+no_defs
""")

# WGS84 Geographic
wgs84_geog = CRS.from_epsg(4326)

# WGS84 UTM
wgs84_utm = CRS.from_epsg(32600 + UTM_ZONE)

# ==========================================================
# TRANSFORMERS
# ==========================================================

# MUTM → WGS84 Geographic (datum handled automatically)
t_mutm_to_wgs84 = Transformer.from_crs(
    mutm, wgs84_geog, always_xy=True
)

# WGS84 Geographic → UTM
t_wgs84_to_utm = Transformer.from_crs(
    wgs84_geog, wgs84_utm, always_xy=True
)

# ==========================================================
# LOAD INPUT EXCEL
# ==========================================================

df = pd.read_excel(INPUT_EXCEL)

required_cols = {"Point", "Easting", "Northing"}
if not required_cols.issubset(df.columns):
    raise ValueError("Excel must contain Point, Easting, Northing columns")

# ==========================================================
# PROCESS
# ==========================================================

lat, lon, utm_e, utm_n = [], [], [], []

for _, r in df.iterrows():
    x, y = r["Easting"], r["Northing"]

    lon_w, lat_w = t_mutm_to_wgs84.transform(x, y)
    e_u, n_u = t_wgs84_to_utm.transform(lon_w, lat_w)

    lon.append(lon_w)
    lat.append(lat_w)
    utm_e.append(e_u)
    utm_n.append(n_u)

# ==========================================================
# OUTPUT
# ==========================================================

df["WGS84_Latitude"] = lat
df["WGS84_Longitude"] = lon
df["UTM_Easting"] = utm_e
df["UTM_Northing"] = utm_n
df["UTM_Zone"] = f"{UTM_ZONE}N"

df.to_excel(OUTPUT_EXCEL, index=False)

print("✔ Conversion successful")
print(f"✔ Output saved to: {OUTPUT_EXCEL}")
