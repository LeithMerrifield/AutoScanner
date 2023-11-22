import subprocess
import json
from zipfile import ZipFile
from urllib.request import urlretrieve, urlopen


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


def get_local_driver_version():
    version = None
    try:
        with open("./src/settings.json", "r") as openfile:
            json_object = json.load(openfile)
            version = json_object["Chrome_Driver_Version"]
    except KeyError:
        version = ""
    return version


def update_version(version):
    with open("./src/settings.json", "r") as openfile:
        json_object = json.load(openfile)
        version = json_object["Chrome_Driver_Version"]


def compare_and_download():
    local_version = get_local_driver_version()
    remote_version = get_driver_version()
    remote_download_link = get_download_link(remote_version)

    if local_version == "":
        print(remote_download_link)
    elif local_version.split(".")[0] != remote_version.split(".")[0]:
        print(remote_download_link)

    urlretrieve(remote_download_link, "./driver.zip")

    with ZipFile("./driver.zip", "r") as zipObj:
        zipObj.extractall()
