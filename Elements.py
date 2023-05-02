from selenium.webdriver.common.by import By

USERNAMEFIELD = (By.ID,"i0116")
PASSWORDFIELD = (By.ID,"i0118")
NEXTBUTTON = (By.ID, "idSIButton9")
NOBUTTON = (By.ID, "idBtn_Back")
NETSUITE_ENVIRONMENT = (By.XPATH, "/html/body/div[2]/div[3]/div/table/tbody/tr[2]/td/table/tbody/tr[2]/td[3]/a")
WMS = (By.XPATH,"/html/body/div/div/div[2]/div[2]/div/div/div[2]/div[2]/img")
WAREHOUSE = (By.XPATH, "/html/body/div/div/div[2]/div[2]/div/div[1]/div[2]/div[1]/div/div/div[6]/div[1]/table/tbody/tr[2]/td")
PICKING = (By.XPATH, "/html/body/div/div/div[2]/div[2]/div/div[1]/div[2]/div[2]")
SINGLEORDER = (By.XPATH, "/html/body/div/div/div[2]/div[2]/div/div[1]/div[2]/div[1]")
RELEASEDORDER = (By.XPATH, "/html/body/div/div/div[2]/div[2]/div/div[1]/div[2]/div[2]")
SALESORDER = (By.XPATH, "/html/body/div/div/div[2]/div[2]/div/div[1]/div[2]/div[1]")

ORDERINPUT = (By.XPATH, "/html/body/div/div/div[2]/div[2]/div/div[1]/div[2]/div[1]/div[2]/input")
ENTERORDER = (By.XPATH, "/html/body/div/div/div[2]/div[2]/div/div[2]/div[1]/div[3]/button")        

FIRSTENTRY = (By.XPATH, "/html/body/div/div/div[2]/div[2]/div/div[1]/div[2]/div[2]/div/div/div[6]/div[1]/table/tbody/tr[1]")
BINNUMBER = (By.XPATH, "/html/body/div/div/div[2]/div[2]/div/div[1]/div[2]/div[2]/span")
ITEMNUMBER = (By.XPATH, "/html/body/div/div/div[2]/div[2]/div/div[1]/div[2]/div[2]/span")
QUANTITY = (By.XPATH, "/html/body/div/div/div[2]/div[2]/div/div[1]/div[2]/div[1]/span")
QUANTITYINPUT = (By.XPATH, "/html/body/div/div/div[2]/div[2]/div/div[1]/div[2]/div[4]/div/div[2]/div/div/input")
NEXTPICKTASK = (By.XPATH, "/html/body/div/div/div[2]/div[2]/div/div[2]/div[1]/div[3]/button")
STATIONINPUT = (By.XPATH, "/html/body/div/div/div[2]/div[2]/div/div[1]/div[2]/div[1]/div[2]/input")
NEXTORDERBUTTON = (By.XPATH, "/html/body/div/div/div[2]/div[2]/div/div[2]/div[1]/div[3]/button")

SALESORDERREFRESH = "/html/body/div/div/div[2]/div[2]/div/div[1]/div[2]/div[1]"
BACKBUTTONREFRESH = "/html/body/div/div/div[2]/div[2]/div/div[2]/div[1]/div[1]/button"