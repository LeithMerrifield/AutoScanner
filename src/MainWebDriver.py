import pickle
from time import sleep
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common import exceptions
from selenium.webdriver.common.alert import Alert
from src import Elements
from src.state import State

MOBILE_EMULATOR = "https://5230881.app.netsuite.com/app/site/hosting/scriptlet.nl?script=4662&deploy=1&compid=5230881"
OFFICEURL = "https://www.office.com"
NETSUITE_SSO = "https://launcher.myapps.microsoft.com/api/signin/fd4bc304-663f-4e7b-9245-93596454cc99?tenantId=7261aa19-728c-457c-bb6e-a31f9a21516d"
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

    def refresh(self, status_flag=None):
        """
        moves back and forth to avoid idle timeout,
        not sure it actually works
        """
        print("Refresh Started")
        self.driver.get(NETSUITE_SSO)
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
        self.GetToOrders(login_flag=status_flag, refresh_flag=True)

    def login(
        self, login_flag=None, username=None, password=None, login_failed_callback=None
    ):
        """
        Goes through the process of logging into microsoft and navigates to netsuite
        """
        self.run_driver()
        sleep(3)
        self.driver.get(NETSUITE_SSO)

        WebDriverWait(self.driver, 50).until(
            EC.element_to_be_clickable(Elements.USERNAMEFIELD)
        ).send_keys(username)
        WebDriverWait(self.driver, 50).until(
            EC.element_to_be_clickable(Elements.NEXTBUTTON)
        ).click()
        sleep(1)

        try:
            self.driver.find_element(By.ID, "usernameError")
            self.exit()
            login_failed_callback()
            print("usernamError")
            return
        except Exception as e:
            # means that the login passed
            pass

        WebDriverWait(self.driver, 50).until(
            EC.element_to_be_clickable(Elements.PASSWORDFIELD)
        ).send_keys(password)

        WebDriverWait(self.driver, 50).until(
            EC.element_to_be_clickable(Elements.NEXTBUTTON)
        ).click()

        try:
            self.driver.find_element(By.ID, "passwordError")
            self.exit()
            login_failed_callback()
            print("pasaError")
            return
        except Exception as e:
            pass

        WebDriverWait(self.driver, 50).until(
            EC.element_to_be_clickable(Elements.NOBUTTON)
        ).click()
        sleep(2)
        # self.driver.get(NETSUITE_SSO)
        WebDriverWait(self.driver, 50).until(
            EC.element_to_be_clickable(Elements.NETSUITE_ENVIRONMENT)
        ).click()
        self.GetToOrders(login_flag)

    def GetToOrders(self, login_flag=None, refresh_flag=False):
        """
        Navigates to the picking section of mobile emulator
        and sets the login_flag to true indicating the login process is done.
        """
        sleep(2)
        if not refresh_flag:
            self.driver.get(MOBILE_EMULATOR)
        WebDriverWait(self.driver, 50).until(
            EC.element_to_be_clickable(Elements.WMS)
        ).click()
        sleep(2)
        WebDriverWait(self.driver, 50).until(
            EC.element_to_be_clickable(Elements.WAREHOUSE)
        ).click()
        sleep(2)
        WebDriverWait(self.driver, 50).until(
            EC.element_to_be_clickable(Elements.PICKING)
        ).click()
        sleep(2)
        WebDriverWait(self.driver, 50).until(
            EC.element_to_be_clickable(Elements.SINGLEORDER)
        ).click()
        sleep(2)
        WebDriverWait(self.driver, 50).until(
            EC.element_to_be_clickable(Elements.RELEASEDORDER)
        ).click()
        sleep(2)
        WebDriverWait(self.driver, 50).until(
            EC.element_to_be_clickable(Elements.SALESORDER)
        ).click()
        self.state.change_state(self.identify_page())
        if login_flag is None:
            return
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
