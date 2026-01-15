from pyproj import CRS

# ============================================================
# WGS84
# ============================================================

def make_wgs84():
    return CRS.from_epsg(4326)


def make_utm(zone: int):
    if not (1 <= zone <= 60):
        raise ValueError("UTM zone must be between 1 and 60")
    return CRS.from_epsg(32600 + zone)


# ============================================================
# MUTM – PROJECTION ONLY (NO DATUM SHIFT)
# Used for MUTM ↔ MUTM
# ============================================================

def make_mutm_local(cm: int):
    if cm not in (81, 84, 87):
        raise ValueError("MUTM central meridian must be 81, 84, or 87")

    return CRS.from_proj4(f"""
    +proj=tmerc
    +lat_0=0
    +lon_0={cm}
    +k=0.9999
    +x_0=500000
    +y_0=0
    +a=6377276.345
    +rf=300.8017
    +units=m
    +no_defs
    """)


# ============================================================
# MUTM – WITH DATUM SHIFT
# Used ONLY when crossing to/from WGS84 or UTM
# ============================================================

def make_mutm_with_towgs(cm: int):
    if cm not in (81, 84, 87):
        raise ValueError("MUTM central meridian must be 81, 84, or 87")

    return CRS.from_proj4(f"""
    +proj=tmerc
    +lat_0=0
    +lon_0={cm}
    +k=0.9999
    +x_0=500000
    +y_0=0
    +a=6377276.345
    +rf=300.8017
    +towgs84=295, 736, 257
    +units=m
    +no_defs
    """)
