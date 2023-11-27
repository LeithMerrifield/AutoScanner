import subprocess
import json
from os.path import exists
from os import remove
from zipfile import ZipFile
from urllib.request import urlretrieve
import shutil

LATEST_RELEASE_STABLE = (
    "curl https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE"
)


def get_webpage_content(url):
    return subprocess.check_output(url, shell=True).decode("utf-8")


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


def check_file(filepath="./src/versions.json"):
    if exists("./src/versions.json"):
        return
    else:
        with open(filepath, "w", encoding="utf-8") as openfile:
            template = {"Chrome_Driver_Version": "", "App_Version": ""}
            json.dump(template, openfile, indent=4)
    return


def unpack_zip(filepath, destination):
    shutil.unpack_archive(filepath, destination, "zip")


def get_local_version(version_type, filepath="./src/versions.json"):
    version = None
    try:
        with open(filepath, "r", encoding="utf-8") as openfile:
            json_object = json.load(openfile)
            version = json_object[version_type]
    except:
        version = ""
    return version


def update_version(version, version_type, filepath="./src/versions.json"):
    json_object = None
    with open(filepath, "r", encoding="utf-8") as openfile:
        json_object = json.load(openfile)

    with open(filepath, "w", encoding="utf-8") as openfile:
        json_object[version_type] = version
        json.dump(json_object, openfile, indent=4)


def clean():
    remove("./driver.zip")
    return


def get_remote_zip(url, filename):
    urlretrieve(url, filename)
    return


def compare_and_download():
    check_file()
    local_version = get_local_version("Chrome_Driver_Version")
    remote_version = get_webpage_content(LATEST_RELEASE_STABLE)

    if local_version.split(".")[0] == remote_version.split(".")[0]:
        print("chrome driver up to date")
        return

    remote_download_link = get_download_link(remote_version)

    get_remote_zip(remote_download_link, "./driver.zip")

    unpack_zip("./driver.zip", "./")

    update_version(remote_version, "Chrome_Driver_Version")
    clean()
