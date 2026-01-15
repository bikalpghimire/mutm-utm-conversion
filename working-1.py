import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
import pandas as pd

from parser import parse_text, parse_file, dd_to_dms
from transform import transform_all

APP_TITLE = "Universal Coordinate Transformer"
FOOTER = "Prepared by: Bikalp Ghimire | Civil Engineer"


def fmt_latlon(x): return f"{x:.8f}"
def fmt_xy(x): return f"{x:.4f}"


class App(ttk.Window):
    def __init__(self):
        super().__init__(themename="flatly")
        self.title(APP_TITLE)
        self.geometry("1200x820")
        self.minsize(1100, 740)
        self._build_ui()

    # ==================================================
    # UI
    # ==================================================
    def _build_ui(self):
        padx, pady = 12, 8
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --------------------------------------------------
        # Source CRS + Order
        # --------------------------------------------------
        src = ttk.LabelFrame(self, text="Source Coordinate System")
        src.grid(row=0, column=0, sticky="ew", padx=padx, pady=(pady, 4))
        src.grid_columnconfigure(0, weight=1)

        top = ttk.Frame(src)
        top.grid(row=0, column=0, sticky="w", padx=padx, pady=4)

        self.src_crs = ttk.Combobox(
            top,
            values=["MUTM81", "MUTM84", "MUTM87", "WGS84", "UTM44", "UTM45"],
            state="readonly",
            width=16
        )
        self.src_crs.set("MUTM84")
        self.src_crs.pack(side=LEFT, padx=(0, 20))
        self.src_crs.bind("<<ComboboxSelected>>", self._update_order_labels)

        self.coord_order = ttk.StringVar(value="XY")
        self.rb1 = ttk.Radiobutton(top, variable=self.coord_order, value="XY")
        self.rb2 = ttk.Radiobutton(top, variable=self.coord_order, value="YX")
        self.rb1.pack(side=LEFT)
        self.rb2.pack(side=LEFT, padx=(10, 0))

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

        self.manual_text = ttk.Text(self.manual_frame, font=("Consolas", 11))
        self.manual_text.pack(fill=BOTH, expand=True, padx=padx, pady=pady)

        # File input
        self.file_frame = ttk.LabelFrame(self.input_container, text="File Input")
        self.file_frame.grid(row=0, column=0, sticky="ew")
        self.file_frame.grid_columnconfigure(0, weight=1)

        file_row = ttk.Frame(self.file_frame)
        file_row.grid(row=0, column=0, sticky="ew", padx=padx, pady=(pady, 2))
        file_row.grid_columnconfigure(0, weight=1)

        self.file_entry = ttk.Entry(file_row)
        self.file_entry.grid(row=0, column=0, sticky="ew")

        ttk.Button(file_row, text="Browse",
                   command=self._browse).grid(row=0, column=1, padx=(8, 0))

        self.file_info = ttk.Label(
            self.file_frame,
            text=(
                "Expected file format:\n"
                "• Columns: Point, X, Y  (or X, Y)\n"
                "• Order auto-detected from headers if possible\n"
                "• Supported formats: .txt, .csv, .xlsx"
            ),
            foreground="gray",
            justify="left"
        )
        self.file_info.grid(row=1, column=0, sticky="w", padx=padx, pady=(4, 6))

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

        def system_block(parent, label_text, var):
            frame = ttk.Frame(parent)
            frame.pack(anchor="w")

            header = ttk.Frame(frame)
            header.pack(anchor="w")

            chk = ttk.Checkbutton(header, variable=var)
            chk.pack(side=LEFT)

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

        self._update_order_labels()

    # ==================================================
    def _update_order_labels(self, *_):
        if self.src_crs.get() == "WGS84":
            self.rb1.configure(text="Lon, Lat")
            self.rb2.configure(text="Lat, Lon")
        else:
            self.rb1.configure(text="E, N")
            self.rb2.configure(text="N, E")

    def _toggle_mode(self):
        if self.mode.get() == "file":
            self.manual_frame.grid_remove()
            self.file_frame.grid()
        else:
            self.file_frame.grid_remove()
            self.manual_frame.grid()

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
        try:
            # ---------- INPUT ----------
            if self.mode.get() == "manual":
                df_in = parse_text(self.manual_text.get("1.0", END), self.src_crs.get())
                if self.coord_order.get() == "YX":
                    df_in[["X", "Y"]] = df_in[["Y", "X"]]
            else:
                df_in = parse_file(self.file_entry.get())
                headers = [c.lower() for c in df_in.columns]
                if headers[1:3] in (["lat", "lon"], ["n", "e"]):
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
            df_out[f"{src}_X"] = df_in["X"].apply(fmt_xy)
            df_out[f"{src}_Y"] = df_in["Y"].apply(fmt_xy)

            outputs = []

            if self.out_wgs.get():
                outputs.append("WGS84")

                lat = df_all["WGS84_Lat"].apply(fmt_latlon)
                lon = df_all["WGS84_Lon"].apply(fmt_latlon)

                # Default WGS84 order = Lat, Lon
                if self.src_crs.get() == "WGS84" and self.coord_order.get() == "XY":
                    # Lon, Lat input → Lon, Lat output
                    df_out["WGS84_Lon"] = lon
                    df_out["WGS84_Lat"] = lat
                else:
                    # Default → Lat, Lon
                    df_out["WGS84_Lat"] = lat
                    df_out["WGS84_Lon"] = lon


            if self.out_utm.get():
                z = self.utm_zone.get()
                outputs.append(f"UTM{z}")

                e = df_all["UTM_E"].apply(fmt_xy)
                n = df_all["UTM_N"].apply(fmt_xy)

                if self.coord_order.get() == "YX":
                    # N, E
                    df_out[f"UTM{z}_N"] = n
                    df_out[f"UTM{z}_E"] = e
                else:
                    # E, N
                    df_out[f"UTM{z}_E"] = e
                    df_out[f"UTM{z}_N"] = n

            if self.out_mutm.get():
                z = self.mutm_zone.get()
                outputs.append(f"MUTM{z}")

                e = df_all["MUTM_E"].apply(fmt_xy)
                n = df_all["MUTM_N"].apply(fmt_xy)

                if self.coord_order.get() == "YX":
                    # N, E
                    df_out[f"MUTM{z}_N"] = n
                    df_out[f"MUTM{z}_E"] = e
                else:
                    # E, N
                    df_out[f"MUTM{z}_E"] = e
                    df_out[f"MUTM{z}_N"] = n


            self._show_preview(df_out, outputs)

        except Exception as e:
            messagebox.showerror("Error", str(e))

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

        def copy_selected(event=None):
            items = tree.selection()
            rows = []

            if not items:
                rows.append("\t".join(df.columns))
            else:
                rows.append("\t".join(df.columns))
                for i in items:
                    rows.append("\t".join(map(str, tree.item(i)["values"])))

            win.clipboard_clear()
            win.clipboard_append("\n".join(rows))

        tree.bind("<Control-c>", copy_selected)

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

        ttk.Button(btns, text="Export to Excel",
                   bootstyle=SUCCESS, command=export_excel).pack(side=LEFT, padx=10)
        ttk.Button(btns, text="Close", command=win.destroy).pack(side=LEFT, padx=10)


if __name__ == "__main__":
    App().mainloop()
