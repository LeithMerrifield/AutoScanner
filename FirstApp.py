from kivy.app import App
from kivy.config import Config

Config.set("graphics", "resizeable", True)
Config.set("graphics", "width", "500")
Config.set("graphics", "height", "800")
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from MainWebDriver import MainWebDriver
from hashlib import pbkdf2_hmac


r = 74
g = 85
b = 105
Window.clearcolor = (r / 255, g / 255, b / 255)

myDriver = MainWebDriver()

class Login(Screen):
    def __init__(self, **kw):
        super(Login, self).__init__(**kw)
        Window.bind(on_key_down=self._keydown)

    def do_login(self):
        myDriver.login()
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "scanner"

    def _keydown(self, instance, keyboard, keycode, text, modifiers):
        if(self.manager.current != "login"):
            return
        if keycode == 40:  # enter
            self.do_login(self.ids.username.text, self.ids.password.text)


class ScannerScreen(Screen):
    def __init__(self, **kw):
        super(ScannerScreen,self).__init__(**kw)
        Window.bind(on_key_down=self._keydown)

    
    def _keydown(self, instance, keyboard, keycode, text, modifiers):
        if(self.manager.current != "scanner"):
            return
        inputBox = self.ids.order_input
        if keycode == 40 and inputBox.text != '':  # enter
            orderLabel = self.ids.order_list
            if orderLabel.text != "":
                orderLabel.text = orderLabel.text + "\n" + inputBox.text
            else:
                orderLabel.text = inputBox.text

            inputBox.text = ""
            Clock.schedule_once(self.show_keyboard)
    
    def do_pick(self):
        Clock.unschedule(self.do_refresh)
        if(self.ids.order_list.text != ""):
            myDriver.Scan(self.ids.order_list.text.split('\n'))
            self.ids.order_list.text = ""
        Clock.schedule_once(self.do_refresh, 600)

    def do_refresh(self,dt):
        myDriver.Refresh()

    def show_keyboard(self,event):
        inputBox = self.ids.order_input
        inputBox.focus = True

class LoginApp(App):
    def build(self):
        manager = ScreenManager()
        manager.add_widget(Login(name="login"))
        manager.add_widget(ScannerScreen(name="scanner"))

        return manager


