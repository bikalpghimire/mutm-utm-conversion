import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
import pandas as pd
import os

from parser import parse_text, parse_file
from transform import transform_all

APP_TITLE = "Universal Coordinate Transformer"
FOOTER = "Prepared by: Bikalp Ghimire | Civil Engineer"

class App(ttk.Window):
    def __init__(self):
        super().__init__(themename="flatly")
        self.title(APP_TITLE)
        self.geometry("1100x780")
        self._build()

    def _build(self):
        pad = 10

        # Input mode
        frm_mode = ttk.LabelFrame(self, text="Input Mode")
        frm_mode.pack(fill=X, padx=pad, pady=(pad, 0))

        self.mode = ttk.StringVar(value="text")
        ttk.Radiobutton(frm_mode, text="Manual", variable=self.mode, value="text", command=self._toggle).pack(side=LEFT, padx=pad)
        ttk.Radiobutton(frm_mode, text="File", variable=self.mode, value="file", command=self._toggle).pack(side=LEFT, padx=pad)

        # Manual
        self.frm_text = ttk.LabelFrame(self, text="Manual Coordinate Entry")
        self.frm_text.pack(fill=BOTH, expand=True, padx=pad, pady=pad)

        self.txt = ttk.Text(self.frm_text, height=10, font=("Consolas", 11))
        self.txt.pack(fill=BOTH, expand=True, padx=pad, pady=pad)
        self.txt.insert("1.0", "P1 27°41'01.96\"N 85°21'12.20\"E\n")

        # File
        self.frm_file = ttk.LabelFrame(self, text="File Input")
        self.entry_file = ttk.Entry(self.frm_file, width=95)
        self.entry_file.pack(side=LEFT, padx=pad, pady=pad)
        ttk.Button(self.frm_file, text="Browse", command=self._browse).pack(side=LEFT, padx=pad)

        # CRS
        frm_crs = ttk.LabelFrame(self, text="Source Coordinate System")
        frm_crs.pack(fill=X, padx=pad, pady=pad)

        self.src = ttk.Combobox(
            frm_crs,
            values=["WGS84", "UTM", "MUTM84_CM81", "MUTM84_CM84", "MUTM84_CM87"],
            state="readonly", width=18
        )
        self.src.set("WGS84")
        self.src.grid(row=0, column=1, padx=pad)

        ttk.Label(frm_crs, text="Source CRS").grid(row=0, column=0, padx=pad)

        # WGS output format
        frm_fmt = ttk.LabelFrame(self, text="WGS84 Output Format")
        frm_fmt.pack(fill=X, padx=pad, pady=pad)

        self.wgs_fmt = ttk.StringVar(value="DD")
        ttk.Radiobutton(frm_fmt, text="Decimal Degrees", variable=self.wgs_fmt, value="DD").pack(side=LEFT, padx=pad)
        ttk.Radiobutton(frm_fmt, text="DMS", variable=self.wgs_fmt, value="DMS").pack(side=LEFT, padx=pad)

        ttk.Button(self, text="Transform", bootstyle=SUCCESS, command=self.run).pack(pady=15)
        ttk.Label(self, text=FOOTER, foreground="gray").pack(side=BOTTOM, pady=5)

    def _toggle(self):
        if self.mode.get() == "file":
            self.frm_text.pack_forget()
            self.frm_file.pack(fill=X, padx=10, pady=10)
        else:
            self.frm_file.pack_forget()
            self.frm_text.pack(fill=BOTH, expand=True, padx=10, pady=10)

    def _browse(self):
        f = filedialog.askopenfilename(filetypes=[("Data files", "*.txt *.csv *.xlsx")])
        self.entry_file.delete(0, END)
        self.entry_file.insert(0, f)

    def run(self):
        try:
            if self.mode.get() == "text":
                df = parse_text(self.txt.get("1.0", END), self.src.get())
            else:
                df = parse_file(self.entry_file.get())

            rows = transform_all(df, self.src.get())

            out_df = pd.DataFrame(rows, columns=[
                "Point",
                "WGS84_Latitude", "WGS84_Longitude",
                "UTM_X", "UTM_Y", "UTM_Zone",
                "MUTM_X", "MUTM_Y", "MUTM_CM"
            ])

            win = ttk.Toplevel(self)
            win.title("Results")
            win.geometry("1050x520")

            text = ttk.Text(win, wrap="none", font=("Consolas", 10))
            text.pack(fill=BOTH, expand=True, padx=10, pady=10)
            text.insert("end", out_df.to_string(index=False))

        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    App().mainloop()
