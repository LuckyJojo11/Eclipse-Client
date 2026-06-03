import customtkinter as ctk
import instanceView
import editInstance
import modsView
import settings   
from data_reader import *

class frame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.fg_color="#000000"
        self.active_frame = "instance"
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frames = {
            "instance": instanceView.frame(self),
            "editor": editInstance.frame(self),
            "mods": modsView.frame(self),
            "settings": settings.frame(self)
        }

        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")
            frame.grid_remove()

        self.show("instance")

    def show(self, tab, instance_name=""):
        for frame in self.frames.values():
            frame.grid_remove()

        if tab == "editor":
            if instance_name == "":
                self.frames[tab].clear()
            else:
                self.frames[tab].load_instance(instance_name)
        if tab == "mods":
            self.frames[tab].load_instance(instance_name)

        self.frames[tab].grid(row=0, column=0, sticky="nsew")
        self.active_frame = tab
        self.frames[tab].refresh()

    def frame_config(self, text: str = "", btn_start_text: str = "", start_instance: str = ""):
        if not text == "":
            self.frames[self.active_frame].set_text(text)
        if not btn_start_text == "":
            self.frames[self.active_frame].set_btn_text(btn_start_text)
        if not start_instance == "":
            self.frames[self.active_frame].set_start_instance(start_instance)
    
    def refresh(self):
        self.frames[self.active_frame].refresh()
