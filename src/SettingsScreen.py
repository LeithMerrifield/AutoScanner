from kivy.uix.screenmanager import Screen, SlideTransition


class SettingsScreen(Screen):
    def __init__(self, **kw) -> None:
        super().__init__(**kw)
        self.previous_screen = "login"

    def save_and_return(self):
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = self.previous_screen
        pass

    def set_previous_screen(self, screen):
        self.previous_screen = screen
