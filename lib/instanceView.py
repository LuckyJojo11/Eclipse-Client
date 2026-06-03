import customtkinter as ctk
import launcher
from data_reader import *
from instances_file_manager import *


class frame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.fg_color="#000000"

        self.start_instance = ""
        self.version = ""
        self.loader = ["Vanilla", ""]
        self.ram = 4096
        self.demo = ctk.BooleanVar(value=False)
        self.updating_settings = False

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.title = ctk.CTkLabel(self, text=self.start_instance, font=("consolas", 24))
        self.title.grid(row=0, column=0, padx=2, pady=2, sticky="new")

        self.start_button = ctk.CTkButton(self, text=f"Launch {self.loader[0]} {self.version}", font=("consolas", 24), command=self.run_game, width=100, height=40)
        self.start_button.grid(row=1, column=0, sticky="", padx=2, pady=2)

        self.restart_button = ctk.CTkButton(self, text="Restart", font=("consolas", 18), command=self.restart_game, width=120)
        self.restart_button.grid(row=2, column=0, sticky="", padx=2, pady=(0, 8))
        self.restart_button.grid_remove()

        self.settings_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.settings_frame.grid(row=3, column=0, sticky="ew", padx=8, pady=8)
        self.settings_frame.grid_columnconfigure(1, weight=1)

        self.ram_label = ctk.CTkLabel(self.settings_frame, text="RAM", font=("consolas", 14))
        self.ram_label.grid(row=0, column=0, padx=(0, 8), pady=2, sticky="w")

        self.ram_slider = ctk.CTkSlider(self.settings_frame, from_=512, to=16384, number_of_steps=31, command=self.ram_slider_changed)
        self.ram_slider.grid(row=0, column=1, padx=4, pady=2, sticky="ew")

        self.ram_input = ctk.CTkEntry(self.settings_frame, width=80, font=("consolas", 14))
        self.ram_input.grid(row=0, column=2, padx=(8, 4), pady=2, sticky="e")
        self.ram_input.bind("<FocusOut>", self.ram_input_changed)
        self.ram_input.bind("<Return>", self.ram_input_changed)

        self.ram_unit = ctk.CTkLabel(self.settings_frame, text="MB", font=("consolas", 14))
        self.ram_unit.grid(row=0, column=3, padx=(0, 0), pady=2, sticky="w")

        self.separator = ctk.CTkFrame(self.settings_frame, height=1, fg_color="#4a4a4a")
        self.separator.grid(row=1, column=0, columnspan=4, padx=0, pady=8, sticky="ew")

        self.demo_checkbox = ctk.CTkCheckBox(self.settings_frame, text="Demo Version", variable=self.demo, command=self.demo_changed, font=("consolas", 14))
        self.demo_checkbox.grid(row=2, column=0, columnspan=2, padx=0, pady=(0, 2), sticky="w")

        self.mods_button = ctk.CTkButton(self.settings_frame, text="Mods", command=self.open_mods, width=120)
        self.mods_button.grid(row=2, column=2, columnspan=2, sticky="e", padx=0, pady=(0, 2))

        launcher.set_state_callback(self.game_state_changed)

        self.refresh()

    def run_game(self):
        if self.start_instance == "":
            return
        self.ram_input_changed()
        if is_instance_running(self.start_instance):
            kill_instance(self.start_instance)
        else:
            self.winfo_toplevel().clicked()
            start_instance(self.start_instance)
        self.refresh()

    def restart_game(self):
        if self.start_instance == "":
            return
        self.ram_input_changed()
        restart_instance(self.start_instance)
        self.refresh()

    def game_state_changed(self, instance_name):
        if instance_name == self.start_instance:
            self.after(0, self.refresh)

    def set_text(self, text):
        self.title.configure(text=text)

    def set_btn_text(self, text):
        self.start_button.configure(text=text)

    def set_start_instance(self, instance):
        self.start_instance = instance
        self.refresh()

    def normalize_ram(self, value):
        try:
            ram = int(float(value))
        except Exception:
            ram = 4096
        ram = max(512, min(16384, ram))
        return int(round(ram / 512) * 512)

    def set_ram_ui(self, ram):
        self.updating_settings = True
        self.ram = self.normalize_ram(ram)
        self.ram_slider.set(self.ram)
        self.ram_input.delete(0, "end")
        self.ram_input.insert(0, str(self.ram))
        self.updating_settings = False

    def save_launch_settings(self):
        if self.updating_settings or self.start_instance == "":
            return
        update_instance_launch_settings(self.start_instance, self.ram, self.demo.get())

    def ram_slider_changed(self, value):
        if self.updating_settings:
            return
        self.set_ram_ui(value)
        self.save_launch_settings()

    def ram_input_changed(self, event=None):
        self.set_ram_ui(self.ram_input.get())
        self.save_launch_settings()

    def demo_changed(self):
        self.save_launch_settings()

    def is_modded(self):
        loader_name = self.loader[0] if len(self.loader) > 0 else "Vanilla"
        return loader_name in ["Fabric", "Forge", "NeoForge"]

    def open_mods(self):
        if self.start_instance == "" or not self.is_modded():
            return
        self.master.show("mods", self.start_instance)

    def refresh(self):
        instances = get_all_instances()
        selected = get_instance(self.start_instance)
        if selected is None and instances:
            selected = instances[0]

        if selected is None:
            self.start_instance = ""
            self.version = ""
            self.loader = ["Vanilla", ""]
            self.title.configure(text="No instances")
            self.start_button.configure(text="Create an instance", state="disabled")
            self.restart_button.grid_remove()
            self.settings_frame.grid_remove()
            self.mods_button.grid_remove()
            return

        self.start_instance = selected.get("name", "")
        self.version = selected.get("version", "")
        self.loader = selected.get("mod_info", ["Vanilla", ""])
        self.ram = selected.get("ram", 4096)
        loader_name = self.loader[0] if len(self.loader) > 0 else "Vanilla"
        running = is_instance_running(self.start_instance)

        self.title.configure(text=self.start_instance)
        if running:
            self.start_button.configure(text=f"Kill {loader_name} {self.version}", state="normal", fg_color="#8f1d1d", hover_color="#651515")
            self.restart_button.configure(text=f"Restart {loader_name} {self.version}")
            self.restart_button.grid()
        else:
            self.start_button.configure(text=f"Launch {loader_name} {self.version}", state="normal", fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"], hover_color=ctk.ThemeManager.theme["CTkButton"]["hover_color"])
            self.restart_button.grid_remove()
        self.settings_frame.grid()
        self.set_ram_ui(self.ram)
        self.demo.set(bool(selected.get("demo", False)))
        if self.is_modded():
            self.mods_button.grid()
        else:
            self.mods_button.grid_remove()
