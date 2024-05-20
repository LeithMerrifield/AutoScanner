from src.MainWebDriver import MainWebDriver
from kivy.config import Config
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.clock import Clock
import json
from cryptography.fernet import Fernet
import os
import threading
from functools import partial

Config.set("graphics", "resizeable", True)
Config.set("graphics", "width", "500")
Config.set("graphics", "height", "800")

# fmt: off
from kivy.core.window import Window  # pylint: disable=wrong-import-position,ungrouped-imports
# fmt: on

R = 74
G = 85
B = 105
Window.clearcolor = (R / 255, G / 255, B / 255)


class LoginScreen(Screen):
    """
    Login Screen for Kivy GUI

    Attributes
    ----------
    driver : Instance of MainWebDriver.py
    login_flag: Used to determine the status of the login process

    Methods
    -------
    do_login()
        Initiates a thread to start the login process with selenium

    """

    driver = MainWebDriver()
    login_flag = [False]

    def __init__(self, **kw):
        super(LoginScreen, self).__init__(**kw)
        Window.bind(on_key_down=self._keydown)
        self.check_users_on_launch()

    def check_users_on_launch(self):
        user = self.read_json()
        if not user:
            return
        if user["remember"]:
            self.ids.username.text = user["username"]
            self.ids.password.text = self.decrypt_pass(
                user["password"], user["encryption_key"]
            )

    def store_login(self, username=None, password=None):
        if username == "" or password == "":
            return
        key = Fernet.generate_key()
        fernet = Fernet(key)
        login_object = {
            "username": username,
            "password": fernet.encrypt(password.encode()).decode(),
            "encryption_key": key.decode(),
            "remember": True,
        }

        with open(r"src\database.json", "w", encoding="utf-8") as openfile:
            json.dump(login_object, openfile, indent=4)

    def reset_database(self):
        default_object = {}
        with open(r"src\database.json", "w", encoding="utf-8") as openfile:
            json.dump(default_object, openfile, indent=4)

    def decrypt_pass(self, password, key):
        fernet = Fernet(key)
        return fernet.decrypt(password).decode()

    def read_json(self):
        if not os.path.exists(r"src\database.json"):
            return None

        with open(r"src\database.json", "r", encoding="utf-8") as openfile:
            json_object = json.load(openfile)

        return json_object

    def do_login(self):
        username = self.ids.username.text
        password = self.ids.password.text
        # if nothing, need to store new login
        # if "@bollebrands.com" not in username.lower() or password == "":
        #    return

        if not self.driver.continue_program:
            return

        if self.ids.login_checkbox.active:
            self.store_login(username, password)

        threading.Thread(
            target=self.driver.login,
            args=(
                self.login_flag,
                username,
                password,
                self.login_failed_callback,
            ),
            daemon=True,
        ).start()

        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "scanner"

    def transition_to_login(self, error_code, dt):
        if error_code == 1 or error_code == 2:
            self.ids.username.text = ""
            self.ids.password.text = ""
            self.reset_database()

        self.manager.current = "login"

    def login_failed_callback(self, error_code=0):
        self.manager.transition = SlideTransition(direction="right")
        Clock.schedule_once(
            partial(
                self.transition_to_login,
                error_code,
            ),
            1,
        )

    def show_settings(self):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "settings"

    def _keydown(self, instance, keyboard, keycode, text, modifiers):
        if self.manager.current != "login":
            return
        if keycode == 40:  # enter
            self.do_login()
