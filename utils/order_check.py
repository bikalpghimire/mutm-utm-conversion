import pandas as pd

def check_consistent_order(xs, ys, src_crs):
    detected = []

    for x, y in zip(xs, ys):
        if pd.isna(x) or pd.isna(y):
            continue

        ax, ay = abs(x), abs(y)

        if src_crs == "WGS84":
            detected.append("LATLON" if ax < ay else "LONLAT")
        else:
            detected.append("EN" if ax < ay else "NE")

    if not detected:
        raise ValueError("No valid coordinate rows found.")

    first = detected[0]
    for d in detected:
        if d != first:
            raise ValueError(
                "Inconsistent coordinate order detected.\n\n"
                "Some rows appear as X,Y while others appear as Y,X."
            )

    return first
