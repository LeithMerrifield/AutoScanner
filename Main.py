import os
import sys

if hasattr(sys, "_MEIPASS"):
    os.environ["KIVY_NO_CONSOLELOG"] = "1"

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from src.LoginScreen import LoginScreen
from src.ScannerScreen import ScannerScreen
from src.SettingsScreen import SettingsScreen
from kivy.base import Builder
import os

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


if __name__ == "__main__":
    LoginApp().run()
