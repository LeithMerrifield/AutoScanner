from time import sleep
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common import exceptions
from selenium.webdriver.common.alert import Alert
from src import Elements
from src.state import State
from selenium.webdriver.chrome.service import (
    Service as ChromeService,
)  # Similar thing for firefox also!
from subprocess import CREATE_NO_WINDOW  # This flag will only be available in windows
import os as os
import json
import threading
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from functools import partial

chrome_service = ChromeService("chromedriver")
chrome_service.creation_flags = CREATE_NO_WINDOW

MOBILE_EMULATOR = "https://5230881.app.netsuite.com/app/site/hosting/scriptlet.nl?script=4662&deploy=1&compid=5230881"
OFFICEURL = "https://www.office.com"
MY_APPS_URL = "https://myapps.microsoft.com/"


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
        # threading.Thread(target=self.run_driver).start()
        self.order_list = []
        self.state = State()
        self.driver = None

    def read_links(self):
        if not os.path.exists(r"src\settings.json"):
            return None

        with open(r".\src\settings.json", "r") as openfile:
            json_object = json.load(openfile)
        return json_object

    def run_driver(self) -> None:
        self.driver = webdriver.Chrome(service=chrome_service)

    # The process of picking an individual order
    def pick(self, order):
        """
        Continually Crawls through individual picking of each item untill it detects
        that the page is not NEXTPICKTASK, meaning all items are fullfilled and a packstation
        is assigned based on whether the order is for Australia or New Zealand
        """
        sleep(2)
        try:
            while True:
                sleep(1)
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(Elements.FIRSTENTRY)
                ).click()
                sleep(1)
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(Elements.BINNUMBER)
                ).click()
                sleep(1)
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(Elements.ITEMNUMBER)
                ).click()
                sleep(3)

                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(Elements.QUANTITY)
                )
                amount = self.driver.find_element(
                    By.XPATH,
                    "/html/body/div/div/div[2]/div[2]/div/div[1]/div[2]/div[1]/span",
                ).text.split(" ")[0]
                amount += "\n"
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(Elements.QUANTITYINPUT)
                ).send_keys(amount)
                sleep(3)

                mark = self.driver.find_element(
                    By.XPATH, "/html/body/div/div/div[1]/div[2]/div[1]"
                )

                print(mark.text.lower() + " : " + "Pick Task Complete".lower())

                if mark.text.lower() == "Pick Task Complete".lower():
                    WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable(Elements.NEXTPICKTASK)
                    ).click()
                else:
                    break

            sleep(3)
            station = ""
            if "sau" in order.lower():
                station = "PackStation03\n"
            else:
                station = "PackStation02\n"

            WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(Elements.STATIONINPUT)
            ).send_keys(station)

            sleep(1)

            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(Elements.NEXTORDERBUTTON)
            ).click()
        except exceptions.NoSuchWindowException:
            self.driver_closed()
            return

    def resync(self):
        """
        Re orients the driver to the start of the mobile emulator website
        """
        try:
            self.driver.get(MOBILE_EMULATOR)
            sleep(3)
            self.get_to_orders()
        except exceptions.NoSuchWindowException:
            self.driver_closed()

    # Will run the scanning/picking process for n orders in order_list
    def scan(self, my_orders: list, status_flag, order_callback, login_callback):
        """
        self.state.change_state(self.identify_page())
        if self.state.current_state != Elements.STAGEDICT["Select Order"]:
            self.resync()
        """

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
                        EC.element_to_be_clickable(Elements.ORDERINPUT)
                    ).send_keys(order)
                except exceptions.TimeoutException:
                    WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable(Elements.ORDERINPUTWITHERROR)
                    ).send_keys(order)
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(Elements.ENTERORDER)
                ).click()

                try:
                    self.pick(order)
                except exceptions.TimeoutException:
                    continue
                except:
                    # Pick Failed
                    my_orders[idx] = f"{order} - Failed, Will Retry"
                    newlist = [e for e in my_orders]
                    newlist.append(f"{order}")
                    newlist.reverse()
                    order_callback(order_list=newlist)
                    my_orders.append(order)
                    self.refresh()
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
        print("Scanning Complete \n Start Again\n")

    def refresh(self, status_flag=None, login_callback=None):
        """
        moves back and forth to avoid idle timeout,
        not sure it actually works
        """
        try:
            self.driver.get(self.netsuite_sso)
            sleep(1)
            alert = Alert(self.driver)
            alert.accept()
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
        self, login_flag=None, username=None, password=None, login_failed_callback=None
    ):
        """
        Goes through the process of logging into microsoft and navigates to netsuite
        """
        links_object = self.read_links()

        if links_object is None:
            raise Exception("Missing settings.json in the source folder.")

        self.netsuite_sso = links_object["Netsuite_SSO"]
        self.run_driver()
        sleep(3)

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
        try:
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(Elements.USERNAMEFIELD)
            ).send_keys(username)
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(Elements.NEXTBUTTON)
            ).click()
            sleep(1)

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
            except Exception as e:
                # means that the login passed
                pass

            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(Elements.PASSWORDFIELD)
            ).send_keys(password)

            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(Elements.NEXTBUTTON)
            ).click()

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
            except Exception as e:
                pass

            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(Elements.NOBUTTON)
            ).click()
            sleep(2)
            # self.driver.get(NETSUITE_SSO)
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(Elements.NETSUITE_ENVIRONMENT)
            ).click()
            self.get_to_orders(login_flag)
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

    def get_to_orders(self, login_flag=None, refresh_flag=False):
        """
        Navigates to the picking section of mobile emulator
        and sets the login_flag to true indicating the login process is done.
        """
        sleep(2)
        if not refresh_flag:
            self.driver.get(MOBILE_EMULATOR)
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(Elements.WMS)
        ).click()
        sleep(2)
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(Elements.WAREHOUSE)
        ).click()
        sleep(2)
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(Elements.PICKING)
        ).click()
        sleep(2)
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(Elements.SINGLEORDER)
        ).click()
        sleep(2)
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(Elements.RELEASEDORDER)
        ).click()
        sleep(2)
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(Elements.SALESORDER)
        ).click()

        self.state.change_state(self.identify_page())
        if login_flag is None:
            return
        login_flag[0] = True

    def test_popup(self, title, content_text, dt):
        popup = Popup(
            title=title,
            content=Label(text=content_text),
            size_hint=(None, None),
            size=(450, 200),
        )
        popup.open()

    def driver_closed(self):
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
