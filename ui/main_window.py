# ui/main_window.py
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox

from controllers.run_controller import run_transform
from ui.preview_window import show_preview
from utils.formatters import fmt_latlon, fmt_xy

APP_TITLE = "Coordinate Transformer --- MUTM | UTM | WGS84 "
FOOTER = "Prepared by: Bikalp Ghimire | Civil Engineer | Pumori Engineering Services (P) Ltd."

MANUAL_PLACEHOLDER = (
    "Example:\n"
    "P1, 634413.7394, 3064905.402\n"
    "634027.2585\t3065117.858"
)


class App(ttk.Window):
    def __init__(self):
        super().__init__(themename="flatly")
        self.title(APP_TITLE)
        self.geometry("800x500")
        self.minsize(600, 500)
        self._build_ui()

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

        # ---- Manual input Text widget (placeholder in gray) ----
        self.manual_text = ttk.Text(
            self.manual_frame,
            font=("Consolas", 11),
            foreground="gray"
        )
        self.manual_text.pack(fill=BOTH, expand=True, padx=padx, pady=pady)

        # Insert placeholder
        self.manual_text.insert("1.0", MANUAL_PLACEHOLDER)

        # ---- Placeholder behavior ----
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
        self.file_entry.grid(row=0, column=0, sticky="ew")

        # ---- File entry placeholder behavior ----
        FILE_PLACEHOLDER = ".csv, .xlsx, .txt"

        self.file_entry.delete(0, END)
        self.file_entry.insert(0, FILE_PLACEHOLDER)
        self.file_entry.configure(foreground="gray")

        def _clear_file_placeholder(event):
            if self.file_entry.get() == FILE_PLACEHOLDER:
                self.file_entry.delete(0, END)
                self.file_entry.configure(foreground="black")

        def _restore_file_placeholder(event):
            if not self.file_entry.get().strip():
                self.file_entry.insert(0, FILE_PLACEHOLDER)
                self.file_entry.configure(foreground="gray")

        self.file_entry.bind("<FocusIn>", _clear_file_placeholder)
        self.file_entry.bind("<FocusOut>", _restore_file_placeholder)



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


    def run(self):
        """UI callback only"""
        try:
            df_out, outputs = run_transform(self)
            self.df_out = df_out
            show_preview(self, df_out, outputs)
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
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
        
        from tkinter import filedialog
        from kml_export import export_to_kml

        path = filedialog.asksaveasfilename(
            defaultextension=".kml",
            filetypes=[("KML files", "*.kml")]
        )

        if not path:
            return

        export_to_kml(
            filepath=path,
            names=self.df_out["Point"],
            lats=self.df_out["WGS84_Lat"].astype(float),
            lons=self.df_out["WGS84_Lon"].astype(float),
            crs_name=self.src_crs.get()
        )


        messagebox.showinfo(
            "Export Complete",
            f"KML file successfully saved:\n{path}"
        )

