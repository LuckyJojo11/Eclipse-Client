import customtkinter as ctk
from data_reader import *
from instances_file_manager import *
from PIL import Image

class frame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#2b2b2b")

        self.name = ""
        self.version = ""
        self.loader_info = []

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)


        self.title = ctk.CTkLabel(self, text=self.name, font=("consolas", 16), anchor="nw")
        self.title.grid(row=0, column=0, padx=2, pady=2, sticky="nw")

        self.version_display = ctk.CTkLabel(self, text=self.version, font=("consolas", 14), anchor="nw")
        self.version_display.grid(row=1, column=0, padx=2, pady=(0, 5), sticky="sw")

        self.button_frame = ctk.CTkFrame(self, fg_color="#2b2b2b")
        self.button_frame.grid(row=0, column=1, rowspan=2, padx=2, pady=2, sticky="e")

        self.edit_image = ctk.CTkImage(dark_image=Image.open("lib\\images\\edit.png"), size=(16, 16))
        self.delete_image = ctk.CTkImage(dark_image=Image.open("lib\\images\\delete.png"), size=(16, 16))

        self.edit_button = ctk.CTkButton(self.button_frame, text="", image=self.edit_image, width=32, height=24, fg_color="#1f6aa5", hover_color="#144870", command=self.edit_instance)
        self.edit_button.grid(row=0, column=0, padx=1, pady=(0, 2))

        self.delete_button = ctk.CTkButton(self.button_frame, text="", image=self.delete_image, width=32, height=24, command=self.delete_instance, fg_color="#8f1d1d", hover_color="#651515")
        self.delete_button.grid(row=1, column=0, padx=1, pady=(2, 0))

        self.bind_all(self)
        self.configure(cursor="hand2")

    def bind_all(self, widget):
        if widget in [self.button_frame, self.edit_button, self.delete_button]:
            return
        widget.bind("<Button-1>", self.clicked)
        for child in widget.winfo_children():
            self.bind_all(child)

    def clicked(self, event):
        app = self.winfo_toplevel()
        app.inspector.show("instance")
        loader_name = self.loader_info[0] if len(self.loader_info) > 0 else "Vanilla"
        app.inspector.frame_config(text=self.name, btn_start_text=f"Launch {loader_name} {self.version}", start_instance=self.name)

    def edit_instance(self):
        self.winfo_toplevel().inspector.show("editor", self.name)

    def delete_instance(self):
        delete_instance(self.name)
        app = self.winfo_toplevel()
        app.instances.refresh()
        app.inspector.show("instance")
        
    def refresh(self):
        loader_name = self.loader_info[0] if len(self.loader_info) > 0 else "Vanilla"
        self.title.configure(text=self.name)
        self.version_display.configure(text=(loader_name + " " + self.version))
