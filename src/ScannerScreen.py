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

    do_refresh()
        initiates MainWebDriver.refresh() so that the website will be started again to circumvent
        idle timeout.
    """

    status_flag = [False]

    def __init__(self, manager, **kw):
        super(ScannerScreen, self).__init__(**kw)
        Window.bind(on_key_down=self._keydown)
        self.login_screen = manager.get_screen("login")
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
        if keycode == 40 and input_box.text != "":  # enter
            order_label = self.ids.order_list
            if order_label.text != "":
                order_label.text = order_label.text + "\n" + input_box.text
            else:
                order_label.text = input_box.text

            input_box.text = ""
            Clock.schedule_once(self._show_keyboard)

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
        self.status_flag[0] = True
        Clock.schedule_once(self.do_refresh, 600)

    def wait_for_status_change(self):
        """
        Continually runs untill status_flag is true, once true run update_status(True)
        to change the image
        """
        while self.status_flag[0] is not True:
            sleep(1)
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
        available = "images/StatusGreen.png"
        unavailable = "images/StatusRed.png"

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
        if not self.status_flag[0] and self.ids.order_list.text != "":
            return

        Clock.unschedule(self.do_refresh)
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
