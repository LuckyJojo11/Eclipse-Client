import customtkinter as ctk
import mainbar
import inspector
import instances
import console
import launcher
from data_reader import *

ctk.set_appearance_mode("dark")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=7)
        self.grid_rowconfigure(1, weight=1)
        
        self.title("Eclipse Client")
        self.iconbitmap("lib\\images\\icon.ico")
        self.geometry("1000x600")
        launcher.refresh_versions_async()
        
        self.mainbar = mainbar.frame(self)
        self.mainbar.configure()
        self.mainbar.grid(row=0, column=0, padx=2, pady=2, sticky="new", columnspan=2)
        
        self.instances = instances.frame(self)
        self.instances.configure()
        self.instances.grid(row=1, column=0, padx=2, pady=2, sticky="nsew")

        self.inspector = inspector.frame(self)
        self.inspector.configure()
        self.inspector.grid(row=1, column=1, padx=2, pady=2, sticky="nsew")

        self.console = console.frame(self)
        self.console.configure()
        self.console.grid(row=2, column=0, padx=2, pady=2, columnspan=2, sticky="nswe")

        self.refresh()
        self.bind_all(self)

    def clicked(self):
        print("Refreshing UI")
        self.inspector.destroy()
        self.inspector = inspector.frame(self)
        self.inspector.configure()
        self.inspector.grid(row=1, column=1, padx=2, pady=2, sticky="nsew")
        self.refresh_all_except_mainbar()
    
    def refresh_all_except_mainbar(self):
        self.inspector.refresh()
        self.instances.refresh()
    
    def refresh(self):
        self.mainbar.refresh()
        self.refresh_all_except_mainbar()


# Run Application
def run():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    print("Please run the App via 'main.py'")
    run()
