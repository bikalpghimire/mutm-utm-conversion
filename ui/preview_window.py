import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox


def show_preview(parent, df, outputs):
    win = ttk.Toplevel(parent)
    win.title("Transformation Results Preview")
    win.geometry("1200x500")
    win.grab_set()

    ttk.Label(
        win,
        text=f"Input CRS: {parent.src_crs.get()} | Output CRS: {', '.join(outputs)}",
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
        command=parent.export_kml
    ).pack(side=LEFT, padx=10)

    ttk.Button(
        btns, text="Close",
        command=win.destroy
    ).pack(side=LEFT, padx=10)
