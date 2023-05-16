from kivy.clock import Clock
from kivy.uix.screenmanager import Screen

import atexit
import threading
from time import sleep
from functools import partial

# fmt: off
from kivy.core.window import Window  # pylint: disable=wrong-import-position,ungrouped-imports
# fmt: on


class ScannerScreen(Screen):
    """
    Class used to drive scanning orders into netsuite

    Attributes
    ----------
    driver : Selenium Webdriver
        The main chrome object
    order_list :
        List that will hold order strings

    Methods
    -------
    says(sound=None)
        Prints the animals name and what sound it makes

    pick(order=None)
        After the order has been started this will loop through and pick all items
        Enters into correct packstation

    scan()
        Continually loops to allow inputting of a list and picking all the orders

    login()
        Logs in and navigates to the WMS order list

    """

    status_flag = [False]

    def __init__(self, manager, **kw):
        super(ScannerScreen, self).__init__(**kw)
        Window.bind(on_key_down=self._keydown)
        self.login_screen = manager.get_screen("login")
        self.driver = self.login_screen.driver
        atexit.register(self.exit_handler)
        threading.Thread(target=self.wait_for_login, daemon=True).start()

    def _keydown(self, instance, keyboard, keycode, text, modifiers):
        if self.manager.current != "scanner":
            return
        input_box = self.ids.order_input
        if keycode == 40 and input_box.text != "":  # enter
            order_label = self.ids.order_list
            if order_label.text != "":
                order_label.text = order_label.text + "\n" + input_box.text
            else:
                order_label.text = input_box.text

            input_box.text = ""
            Clock.schedule_once(self.show_keyboard)

    def wait_for_login(self):
        while self.login_screen.login_flag[0] is not True:
            sleep(1)
        self.update_status(True)
        self.status_flag[0] = True

    def wait_for_status_change(self):
        while self.status_flag[0] is not True:
            sleep(1)
        self.update_status(True)

    def schedule_image_update(self, source, *largs):
        self.ids.status_image.source = source

    def update_status(self, availability):
        available = "images/StatusGreen.png"
        unavailable = "images/StatusRed.png"

        if availability:
            Clock.schedule_once(partial(self.schedule_image_update, available), 1)
        else:
            Clock.schedule_once(partial(self.schedule_image_update, unavailable), 1)

    def do_pick(self):
        if not self.status_flag[0]:
            return
        Clock.unschedule(self.do_refresh)
        if self.ids.order_list.text != "":
            self.update_status(False)
            self.status_flag[0] = False

            threading.Thread(
                target=self.driver.scan,
                args=(
                    self.ids.order_list.text.split("\n"),
                    self.status_flag,
                ),
                daemon=True,
            ).start()

            threading.Thread(target=self.wait_for_status_change, daemon=True).start()
            self.ids.order_list.text = ""
        Clock.schedule_once(self.do_refresh, 600)

    # Create callback to change text

    def do_refresh(self, dt):
        self.driver.refresh()

    def show_keyboard(self, event):
        input_box = self.ids.order_input
        input_box.focus = True

    def exit_handler(self):
        self.driver.exit()
