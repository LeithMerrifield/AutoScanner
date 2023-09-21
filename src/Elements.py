from selenium.webdriver.common.by import By

USERNAMEFIELD = (By.ID, "i0116")
PASSWORDFIELD = (By.ID, "i0118")
NEXTBUTTON = (By.ID, "idSIButton9")
NOBUTTON = (By.ID, "idBtn_Back")

NETSUITELOGINEMAIL = (By.ID, "email")
NETSUITELOGINPASSWORD = (By.ID, "password")
NETSUITELOGINBUTTON = (By.ID, "login-submit")

NETSUITE_ENVIRONMENT = (
    By.XPATH,
    "/html/body/div[2]/div[3]/div/table/tbody/tr[2]/td/table/tbody/tr[2]/td[3]/a",
)
WMS = (By.XPATH, "/html/body/div/div/div[2]/div[2]/div/div/div[2]/div[2]/img")
WAREHOUSE = (
    By.XPATH,
    "/html/body/div/div/div[2]/div[2]/div/div[1]/div[2]/div[1]/div/div/div[6]/div[1]/table/tbody/tr[2]/td",
)
PICKING = (By.XPATH, "/html/body/div/div/div[2]/div[2]/div/div[1]/div[2]/div[2]")
SINGLEORDER = (By.XPATH, "/html/body/div/div/div[2]/div[2]/div/div[1]/div[2]/div[1]")
RELEASEDORDER = (By.XPATH, "/html/body/div/div/div[2]/div[2]/div/div[1]/div[2]/div[2]")
SALESORDER = (By.XPATH, "/html/body/div/div/div[2]/div[2]/div/div[1]/div[2]/div[1]")

ORDERINPUT = (
    By.XPATH,
    "/html/body/div/div/div[2]/div[2]/div/div[1]/div[2]/div[1]/div[2]/input",
)
ORDERINPUTWITHERROR = (
    By.XPATH,
    "/html/body/div/div/div[2]/div[2]/div/div[1]/div[3]/div[1]/div[2]/input",
)
ENTERORDER = (
    By.XPATH,
    "/html/body/div/div/div[2]/div[2]/div/div[2]/div[1]/div[3]/button",
)

FIRSTENTRY = (
    By.XPATH,
    "/html/body/div/div/div[2]/div[2]/div/div[1]/div[2]/div[2]/div/div/div[6]/div[1]/table/tbody/tr[1]",
)
BINNUMBER = (By.XPATH, "/html/body/div/div/div[2]/div[2]/div/div[1]/div[2]/div[2]/span")
ITEMNUMBER = (
    By.XPATH,
    "/html/body/div/div/div[2]/div[2]/div/div[1]/div[2]/div[2]/span",
)
QUANTITY = (By.XPATH, "/html/body/div/div/div[2]/div[2]/div/div[1]/div[2]/div[1]/span")
QUANTITYINPUT = (
    By.XPATH,
    "/html/body/div/div/div[2]/div[2]/div/div[1]/div[2]/div[4]/div/div[2]/div/div/input",
)
NEXTPICKTASK = (
    By.XPATH,
    "/html/body/div/div/div[2]/div[2]/div/div[2]/div[1]/div[3]/button",
)
STATIONINPUT = (
    By.XPATH,
    "/html/body/div/div/div[2]/div[2]/div/div[1]/div[2]/div[1]/div[2]/input",
)
NEXTORDERBUTTON = (
    By.XPATH,
    "/html/body/div/div/div[2]/div[2]/div/div[2]/div[1]/div[3]/button",
)

SALESORDERREFRESH = "/html/body/div/div/div[2]/div[2]/div/div[1]/div[2]/div[1]"
BACKBUTTONREFRESH = "/html/body/div/div/div[2]/div[2]/div/div[2]/div[1]/div[1]/button"

STAGE = [
    "Select Application",
    "Select Warehouse",
    "Main Menu",
    "Picking",
    "Select Picking Mode",
    "Select Order Type",
    "Select Order",
]
STAGEDICT = {
    STAGE[0]: 1,  # Select Application = 1
    STAGE[1]: 2,  # Select Warehouse = 2
    STAGE[2]: 3,  # Main Menu = 3
    STAGE[3]: 4,  # Picking = 4
    STAGE[4]: 5,  # Select Picking Mode = 5
    STAGE[5]: 6,  # Select Order Type = 6
    STAGE[6]: 7,  # Select Order = 7
}
# Pick Task Complete
# Enter Staging Bin
