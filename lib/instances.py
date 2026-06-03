import customtkinter as ctk
import launcher
from data_reader import *
from instances_file_manager import *
import single_instance_display
import editInstance

class frame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.displays = []
        self.empty_label = None

        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.grid(row=0, column=0, sticky="ew", padx=2, pady=2)
        self.header.grid_columnconfigure(0, weight=1)

        self.title = ctk.CTkLabel(self, text="Instances", font=("consolas", 24))
        self.title.grid(row=0, column=0, padx=2, pady=2, sticky="w")

        self.new_instance_button = ctk.CTkButton(
            self.header,
            text="+",
            font=("consolas", 24),
            command=self.create_instance,
            width=35
        )
        self.new_instance_button.grid(row=0, column=1, padx=2, pady=2, sticky="e")

        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_frame.grid(row=1, column=0, sticky="nsew", padx=2, pady=(0, 2))
        self.list_frame.grid_columnconfigure(0, weight=1)

        self.refresh()
        self.toplevel = None

    def create_instance(self):
        self.master.inspector.show("editor")

    def refresh(self):
        for display in self.displays:
            display.destroy()
        self.displays.clear()

        if self.empty_label is not None:
            self.empty_label.destroy()
            self.empty_label = None

        instances = get_all_instances()
        if not instances:
            self.empty_label = ctk.CTkLabel(self.list_frame, text="No instances yet", font=("consolas", 14))
            self.empty_label.grid(row=0, column=0, sticky="new", padx=2, pady=12)
            return

        for index, i in enumerate(instances):
            display = single_instance_display.frame(self.list_frame)
            display.name = i.get("name", "")
            display.version = i.get("version", "")
            display.loader_info = i.get("mod_info", ["Vanilla", ""])
            display.grid(row=index, column=0, sticky="new", padx=2, pady=2)
            display.refresh()

            self.displays.append(display)
