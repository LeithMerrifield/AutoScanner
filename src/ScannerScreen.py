from kivy.clock import Clock
from kivy.uix.screenmanager import Screen, SlideTransition

import atexit
import threading
import os as os
import json
from time import sleep
from functools import partial
# fmt: off
from kivy.core.window import Window  # pylint: disable=wrong-import-position,ungrouped-imports
# fmt: on


class ScannerScreen(Screen):
    """
    Scanner Screen for Kivy GUI
     Facilitates picking function

    Attributes
    ----------
    status_flag : Used to determine whether a selenium task is in progress

    Methods
    -------

    wait_for_login()
        Runs update_status(True) once the login process is complete.

    wait_for_status_change()
        Runs update_status(True) once the current selenium process is complete.

    schedule_image_update(source=string)
        Will schedule the status image to change based on the address provided.

    update_status(availability=bool)
        Based on availability it will run schedule_image_update to update the status
        accordingly

    do_pick()
        if status_flag is true then it will take the text from kivy element order_list
        and create a list of each order number. This list will be passed to a created thread
        running MainWebDriver.scan(order_list) to initiate the scanning/picking process.

    do_remove_all()
        removes text from 'order_list' label

    do_remove_last()
        removes latest line of text from 'order_list' label

    do_refresh()
        initiates MainWebDriver.refresh() so that the website will be started again to circumvent
        idle timeout.
    """

    status_flag = [False]

    def __init__(self, manager, **kw):
        super(ScannerScreen, self).__init__(**kw)
        Window.bind(on_key_down=self._keydown)
        self.login_screen = manager.get_screen("login")
        self.settings_screen = manager.get_screen("settings")
        self.driver = self.login_screen.driver
        atexit.register(self._exit_handler)
        threading.Thread(target=self.wait_for_login, daemon=True).start()

    def _keydown(self, instance, keyboard, keycode, text, modifiers):
        """
        After a key is pressed this function is run and if the keycode is 40 (space)
        then add the order number to the label
        """
        if self.manager.current != "scanner":
            return

        input_box = self.ids.order_input

        if keycode == 40 and input_box.text != "":
            self.add_order_to_list()

    def add_order_to_list(self):
        input_box = self.ids.order_input

        order_label = self.ids.order_list

        if order_label.text != "":
            if not input_box.text in order_label.text:
                order_label.text = order_label.text + "\n" + input_box.text
        else:
            order_label.text = input_box.text

        input_box.text = ""
        Clock.schedule_once(self._show_keyboard, 1)

    def _show_keyboard(self, event):
        """
        Automatically focuses on the textbox for the next order to inputted
        """
        input_box = self.ids.order_input
        input_box.focus = True

    def _exit_handler(self):
        """
        Closes the selenium driver on exit
        """
        self.driver.exit()

    def wait_for_login(self):
        """
        Continually run untill login_flag from the login screen is true
        once true it means the login process is complete and status_flag is updated to true
        """
        while self.login_screen.login_flag[0] is not True:
            sleep(1)
        self.update_status(True)
        # in the event that we need to do the login process again reset login_flag to false
        self.login_screen.login_flag[0] = False
        Clock.schedule_once(self.do_refresh, 1200)

    def wait_for_status_change(self):
        """
        Continually runs untill status_flag is true, once true run update_status(True)
        to change the image
        """
        while self.status_flag[0] is not True:
            sleep(1)
        self.ids.order_list.text = ""
        self.update_status(True)

    def schedule_image_update(self, source, *largs):
        """
        Changes the status_image source to the desired image at address
        """
        self.ids.status_image.source = source

    def update_status(self, availability):
        """
        Based on the passed in boolean it will schedule the update of the status_image.
        """
        self.status_flag[0] = availability
        path = os.getcwd()
        available = path + "/src/images/StatusGreen.png"
        unavailable = path + "/src/images/StatusRed.png"

        if availability:
            Clock.schedule_once(partial(self.schedule_image_update, available), 1)
        else:
            Clock.schedule_once(partial(self.schedule_image_update, unavailable), 1)

    def do_pick(self):
        """
        Only runs if the status_flag is True and the label text is not empty \n
        Reset the timer of do_refresh \n
        Updates the status to false or in use \n
        Take all of the text from order_list and split on newline, pass this list to the scan
        function of the selenium driver along with the status_flag so that it can indicated when the
        proccess is done

        """
        if not self.status_flag[0] or self.ids.order_list.text == "":
            return

        Clock.unschedule(self.do_refresh)
        self.update_status(False)

        threading.Thread(
            target=self.driver.scan,
            args=(
                self.ids.order_list.text.split("\n"),
                self.status_flag,
                self.order_callback,
                self.login_callback,
            ),
            daemon=True,
        ).start()

        threading.Thread(target=self.wait_for_status_change, daemon=True).start()
        # self.ids.order_list.text = ""
        Clock.schedule_once(self.do_refresh, 1200)

    def do_remove_all(self):
        """
        removes all text from the order label
        """
        self.ids.order_list.text = ""

    def do_remove_last(self):
        """
        removes lastest entry in order label
        """
        orders = self.ids.order_list.text.split("\n")
        orders = orders[:-1]
        text = "\n".join(orders)
        self.ids.order_list.text = text

    def order_callback(self, order_list):
        self.ids.order_list.text = "\n".join(order_list)
        return

    def do_refresh(self, dt):
        settings = self.read_links()
        if not settings["Timeout_Avoidance"]:
            Clock.schedule_once(self.do_refresh, 1200)
            return
        self.update_status(False)
        threading.Thread(
            target=self.driver.refresh,
            args=(self.status_flag, self.login_callback),
            daemon=True,
        ).start()
        threading.Thread(target=self.wait_for_status_change, daemon=True).start()
        Clock.schedule_once(self.do_refresh, 1200)

    def show_settings(self):
        self.settings_screen.set_previous_screen("scanner")
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "settings"

    def transition_to_login(self, error_code, dt):
        if error_code == 3:
            self.ids.order_list.text = ""
            self.update_status(True)
        self.update_status(False)
        threading.Thread(target=self.wait_for_login, daemon=True).start()
        self.manager.current = "login"

    def login_callback(self, error_code=0):
        """
        Error Codes:
        1
        2
        3 - No driver window when gone to pick, wipes order_list and resets status
        """
        self.manager.transition = SlideTransition(direction="right")
        Clock.schedule_once(
            partial(
                self.transition_to_login,
                error_code,
            ),
            1,
        )

    def read_links(self):
        if not os.path.exists(r"src\settings.json"):
            return None

        with open(r".\src\settings.json", "r") as openfile:
            json_object = json.load(openfile)
            openfile.close()
        return json_object
