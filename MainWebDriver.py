import pickle
from time import sleep
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common import exceptions
import Elements
import Login
import asyncio

cookieSite = "https://5230881.app.netsuite.com/"
mobileEmulator = "https://5230881.app.netsuite.com/app/site/hosting/scriptlet.nl?script=4662&deploy=1&compid=5230881"
cookieFilePath = "cookies.pkl"
officeURL = "https://www.office.com"
netsuiteSSO = "https://account.activedirectory.windowsazure.com/applications/signin/3b7330ae-2893-492f-8157-09fecce53355?tenantId=7261aa19-728c-457c-bb6e-a31f9a21516d"
myappURL = "https://myapps.microsoft.com/"

class MainWebDriver(object):
    """
    Class used to drive scanning orders into netsuite

    Attributes
    ----------
    driver : Selenium Webdriver
        The main chrome object
    OrderList : 
        List that will hold order strings

    Methods
    -------
    says(sound=None)
        Prints the animals name and what sound it makes
    
    InputOrders()
        Takes user input and places them in OrderList
    
    Pick(order=None)
        After the order has been started this will loop through and pick all items
        Enters into correct packstation
    
    Scan()
        Continually loops to allow inputting of a list and picking all the orders
    
    Login()
        Logs in and navigates to the WMS order list
        
    """
    def __init__(self) -> None:
        self.driver = webdriver.Chrome()
        #self.driver.get(netsuiteSSO)
        #self.driver.delete_all_cookies()
        self.OrderList = []
    
    def save_cookies(self):
        cookies = self.driver.get_cookies()
        pickle.dump(cookies,open(self.cookiePath,'wb'))

    def load_cookies(self):
        cookies = pickle.load(open("cookies.pkl","rb"))
        for cookie in cookies:
            try:
                cookie['domain'] = ".microsoftonline.com"
                print(cookie['domain'])
                self.driver.add_cookie(cookie)
            except exceptions.InvalidCookieDomainException as e:
                print(e.msg)

    def getOrderLength(self):
        table = "/html/body/div/div/div[2]/div[2]/div/div[1]/div[2]/div[2]/div/div/div[6]/div[1]/table/tbody" # need xpath of table
        WebDriverWait(self.driver, 50).until(EC.element_to_be_clickable((By.XPATH, table)))
        foo = self.driver.find_element(By.XPATH, table)
        bar = foo.find_elements(By.XPATH, ".//tr")
        return len(bar)

    # Allows for input of a list of orders.
    def InputOrders(self):
        self.OrderList = []
        orderNumber = 1
        while True:
            flag = input("Enter Order {}: ".format(orderNumber))

            if "saus" not in flag.lower() and "snz" not in flag.lower():
                if flag != "":
                    print("This is not a valid order number\n")
                    continue
            if flag != "":
                self.OrderList.append(flag)
                orderNumber += 1
            else:
                break
                
    # The process of picking an individual order
    def Pick(self,order):
        sleep(2)
        length = self.getOrderLength()
        lengthFlag = True if length > 9 else False
        print(length)

        for i in range(length):
            sleep(1)
            WebDriverWait(self.driver, 50).until(EC.element_to_be_clickable(Elements.FIRSTENTRY)).click()
            sleep(1)
            WebDriverWait(self.driver, 50).until(EC.element_to_be_clickable(Elements.BINNUMBER)).click()
            sleep(1)
            WebDriverWait(self.driver, 50).until(EC.element_to_be_clickable(Elements.ITEMNUMBER)).click()
            sleep(3)
            WebDriverWait(self.driver, 50).until(EC.presence_of_element_located(Elements.QUANTITY))
            Amount = self.driver.find_element(By.XPATH,"/html/body/div/div/div[2]/div[2]/div/div[1]/div[2]/div[1]/span" ).text.split(" ")[0]
            Amount += "\n"
            WebDriverWait(self.driver, 50).until(EC.element_to_be_clickable(Elements.QUANTITYINPUT)).send_keys(Amount)
            sleep(1)
            if i == length - 1 and not lengthFlag:
                continue
            try:
                WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(Elements.NEXTPICKTASK)).click()
            except:
                length = False
                # means the order is exactly 10 and I don't think there is an elegant way to differentiate between exactly 10 and > 10 items
                continue
            
        # recursive to handle longer orders.
        if lengthFlag:
            print("Next Rotation")
            self.Pick(order)
            return

        sleep(3)
        station = ""
        if "sau" in order.lower():
            station = "PackStation03\n"
        else:
            station = "PackStation02\n"
        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(Elements.STATIONINPUT)).send_keys(station)
        sleep(1)
        WebDriverWait(self.driver, 50).until(EC.element_to_be_clickable(Elements.NEXTORDERBUTTON)).click()
        
    
    # Will run the scanning/picking process for n orders in orderlist
    def Scan(self,myOrders: list):
        #self.InputOrders()
        myOrders.reverse()
        for order in myOrders:
            sleep(2)
            WebDriverWait(self.driver, 50).until(EC.element_to_be_clickable(Elements.ORDERINPUT)).send_keys(order)
            WebDriverWait(self.driver, 50).until(EC.element_to_be_clickable(Elements.ENTERORDER)).click()
            self.Pick(order)
        print("Scanning Complete \n Start Again\n")

    def Refresh(self):
        self.driver.find_element(By.XPATH, Elements.BACKBUTTONREFRESH).click()
        sleep(2)
        self.driver.find_element(By.XPATH, Elements.SALESORDERREFRESH).click()

    # Goes through the process of logging into microsoft and navigates to the list of active orders.
    def login(self):
        self.driver.get(netsuiteSSO)
        WebDriverWait(self.driver, 50).until(EC.element_to_be_clickable(Elements.USERNAMEFIELD)).send_keys(Login.Username)
        WebDriverWait(self.driver, 50).until(EC.element_to_be_clickable(Elements.NEXTBUTTON)).click()
        WebDriverWait(self.driver, 50).until(EC.element_to_be_clickable(Elements.PASSWORDFIELD)).send_keys(Login.Password)
        WebDriverWait(self.driver, 50).until(EC.element_to_be_clickable(Elements.NEXTBUTTON)).click()
        WebDriverWait(self.driver, 50).until(EC.element_to_be_clickable(Elements.NOBUTTON)).click()
        WebDriverWait(self.driver,50).until(EC.element_to_be_clickable(Elements.NETSUITE_ENVIRONMENT)).click()
        self.driver.get(mobileEmulator)
        WebDriverWait(self.driver,50).until(EC.element_to_be_clickable(Elements.WMS)).click()
        WebDriverWait(self.driver,50).until(EC.element_to_be_clickable(Elements.WAREHOUSE)).click()
        sleep(1)
        WebDriverWait(self.driver,50).until(EC.element_to_be_clickable(Elements.PICKING)).click()
        sleep(1)
        WebDriverWait(self.driver,50).until(EC.element_to_be_clickable(Elements.SINGLEORDER)).click()
        sleep(1)
        WebDriverWait(self.driver,50).until(EC.element_to_be_clickable(Elements.RELEASEDORDER)).click()
        sleep(1)
        WebDriverWait(self.driver,50).until(EC.element_to_be_clickable(Elements.SALESORDER)).click()