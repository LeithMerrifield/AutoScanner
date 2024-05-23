import subprocess
import json
from os.path import exists
from os import remove
from urllib.request import urlretrieve
import shutil

LATEST_RELEASE_STABLE = (
    "curl https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE"
)


def get_webpage_content(url):
    """Returns the page content of specified url

    Args:
        url (str): url to downloadable content

    Returns:
        str: Returns string value of content
    """
    return subprocess.check_output(url, shell=True).decode("utf-8")


def get_download_link(version_number):
    """Sifts through google's json API endpoints to find
    the matching chromedriver download to specified version

    Args:
        version_number (str): version to find the download for

    Returns:
        str: returns url of zip to download
    """
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
    """checks to see if the versions.json exists
    if not, it will create one.

    Args:
        filepath (str, optional): Defaults to "./src/versions.json".
    """
    if exists("./src/versions.json"):
        return
    else:
        with open(filepath, "w", encoding="utf-8") as openfile:
            template = {"Chrome_Driver_Version": "", "App_Version": ""}
            json.dump(template, openfile, indent=4)
    return


def unpack_zip(filepath, destination):
    """unpacks zip from filepath to destination

    Args:
        filepath (str): path to zip
        destination (str): unpack path
    """
    shutil.unpack_archive(filepath, destination, "zip")


def get_local_version(version_type, filepath="./src/versions.json"):
    """Gets the installed version of specified version type  from versions.json

    Args:
        version_type (str): will return this version from the json
        filepath (str, optional): Defaults to "./src/versions.json".

    Returns:
        str: version from versions.json
    """
    with open(filepath, "r", encoding="utf-8") as openfile:
        json_object = json.load(openfile)
        version = json_object[version_type]
    return version


def update_version(version, version_type, filepath="./src/versions.json"):
    """_summary_

    Args:
        version (_type_): _description_
        version_type (_type_): _description_
        filepath (str, optional): _description_. Defaults to "./src/versions.json".
    """
    json_object = None
    with open(filepath, "r", encoding="utf-8") as openfile:
        json_object = json.load(openfile)

    with open(filepath, "w", encoding="utf-8") as openfile:
        json_object[version_type] = version
        json.dump(json_object, openfile, indent=4)


def clean():
    """removes the zip file as it unnecessary once unpacked"""
    remove("./driver.zip")
    return


def get_remote_zip(url, filename):
    """downloads the zip from the url

    Args:
        url (str): url of download
        filename (str): what to name the downloaded file
    """
    urlretrieve(url, filename)
    return


def get_local_chrome_version():
    """Tries to retrieve the installed version of chrome
    by looking for the shortcut and finding the target path

    If there is no chrome found it will simply return the latest version of
    chrome available.

    Returns:
        str: version of chrome to match the driver to be downloaded.
    """
    shortcut_path_command = "wmic path win32_shortcutfile where name='C:\\\\ProgramData\\\\Microsoft\\\\Windows\\\\Start Menu\\\\Programs\\\\Google Chrome.lnk' get target /value"
    shortcut_output = subprocess.check_output(
        shortcut_path_command, shell=True, universal_newlines=True
    )
    shortcut = shortcut_output.split("\n")
    shortcut = [x for x in shortcut if x]

    # if there is something wrong with the path to chrome
    # this allow me to download the latest version instead
    # of matching chrome
    if not shortcut:
        return get_webpage_content(LATEST_RELEASE_STABLE)

    shortcut = shortcut[0].split("=")[1]
    shortcut = shortcut.replace("\\", "\\\\")
    command = f"wmic datafile where name='{shortcut}' get Version /value"
    version_output = subprocess.check_output(
        command, shell=True, universal_newlines=True
    )
    version_output = version_output.split("\n")
    version_output = [x for x in version_output if x]
    version_output = version_output[0].split("=")[1]
    version_output = version_output.split(".")
    version_output[-1] = "0"
    version_output = ".".join(version_output)
    return version_output


def compare_and_download():
    """Finds the current installed version of the chromedriver
    and downloads the required version"""
    check_file()
    local_version = get_local_version("Chrome_Driver_Version")

    remote_version = get_local_chrome_version()

    if local_version == remote_version:
        print("chrome driver up to date")
        return

    remote_download_link = get_download_link(remote_version)

    get_remote_zip(remote_download_link, "./driver.zip")

    unpack_zip("./driver.zip", "./")

    update_version(remote_version, "Chrome_Driver_Version")
    clean()
