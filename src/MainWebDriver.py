from time import sleep
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common import exceptions
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.chrome.options import Options
from src.Elements import ElementClass
from src.state import State
from src.CheckDriver import compare_and_download as update_driver
from selenium.webdriver.chrome.service import (
    Service as ChromeService,
)  # Similar thing for firefox also!
from subprocess import CREATE_NO_WINDOW  # This flag will only be available in windows
import os
import json
import pathlib
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from functools import partial
import shutil

MOBILE_EMULATOR = "https://5230881.app.netsuite.com/app/site/hosting/scriptlet.nl?script=4662&deploy=1&compid=5230881"
OFFICEURL = "https://www.office.com"
MY_APPS_URL = "https://myapps.microsoft.com/"
TIMOUT = 20


class MainWebDriver(object):
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
    pick(order=None)
        After the order has been started this will loop through and pick all items
        Enters into correct packstation

    scan()
        Continually loops to allow inputting of a list and picking all the orders

    login()
        Logs in and navigates to the WMS order list

    """

    def __init__(self) -> None:
        self.order_list = []
        self.state = State()
        self.driver = None
        self.continue_program = True
        self.pick_delay = 1
        self.elements = ElementClass()
        self.check_if_elements_exist()

    def read_links(self):
        """Reads settings json file and returns json object

        Returns:
            json object: All settings
        """
        if not os.path.exists(r"src\settings.json"):
            return None

        with open(r".\src\settings.json", "r") as openfile:
            json_object = json.load(openfile)
        return json_object

    def run_driver(self, chrome_service, chrome_options, manual_flag) -> None:
        """Launches web driver

        Args:
            chrome_service (str): path to chrome driver
            chrome_options (Options): Set of options for the web driver
            manual_flag (bool): set to determine if self defined path to chrome driver
        """
        self.driver = webdriver.Chrome(
            service=chrome_service, chrome_options=chrome_options
        )

    def check_if_elements_exist(self):
        if self.elements.element_error_flag:
            Clock.schedule_once(
                partial(
                    self.test_popup,
                    "elements.json doesn't exist",
                    "reinstall autoscanner",
                ),
                1,
            )
            self.continue_program = False

    def pick(self, order):
        """
        Continually Crawls through individual picking of each item untill it detects
        that the page is not NEXTPICKTASK, meaning all items are fullfilled and a packstation
        is assigned based on whether the order is for Australia or New Zealand

        Args:
            order (str): Order Number
        """
        sleep(1)
        try:
            while True:
                self.try_click_element(self.elements.FIRSTENTRY)
                self.try_click_element(self.elements.BINNUMBER)
                self.try_click_element(self.elements.ITEMNUMBER)

                amount = self.try_return_text_element(
                    self.elements.QUANTITYAMOUNT
                ).split(" ")[0]

                self.try_send_keys_element(self.elements.QUANTITYINPUT, amount)
                self.try_click_element(self.elements.QUANTITYBUTTON)

                mark = self.try_return_text_element(
                    (By.XPATH, "/html/body/div/div/div[1]/div[2]/div[1]")
                )

                if mark.lower() == "Pick Task Complete".lower():
                    self.try_click_element(self.elements.NEXTPICKTASK)
                else:
                    break

            sleep(self.pick_delay)
            station = ""
            if "sau" in order.lower():
                station = "PackStation03"
            else:
                station = "PackStation02"

            self.try_send_keys_element(self.elements.STATIONINPUT, station)
            self.try_click_element(self.elements.STATIONBUTTON)
            self.try_click_element(self.elements.NEXTORDERBUTTON)
        except exceptions.NoSuchWindowException:
            self.driver_closed()
            return

    def try_click_element(self, element, T=10):
        for i in range(T):
            try:
                self.driver.find_element(element[0], element[1]).click()
                sleep(self.pick_delay)
                return
            except Exception as e:
                sleep(self.pick_delay)
                continue
        raise exceptions.NoSuchElementException

    def try_send_keys_element(self, element, text):
        for i in range(10):
            try:
                self.driver.find_element(element[0], element[1]).send_keys(text)
                sleep(self.pick_delay)
                return
            except Exception as e:
                sleep(self.pick_delay)
                continue
        raise exceptions.NoSuchElementException

    def try_return_text_element(self, element):
        for i in range(10):
            try:
                text = self.driver.find_element(element[0], element[1]).text
                return text
            except Exception as e:
                sleep(self.pick_delay)
                continue
        raise exceptions.NoSuchElementException

    def scan(
        self,
        my_orders: list,
        status_flag: bool,
        order_callback: callable,
        login_callback: callable,
        force_refresh_flag: bool,
    ):
        """Takes a list of orders and processes them

        Args:
            my_orders (list): List of orders to be processed
            status_flag (bool): Used to set the status indicator of the app
            order_callback (callable): Used to update the gui text with status
            login_callback (callable): Will trigger on exception to create pop up on gui
            force_refresh_flag (bool): Used to refresh driver in the event netsuite has timeout.

        Raises:
            exceptions.TimeoutException: A certain element isn't found in time.
            exceptions.NoSuchWindowException: Main window is closed
            exceptions.UnexpectedAlertPresentException: Random popup has appeared
        """
        if force_refresh_flag[0]:
            self.refresh(force_refresh_flag=force_refresh_flag)

        my_orders.reverse()

        for idx, order in enumerate(my_orders):
            sleep(2)

            my_orders[idx] = f"{order} - Started"
            newlist = [e for e in my_orders]
            newlist.reverse()
            order_callback(order_list=newlist)

            try:
                # Checks for error popup that would change xpath of input
                # probably could run a check for if the input exists at xpath
                # but I may aswell do it this way
                try:
                    WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable(self.elements.ORDERINPUT)
                    ).clear()
                    WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable(self.elements.ORDERINPUT)
                    ).send_keys(order)
                except exceptions.TimeoutException:
                    # Timeout in finding the normal textbox to enter the order into
                    try:
                        WebDriverWait(self.driver, 2).until(
                            EC.element_to_be_clickable(
                                self.elements.ORDERINPUTWITHERROR
                            )
                        ).clear()
                        WebDriverWait(self.driver, 2).until(
                            EC.element_to_be_clickable(
                                self.elements.ORDERINPUTWITHERROR
                            )
                        ).send_keys(order)
                    except exceptions.TimeoutException as e:
                        # At this point there is no text box to enter into at all
                        # so a refresh is in order
                        my_orders[idx] = f"{order} - Failed, Will Retry"
                        newlist = [e for e in my_orders]
                        newlist.append(f"{order}")
                        newlist.reverse()
                        order_callback(order_list=newlist)
                        my_orders.append(order)
                        self.refresh()
                        with open("./errorlog.txt", "a", encoding="UTF-8") as errorlog:
                            errorlog.write("\n" + str(e))
                        continue

                WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable(self.elements.ENTERORDER)
                ).click()

                try:
                    for i in range(5):
                        print(self.identify_page())
                        if self.identify_page().lower() == "Select Pick Task".lower():
                            break
                        else:
                            sleep(1)

                        if i == 4:
                            raise exceptions.TimeoutException

                    self.pick(order)
                except exceptions.TimeoutException:
                    continue
                except Exception as e:
                    # Pick Failed
                    if (
                        isinstance(e, exceptions.StaleElementReferenceException)
                        or isinstance(e, exceptions.NoSuchElementException)
                    ) and self.pick_delay < 3:
                        self.pick_delay += 1

                    my_orders[idx] = f"{order} - Failed, Will Retry"
                    newlist = [e for e in my_orders]
                    newlist.append(f"{order}")
                    newlist.reverse()
                    order_callback(order_list=newlist)
                    my_orders.append(order)
                    self.refresh()

                    with open("./errorlog.txt", "a", encoding="UTF-8") as errorlog:
                        errorlog.write("\n" + str(e))

                    continue
            except (
                exceptions.NoSuchWindowException,
                exceptions.UnexpectedAlertPresentException,
            ):
                login_callback(3)
                self.driver_closed()
                return

            my_orders[idx] = f"{order} - Complete"
            newlist = [e for e in my_orders]
            newlist.reverse()
            order_callback(order_list=newlist)

        status_flag[0] = True

    def refresh(self, force_refresh_flag=None, status_flag=None, login_callback=None):
        """Re-orients the driver to the start of the mobile emulator website

        Args:
            force_refresh_flag (bool, optional): Determines if a forced refresh is being triggered. Defaults to None.
            status_flag (bool, optional): Used to set the status indicator of the app . Defaults to None.
            login_callback (callable, optional): Used to initiate error popup . Defaults to None.
        """
        try:
            if force_refresh_flag is None:
                pass
            else:
                force_refresh_flag[0] = False

            self.driver.get(self.netsuite_sso)
            sleep(1)

            try:
                alert = Alert(self.driver)
                alert.accept()
            except exceptions.NoAlertPresentException:
                #   no alert for some reason
                pass
            sleep(5)
            self.driver.get(MOBILE_EMULATOR)
            sleep(2)
            next_button = (By.XPATH, "/html/body/div/div/div[3]/button")
            WebDriverWait(self.driver, 50).until(
                EC.element_to_be_clickable(next_button)
            ).click()
            sleep(1)
            self.get_to_orders(login_flag=status_flag, refresh_flag=True)
        except exceptions.NoSuchWindowException:
            login_callback()
            self.driver_closed()
            return

    def login(
        self,
        login_flag,
        username,
        password,
        login_callback,
    ):
        """Setups and creates webdriver, also responsible for automated
        login and navigation to wms picking screen

        Args:
            login_flag (list[bool]): Used as a pass by reference to set the status
            of the application.
            username (str): Username to be entered into login.
            password (str): Password to be entered into login.
            login_callback (callable):  Used to initiate error popup.

        Raises:
            Exception:
                exceptions.SessionNotCreatedException: Means the
                webdriver did not initiate properly.
        """
        links_object = self.read_links()

        if links_object is None:
            raise Exception("Missing settings.json in the source folder.")

        self.netsuite_sso = links_object["Netsuite_SSO"]

        chrome_service = ChromeService(
            executable_path="./chromedriver-win64/chromedriver.exe"
        )
        chrome_service.creation_flags = CREATE_NO_WINDOW
        chrome_options = Options()

        try:
            shutil.rmtree("userdata/default/network", ignore_errors=False, onerror=None)
        except:
            pass

        chrome_options.add_argument(
            f"user-data-dir={pathlib.Path().absolute()}\\userdata"
        )

        try:
            self.run_driver(chrome_service, chrome_options, False)
        except (
            exceptions.SessionNotCreatedException,
            exceptions.SeleniumManagerException,
        ):
            login_callback()
            Clock.schedule_once(
                partial(
                    self.test_popup,
                    "Chrome Driver Issue",
                    "  I've downloaded the new driver\n \
                       Try again",
                ),
                1,
            )
            update_driver()
            return
        except exceptions.WebDriverException as e:
            login_callback()
            if "cannot find chrome binary" in e.msg.lower():
                Clock.schedule_once(
                    partial(
                        self.test_popup,
                        "Chrome Issue",
                        "Chrome isn't installed",
                    ),
                    1,
                )
            return
        sleep(3)

        self.login_microsoft(login_flag, username, password, login_callback)

    def login_microsoft(self, login_flag, username, password, login_failed_callback):
        """Was separated from login function to accomodate for netsuite only
        logins

            login_flag (list[bool]): Used as a pass by reference to set the status
            of the application.
            username (str): Username to be entered into login.
            password (str): Password to be entered into login.
            login_callback (callable):  Used to initiate error popup.
        """
        try:
            self.driver.get(self.netsuite_sso)
        except exceptions.NoSuchWindowException:
            login_failed_callback()
            self.driver_closed()
            return
        except exceptions.InvalidArgumentException:
            self.exit()
            login_failed_callback()
            Clock.schedule_once(
                partial(
                    self.test_popup,
                    "SSO Issue",
                    "You need to set the Netsuite SSO link in the settings menu",
                ),
                1,
            )
            return

        try:
            if "login.microsoftonline.com" not in self.driver.current_url:
                login_failed_callback()
                Clock.schedule_once(
                    partial(
                        self.test_popup,
                        "SSO Issue",
                        "The link is valid but it's not the netsuite SSO",
                    ),
                    1,
                )
                self.exit()
                login_failed_callback()
                return
        except exceptions.NoSuchWindowException:
            login_failed_callback()
            self.driver_closed()
            return
        # overall try will check for if the driver closes
        existing_login = False
        try:
            # Will check to see if the username field exists
            # It will exist if there is no previous data or data has been wiped
            sleep(2)
            self.try_send_keys_element(self.elements.USERNAMEFIELD, username)
            self.try_click_element(self.elements.NEXTBUTTON)

            try:
                self.driver.find_element(By.ID, "usernameError")
                self.exit()
                login_failed_callback(error_code=1)
                Clock.schedule_once(
                    partial(
                        self.test_popup,
                        "Login Issue",
                        "Your username was entered incorrectly",
                    ),
                    1,
                )
                return
            except exceptions.NoSuchElementException:
                # means that the login passed
                pass

            self.try_send_keys_element(self.elements.PASSWORDFIELD, password)
            self.try_click_element(self.elements.NEXTBUTTON)

            try:
                self.driver.find_element(By.ID, "passwordError")
                self.exit()
                login_failed_callback(error_code=2)
                Clock.schedule_once(
                    partial(
                        self.test_popup,
                        "Login Issue",
                        "Your password was entered incorrectly",
                    ),
                    1,
                )
                return
            except exceptions.NoSuchElementException:
                # means the password was successfully entered
                pass

            self.try_click_element(self.elements.NOBUTTON)

            self.try_click_element(self.elements.NETSUITE_ENVIRONMENT)

            sleep(2)

            self.get_to_orders(login_flag=login_flag)
        except (exceptions.TimeoutException, exceptions.StaleElementReferenceException):
            login_failed_callback()
            Clock.schedule_once(
                partial(
                    self.test_popup,
                    "Web Client Timeout",
                    "Start Login Process Again",
                ),
                1,
            )
            self.exit()
        except exceptions.NoSuchWindowException:
            login_failed_callback()
            self.driver_closed()
            return

    def get_to_orders(self, login_flag, refresh_flag=False):
        """Navigates to the picking section of mobile emulator
        and sets the login_flag to true indicating the login process is done.

        Args:
            login_flag (list[bool]): Used as a pass by reference to set the status
            of the application.
            refresh_flag (bool, optional): If it's true it means there is a refresh occuring and to not
            get the url again
        """

        sleep(2)
        if not refresh_flag:
            self.driver.get(MOBILE_EMULATOR)

        try:
            self.try_click_element(self.elements.LASTSESSIONBUTTON, 2)
        except exceptions.NoSuchElementException:
            pass

        self.try_click_element(self.elements.WMS)
        self.try_click_element(self.elements.WAREHOUSE)
        self.try_click_element(self.elements.PICKING)
        self.try_click_element(self.elements.SINGLEORDER)
        self.try_click_element(self.elements.RELEASEDORDER)
        self.try_click_element(self.elements.SALESORDER)

        self.state.change_state(self.identify_page())
        if login_flag is None:
            return
        login_flag[0] = True

    def test_popup(self, title, content_text, dt):
        """Creates a popup with the passed content_text

        Args:
            title (str): title text of the popup
            content_text (str): The content text of the popup
            dt (int): used by clock scheduling tasks
        """
        popup = Popup(
            title=title,
            content=Label(text=content_text),
            size_hint=(None, None),
            size=(450, 200),
        )
        popup.open()

    def driver_closed(self):
        """
        initiates pop up
        """
        Clock.schedule_once(
            partial(
                self.test_popup,
                "Web Client Closed",
                "Start Login Process Again",
            ),
            1,
        )

    def exit(self):
        """
        closes the selenium driver
        """
        if self.driver is not None:
            self.driver.quit()

    def identify_page(self):
        """
        returns the current page
        """
        mark = self.driver.find_element(
            By.XPATH, "/html/body/div/div/div[1]/div[2]/div[1]"
        )
        return mark.text

    def wait_for_element(self, value: tuple = None, timeout: int = 30):
        count = 0
        while count < timeout:
            try:
                element = self.driver.find_element(by=value[0], value=value[1])
                return element
            except:
                pass
            count += 1
            sleep(1)
        raise exceptions.TimeoutException
