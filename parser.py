import re
import pandas as pd

# ==================================================
# Helpers
# ==================================================

def clean_angle(val: str) -> float:
    """
    Accepts:
    - Decimal degrees: 27.69595
    - Decimal with symbol: 27.69595°
    - DMS symbols: 27°41'59.88" N
    - DMS words: 27degree 41min 59.88sec N
    - DMS spaces: 27 41 59.88 N
    - Hemisphere letters: N E S W (case-insensitive)
    """

    s = str(val).strip().upper()

    # --------------------------------------------------
    # DMS with symbols: 27°41'59.88" N
    # --------------------------------------------------
    dms_symbol = re.match(
        r"""^\s*
        (\d+(?:\.\d+)?)\s*[°]\s*
        (\d+(?:\.\d+)?)\s*['’]\s*
        (\d+(?:\.\d+)?)\s*["”]?\s*
        ([NSEW])\s*$
        """,
        s,
        re.VERBOSE
    )

    # --------------------------------------------------
    # DMS with words: 27degree 41min 59.88sec N
    # --------------------------------------------------
    dms_words = re.match(
        r"""^\s*
        (\d+(?:\.\d+)?)\s*
        (?:DEGREE|DEGREES|DEG)\s*
        (\d+(?:\.\d+)?)\s*
        (?:MIN|MINUTE|MINUTES)\s*
        (\d+(?:\.\d+)?)\s*
        (?:SEC|SECOND|SECONDS)\s*
        ([NSEW])\s*$
        """,
        s,
        re.VERBOSE
    )

    # --------------------------------------------------
    # DMS with spaces: 27 41 59.88 N
    # --------------------------------------------------
    dms_spaces = re.match(
        r"""^\s*
        (\d+(?:\.\d+)?)\s+
        (\d+(?:\.\d+)?)\s+
        (\d+(?:\.\d+)?)\s+
        ([NSEW])\s*$
        """,
        s,
        re.VERBOSE
    )

    if dms_symbol or dms_words or dms_spaces:
        m = dms_symbol or dms_words or dms_spaces

        deg = float(m.group(1))
        minute = float(m.group(2))
        sec = float(m.group(3))
        hemi = m.group(4)

        dd = deg + minute / 60 + sec / 3600
        if hemi in ("S", "W"):
            dd = -dd

        return dd

    # --------------------------------------------------
    # Decimal degrees fallback
    # --------------------------------------------------
    return float(
        s.replace("°", "")
         .replace("º", "")
         .replace(",", "")
         .strip()
    )


def dd_to_dms(dd, is_lat=True):
    dd = float(dd)

    deg = int(abs(dd))
    min_float = (abs(dd) - deg) * 60
    minute = int(min_float)
    sec = (min_float - minute) * 60

    if is_lat:
        hemi = "N" if dd >= 0 else "S"
    else:
        hemi = "E" if dd >= 0 else "W"

    return f'{deg}°{minute}\'{sec:.4f}" {hemi}'


# ==================================================
# Column alias resolver
# ==================================================

def find_column(cols, aliases):
    for i, c in enumerate(cols):
        if c in aliases:
            return i
    return None


# ==================================================
# Manual text parsing (comma / tab ONLY)
# ==================================================

def parse_text(text: str, src_crs: str):
    rows = []

    for ln, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue

        # Allow ONLY comma or tab
        if "," in line:
            parts = [p.strip() for p in line.split(",")]
        elif "\t" in line:
            parts = [p.strip() for p in line.split("\t")]
        else:
            raise ValueError(
                f"Line {ln}: Invalid separator. "
                "Use comma (,) or tab only."
            )

        if len(parts) == 2:
            name = ""
            x, y = parts
        elif len(parts) == 3:
            name, x, y = parts
        else:
            raise ValueError(
                f"Line {ln}: Expected 2 or 3 values, got {len(parts)}"
            )

        rows.append([
            name,
            clean_angle(x),
            clean_angle(y)
        ])

    if not rows:
        raise ValueError("No valid coordinate rows found.")

    return pd.DataFrame(rows, columns=["Point", "X", "Y"])


# ==================================================
# File parsing (.txt, .csv, .xlsx)
# ==================================================

def parse_file(path: str, has_header: bool = True):

    ext = path.lower()

    try:
        if ext.endswith(".xlsx"):
            df = pd.read_excel(
                path,
                header=0 if has_header else None
            )

        elif ext.endswith((".csv", ".txt")):
            df = pd.read_csv(
                path,
                header=0 if has_header else None,
                sep=None,
                engine="python"
            )
        else:
            raise ValueError("Unsupported file type. Use .txt, .csv, or .xlsx")

    except Exception as e:
        raise ValueError(f"Failed to read file: {e}")
    
    if not has_header:
        df.columns = range(df.shape[1])

    # --------------------------------------------------
    # Normalize column names
    # --------------------------------------------------
    df.columns = [str(c).strip() for c in df.columns]
    lower_cols = [c.lower() for c in df.columns]

    # Accepted aliases (professional-grade)
    x_aliases = {"x", "e", "easting", "lon", "longitude"}
    y_aliases = {"y", "n", "northing", "lat", "latitude"}
    p_aliases = {"point", "id", "name", "station"}

    x_idx = find_column(lower_cols, x_aliases)
    y_idx = find_column(lower_cols, y_aliases)
    p_idx = find_column(lower_cols, p_aliases)

    # --------------------------------------------------
    # Case 1: Header-based detection
    # --------------------------------------------------
    if x_idx is not None and y_idx is not None:
        out = pd.DataFrame()
        out["Point"] = df.iloc[:, p_idx] if p_idx is not None else ""
        out["X"] = df.iloc[:, x_idx]
        out["Y"] = df.iloc[:, y_idx]

    # --------------------------------------------------
    # Case 2: No headers → positional
    # --------------------------------------------------
    else:
        if df.shape[1] not in (2, 3):
            raise ValueError(
                "Invalid file format.\n"
                "Expected:\n"
                "• X, Y\n"
                "• Point, X, Y\n"
                "Comma or tab separated only."
            )

        out = pd.DataFrame()
        if df.shape[1] == 2:
            out["Point"] = ""
            out["X"] = df.iloc[:, 0]
            out["Y"] = df.iloc[:, 1]
        else:
            out["Point"] = df.iloc[:, 0]
            out["X"] = df.iloc[:, 1]
            out["Y"] = df.iloc[:, 2]

    # --------------------------------------------------
    # Numeric validation
    # --------------------------------------------------
    try:
        out["X"] = out["X"].astype(str).apply(clean_angle)
        out["Y"] = out["Y"].astype(str).apply(clean_angle)
    except Exception:
        raise ValueError(
            "X and Y columns must contain numeric coordinates."
        )

    if out.empty:
        raise ValueError("File contains no valid coordinate rows.")

    return out
