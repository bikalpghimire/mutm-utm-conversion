import pandas as pd
from parser import parse_text, parse_file, dd_to_dms
from transform import transform_all
from utils.order_check import check_consistent_order
from utils.formatters import fmt_latlon, fmt_xy


def run_transform(app):
    if app.mode.get() == "manual":
        text = app.manual_text.get("1.0", "end")
        if not text.strip():
            raise ValueError("Please enter coordinate data.")
        df_in = parse_text(text, app.src_crs.get())
    else:
        path = app.file_entry.get().strip()
        if not path:
            raise ValueError("Please select a file.")
        df_in = parse_file(path, app.has_header.get())

    order = check_consistent_order(
        df_in["X"].astype(float),
        df_in["Y"].astype(float),
        app.src_crs.get()
    )

    if order in ("NE", "LATLON"):
        df_in[["X", "Y"]] = df_in[["Y", "X"]]

    rows = transform_all(
        df_in,
        app.src_crs.get(),
        int(app.utm_zone.get()),
        int(app.mutm_zone.get())
    )

    df_all = pd.DataFrame(rows, columns=[
        "Point",
        "WGS84_Lat", "WGS84_Lon",
        "UTM_E", "UTM_N", "UTM_Zone",
        "MUTM_E", "MUTM_N", "MUTM_CM"
    ])

    df_out = pd.DataFrame()
    df_out["Point"] = df_in["Point"]

    outputs = []

    if app.out_wgs.get():
        outputs.append("WGS84")

        if app.wgs_fmt.get() == "DMS":
            lat = df_all["WGS84_Lat"].apply(lambda v: dd_to_dms(v, is_lat=True))
            lon = df_all["WGS84_Lon"].apply(lambda v: dd_to_dms(v, is_lat=False))
        else:
            lat = df_all["WGS84_Lat"].apply(fmt_latlon)
            lon = df_all["WGS84_Lon"].apply(fmt_latlon)

        df_out["WGS84_Lat"] = lat
        df_out["WGS84_Lon"] = lon

    if app.out_utm.get():
        z = app.utm_zone.get()
        outputs.append(f"UTM{z}")
        df_out[f"UTM{z}_E"] = df_all["UTM_E"].apply(fmt_xy)
        df_out[f"UTM{z}_N"] = df_all["UTM_N"].apply(fmt_xy)

    if app.out_mutm.get():
        z = app.mutm_zone.get()
        outputs.append(f"MUTM{z}")
        df_out[f"MUTM{z}_E"] = df_all["MUTM_E"].apply(fmt_xy)
        df_out[f"MUTM{z}_N"] = df_all["MUTM_N"].apply(fmt_xy)

    return df_out, outputs
