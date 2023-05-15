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
import atexit
import threading

r = 74
g = 85
b = 105
Window.clearcolor = (r / 255, g / 255, b / 255)

class Login(Screen):
    driver = MainWebDriver()
    def __init__(self, **kw):
        super(Login, self).__init__(**kw)
        Window.bind(on_key_down=self._keydown)

    def do_login(self):
        threading.Thread(target=self.driver.login).start()
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "scanner"

    def _keydown(self, instance, keyboard, keycode, text, modifiers):
        if(self.manager.current != "login"):
            return
        if keycode == 40:  # enter
            self.do_login(self.ids.username.text, self.ids.password.text)

class ScannerScreen(Screen):
    def __init__(self,manager, **kw):
        super(ScannerScreen,self).__init__(**kw)
        Window.bind(on_key_down=self._keydown)
        self.driver = manager.get_screen("login").driver
        atexit.register(self.exit_handler)

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
            threading.Thread(target=self.driver.Scan,args=self.ids.order_list.text.split('\n'))
            self.ids.order_list.text = ""
        Clock.schedule_once(self.do_refresh, 600)

    def do_refresh(self,dt):
        self.driver.Refresh()

    def show_keyboard(self,event):
        inputBox = self.ids.order_input
        inputBox.focus = True

    def exit_handler(self):
        self.driver.Exit()


class LoginApp(App):
    def build(self):
        manager = ScreenManager()
        manager.add_widget(Login(name="login"))
        manager.add_widget(ScannerScreen(name="scanner", manager = manager))

        return manager

if __name__ == "__main__":
    LoginApp().run()