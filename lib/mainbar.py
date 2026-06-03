import customtkinter as ctk
import microsoft_login as mslgin
import threading
from data_reader import *
import json
from PIL import Image, ImageDraw
import requests
from io import BytesIO
from CTkToolTip import *

class frame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.fg_color="#000000"
        
        self.username = ""
        self.id = ""
        self.access_token = ""
        self.refresh_token = ""
        self.profile_url = ""
        
        self.image_size = 48
        self.logged_in = False
        self.refreshing_token = False
        self.startup_refresh_done = False
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        
        self.profile_head = ctk.CTkImage(dark_image=Image.open("lib\\images\\icon.ico"), size=(self.image_size, self.image_size))
        self.profile_label = ctk.CTkLabel(self, image=self.profile_head, text="", font=("consolas", 26))
        self.profile_label.grid(padx=(2, 5), pady=2, rowspan=2)
        
        self.login_button = ctk.CTkButton(self, text="", command=lambda: self.button_pressed("login"), fg_color="transparent", hover_color="#1c1c1c", font=("consolas", 12), width=20)
        self.login_button.grid(row=1, column=1,padx=2, pady=(0, 2), sticky="nw")
        
        self.namedisplay = ctk.CTkLabel(self, text="", font=("consolas", 16))
        self.namedisplay.grid(row=0, column=1,padx=2, pady=(2, 0), sticky="nw")

        self.reload_image = ctk.CTkImage(dark_image=Image.open("lib\\images\\reload.png"))
        
        self.token_button = ctk.CTkButton(self, text="", image=self.reload_image, command=lambda: self.button_pressed("token"), width=40, height=30)
        self.token_button.grid(row=0, column=3,padx=2, pady=(0, 2), sticky="w", rowspan=2)
        self.token_tooltip = CTkToolTip(self.token_button, delay=0.5, message="Request a new Minecraft Session Token")

        self.offline_indicator = ctk.CTkLabel(self, text="Eclipse Client", font=("consolas", 34))
        self.offline_indicator.grid(row=0, column=2,padx=2, pady=(0, 2), sticky="nsw", rowspan=2)

        self.after(500, self.refresh_token_on_startup)
    
    def button_pressed(self, button): # Handle a pressed Button on the UI
        if button == "login":
            threading.Thread(target=self._login, daemon=True).start()
        elif button == "logout":
            threading.Thread(target=self.logout, daemon=True).start()
        elif button == "token":
            threading.Thread(target=self.get_token, daemon=True).start()
        
    def _login(self): # Open the Browser to log in to Microsoft
        try:
            user = mslgin.login()
            if user:
                self.after(0, lambda: self._login_success(user))
            else:
                self.after(0, self._login_error)
        except Exception as e:
            self.after(0, self._login_error)
        
    def _login_success(self, user): # If the login worked, the recieved Userdata is saved
        self.username = user.get("name", "")
        self.id = user.get("id", "")
        self.access_token = user.get("access_token", "")
        self.refresh_token = user.get("refresh_token", self.refresh_token)
        self.profile_url = self.get_profile_url(user)
        if not self.username or not self.id or not self.access_token:
            self._login_error()
            return
        print(f"Successfully logged in as {self.username}")
        create_permanent_key("name", self.username)
        create_permanent_key("uuid", self.id)
        create_permanent_key("token", self.access_token)
        create_permanent_key("refresh", self.refresh_token)
        create_permanent_key("profile", self.profile_url)
        self.logged_in = True
        self.refresh()
        
    def _login_error(self): # Login Error Handler
        print("Failed to log in.")
        self.logged_in = False
        self.refresh()

    def get_profile_url(self, user):
        skins = user.get("skins", [])
        if skins and isinstance(skins[0], dict):
            return skins[0].get("url", self.profile_url)
        return self.profile_url
        
    def logout(self): # Deletes User's Data
        create_permanent_key("name", "")
        delete_permanent_key("uuid")
        delete_permanent_key("token")
        delete_permanent_key("refresh")
        delete_permanent_key("profile")
        self.logged_in = False
        self.refresh()    
        
    def get_token(self):
        self.refresh_saved_token(open_login_on_fail=True)

    def refresh_token_on_startup(self):
        if self.startup_refresh_done:
            return
        self.startup_refresh_done = True
        try:
            refresh_token = get_permanent_key("refresh")
        except Exception:
            return
        if refresh_token:
            threading.Thread(target=lambda: self.refresh_saved_token(open_login_on_fail=False), daemon=True).start()

    def refresh_saved_token(self, open_login_on_fail=False):
        if self.refreshing_token:
            return
        self.refreshing_token = True
        self.after(0, self.show_token_loading)
        try:
            if not mslgin.internet():
                return
            saved_refresh_token = get_permanent_key("refresh")
            self.refresh_token = saved_refresh_token
            user = mslgin.refresh(saved_refresh_token)
            if user:
                self.after(0, lambda: self._login_success(user))
            elif open_login_on_fail:
                self.button_pressed("login")
        except Exception as e:
            if open_login_on_fail:
                self.button_pressed("login")
        finally:
            self.refreshing_token = False
            self.after(0, self.show_token_ready)

    def show_token_loading(self):
        self.reload_image = ctk.CTkImage(dark_image=Image.open("lib\\images\\wait.png"))
        self.token_button.configure(text="", image=self.reload_image, state="disabled")

    def show_token_ready(self):
        self.reload_image = ctk.CTkImage(dark_image=Image.open("lib\\images\\reload.png"))
        self.token_button.configure(text="", image=self.reload_image, state="enabled" if self.logged_in else "disabled")
            
    def refresh(self): # Update UI Elements in this Frame
        try:
            self.username = get_permanent_key("name")
            self.id = get_permanent_key("uuid")
            self.access_token = get_permanent_key("token")
            self.refresh_token = get_permanent_key("refresh")
            self.profile_url = get_permanent_key("profile")
            #print(f"User found: {self.username}, {self.id}, {self.profile_url}")
        except Exception as e:
            self.username = ""
            create_permanent_key("name", "")

        if self.username == "":
            self.logged_in = False
            self.login_button.configure(text="Log In", command=lambda: self.button_pressed("login"))
            self.namedisplay.configure(text="Not logged in!")
            self.profile_head = ctk.CTkImage(dark_image=self._make_circle(Image.open("lib\\images\\icon.ico")), size=(self.image_size, self.image_size))
            self.profile_label.configure(image=self.profile_head)
        else:
            self.logged_in = True
            self.login_button.configure(text="Log Out", command=lambda: self.button_pressed("logout"))
            self.namedisplay.configure(text=self.username)
            threading.Thread(target=self._update_profile_pic, daemon=True).start()

        if self.logged_in:
            #self.master.start_button.configure(state="enabled")
            self.token_button.configure(state="enabled")
        else:
            #self.master.start_button.configure(state="disabled")
            self.token_button.configure(state="disabled")

            image = Image.open("lib\\images\\icon.ico")
            if mslgin.internet():
                self.offline_indicator.configure(text="Eclipse Client")
                self.profile_head = ctk.CTkImage(dark_image=image, size=(self.image_size, self.image_size))
                self.profile_label.configure(image=self.profile_head)
            else:
                self.offline_indicator.configure(text="Eclipse Client (Offline)")
                image = Image.open("lib\\images\\icon.ico")
                image = image.resize((self.image_size, self.image_size), Image.NEAREST)
                image = self._make_circle(image)
                self.profile_head = ctk.CTkImage(dark_image=image, size=(self.image_size, self.image_size))
                self.profile_label.configure(image=self.profile_head)
            
    def _update_profile_pic(self): # Loads the Minecraft Skin and Resizes it to the head of the Player
        url = self.profile_url
        try:
            response = requests.get(url)
            img_data = BytesIO(response.content)
            image = Image.open(img_data)
            image=image.crop((8, 8, 16, 16))
            image = image.resize((self.image_size, self.image_size), Image.NEAREST)
            image = self._make_circle(image)
            
            self.offline_indicator.configure(text="Eclipse Client")
            self.profile_head = ctk.CTkImage(dark_image=image, size=(self.image_size, self.image_size))
            self.profile_label.configure(image=self.profile_head)
        except Exception as e:
            self.offline_indicator.configure(text="Eclipse Client (Offline)")
            image = Image.open("lib\\images\\icon.ico")
            image = image.resize((self.image_size, self.image_size), Image.NEAREST)
            image = self._make_circle(image)
            self.profile_head = ctk.CTkImage(dark_image=image, size=(self.image_size, self.image_size))
            self.profile_label.configure(image=self.profile_head)
            
        
    def _make_circle(self, img):
        size = img.size  # (width, height)
        #print(size)

        # Create Circle Mask
        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0, size[0], size[1]),size[0]/4, fill=255, corners=[True, True, False, True])

        # Mask Transparent
        result = Image.new("RGBA", size)
        result.paste(img, (0, 0), mask)

        return result
            
if __name__ == "__main__":
    print("Please run the App via 'main.py'")
