import pickle
from time import sleep
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common import exceptions
from src import Elements, Login
from src.state import State
import threading

MOBILE_EMULATOR = "https://5230881.app.netsuite.com/app/site/hosting/scriptlet.nl?script=4662&deploy=1&compid=5230881"
OFFICEURL = "https://www.office.com"
NETSUITE_SSO = "https://account.activedirectory.windowsazure.com/applications/signin/3b7330ae-2893-492f-8157-09fecce53355?tenantId=7261aa19-728c-457c-bb6e-a31f9a21516d"
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
        threading.Thread(target=self.run_driver).start()
        self.order_list = []
        self.state = State()

    def run_driver(self) -> None:
        self.driver = webdriver.Chrome()

    def save_cookies(self) -> None:
        cookies = self.driver.get_cookies()
        pickle.dump(cookies, open(self.cookiePath, "wb"))

    def load_cookies(self) -> None:
        cookies = pickle.load(open("cookies.pkl", "rb"))
        for cookie in cookies:
            try:
                cookie["domain"] = ".microsoftonline.com"
                print(cookie["domain"])
                self.driver.add_cookie(cookie)
            except exceptions.InvalidCookieDomainException as e:
                print(e.msg)

    # The process of picking an individual order
    def pick(self, order):
        """
        Continually Crawls through individual picking of each item untill it detects
        that the page is not NEXTPICKTASK, meaning all items are fullfilled and a packstation
        is assigned based on whether the order is for Australia or New Zealand
        """
        sleep(2)
        while True:
            sleep(1)
            WebDriverWait(self.driver, 50).until(
                EC.element_to_be_clickable(Elements.FIRSTENTRY)
            ).click()
            sleep(1)
            WebDriverWait(self.driver, 50).until(
                EC.element_to_be_clickable(Elements.BINNUMBER)
            ).click()
            sleep(1)
            WebDriverWait(self.driver, 50).until(
                EC.element_to_be_clickable(Elements.ITEMNUMBER)
            ).click()
            sleep(3)

            WebDriverWait(self.driver, 50).until(
                EC.presence_of_element_located(Elements.QUANTITY)
            )
            amount = self.driver.find_element(
                By.XPATH,
                "/html/body/div/div/div[2]/div[2]/div/div[1]/div[2]/div[1]/span",
            ).text.split(" ")[0]
            amount += "\n"
            WebDriverWait(self.driver, 50).until(
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

        WebDriverWait(self.driver, 50).until(
            EC.element_to_be_clickable(Elements.NEXTORDERBUTTON)
        ).click()

    def resync(self):
        """
        Re orients the driver to the start of the mobile emulator website
        """
        self.driver.get(MOBILE_EMULATOR)
        sleep(3)
        self.GetToOrders()

    # Will run the scanning/picking process for n orders in order_list
    def scan(self, my_orders: list, status_flag):
        self.state.change_state(self.identify_page())
        if self.state.current_state != Elements.STAGEDICT["Select Order"]:
            self.resync()
        my_orders.reverse()
        for order in my_orders:
            sleep(2)
            WebDriverWait(self.driver, 50).until(
                EC.element_to_be_clickable(Elements.ORDERINPUT)
            ).send_keys(order)
            WebDriverWait(self.driver, 50).until(
                EC.element_to_be_clickable(Elements.ENTERORDER)
            ).click()
            self.pick(order)
        status_flag[0] = True
        print("Scanning Complete \n Start Again\n")

    def refresh(self):
        """
        moves back and forth to avoid idle timeout,
        not sure it actually works
        """
        self.driver.find_element(By.XPATH, Elements.BACKBUTTONREFRESH).click()
        sleep(2)
        self.driver.find_element(By.XPATH, Elements.SALESORDERREFRESH).click()

    def login(self, login_flag=None):
        """
        Goes through the process of logging into microsoft and navigates to netsuite
        """
        self.driver.get(NETSUITE_SSO)
        WebDriverWait(self.driver, 50).until(
            EC.element_to_be_clickable(Elements.USERNAMEFIELD)
        ).send_keys(Login.Username)
        WebDriverWait(self.driver, 50).until(
            EC.element_to_be_clickable(Elements.NEXTBUTTON)
        ).click()
        WebDriverWait(self.driver, 50).until(
            EC.element_to_be_clickable(Elements.PASSWORDFIELD)
        ).send_keys(Login.Password)
        WebDriverWait(self.driver, 50).until(
            EC.element_to_be_clickable(Elements.NEXTBUTTON)
        ).click()
        WebDriverWait(self.driver, 50).until(
            EC.element_to_be_clickable(Elements.NOBUTTON)
        ).click()
        WebDriverWait(self.driver, 50).until(
            EC.element_to_be_clickable(Elements.NETSUITE_ENVIRONMENT)
        ).click()
        self.GetToOrders(login_flag)

    def GetToOrders(self, login_flag=None):
        """
        Navigates to the picking section of mobile emulator
        and sets the login_flag to true indicating the login process is done.
        """
        self.driver.get(MOBILE_EMULATOR)
        WebDriverWait(self.driver, 50).until(
            EC.element_to_be_clickable(Elements.WMS)
        ).click()
        WebDriverWait(self.driver, 50).until(
            EC.element_to_be_clickable(Elements.WAREHOUSE)
        ).click()
        sleep(1)
        WebDriverWait(self.driver, 50).until(
            EC.element_to_be_clickable(Elements.PICKING)
        ).click()
        sleep(1)
        WebDriverWait(self.driver, 50).until(
            EC.element_to_be_clickable(Elements.SINGLEORDER)
        ).click()
        sleep(1)
        WebDriverWait(self.driver, 50).until(
            EC.element_to_be_clickable(Elements.RELEASEDORDER)
        ).click()
        sleep(1)
        WebDriverWait(self.driver, 50).until(
            EC.element_to_be_clickable(Elements.SALESORDER)
        ).click()
        self.state.change_state(self.identify_page())
        if login_flag is None:
            login_flag[0] = False
        login_flag[0] = True

    def exit(self):
        """
        closes the selenium driver
        """
        self.driver.close()

    def identify_page(self):
        """
        returns the current page
        """
        mark = self.driver.find_element(
            By.XPATH, "/html/body/div/div/div[1]/div[2]/div[1]"
        )
        return mark.text
