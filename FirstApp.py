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
from time import sleep
from functools import partial


r = 74
g = 85
b = 105
Window.clearcolor = (r / 255, g / 255, b / 255)

class Login(Screen):
    driver = MainWebDriver()
    loginFlag = [False]
    def __init__(self, **kw):
        super(Login, self).__init__(**kw)
        Window.bind(on_key_down=self._keydown)

    def do_login(self):
        threading.Thread(target=self.driver.login, args=(self.loginFlag,),daemon=True ).start()
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "scanner"

    def _keydown(self, instance, keyboard, keycode, text, modifiers):
        if(self.manager.current != "login"):
            return
        if keycode == 40:  # enter
            self.do_login(self.ids.username.text, self.ids.password.text)

class ScannerScreen(Screen):
    statusFlag = [False]
    def __init__(self,manager, **kw):
        super(ScannerScreen,self).__init__(**kw)
        Window.bind(on_key_down=self._keydown)
        self.loginScreen = manager.get_screen("login")
        self.driver = self.loginScreen.driver
        atexit.register(self.exit_handler)
        threading.Thread(target=self.WaitForLogin,daemon=True ).start()

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

    def WaitForLogin(self):
        while self.loginScreen.loginFlag[0] != True:
            sleep(1)
        self.UpdateStatus(True)
        self.statusFlag[0] = True
    
    def WaitForStatusChange(self):
        while self.statusFlag[0] != True:
            sleep(1)
        self.UpdateStatus(True)

    def ScheduleImageUpdate(self,source,*largs):
        self.ids.status_image.source = source

    def UpdateStatus(self,availability):
        available = "StatusGreen.png"
        unavailable = "StatusRed.png"

        if availability:
            Clock.schedule_once(partial(self.ScheduleImageUpdate,available),1)
        else:
            Clock.schedule_once(partial(self.ScheduleImageUpdate,unavailable),1)

    def do_pick(self):
        if not self.statusFlag[0]:
            return
        Clock.unschedule(self.do_refresh)
        if(self.ids.order_list.text != ""):
            self.UpdateStatus(False)
            self.statusFlag[0] = False
            threading.Thread(target=self.driver.Scan,args=(self.ids.order_list.text.split('\n'),self.statusFlag,),daemon=True).start()
            threading.Thread(target=self.WaitForStatusChange,daemon=True ).start()
            self.ids.order_list.text = ""
        Clock.schedule_once(self.do_refresh, 600)

#Create callback to change text

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