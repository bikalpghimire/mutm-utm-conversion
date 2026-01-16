import numpy as np
from pyproj import CRS, Transformer

# =========================================================
# 1. CRS DEFINITIONS
# =========================================================

# MUTM (Everest 1830) – adjust lon_0 if your MUTM CM differs
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

everest_geo = CRS.from_proj4("""
+proj=longlat
+a=6377276.345
+rf=300.8017
+no_defs
""")

everest_xyz = CRS.from_proj4("""
+proj=geocent
+a=6377276.345
+rf=300.8017
+units=m
+no_defs
""")

wgs84_geo = CRS.from_epsg(4326)
wgs84_xyz = CRS.from_epsg(4978)

# Transformers
t_mutm_evt = Transformer.from_crs(mutm, everest_geo, always_xy=True)
t_evt_xyz  = Transformer.from_crs(everest_geo, everest_xyz, always_xy=True)
t_wgs_xyz  = Transformer.from_crs(wgs84_geo, wgs84_xyz, always_xy=True)

# =========================================================
# 2. INPUT DATA (ORDER MUST MATCH)
# =========================================================

points = [
    "ARP03","ARP01","ARP02","ACP4","HAN01",
    "HAN02","YC20","JZ001","AVIC2","AVIC3"
]

# WGS84
lat = np.array([
27.6959917, 27.69794782, 27.69900009, 27.70980646,
27.70599277, 27.69652912, 27.67877339, 27.6855344,
27.71102263, 27.70865259
])

lon = np.array([
85.36060931, 85.35671598, 85.36135136, 85.36455331,
85.36847138, 85.36576533, 85.35107038, 85.35006497,
85.36003881, 85.35636264
])

h = np.array([
1333.46427, 1333.27477, 1335.0389, 1336.18294,
1322.837, 1311.588, 1309.104, 1297.752,
1333.006, 1320.208
])

# MUTM
E = np.array([
634413.7394, 634027.2585, 634483.1774, 634785.476,
635176.7043, 634921.6643, 633494.1549, 633386.5897,
634338.6971, 633979.0765
])

N = np.array([
3064905.402, 3065117.858, 3065239.617, 3066440.749,
3066022.488, 3064970.699, 3062986.706, 3063734.849,
3066570.499, 3066303.77
])

# =========================================================
# 3. COORDINATE CONVERSION
# =========================================================

# MUTM → Everest geographic
lon_evt, lat_evt = t_mutm_evt.transform(E, N)

# Everest → XYZ
Xe, Ye, Ze = t_evt_xyz.transform(lon_evt, lat_evt, h)

# WGS84 → XYZ
Xw, Yw, Zw = t_wgs_xyz.transform(lon, lat, h)

# =========================================================
# 4. HELMERT 7-PARAMETER SOLUTION
# =========================================================

def helmert_7(X1, Y1, Z1, X2, Y2, Z2):
    n = len(X1)
    A = np.zeros((3*n, 7))
    L = np.zeros((3*n, 1))

    for i in range(n):
        A[3*i]   = [1, 0, 0, 0,  Z1[i], -Y1[i], X1[i]]
        A[3*i+1] = [0, 1, 0, -Z1[i], 0, X1[i], Y1[i]]
        A[3*i+2] = [0, 0, 1, Y1[i], -X1[i], 0, Z1[i]]

        L[3*i]   = X2[i] - X1[i]
        L[3*i+1] = Y2[i] - Y1[i]
        L[3*i+2] = Z2[i] - Z1[i]

    p, *_ = np.linalg.lstsq(A, L, rcond=None)
    return p.flatten()

Tx, Ty, Tz, Rx, Ry, Rz, s = helmert_7(Xe, Ye, Ze, Xw, Yw, Zw)

# Unit conversion
Rx_as = Rx * 206264.806
Ry_as = Ry * 206264.806
Rz_as = Rz * 206264.806
s_ppm = s * 1e6

# =========================================================
# 5. APPLY TRANSFORMATION & COMPUTE RESIDUALS
# =========================================================

def apply_helmert(X, Y, Z, Tx, Ty, Tz, Rx, Ry, Rz, s):
    X2 = Tx + (1+s)*(X - Rz*Y + Ry*Z)
    Y2 = Ty + (1+s)*(Rz*X + Y - Rx*Z)
    Z2 = Tz + (1+s)*(-Ry*X + Rx*Y + Z)
    return X2, Y2, Z2

Xp, Yp, Zp = apply_helmert(Xe, Ye, Ze, Tx, Ty, Tz, Rx, Ry, Rz, s)

dX = Xp - Xw
dY = Yp - Yw
dZ = Zp - Zw
d3D = np.sqrt(dX**2 + dY**2 + dZ**2)

# =========================================================
# 6. OUTPUT RESULTS
# =========================================================

print("\n====== 7-PARAMETER HELMERT (MUTM → WGS84) ======\n")
print(f"Tx = {Tx:.4f} m")
print(f"Ty = {Ty:.4f} m")
print(f"Tz = {Tz:.4f} m")
print(f"Rx = {Rx_as:.6f} arc-sec")
print(f"Ry = {Ry_as:.6f} arc-sec")
print(f"Rz = {Rz_as:.6f} arc-sec")
print(f"Scale = {s_ppm:.6f} ppm")

print("\n+towgs84 string:")
print(f"+towgs84={Tx:.4f},{Ty:.4f},{Tz:.4f},{Rx_as:.6f},{Ry_as:.6f},{Rz_as:.6f},{s_ppm:.6f}")

print("\n====== RESIDUALS (meters) ======")
print("Point     dX      dY      dZ     3D")

for i, p in enumerate(points):
    print(f"{p:<8} {dX[i]:7.4f} {dY[i]:7.4f} {dZ[i]:7.4f} {d3D[i]:7.4f}")

print("\nRMS Errors:")
print(f"RMS dX = {np.sqrt(np.mean(dX**2)):.4f} m")
print(f"RMS dY = {np.sqrt(np.mean(dY**2)):.4f} m")
print(f"RMS dZ = {np.sqrt(np.mean(dZ**2)):.4f} m")
print(f"RMS 3D = {np.sqrt(np.mean(d3D**2)):.4f} m")
