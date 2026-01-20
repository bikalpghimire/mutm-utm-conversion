import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


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