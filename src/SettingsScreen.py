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
        self.netsuite = self.ids.netsuite_setting.text
        self.timeout_avoidance = self.ids.timeout_avoidance_setting.active
        json_object = {
            "Netsuite_SSO": self.netsuite_sso,
            "Netsuite": self.netsuite,
            "Timeout_Avoidance": self.timeout_avoidance,
        }

        with open(r"src\settings.json", "w", encoding="utf-8") as openfile:
            json.dump(json_object, openfile, indent=4)

        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = self.previous_screen

    def set_previous_screen(self, screen):
        self.previous_screen = screen

    def load_settings(self):
        if not os.path.exists(r"src\settings.json"):
            with open(r".\src\settings.json", "w", encoding="utf-8") as openfile:
                json_object = {
                    "Netsuite_SSO": "Replace with Netsuite SSO",
                    "Netsuite": "https://5230881.app.netsuite.com/app/center/card.nl?sc=-29&whence=",
                    "Timeout_Avoidance": True,
                }
                json.dump(json_object, openfile, indent=4)

        with open(r".\src\settings.json", "r", encoding="utf-8") as openfile:
            json_object = json.load(openfile)

        self.netsuite_sso = json_object["Netsuite_SSO"]
        self.netsuite = json_object["Netsuite"]
        self.timeout_avoidance = json_object["Timeout_Avoidance"]

        self.ids.timeout_avoidance_setting.active = self.timeout_avoidance
        self.ids.netsuite_sso_setting.text = self.netsuite_sso
        self.ids.netsuite_setting.text = self.netsuite
        openfile.close()
