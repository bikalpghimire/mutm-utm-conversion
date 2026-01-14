from pyproj import Transformer
from crs_utils import make_wgs84, make_utm, make_mutm, utm_zone_from_lon

def transform_all(df, src):
    rows = []
    wgs84 = make_wgs84()

    # --- source CRS ---
    if src.startswith("MUTM84_CM"):
        cm = int(src.split("CM")[1])
        src_crs = make_mutm(cm)

    elif src == "UTM":
        raise ValueError("UTM input requires zone selection (future enhancement).")

    else:  # WGS84
        src_crs = wgs84

    for _, r in df.iterrows():
        x, y = r["X"], r["Y"]

        # → WGS84
        if src == "WGS84":
            lat, lon = x, y
        else:
            to_wgs = Transformer.from_crs(src_crs, wgs84, always_xy=True)
            lon, lat = to_wgs.transform(x, y)

        # WGS84 → UTM
        utm_zone = utm_zone_from_lon(lon)
        utm = make_utm(utm_zone)
        t_utm = Transformer.from_crs(wgs84, utm, always_xy=True)
        utm_x, utm_y = t_utm.transform(lon, lat)

        # WGS84 → MUTM (same CM as source if MUTM)
        if src.startswith("MUTM84_CM"):
            mutm_cm = cm
        else:
            mutm_cm = 84  # default engineering choice

        mutm = make_mutm(mutm_cm)
        t_mutm = Transformer.from_crs(wgs84, mutm, always_xy=True)
        mutm_x, mutm_y = t_mutm.transform(lon, lat)

        rows.append([
            r["Point"],
            lat, lon,
            utm_x, utm_y, utm_zone,
            mutm_x, mutm_y, mutm_cm
        ])

    return rows
