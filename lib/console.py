import customtkinter as ctk
import launcher
import threading
from data_reader import *

class frame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.configure(fg_color="#000000")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.toolbar = ctk.CTkFrame(self, fg_color="transparent")
        self.toolbar.grid(row=0, column=0, sticky="ew", padx=2, pady=(0, 2))
        self.toolbar.grid_columnconfigure(0, weight=1)

        self.title = ctk.CTkLabel(self.toolbar, text="Console | Game Output", font=("consolas", 18))
        self.title.grid(row=0, column=0, padx=2, pady=2, sticky="w")

        self.copy_button = ctk.CTkButton(self.toolbar, text="Copy", width=80, command=self.copy_log)
        self.copy_button.grid(row=0, column=1, padx=2, pady=2, sticky="e")

        self.clear_button = ctk.CTkButton(self.toolbar, text="Clear", width=80, command=self.clear_log)
        self.clear_button.grid(row=0, column=2, padx=2, pady=2, sticky="e")

        self.console_frame = ctk.CTkTextbox(self, state="disabled", fg_color="#000000", font=("consolas", 18))
        self.console_frame.grid(row=1, column=0, sticky="nsew")

        self.log("Eclipse Client by LuckyJojo11")
        launcher.set_log_callback(self.log)
        
    def refresh(self):
        pass

    def log(self, to_log: str = ""):
        if threading.current_thread() is not threading.main_thread():
            self.after(0, lambda: self.log(to_log))
            return
        self.console_frame.configure(state="normal")
        self.console_frame.insert("end", to_log + "\n")
        self.console_frame.see("end")
        self.console_frame.configure(state="disabled")

    def copy_log(self):
        text = self.console_frame.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(text)

    def clear_log(self):
        self.console_frame.configure(state="normal")
        self.console_frame.delete("1.0", "end")
        self.console_frame.configure(state="disabled")
