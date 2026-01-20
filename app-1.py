import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox

from ui.main_window import App
from ui.startup_window import StartupWindow
from ui.preview_window import show_preview
from controllers.run_controller import run_transform



def run(self):
    try:
        df_out, outputs = run_transform(self)
        show_preview(self, df_out, outputs)
    except Exception as e:
        messagebox.showerror("Error", str(e))

    
if __name__ == "__main__":
    root = App()
    root.withdraw()

    def show_main():
        root.deiconify()

    StartupWindow(root, show_main)
    root.mainloop()
