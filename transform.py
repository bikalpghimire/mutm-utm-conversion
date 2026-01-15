from pyproj import Transformer

from crs_utils import (
    make_wgs84,
    make_utm,
    make_mutm_local,
    make_mutm_with_towgs
)

# ============================================================
# Main transformation engine
# ============================================================

def transform_all(df, src_crs_name, out_utm_zone, out_mutm_cm):
    """
    Returns list of rows:
    [Point, WGS84_lat, WGS84_lon, UTM_E, UTM_N, UTM_zone, MUTM_E, MUTM_N, MUTM_CM]
    """

    rows = []

    # ---------------------------
    # Decode source CRS
    # ---------------------------
    if src_crs_name.startswith("MUTM"):
        src_cm = int(src_crs_name.replace("MUTM", ""))
        src_is_mutm = True
    else:
        src_cm = None
        src_is_mutm = False

    src_is_wgs = src_crs_name == "WGS84"
    src_is_utm = src_crs_name.startswith("UTM")

    # ---------------------------
    # STEP 1: Source → WGS84
    # ---------------------------
    if src_is_wgs:
        to_wgs = None

    elif src_is_utm:
        zone = int(src_crs_name.replace("UTM", ""))
        to_wgs = Transformer.from_crs(
            make_utm(zone),
            make_wgs84(),
            always_xy=True
        )

    elif src_is_mutm:
        # MUTM → WGS84 MUST use datum shift
        to_wgs = Transformer.from_crs(
            make_mutm_with_towgs(src_cm),
            make_wgs84(),
            always_xy=True
        )

    else:
        raise ValueError(f"Unsupported source CRS: {src_crs_name}")

    # ---------------------------
    # STEP 2: WGS84 → UTM
    # ---------------------------
    wgs_to_utm = Transformer.from_crs(
        make_wgs84(),
        make_utm(out_utm_zone),
        always_xy=True
    )

    # ---------------------------
    # STEP 3: WGS84 → MUTM
    # ---------------------------
    wgs_to_mutm = Transformer.from_crs(
        make_wgs84(),
        make_mutm_with_towgs(out_mutm_cm),
        always_xy=True
    )

    # ---------------------------
    # STEP 4: MUTM → MUTM (projection-only)
    # ---------------------------
    if src_is_mutm and src_cm != out_mutm_cm:
        mutm_to_mutm = Transformer.from_crs(
            make_mutm_local(src_cm),
            make_mutm_local(out_mutm_cm),
            always_xy=True
        )
    else:
        mutm_to_mutm = None

    # ========================================================
    # PROCESS EACH POINT
    # ========================================================
    for _, r in df.iterrows():
        name = r["Point"]
        x = r["X"]
        y = r["Y"]

        # ---------------------------
        # WGS84
        # ---------------------------
        if src_is_wgs:
            lon, lat = x, y
        else:
            lon, lat = to_wgs.transform(x, y)

        # ---------------------------
        # UTM
        # ---------------------------
        utm_e, utm_n = wgs_to_utm.transform(lon, lat)

        # ---------------------------
        # MUTM
        # ---------------------------
        if src_is_mutm and src_cm == out_mutm_cm:
            mutm_e, mutm_n = x, y
        elif src_is_mutm and mutm_to_mutm:
            mutm_e, mutm_n = mutm_to_mutm.transform(x, y)
        else:
            mutm_e, mutm_n = wgs_to_mutm.transform(lon, lat)

        rows.append([
            name,
            round(lat, 8),
            round(lon, 8),
            round(utm_e, 4),
            round(utm_n, 4),
            out_utm_zone,
            round(mutm_e, 4),
            round(mutm_n, 4),
            out_mutm_cm
        ])

    return rows
