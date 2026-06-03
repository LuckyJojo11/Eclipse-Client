import customtkinter as ctk
from tkinter import filedialog
import threading
import launcher
import mod_manager
from data_reader import *
from instances_file_manager import *

class frame(ctk.CTkScrollableFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        self.loaders = ["Vanilla", "Fabric", "Forge", "NeoForge"]
        self.editing_name = ""
        self.current_version = ""
        self.current_loader_version = ""
        self.show_all_versions = ctk.BooleanVar(value=False)
        self.version_selecting = False
        
        self.title = ctk.CTkLabel(self, text="CREATE OR EDIT INSTANCE", font=("consolas", 24))
        self.title.grid(sticky="new", padx=2, pady=2, column=1)

        #Name
        ctk.CTkLabel(self, text="Name", font=("consolas", 14)).grid(sticky="nw", padx=2, pady=(2, 0), column=1)
        self.name = ctk.CTkEntry(self, placeholder_text="My Custom Instance", font=("consolas", 14))
        self.name.grid(sticky="new", padx=2, pady=2, column=1)

        #Loader
        ctk.CTkLabel(self, text="Loader", font=("consolas", 14)).grid(sticky="nw", padx=2, pady=(2, 0), column=1)
        self.loader = ctk.CTkSegmentedButton(self, values=self.loaders, font=("consolas", 14), command=self.loader_changed)
        self.loader.grid(sticky="new", padx=2, pady=2, column=1)
        self.loader.set(self.loaders[0])

        #Game Version
        ctk.CTkLabel(self, text="Version", font=("consolas", 14)).grid(sticky="nw", padx=2, pady=(2, 0), column=1)
        self.version_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.version_frame.grid(sticky="new", padx=2, pady=2, column=1)
        self.version_frame.grid_columnconfigure(0, weight=1)

        self.version = ctk.CTkOptionMenu(self.version_frame, values=self.get_version_values(), font=("consolas", 14), command=self.version_changed)
        self.version.grid(row=0, column=0, sticky="new", padx=(0, 6))

        self.release_frame = ctk.CTkFrame(self.version_frame, fg_color="transparent")
        self.release_frame.grid(row=0, column=0, sticky="new", padx=(0, 6))
        self.release_frame.grid_columnconfigure(0, weight=1)
        self.release_frame.grid_columnconfigure(1, weight=1)
        self.release_frame.grid_columnconfigure(2, weight=1)

        self.major = ctk.CTkOptionMenu(self.release_frame, values=["1"], font=("consolas", 14), command=self.major_changed)
        self.major.grid(row=0, column=0, sticky="new", padx=(0, 2))

        self.minor = ctk.CTkOptionMenu(self.release_frame, values=["21"], font=("consolas", 14), command=self.minor_changed)
        self.minor.grid(row=0, column=1, sticky="new", padx=2)

        self.patch = ctk.CTkOptionMenu(self.release_frame, values=["4"], font=("consolas", 14), command=self.patch_changed)
        self.patch.grid(row=0, column=2, sticky="new", padx=(2, 0))

        self.show_all_checkbox = ctk.CTkCheckBox(
            self.version_frame,
            text="Show all Versions",
            variable=self.show_all_versions,
            command=self.update_version_ui,
            font=("consolas", 14)
        )
        self.show_all_checkbox.grid(row=0, column=1, sticky="e")

        #Loader Version
        self.loader_version_label = ctk.CTkLabel(self, text="Loader Version", font=("consolas", 14))
        self.loader_version_label.grid(sticky="nw", padx=2, pady=(2, 0), column=1)
        self.loader_version = ctk.CTkOptionMenu(self, values=self.get_loader_version_values(), font=("consolas", 14), command=self.loader_version_changed)
        self.loader_version.grid(sticky="new", padx=2, pady=2, column=1)

        self.error = ctk.CTkLabel(self, text="", text_color="#ff5a5a", font=("consolas", 14))
        self.error.grid(sticky="new", padx=2, pady=2, column=1)

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(sticky="new", padx=2, pady=2, column=1)
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)

        self.cancel_button = ctk.CTkButton(self.button_frame, text="Cancel", command=self.cancel)
        self.cancel_button.grid(row=0, column=0, sticky="new", padx=(0, 2))

        self.save_button = ctk.CTkButton(self.button_frame, text="Save", command=self.save)
        self.save_button.grid(row=0, column=1, sticky="new", padx=(2, 0))

        self.import_button = ctk.CTkButton(self, text="Import .mrpack", command=self.import_mrpack)
        self.import_button.grid(sticky="new", padx=2, pady=(4, 2), column=1)

        self.loader_changed(self.loaders[0])
        self.update_version_ui()

    def app(self):
        return self.winfo_toplevel()

    def get_version_values(self):
        versions = launcher.get_versions(self.show_all_versions.get())
        if self.current_version and self.current_version not in versions:
            return [self.current_version] + versions
        if versions:
            return versions
        return ["1.21.4"]

    def get_loader_version_values(self):
        versions = launcher.get_loader_versions(self.loader.get(), self.get_selected_game_version())
        if self.current_loader_version and self.current_loader_version not in versions:
            return [self.current_loader_version] + versions
        if versions:
            return versions
        if self.loader.get() == "Fabric":
            return ["0.16.10"]
        return ["No versions loaded"]

    def get_selected_game_version(self):
        if self.show_all_versions.get():
            return self.version.get().strip()
        return self.compose_release_version()

    def update_loader_version_dropdown(self):
        values = self.get_loader_version_values()
        self.loader_version.configure(values=values)
        if self.current_loader_version in values:
            self.loader_version.set(self.current_loader_version)
        else:
            self.current_loader_version = values[0]
            self.loader_version.set(self.current_loader_version)

    def loader_version_changed(self, selected):
        self.current_loader_version = selected

    def get_release_parts(self):
        parts = []
        for version in launcher.get_versions(False):
            split_version = version.split(".")
            if len(split_version) not in [2, 3]:
                continue
            if not all(part.isdigit() for part in split_version):
                continue

            major = split_version[0]
            minor = split_version[1]
            patch = split_version[2] if len(split_version) == 3 else "0"
            parts.append((major, minor, patch))

        if parts:
            return parts
        return [("1", "21", "4")]

    def values_for_index(self, index, major="", minor=""):
        values = []
        for parts in self.get_release_parts():
            if major and parts[0] != major:
                continue
            if minor and parts[1] != minor:
                continue
            value = parts[index]
            if value not in values:
                values.append(value)
        return values if values else ["0"]

    def compose_release_version(self):
        major = self.major.get()
        minor = self.minor.get()
        patch = self.patch.get()
        if patch == "0":
            return f"{major}.{minor}"
        return f"{major}.{minor}.{patch}"

    def split_release_version(self, version):
        split_version = version.split(".")
        if len(split_version) == 2 and all(part.isdigit() for part in split_version):
            return split_version[0], split_version[1], "0"
        if len(split_version) == 3 and all(part.isdigit() for part in split_version):
            return split_version[0], split_version[1], split_version[2]
        return None

    def set_release_dropdowns(self, version=""):
        self.version_selecting = True
        parts = self.split_release_version(version) if version else None
        majors = self.values_for_index(0)
        major = parts[0] if parts and parts[0] in majors else majors[0]
        self.major.configure(values=majors)
        self.major.set(major)

        minors = self.values_for_index(1, major=major)
        minor = parts[1] if parts and parts[1] in minors else minors[0]
        self.minor.configure(values=minors)
        self.minor.set(minor)

        patches = self.values_for_index(2, major=major, minor=minor)
        patch = parts[2] if parts and parts[2] in patches else patches[0]
        self.patch.configure(values=patches)
        self.patch.set(patch)
        self.version_selecting = False
        self.current_version = self.compose_release_version()

    def major_changed(self, selected):
        if self.version_selecting:
            return
        minors = self.values_for_index(1, major=selected)
        self.minor.configure(values=minors)
        self.minor.set(minors[0])
        patches = self.values_for_index(2, major=selected, minor=minors[0])
        self.patch.configure(values=patches)
        self.patch.set(patches[0])
        self.current_version = self.compose_release_version()
        self.update_loader_version_dropdown()

    def minor_changed(self, selected):
        if self.version_selecting:
            return
        patches = self.values_for_index(2, major=self.major.get(), minor=selected)
        self.patch.configure(values=patches)
        self.patch.set(patches[0])
        self.current_version = self.compose_release_version()
        self.update_loader_version_dropdown()

    def patch_changed(self, selected):
        if self.version_selecting:
            return
        self.current_version = self.compose_release_version()
        self.update_loader_version_dropdown()

    def update_version_ui(self):
        if self.show_all_versions.get():
            self.release_frame.grid_remove()
            self.version.grid(row=0, column=0, sticky="new", padx=(0, 6))
            self.update_version_dropdown()
        else:
            self.version.grid_remove()
            self.release_frame.grid(row=0, column=0, sticky="new", padx=(0, 6))
            self.set_release_dropdowns(self.current_version)

    def update_version_dropdown(self):
        values = self.get_version_values()
        self.version.configure(values=values)
        if self.current_version in values:
            self.version.set(self.current_version)
        else:
            self.current_version = values[0]
            self.version.set(self.current_version)

    def version_changed(self, selected):
        self.current_version = selected
        self.update_loader_version_dropdown()

    def clear(self):
        self.editing_name = ""
        self.title.configure(text="CREATE INSTANCE")
        self.name.delete(0, "end")
        self.current_version = ""
        self.show_all_versions.set(False)
        self.update_version_ui()
        self.loader.set(self.loaders[0])
        self.current_loader_version = ""
        self.update_loader_version_dropdown()
        self.error.configure(text="")
        self.loader_changed(self.loaders[0])

    def load_instance(self, name):
        instance = get_instance(name)
        if instance is None:
            self.clear()
            return

        loader_info = instance.get("mod_info", ["Vanilla", ""])
        loader = loader_info[0] if len(loader_info) > 0 else "Vanilla"
        loader_version = loader_info[1] if len(loader_info) > 1 else ""

        self.editing_name = instance.get("name", "")
        self.title.configure(text="EDIT INSTANCE")
        self.name.delete(0, "end")
        self.name.insert(0, instance.get("name", ""))
        self.current_version = instance.get("version", "")
        self.show_all_versions.set(self.split_release_version(self.current_version) is None)
        self.update_version_ui()
        self.loader.set(loader)
        self.current_loader_version = loader_version
        self.update_loader_version_dropdown()
        self.error.configure(text="")
        self.loader_changed(loader)

    def loader_changed(self, selected):
        self.update_loader_version_dropdown()
        if selected in ["Fabric", "Forge", "NeoForge"]:
            self.loader_version_label.configure(text=f"{selected} Loader Version")
            self.loader_version_label.grid()
            self.loader_version.grid()
        else:
            self.loader_version_label.grid_remove()
            self.loader_version.grid_remove()

    def save(self):
        name = self.name.get().strip()
        version = self.version.get().strip() if self.show_all_versions.get() else self.compose_release_version()
        loader = self.loader.get()
        loader_version = self.loader_version.get().strip() if loader in ["Fabric", "Forge", "NeoForge"] else ""

        if not name:
            self.error.configure(text="Please enter a name.")
            return
        if not version:
            self.error.configure(text="Please enter a Minecraft version.")
            return
        if loader_version == "No versions loaded":
            loader_version = ""
        if loader in ["Fabric", "Forge", "NeoForge"] and not loader_version:
            self.error.configure(text=f"Please select a {loader} loader version.")
            return

        if not create_or_edit_instance(name, version, [loader, loader_version], self.editing_name):
            self.error.configure(text="This name is already used.")
            return

        app = self.app()
        app.instances.refresh()
        app.inspector.show("instance")
        app.inspector.frame_config(text=name, btn_start_text=f"Launch {loader} {version}", start_instance=name)

    def cancel(self):
        self.error.configure(text="")
        self.app().inspector.show("instance")

    def import_mrpack(self):
        path = filedialog.askopenfilename(
            title="Import .mrpack",
            filetypes=[("Modrinth packs", "*.mrpack"), ("All files", "*.*")]
        )
        if path == "":
            return
        self.import_button.configure(state="disabled", text="Importing...")
        threading.Thread(target=self._import_mrpack, args=(path,), daemon=True).start()

    def _import_mrpack(self, path):
        try:
            name = self.name.get().strip()
            if name == "":
                name = safe_folder_name(path.rsplit("/", 1)[-1].rsplit("\\", 1)[-1].replace(".mrpack", ""))
            directory = get_unique_instance_directory(name)
            imported = mod_manager.import_mrpack(path, directory)
            imported_name = imported.get("name", name).strip() or name
            version = imported.get("version", "")
            mod_info = imported.get("mod_info", ["Vanilla", ""])
            if not create_or_edit_instance(imported_name, version, mod_info, directory=directory):
                self.after(0, lambda: self.error.configure(text="Could not import this pack."))
                return
            self.after(0, lambda: self.finish_mrpack_import(imported_name, mod_info, version))
        except Exception as e:
            message = str(e)
            self.after(0, lambda: self.error.configure(text=message))
        finally:
            self.after(0, lambda: self.import_button.configure(state="normal", text="Import .mrpack"))

    def finish_mrpack_import(self, imported_name, mod_info, version):
        app = self.app()
        app.instances.refresh()
        app.inspector.show("instance")
        app.inspector.frame_config(text=imported_name, btn_start_text=f"Launch {mod_info[0]} {version}", start_instance=imported_name)
        
    def refresh(self):
        self.update_version_ui()
        self.update_loader_version_dropdown()
