import os
import threading
from io import BytesIO
from urllib.request import Request, urlopen

import customtkinter as ctk
from PIL import Image

import launcher
import mod_manager
from instances_file_manager import *

class frame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.fg_color = "#000000"
        self.instance_name = ""
        self.instance = None
        self.results = []
        self.filtered_results = []
        self.images = []
        self.search_job = None
        self.search_id = 0

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.grid(row=0, column=0, sticky="ew", padx=6, pady=6)
        self.header.grid_columnconfigure(1, weight=1)

        self.back_button = ctk.CTkButton(self.header, text="Back", width=80, command=self.back)
        self.back_button.grid(row=0, column=0, padx=(0, 6), pady=2, sticky="w")

        self.title = ctk.CTkLabel(self.header, text="Mods", font=("consolas", 24))
        self.title.grid(row=0, column=1, padx=2, pady=2, sticky="w")

        self.controls = ctk.CTkFrame(self, fg_color="transparent")
        self.controls.grid(row=1, column=0, sticky="ew", padx=6, pady=(0, 6))
        self.controls.grid_columnconfigure(1, weight=1)

        self.provider = ctk.CTkOptionMenu(self.controls, values=["Modrinth", "CurseForge"], width=130, command=lambda value: self.search(reset_page=True))
        self.provider.grid(row=0, column=0, padx=(0, 6), pady=2, sticky="w")

        self.query = ctk.CTkEntry(self.controls, placeholder_text="Search mods", font=("consolas", 14))
        self.query.grid(row=0, column=1, padx=2, pady=2, sticky="ew")
        self.query.bind("<Return>", lambda event: self.search(reset_page=True))
        self.query.bind("<KeyRelease>", self.schedule_search)

        self.search_button = ctk.CTkButton(self.controls, text="Search", width=90, command=lambda: self.search(reset_page=True))
        self.search_button.grid(row=0, column=2, padx=(6, 0), pady=2, sticky="e")

        self.search_mode = ctk.CTkOptionMenu(self.controls, values=["Name", "Description"], width=140, command=lambda value: self.search(reset_page=True))
        self.search_mode.grid(row=1, column=0, padx=(0, 6), pady=2, sticky="w")

        self.filter_mode = ctk.CTkOptionMenu(self.controls, values=["All", "Installed", "Not Installed"], width=140, command=lambda value: self.apply_filter())
        self.filter_mode.grid(row=1, column=1, padx=2, pady=2, sticky="w")

        self.limit = ctk.CTkOptionMenu(self.controls, values=["20", "50", "100"], width=90, command=lambda value: self.search(reset_page=True))
        self.limit.grid(row=1, column=2, padx=(6, 0), pady=2, sticky="e")

        self.page_frame = ctk.CTkFrame(self.controls, fg_color="transparent")
        self.page_frame.grid(row=2, column=0, columnspan=3, padx=0, pady=2, sticky="e")

        self.page_label = ctk.CTkLabel(self.page_frame, text="Page", font=("consolas", 14))
        self.page_label.grid(row=0, column=0, padx=(0, 6), sticky="e")

        self.page_down = ctk.CTkButton(self.page_frame, text="-", width=30, command=lambda: self.change_page(-1))
        self.page_down.grid(row=0, column=1, padx=2, sticky="e")

        self.page_input = ctk.CTkEntry(self.page_frame, width=70, font=("consolas", 14))
        self.page_input.grid(row=0, column=2, padx=2, sticky="e")
        self.page_input.insert(0, "1")
        self.page_input.bind("<Return>", self.search_from_page_input)
        self.page_input.bind("<FocusOut>", self.search_from_page_input)

        self.page_up = ctk.CTkButton(self.page_frame, text="+", width=30, command=lambda: self.change_page(1))
        self.page_up.grid(row=0, column=3, padx=2, sticky="e")

        self.results_frame = ctk.CTkScrollableFrame(self, fg_color="#000000")
        self.results_frame.grid(row=2, column=0, sticky="nsew", padx=6, pady=(0, 6))
        self.results_frame.grid_columnconfigure(0, weight=1)

    def load_instance(self, instance_name):
        self.instance_name = instance_name
        self.instance = get_instance(instance_name)
        self.results = []
        self.filtered_results = []
        self.title.configure(text=f"Mods - {instance_name}")
        self.render_results([])
        self.search(reset_page=True)

    def back(self):
        self.master.show("instance")
        self.master.frame_config(start_instance=self.instance_name)

    def refresh(self):
        if self.instance_name:
            self.instance = get_instance(self.instance_name)
            self.apply_filter()

    def is_ready(self):
        if self.instance is None:
            launcher.log("No instance selected.")
            return False
        loader = self.instance.get("mod_info", ["Vanilla", ""])[0]
        if loader not in ["Fabric", "Forge", "NeoForge"]:
            launcher.log("Mods can only be installed for modded instances.")
            return False
        return True

    def schedule_search(self, event=None):
        if self.search_job is not None:
            self.after_cancel(self.search_job)
        self.search_job = self.after(450, lambda: self.search(reset_page=True))

    def selected_limit(self):
        try:
            return int(self.limit.get())
        except Exception:
            return 20

    def selected_page(self):
        try:
            page = int(self.page_input.get())
        except Exception:
            page = 1
        return max(1, page)

    def normalize_page(self):
        self.page_input.delete(0, "end")
        self.page_input.insert(0, str(self.selected_page()))

    def change_page(self, change):
        page = max(1, self.selected_page() + change)
        self.page_input.delete(0, "end")
        self.page_input.insert(0, str(page))
        self.search(reset_page=False)

    def search_from_page_input(self, event=None):
        self.normalize_page()
        self.search(reset_page=False)

    def search(self, reset_page=False):
        if not self.is_ready():
            return
        self.search_job = None
        if reset_page:
            self.page_input.delete(0, "end")
            self.page_input.insert(0, "1")
        self.normalize_page()
        query = self.query.get().strip()
        limit = self.selected_limit()
        offset = (self.selected_page() - 1) * limit
        self.search_id += 1
        search_id = self.search_id
        self.search_button.configure(state="disabled", text="...")
        self.render_loading()
        threading.Thread(target=self._search, args=(query, limit, offset, search_id), daemon=True).start()

    def _search(self, query, limit, offset, search_id):
        try:
            loader = self.instance.get("mod_info", ["Vanilla", ""])[0]
            version = self.instance.get("version", "")
            results = mod_manager.search_mods(self.provider.get(), query, version, loader, self.search_mode.get(), limit, offset)
            if self.search_mode.get() == "Description":
                query_lower = query.lower()
                if query_lower:
                    results = [result for result in results if query_lower in result.get("description", "").lower()]
            self.after(0, lambda: self.finish_search(results, search_id))
        except Exception as e:
            launcher.log(str(e))
            self.after(0, lambda: self.finish_search([], search_id))

    def finish_search(self, results, search_id=None):
        if search_id is not None and search_id != self.search_id:
            return
        self.results = results
        self.search_button.configure(state="normal", text="Search")
        self.apply_filter()

    def apply_filter(self):
        mode = self.filter_mode.get()
        if mode == "Installed":
            self.filtered_results = [result for result in self.results if self.is_installed(result)]
        elif mode == "Not Installed":
            self.filtered_results = [result for result in self.results if not self.is_installed(result)]
        else:
            self.filtered_results = list(self.results)
        self.render_results(self.filtered_results)

    def render_loading(self):
        self.clear_results()
        label = ctk.CTkLabel(self.results_frame, text="Searching...", font=("consolas", 16))
        label.grid(row=0, column=0, padx=8, pady=8, sticky="ew")

    def clear_results(self):
        for child in self.results_frame.winfo_children():
            child.destroy()
        self.images.clear()

    def render_results(self, results):
        self.clear_results()
        if not results:
            label = ctk.CTkLabel(self.results_frame, text="No mods loaded", font=("consolas", 16))
            label.grid(row=0, column=0, padx=8, pady=8, sticky="ew")
            return

        for row, result in enumerate(results):
            self.add_result_card(row, result)

    def add_result_card(self, row, result):
        card = ctk.CTkFrame(self.results_frame)
        card.grid(row=row, column=0, padx=4, pady=4, sticky="ew")
        card.grid_columnconfigure(1, weight=1)

        image = self.load_preview_image(result.get("icon_url", ""))
        self.images.append(image)
        image_label = ctk.CTkLabel(card, text="", image=image, width=56, height=56)
        image_label.grid(row=0, column=0, rowspan=2, padx=8, pady=8, sticky="nw")

        title = ctk.CTkLabel(card, text=result.get("title", ""), font=("consolas", 16), anchor="w")
        title.grid(row=0, column=1, padx=4, pady=(8, 0), sticky="ew")

        description = ctk.CTkLabel(card, text=result.get("description", ""), font=("consolas", 12), anchor="w", justify="left", wraplength=520)
        description.grid(row=1, column=1, padx=4, pady=(0, 8), sticky="ew")

        installed = self.is_installed(result)
        text = "Remove" if installed else "Add"
        button = ctk.CTkButton(card, text=text, width=90, command=lambda r=result: self.toggle_mod(r))
        button.grid(row=0, column=2, rowspan=2, padx=8, pady=8, sticky="e")

    def load_preview_image(self, url):
        try:
            if url:
                request = Request(url, headers={"User-Agent": mod_manager.USER_AGENT})
                with urlopen(request, timeout=10) as response:
                    image = Image.open(BytesIO(response.read())).convert("RGBA")
            else:
                image = Image.new("RGBA", (56, 56), "#202020")
        except Exception:
            image = Image.new("RGBA", (56, 56), "#202020")
        return ctk.CTkImage(dark_image=image, size=(56, 56))

    def is_installed(self, result):
        for mod in get_installed_mods(self.instance_name):
            if mod.get("provider") == result.get("provider") and mod.get("project_id") == result.get("project_id"):
                return True
        return False

    def toggle_mod(self, result):
        if self.is_installed(result):
            self.remove_mod(result)
        else:
            self.add_mod(result)

    def add_mod(self, result):
        launcher.log(f"Installing mod: {result.get('title', '')}")
        threading.Thread(target=self._add_mod, args=(result,), daemon=True).start()

    def _add_mod(self, result):
        try:
            instance = get_instance(self.instance_name)
            loader = instance.get("mod_info", ["Vanilla", ""])[0]
            version = instance.get("version", "")
            directory = ensure_instance_directory(instance)
            installed = mod_manager.install_mod(result.get("provider", ""), result.get("project_id", ""), version, loader, directory)
            mod = {
                "provider": result.get("provider", ""),
                "project_id": result.get("project_id", ""),
                "title": result.get("title", ""),
                "path": installed.get("path", "")
            }
            add_installed_mod(self.instance_name, mod)
            for dependency in installed.get("dependencies", []):
                add_installed_mod(self.instance_name, dependency)
                launcher.log(f"Installed dependency: {dependency.get('title', '')}")
            launcher.log(f"Installed mod: {installed.get('path', '')}")
        except Exception as e:
            launcher.log(str(e))
        finally:
            self.after(0, self.refresh)

    def remove_mod(self, result):
        removed = remove_installed_mod(self.instance_name, result.get("provider", ""), result.get("project_id", ""))
        if removed is None:
            return
        path = removed.get("path", "")
        try:
            if path and os.path.exists(path):
                os.remove(path)
                launcher.log(f"Removed mod: {path}")
        except Exception as e:
            launcher.log(str(e))
        self.refresh()
