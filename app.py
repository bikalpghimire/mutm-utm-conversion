import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
import pandas as pd

from parser import parse_text, parse_file, dd_to_dms
from transform import transform_all
from kml_export import export_to_kml


APP_TITLE = "Coordinate Transformer --- MUTM | UTM | WGS84 "
FOOTER = "Prepared by: Bikalp Ghimire | Civil Engineer | Pumori Engineering Services (P) Ltd."

MANUAL_PLACEHOLDER = (
    "Example:\n"
    "P1, 634413.7394, 3064905.402\n"
    "634027.2585\t3065117.858"
)


def fmt_latlon(x): return f"{x:.8f}"
def fmt_xy(x): return f"{x:.4f}"


# ==================================================
# AUTO-DETECT COORDINATE ORDER
# ==================================================

def check_consistent_order(xs, ys, src_crs):
    """
    Determines and enforces consistent coordinate order.
    Nepal-specific rule:
    - WGS84: |Latitude| < |Longitude|
    - Projected: |Easting| < |Northing|
    """

    detected = []

    for i, (x, y) in enumerate(zip(xs, ys), start=1):
        if pd.isna(x) or pd.isna(y):
            continue

        ax, ay = abs(x), abs(y)

        # ---------------- WGS84 (Nepal-specific) ----------------
        if src_crs == "WGS84":
            detected.append("LATLON" if ax < ay else "LONLAT")

        # ---------------- Projected (UTM / MUTM) ----------------
        else:
            detected.append("EN" if ax < ay else "NE")

    if not detected:
        raise ValueError("No valid coordinate rows found.")

    first = detected[0]
    for d in detected:
        if d != first:
            raise ValueError(
                "Inconsistent coordinate order detected.\n\n"
                "Some rows appear as X,Y while others appear as Y,X.\n"
                "Please ensure all rows use the same coordinate order."
            )

    return first

class StartupWindow(ttk.Toplevel):
    def __init__(self, master, on_start):
        super().__init__(master)
        self.on_start = on_start

        self.title("MUTM Parameters & Disclaimer")
        self.geometry("720x520")
        self.resizable(False, False)

        self.protocol("WM_DELETE_WINDOW", self.start_app)

        # ✅ DEFINE container FIRST
        container = ttk.Frame(self, padding=20)
        container.pack(fill=BOTH, expand=True)

        # ---------- Title ----------
        ttk.Label(
            container,
            text="Modified Universal Transverse Mercator (MUTM)",
            font=("TkDefaultFont", 14, "bold")
        ).pack(anchor="w", pady=(0, 6))

        # ---------- Projection Parameters ----------
        param_frame = ttk.Frame(container)
        param_frame.pack(anchor="w", fill="x", padx=(10, 0))

        params = [
            ("Projection", "Transverse Mercator"),
            ("Scale factor (k₀)", "0.9999"),
            ("False Easting", "500,000 m"),
            ("False Northing", "0 m"),
            ("Ellipsoid", "Everest 1830 (Modified 1937)"),
            ("Semi-major axis (a)", "6,377,276.345 m"),
            ("Inverse flattening (1/f)", "300.8017"),
            ("Central Meridians", "81°, 84°, 87°"),
        ]

        # Give breathing room
        param_frame.grid_columnconfigure(1, minsize=160)  # left value width
        param_frame.grid_columnconfigure(2, minsize=40)   # separator gap
        param_frame.grid_columnconfigure(4, minsize=160)  # right value width

        # Single vertical separator (does NOT affect row height)
        sep = ttk.Separator(param_frame, orient="vertical")
        sep.grid(
            row=0,
            column=2,
            rowspan=(len(params) + 1) // 2,
            sticky="ns",
            padx=(12, 24)
        )


        for i in range(0, len(params), 2):
            row = i // 2

            # Left pair
            k1, v1 = params[i]
            ttk.Label(param_frame, text=f"{k1}:").grid(row=row, column=0, sticky="w", pady=2)
            ttk.Label(param_frame, text=v1).grid(row=row, column=1, sticky="w", padx=(8, 0), pady=2)


            # Right pair (if exists)
            if i + 1 < len(params):
                k2, v2 = params[i + 1]
                ttk.Label(param_frame, text=f"{k2}:").grid(row=row, column=3, sticky="w", pady=2)
                ttk.Label(param_frame, text=v2).grid(row=row, column=4, sticky="w", padx=(8, 0), pady=2)


        # ---------- Datum Transformation ----------
        ttk.Label(
            container,
            text="Datum Transformation:",
            font=("TkDefaultFont", 11, "bold")
        ).pack(anchor="w", pady=(8, 2))

        datum = ttk.Entry(container)
        datum.insert(0, "TOWGS84 = (295, 736, 257)")
        datum.configure(state="readonly")
        datum.pack(anchor="w", fill="x", padx=(10, 0))

        # ---------- Source / Disclaimer ----------
        info = tk.Text(
            container,
            height=5,
            wrap="word",
            borderwidth=0,
            background=self.cget("background")
        )
        info.insert(
            "1.0",
            "Source:\n"
            "Survey Report submitted by ADPi to\n"
            "Air Transport Capacity Enhancement Project (AETCEP),\n"
            "Sinamangal, Kathmandu.\n\n"
            "These parameters are used for engineering and\n"
            "survey reference purposes only."
        )
        info.configure(state="disabled")
        info.pack(fill="x", pady=(6, 8))

        ttk.Separator(container).pack(fill="x", pady=(6, 6))

        # ---------- Prepared by (left-aligned, clickable email) ----------
        prepared = tk.Text(
            container,
            height=3,
            wrap="word",
            borderwidth=0,
            background=self.cget("background"),
            cursor="arrow"
        )

        prepared.insert(
            "1.0",
            "Prepared by:\n"
            "Bikalp Ghimire | Civil Engineer | Pumori Engineering Services (P) Ltd.\n"
            "Email: "
        )

        # Insert clickable email
        prepared.insert("end", "bikalp.pumori@gmail.com", "email")

        prepared.insert(
            "end",
            " | Contact No.: +9779860477581"
        )

        # Configure clickable email
        prepared.tag_configure("email", foreground="blue", underline=1)
        prepared.tag_bind(
            "email",
            "<Button-1>",
            lambda e: __import__("webbrowser").open("mailto:bikalp.pumori@gmail.com")
        )

        prepared.configure(state="disabled")
        prepared.pack(fill="x", pady=(0, 6))


        ttk.Button(
            container,
            text="Start Application",
            bootstyle=SUCCESS,
            width=20,
            command=self.start_app
        ).pack(pady=(8, 0))

        self.after(30000, self.start_app)

    def start_app(self):
        if self.winfo_exists():
            self.destroy()
            self.on_start()


