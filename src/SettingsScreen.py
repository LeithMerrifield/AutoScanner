from kivy.uix.screenmanager import Screen, SlideTransition
import json
import os


class SettingsScreen(Screen):
    def __init__(self, **kw) -> None:
        super().__init__(**kw)
        self.previous_screen = "login"
        self.load_settings()

    def save_and_return(self):
        self.netsuite_sso = self.ids.netsuite_sso_setting.text
        json_object = {"Netsuite_SSO": self.netsuite_sso}

        with open(r"src\settings.json", "w") as openfile:
            json.dump(json_object, openfile, indent=4)

        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = self.previous_screen

    def set_previous_screen(self, screen):
        self.previous_screen = screen

    def load_settings(self):
        if not os.path.exists(r"src\settings.json"):
            with open(r".\src\settings.json", "w") as openfile:
                json_object = {"Netsuite_SSO": "Replace with SSO"}
                json.dump(json_object, openfile, indent=4)

        with open(r".\src\settings.json", "r") as openfile:
            json_object = json.load(openfile)
        self.netsuite_sso = json_object["Netsuite_SSO"]
        self.ids.netsuite_sso_setting.text = self.netsuite_sso
        openfile.close()
