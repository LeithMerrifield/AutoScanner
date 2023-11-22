import subprocess
import json
from os.path import exists
from os import remove
from zipfile import ZipFile
from urllib.request import urlretrieve


def get_driver_version():
    ps = "curl https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE"
    return subprocess.check_output(ps, shell=True).decode("utf-8")


def get_download_link(version_number):
    downloads_json = "curl https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
    downloads = subprocess.check_output(downloads_json, shell=True)
    link = None
    # converts to json format and grabs only the versions dict
    downloads = json.loads(downloads)["versions"]

    # loops through dict looking for the correct version number from download list
    # returns download link
    for version in downloads:
        if version["version"] == version_number:
            platforms = version["downloads"]["chromedriver"]
            for platform in platforms:
                if platform["platform"] == "win64":
                    link = platform["url"]
    return link


def check_file():
    if exists("./src/driver_version.json"):
        return
    else:
        with open("./src/driver_version.json", "w", encoding="utf-8") as openfile:
            template = {"Chrome_Driver_Version": ""}
            json.dump(template, openfile, indent=4)
    return


def get_local_driver_version():
    version = None
    try:
        with open("./src/driver_version.json", "r", encoding="utf-8") as openfile:
            json_object = json.load(openfile)
            version = json_object["Chrome_Driver_Version"]
    except KeyError:
        version = ""
    return version


def update_version(version):
    json_object = None
    with open("./src/driver_version.json", "r", encoding="utf-8") as openfile:
        json_object = json.load(openfile)

    with open("./src/driver_version.json", "w", encoding="utf-8") as openfile:
        json_object["Chrome_Driver_Version"] = version
        json.dump(json_object, openfile, indent=4)


def clean():
    remove("./driver.zip")
    return


def compare_and_download():
    check_file()
    local_version = get_local_driver_version()
    remote_version = get_driver_version()

    if local_version.split(".")[0] == remote_version.split(".")[0]:
        print("chrome driver up to date")
        return

    remote_download_link = get_download_link(remote_version)

    urlretrieve(remote_download_link, "./driver.zip")

    with ZipFile("./driver.zip", "r") as zipObj:
        zipObj.extractall()
    update_version(remote_version)
    clean()
