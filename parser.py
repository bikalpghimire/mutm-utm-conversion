import re
import pandas as pd

# --------------------------------------------------
# Helpers
# --------------------------------------------------

def clean_angle(val: str) -> float:
    """
    Cleans decimal degree input such as:
    27.12568292°
    27.12568292 º
    """
    return float(
        val.replace("°", "")
           .replace("º", "")
           .strip()
    )


def dd_to_dms(dd, is_lat=True):
    deg = int(abs(dd))
    min_float = (abs(dd) - deg) * 60
    minute = int(min_float)
    sec = (min_float - minute) * 60

    hemi = (
        "N" if dd >= 0 else "S"
        if is_lat else
        "E" if dd >= 0 else "W"
    )

    return f"{deg}°{minute}'{sec:.4f}\" {hemi}"


# --------------------------------------------------
# Manual text parsing
# --------------------------------------------------

def parse_text(text: str, src_crs: str):
    rows = []
    for line in text.splitlines():
        if not line.strip():
            continue

        parts = re.split(r"[,\t ]+", line.strip())

        if len(parts) == 2:
            name = ""
            x, y = parts
        else:
            name = parts[0]
            x, y = parts[1], parts[2]

        rows.append([
            name,
            clean_angle(x),
            clean_angle(y)
        ])

    return pd.DataFrame(rows, columns=["Point", "X", "Y"])


# --------------------------------------------------
# File parsing
# --------------------------------------------------

def parse_file(path: str):
    if path.lower().endswith(".xlsx"):
        df = pd.read_excel(path)
    else:
        df = pd.read_csv(path)

    df.columns = [c.strip() for c in df.columns]

    if len(df.columns) == 2:
        df.insert(0, "Point", "")

    df.columns = ["Point", "X", "Y"]

    df["X"] = df["X"].astype(str).apply(clean_angle)
    df["Y"] = df["Y"].astype(str).apply(clean_angle)

    return df