class App(ttk.Window):
    def __init__(self):
        super().__init__(themename="flatly")
        self.title(APP_TITLE)
        self.geometry("800x500")
        self.minsize(600, 500)
        self._build_ui()

    # ==================================================
    # UI
    # ==================================================
    def _build_ui(self):
        padx, pady = 12, 8
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --------------------------------------------------
        # Source CRS
        # --------------------------------------------------
        src = ttk.LabelFrame(self, text="Source Coordinate System")
        src.grid(row=0, column=0, sticky="ew", padx=padx, pady=(pady, 4))

        self.src_crs = ttk.Combobox(
            src,
            values=["MUTM81", "MUTM84", "MUTM87", "WGS84", "UTM44", "UTM45"],
            state="readonly",
            width=16
        )
        self.src_crs.set("MUTM84")
        self.src_crs.pack(anchor="w", padx=padx, pady=6)

        self.src_crs.bind(
            "<<ComboboxSelected>>",
            lambda e: self._sync_output_checkboxes()
        )


        # --------------------------------------------------
        # Input type
        # --------------------------------------------------
        mode = ttk.LabelFrame(self, text="Input Type")
        mode.grid(row=1, column=0, sticky="ew", padx=padx, pady=4)

        self.mode = ttk.StringVar(value="manual")
        ttk.Radiobutton(mode, text="Manual Input",
                        variable=self.mode, value="manual",
                        command=self._toggle_mode).pack(side=LEFT, padx=padx)
        ttk.Radiobutton(mode, text="File Input",
                        variable=self.mode, value="file",
                        command=self._toggle_mode).pack(side=LEFT)

        # --------------------------------------------------
        # Input container
        # --------------------------------------------------
        self.input_container = ttk.Frame(self)
        self.input_container.grid(row=2, column=0, sticky="nsew", padx=padx, pady=4)
        self.input_container.grid_rowconfigure(0, weight=1)
        self.input_container.grid_columnconfigure(0, weight=1)

        # Manual input
        self.manual_frame = ttk.LabelFrame(self.input_container, text="Manual Coordinate Input")
        self.manual_frame.grid(row=0, column=0, sticky="nsew")

        self.manual_text = ttk.Text(
            self.manual_frame,
            font=("Consolas", 11),
            foreground="gray"
        )
        self.manual_text.pack(fill=BOTH, expand=True, padx=padx, pady=pady)

        # Insert placeholder
        self.manual_text.insert("1.0", MANUAL_PLACEHOLDER)


        # File input
        self.file_frame = ttk.LabelFrame(self.input_container, text="File Input")
        self.file_frame.grid(row=0, column=0, sticky="ew")
        self.file_frame.grid_columnconfigure(0, weight=1)

        file_row = ttk.Frame(self.file_frame)
        file_row.grid(row=0, column=0, sticky="ew", padx=padx, pady=(pady, 2))
        file_row.grid_columnconfigure(0, weight=1)

        self.file_entry = ttk.Entry(
            file_row,
            foreground="gray"
        )
        self.file_entry.insert(0, ".csv, .xlsx, .txt")
        self.file_entry.grid(row=0, column=0, sticky="ew")


        ttk.Button(file_row, text="Browse",
                   command=self._browse).grid(row=0, column=1, padx=(8, 0))

        self.file_info = ttk.Label(
            self.file_frame,
            text="Expected format: (Point, Value1, Value2) or (Value1, Value2)",
            foreground="gray"
        )

        self.file_info.grid(row=1, column=0, sticky="w", padx=padx, pady=(4, 6))

        self.has_header = ttk.BooleanVar(value=True)

        ttk.Checkbutton(
            self.file_frame,
            text="File has header row",
            variable=self.has_header
        ).grid(row=2, column=0, sticky="w", padx=padx, pady=(0, 6))

        self.file_frame.grid_remove()

        # --------------------------------------------------
        # Output options
        # --------------------------------------------------
        out = ttk.LabelFrame(self, text="Output Coordinate Systems")
        out.grid(row=3, column=0, sticky="ew", padx=padx, pady=6)
        out.grid_columnconfigure((0, 1, 2), weight=1)

        self.out_wgs = ttk.BooleanVar(value=True)
        self.out_utm = ttk.BooleanVar(value=True)
        self.out_mutm = ttk.BooleanVar(value=True)

        def _clear_placeholder(event):
            if self.manual_text.get("1.0", "end-1c") == MANUAL_PLACEHOLDER:
                self.manual_text.delete("1.0", END)
                self.manual_text.configure(foreground="black")

        def _restore_placeholder(event):
            if not self.manual_text.get("1.0", "end-1c").strip():
                self.manual_text.insert("1.0", MANUAL_PLACEHOLDER)
                self.manual_text.configure(foreground="gray")

        self.manual_text.bind("<FocusIn>", _clear_placeholder)
        self.manual_text.bind("<FocusOut>", _restore_placeholder)


        def system_block(parent, label_text, var):
            frame = ttk.Frame(parent)
            frame.pack(anchor="w")

            header = ttk.Frame(frame)
            header.pack(anchor="w")

            ttk.Checkbutton(header, variable=var).pack(side=LEFT)
            lbl = ttk.Label(header, text=label_text,
                            font=("TkDefaultFont", 10, "bold"))
            lbl.pack(side=LEFT, padx=(4, 0))

            opts = ttk.Frame(frame)
            opts.pack(anchor="w", padx=(22, 0), pady=(4, 0))

            def toggle(*_):
                state = NORMAL if var.get() else DISABLED
                for c in opts.winfo_children():
                    c.configure(state=state)
                lbl.configure(font=("TkDefaultFont", 10, "bold" if var.get() else "normal"))

            var.trace_add("write", toggle)
            toggle()

            return opts

        # WGS84
        wgs = ttk.Frame(out)
        wgs.grid(row=0, column=0, sticky="w", padx=30)
        wgs_opts = system_block(wgs, "WGS84", self.out_wgs)

        self.wgs_fmt = ttk.StringVar(value="DD")
        ttk.Radiobutton(wgs_opts, text="Decimal Degrees",
                        variable=self.wgs_fmt, value="DD").pack(anchor="w")
        ttk.Radiobutton(wgs_opts, text="DMS",
                        variable=self.wgs_fmt, value="DMS").pack(anchor="w")

        # UTM
        utm = ttk.Frame(out)
        utm.grid(row=0, column=1, sticky="w", padx=30)
        utm_opts = system_block(utm, "UTM", self.out_utm)

        self.utm_zone = ttk.StringVar(value="45")
        ttk.Radiobutton(utm_opts, text="Zone 44",
                        variable=self.utm_zone, value="44").pack(anchor="w")
        ttk.Radiobutton(utm_opts, text="Zone 45",
                        variable=self.utm_zone, value="45").pack(anchor="w")

        # MUTM
        mutm = ttk.Frame(out)
        mutm.grid(row=0, column=2, sticky="w", padx=30)
        mutm_opts = system_block(mutm, "MUTM", self.out_mutm)

        self.mutm_zone = ttk.StringVar(value="84")
        for cm in ("81", "84", "87"):
            ttk.Radiobutton(mutm_opts, text=f"CM {cm}",
                            variable=self.mutm_zone, value=cm).pack(anchor="w")

        # --------------------------------------------------
        # Transform button
        # --------------------------------------------------
        ttk.Button(
            self,
            text="Transform Coordinates",
            bootstyle=SUCCESS,
            width=28,
            command=self.run
        ).grid(row=4, column=0, pady=10)

        ttk.Label(self, text=FOOTER, foreground="gray").grid(row=5, column=0, pady=(0, 6))

        self._sync_output_checkboxes()

    # ==================================================
    def _toggle_mode(self):
        if self.mode.get() == "file":
            self.manual_frame.grid_remove()
            self.file_frame.grid()
        else:
            self.file_frame.grid_remove()
            self.manual_frame.grid()

    def _sync_output_checkboxes(self):
        src = self.src_crs.get()

        self.out_wgs.set(src != "WGS84")
        self.out_utm.set(not src.startswith("UTM"))
        self.out_mutm.set(not src.startswith("MUTM"))


    def _browse(self):
        f = filedialog.askopenfilename(
            filetypes=[("Data files", "*.txt *.csv *.xlsx")]
        )
        if f:
            self.file_entry.delete(0, END)
            self.file_entry.insert(0, f)

    # ==================================================
    # Main run
    # ==================================================
    def run(self):
        text = self.manual_text.get("1.0", END)
        if text.strip() == MANUAL_PLACEHOLDER.strip():
            raise ValueError("Please enter coordinate data before transforming.")

        try:
            self._sync_output_checkboxes()
            # ---------- INPUT ----------
            df_in = (
                parse_text(self.manual_text.get("1.0", END), self.src_crs.get())
                if self.mode.get() == "manual"
                else parse_file(self.file_entry.get(), self.has_header.get())
            )

            # Ensure ALL rows use the same order
            order = check_consistent_order(
                df_in["X"].astype(float),
                df_in["Y"].astype(float),
                self.src_crs.get()
            )



            # Normalize internal order → X = E/Lon, Y = N/Lat
            if order in ("NE", "LATLON"):
                df_in[["X", "Y"]] = df_in[["Y", "X"]]

            # ---------- TRANSFORM ----------
            rows = transform_all(
                df_in,
                self.src_crs.get(),
                int(self.utm_zone.get()),
                int(self.mutm_zone.get())
            )

            df_all = pd.DataFrame(rows, columns=[
                "Point",
                "WGS84_Lat", "WGS84_Lon",
                "UTM_E", "UTM_N", "UTM_Zone",
                "MUTM_E", "MUTM_N", "MUTM_CM"
            ])

            src = self.src_crs.get()
            df_out = pd.DataFrame()
            df_out["Point"] = df_in["Point"]

            src = self.src_crs.get()

            # ---------------- INPUT COLUMN NAMES ----------------
            if src == "WGS84":
                if order == "LATLON":
                    df_out["WGS84_Lat"] = df_in["Y"].apply(fmt_latlon)
                    df_out["WGS84_Lon"] = df_in["X"].apply(fmt_latlon)
                else:  # LONLAT
                    df_out["WGS84_Lon"] = df_in["X"].apply(fmt_latlon)
                    df_out["WGS84_Lat"] = df_in["Y"].apply(fmt_latlon)

            else:
                # MUTM / UTM → preserve original order
                if order == "EN":
                    df_out[f"{src}_E"] = df_in["X"].apply(fmt_xy)
                    df_out[f"{src}_N"] = df_in["Y"].apply(fmt_xy)
                else:  # NE
                    df_out[f"{src}_N"] = df_in["Y"].apply(fmt_xy)
                    df_out[f"{src}_E"] = df_in["X"].apply(fmt_xy)

            outputs = []

            # ---------- WGS84 ----------
            if self.out_wgs.get():
                outputs.append("WGS84")

                if self.wgs_fmt.get() == "DMS":
                    lat = df_all["WGS84_Lat"].apply(lambda v: dd_to_dms(v, is_lat=True))
                    lon = df_all["WGS84_Lon"].apply(lambda v: dd_to_dms(v, is_lat=False))
                else:
                    lat = df_all["WGS84_Lat"].apply(fmt_latlon)
                    lon = df_all["WGS84_Lon"].apply(fmt_latlon)

                if order == "LONLAT":
                    df_out["WGS84_Lon"] = lon
                    df_out["WGS84_Lat"] = lat
                else:
                    df_out["WGS84_Lat"] = lat
                    df_out["WGS84_Lon"] = lon


            # ---------- UTM ----------
            if self.out_utm.get():
                z = self.utm_zone.get()
                outputs.append(f"UTM{z}")
                e = df_all["UTM_E"].apply(fmt_xy)
                n = df_all["UTM_N"].apply(fmt_xy)

                if order == "NE":
                    df_out[f"UTM{z}_N"] = n
                    df_out[f"UTM{z}_E"] = e
                else:
                    df_out[f"UTM{z}_E"] = e
                    df_out[f"UTM{z}_N"] = n

            # ---------- MUTM ----------
            if self.out_mutm.get():
                z = self.mutm_zone.get()
                outputs.append(f"MUTM{z}")
                e = df_all["MUTM_E"].apply(fmt_xy)
                n = df_all["MUTM_N"].apply(fmt_xy)

                if order == "NE":
                    df_out[f"MUTM{z}_N"] = n
                    df_out[f"MUTM{z}_E"] = e
                else:
                    df_out[f"MUTM{z}_E"] = e
                    df_out[f"MUTM{z}_N"] = n
            self.df_out = df_out
            self._show_preview(df_out, outputs)

        except Exception as e:
            messagebox.showerror("Error", str(e))
    # ---- Export to KML ----
    def export_kml(self):
        if not hasattr(self, "df_out"):
            messagebox.showwarning(
                "No Data",
                "Please run the conversion before exporting KML."
            )
            return

        if "WGS84_Lat" not in self.df_out or "WGS84_Lon" not in self.df_out:
            messagebox.showerror(
                "Missing Data",
                "WGS84 coordinates are required for KML export."
            )
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".kml",
            filetypes=[("KML files", "*.kml")]
        )

        if not path:
            return

        export_to_kml(
            filepath=path,
            names=self.df_out.get("Point", []),
            lats=self.df_out["WGS84_Lat"],
            lons=self.df_out["WGS84_Lon"],
            crs_name=self.src_crs.get()
        )

        messagebox.showinfo(
            "Export Complete",
            f"KML file successfully saved:\n{path}"
        )

    # ==================================================
    # Preview + export + copy headers
    # ==================================================
    def _show_preview(self, df, outputs):
        win = ttk.Toplevel(self)
        win.title("Transformation Results Preview")
        win.geometry("1200x500")
        win.grab_set()

        ttk.Label(
            win,
            text=f"Input CRS: {self.src_crs.get()} | Output CRS: {', '.join(outputs)}",
            font=("TkDefaultFont", 10, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        frame = ttk.Frame(win)
        frame.pack(fill=BOTH, expand=True, padx=10, pady=5)

        tree = ttk.Treeview(frame, columns=list(df.columns), show="headings")
        tree.pack(fill=BOTH, expand=True)

        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=140)

        for _, r in df.iterrows():
            tree.insert("", END, values=list(r))

        # ---- Copy including headers ----
        def copy_selected(event=None):
            rows = ["\t".join(df.columns)]
            for i in tree.selection():
                rows.append("\t".join(map(str, tree.item(i)["values"])))
            win.clipboard_clear()
            win.clipboard_append("\n".join(rows))

        tree.bind("<Control-c>", copy_selected)

        # ---- Export to Excel ----
        def export_excel():
            path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel file", "*.xlsx")]
            )
            if path:
                df.to_excel(path, index=False)
                messagebox.showinfo("Exported", f"Saved to:\n{path}")
        

        btns = ttk.Frame(win)
        btns.pack(pady=6)

        ttk.Button(
            btns, text="Export to Excel",
            bootstyle=SUCCESS,
            command=export_excel
        ).pack(side=LEFT, padx=10)

        ttk.Button(
            btns,
            text="Export KML",
            bootstyle=INFO,
            command=self.export_kml
        ).pack(side="left", padx=10)


        ttk.Button(
            btns, text="Close",
            command=win.destroy
        ).pack(side=LEFT, padx=10)


if __name__ == "__main__":
    root = App()
    root.withdraw()  # hide main window initially

    def show_main_app():
        root.deiconify()

    StartupWindow(root, show_main_app)
    root.mainloop()

