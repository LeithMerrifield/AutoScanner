from src.MainWebDriver import MainWebDriver
from kivy.config import Config
from kivy.uix.screenmanager import Screen, SlideTransition

import threading

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

    def do_login(self):
        threading.Thread(
            target=self.driver.login, args=(self.login_flag,), daemon=True
        ).start()
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "scanner"

    def _keydown(self, instance, keyboard, keycode, text, modifiers):
        if self.manager.current != "login":
            return
        if keycode == 40:  # enter
            self.do_login()
