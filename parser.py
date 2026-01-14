import pandas as pd
import re
import os

DMS_PATTERN = re.compile(
    r"""(?P<deg>\d+)[°:\s]+(?P<min>\d+)[']?(?P<sec>[\d.]+)?["]?\s*(?P<hem>[NSEW])""",
    re.IGNORECASE
)

def dms_to_dd(text):
    m = DMS_PATTERN.search(text.strip())
    if not m:
        return float(text)

    deg = float(m.group("deg"))
    minutes = float(m.group("min"))
    seconds = float(m.group("sec") or 0)
    hem = m.group("hem").upper()

    dd = deg + minutes / 60 + seconds / 3600
    if hem in ("S", "W"):
        dd = -dd
    return dd

def parse_text(text, source_crs):
    rows = []
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    for i, line in enumerate(lines, start=1):
        parts = re.split(r"[,\s\t]+", line)

        if len(parts) == 2:
            name = f"P{i}"
            x, y = parts
        elif len(parts) >= 3:
            name, x, y = parts[:3]
        else:
            raise ValueError(f"Invalid line: {line}")

        if source_crs == "WGS84":
            x = dms_to_dd(x)
            y = dms_to_dd(y)

        rows.append([name, float(x), float(y)])

    return pd.DataFrame(rows, columns=["Point", "X", "Y"])

def parse_file(path):
    ext = os.path.splitext(path)[1].lower()

    if ext == ".xlsx":
        df = pd.read_excel(path)
    elif ext == ".csv":
        df = pd.read_csv(path)
    elif ext == ".txt":
        df = pd.read_csv(path, sep=r"[,\s\t]+", engine="python", header=None)
    else:
        raise ValueError("Unsupported file format")

    if df.shape[1] == 2:
        df.insert(0, "Point", [f"P{i+1}" for i in range(len(df))])
        df.columns = ["Point", "X", "Y"]
    elif df.shape[1] >= 3:
        df = df.iloc[:, :3]
        df.columns = ["Point", "X", "Y"]

    return df
