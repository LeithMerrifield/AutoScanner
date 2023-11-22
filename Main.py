import os
import sys
import logging
import threading
import json
from datetime import datetime

# os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
if hasattr(sys, "_MEIPASS"):
    os.environ["KIVY_NO_CONSOLELOG"] = "1"

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from src.LoginScreen import LoginScreen
from src.ScannerScreen import ScannerScreen
from src.SettingsScreen import SettingsScreen
from src.CheckDriver import compare_and_download as driver_update
from kivy.base import Builder

Builder.load_file("./src/kv/Login.kv")


class LoginApp(App):
    def build(self):
        self.path = os.getcwd()
        self.icon = "./src/images/FireIcon.png"
        self.title = "AutoScanner"
        self.previous_screen = "login"
        manager = ScreenManager()
        manager.add_widget(LoginScreen(name="login"))
        manager.add_widget(SettingsScreen(name="settings"))
        manager.add_widget(ScannerScreen(name="scanner", manager=manager))
        return manager


def Bypass_Reopen_Tabs():
    json_object = {}
    try:
        with open(r".\userdata\default\Preferences", "r", encoding="utf-8") as openfile:
            json_object = json.load(openfile)
            openfile.close()
    except:
        return

    with open(r".\userdata\default\Preferences", "w", encoding="utf-8") as openfile:
        json_object["profile"]["exit_type"] = "normal"
        json.dump(json_object, openfile, indent=4)
        openfile.close()


# userdata -> default -> Preferences


if __name__ == "__main__":
    threading.Thread(
        target=Bypass_Reopen_Tabs,
        daemon=True,
    ).start()

    threading.Thread(
        target=driver_update,
        daemon=True,
    ).start()
    LoginApp().run()
