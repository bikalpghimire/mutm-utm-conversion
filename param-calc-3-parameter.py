import numpy as np
from pyproj import CRS, Transformer

# =========================================================
# 1. CRS DEFINITIONS
# =========================================================

# MUTM (Everest 1830, CM=84)
mutm = CRS.from_proj4("""
+proj=tmerc
+lat_0=0
+lon_0=84
+k=0.9999
+x_0=500000
+y_0=0
+a=6377276.345
+rf=300.8017
+units=m
+no_defs
""")

# Everest geographic
everest_geo = CRS.from_proj4("""
+proj=longlat
+a=6377276.345
+rf=300.8017
+no_defs
""")

# Everest geocentric
everest_xyz = CRS.from_proj4("""
+proj=geocent
+a=6377276.345
+rf=300.8017
+units=m
+no_defs
""")

# WGS84
wgs84_geo = CRS.from_epsg(4326)
wgs84_xyz = CRS.from_epsg(4978)

# Transformers
t_mutm_evt = Transformer.from_crs(mutm, everest_geo, always_xy=True)
t_evt_xyz  = Transformer.from_crs(everest_geo, everest_xyz, always_xy=True)
t_wgs_xyz  = Transformer.from_crs(wgs84_geo, wgs84_xyz, always_xy=True)

# =========================================================
# 2. INPUT DATA
# =========================================================

lat = np.array([
    27.6959917, 27.69794782, 27.69900009
])

lon = np.array([
    85.36060931, 85.35671598, 85.36135136
])

h = np.array([
    1333.46427, 1333.27477, 1335.0389
])

E = np.array([
    634413.7394, 634027.2585, 634483.1774
])

N = np.array([
    3064905.402, 3065117.858, 3065239.617
])

# =========================================================
# 3. COORDINATE CONVERSIONS
# =========================================================

# MUTM → Everest geographic
lon_evt, lat_evt = t_mutm_evt.transform(E, N)

# Everest → XYZ
Xe, Ye, Ze = t_evt_xyz.transform(lon_evt, lat_evt, h)

# WGS84 → XYZ
Xw, Yw, Zw = t_wgs_xyz.transform(lon, lat, h)

# =========================================================
# 4. MOLODENSKY 3-PARAMETER (TRANSLATION ONLY)
# =========================================================

dX = Xw - Xe
dY = Yw - Ye
dZ = Zw - Ze

Tx = np.mean(dX)
Ty = np.mean(dY)
Tz = np.mean(dZ)

# Residuals
rx = dX - Tx
ry = dY - Ty
rz = dZ - Tz
r3d = np.sqrt(rx**2 + ry**2 + rz**2)

# =========================================================
# 5. OUTPUT
# =========================================================

print("\n====== MOLODENSKY 3-PARAMETER (MUTM → WGS84) ======\n")
print(f"Tx = {Tx:.4f} m")
print(f"Ty = {Ty:.4f} m")
print(f"Tz = {Tz:.4f} m")

print("\n+towgs84 string:")
print(f"+towgs84={Tx:.4f},{Ty:.4f},{Tz:.4f}")

print("\nRMS Residuals:")
print(f"RMS dX = {np.sqrt(np.mean(rx**2)):.4f} m")
print(f"RMS dY = {np.sqrt(np.mean(ry**2)):.4f} m")
print(f"RMS dZ = {np.sqrt(np.mean(rz**2)):.4f} m")
print(f"RMS 3D = {np.sqrt(np.mean(r3d**2)):.4f} m")
