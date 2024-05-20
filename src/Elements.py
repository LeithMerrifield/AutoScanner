from selenium.webdriver.common.by import By
import json


class ElementClass:
    def __init__(self) -> None:
        self.element_error_flag = False
        self.elements = self.read_elements_from_json()

        if self.element_error_flag:
            return

        self.assign_ui_elements(self.elements)

    def read_elements_from_json(self):
        try:
            with open(r".\src\elements.json", "r", encoding="utf-8") as openfile:
                return json.load(openfile)
        except FileNotFoundError:
            self.element_error_flag = True

    def assign_ui_elements(self, dict):
        self.USERNAMEFIELD = self.elements["USERNAMEFIELD"]
        self.PASSWORDFIELD = self.elements["PASSWORDFIELD"]
        self.NEXTBUTTON = self.elements["NEXTBUTTON"]
        self.NOBUTTON = self.elements["NOBUTTON"]
        self.NETSUITEHOMEPAGE = self.elements[
            "NETSUITEHOMEPAGE"
        ]  # netsuite homepage identifier?
        self.NETSUITE_ENVIRONMENT = (
            self.elements["NETSUITE_ENVIRONMENT"][0],
            self.elements["NETSUITE_ENVIRONMENT"][1],
        )
        self.WMS = (self.elements["WMS"][0], self.elements["WMS"][1])
        self.WAREHOUSE = (self.elements["WAREHOUSE"][0], self.elements["WAREHOUSE"][1])
        self.PICKING = (self.elements["PICKING"][0], self.elements["PICKING"][1])
        self.SINGLEORDER = (
            self.elements["SINGLEORDER"][0],
            self.elements["SINGLEORDER"][1],
        )
        self.RELEASEDORDER = (
            self.elements["RELEASEDORDER"][0],
            self.elements["RELEASEDORDER"][1],
        )
        self.SALESORDER = (
            self.elements["SALESORDER"][0],
            self.elements["SALESORDER"][1],
        )
        self.ORDERINPUT = (
            self.elements["ORDERINPUT"][0],
            self.elements["ORDERINPUT"][1],
        )
        self.ORDERINPUTWITHERROR = (
            self.elements["ORDERINPUTWITHERROR"][0],
            self.elements["ORDERINPUTWITHERROR"][1],
        )
        self.ENTERORDER = (
            self.elements["ENTERORDER"][0],
            self.elements["ENTERORDER"][1],
        )
        self.FIRSTENTRY = (
            self.elements["FIRSTENTRY"][0],
            self.elements["FIRSTENTRY"][1],
        )
        self.BINNUMBER = (self.elements["BINNUMBER"][0], self.elements["BINNUMBER"][1])
        self.ITEMNUMBER = (
            self.elements["ITEMNUMBER"][0],
            self.elements["ITEMNUMBER"][1],
        )
        self.QUANTITYAMOUNT = (
            self.elements["QUANTITYAMOUNT"][0],
            self.elements["QUANTITYAMOUNT"][1],
        )
        self.QUANTITYINPUT = (
            self.elements["QUANTITYINPUT"][0],
            self.elements["QUANTITYINPUT"][1],
        )
        self.NEXTPICKTASK = (
            self.elements["NEXTPICKTASK"][0],
            self.elements["NEXTPICKTASK"][1],
        )
        self.STATIONINPUT = (
            self.elements["STATIONINPUT"][0],
            self.elements["STATIONINPUT"][1],
        )
        self.NEXTORDERBUTTON = (
            self.elements["NEXTORDERBUTTON"][0],
            self.elements["NEXTORDERBUTTON"][1],
        )

        SALESORDERREFRESH = "/html/body/div/div/div[2]/div[2]/div/div[1]/div[2]/div[1]"
        BACKBUTTONREFRESH = (
            "/html/body/div/div/div[2]/div[2]/div/div[2]/div[1]/div[1]/button"
        )


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
