import subprocess
from urllib.request import urlretrieve
import src.CheckDriver as CheckDriver
import json
import shutil
import os
import tempfile
from time import sleep
from zipfile import ZipFile
from win32api import GetLongPathName

LATEST_APP_VERSION = "curl https://leithmerrifield.github.io/Autoscanner/LATESTVERSION"
DOWNLOAD_LIST = "curl https://leithmerrifield.github.io/Autoscanner/downloads.json"


def get_app_download_link(target_version):
    downloads = CheckDriver.get_webpage_content(DOWNLOAD_LIST)

    downloads_json = json.loads(downloads)
    for version in downloads_json:
        if version["Version"] == target_version:
            return version["Link"]


def delete_contents():
    keep = ["Updater.exe", "database.json", "src", "userdata", "app.zip"]
    for root, dir, files in os.walk("./Scanner"):
        for name in files:
            if name not in keep:
                try:
                    os.remove(os.path.join(root, name))
                    # print(os.path.join(root, name))
                except:
                    pass
        for name in dir:
            if name not in keep and "userdata" not in root:
                shutil.rmtree(os.path.join(root, name))


def move_from_temp():
    temp_destination = GetLongPathName(tempfile.gettempdir())
    shutil.copytree(
        temp_destination + "/Autoscanner",
        "./",
        dirs_exist_ok=True,
    )


def check_scanner_folder():
    if not os.path.isdir("./Scanner"):
        os.mkdir("./Scanner")
    return


def create_shortcut():
    ps = subprocess.check_output(
        "powershell.exe" + " [System.Environment]::GetFolderPath('Desktop')",
        stderr=subprocess.STDOUT,
        shell=True,
    )
    desktop = ps.decode("UTF-8")[:-2]
    items = os.listdir(desktop)
    for item in items:
        if "Autoscanner" in item:
            os.remove(desktop + "/" + item)

    current_dir = os.path.abspath(os.getcwd() + "/Scanner/Autoscanner.exe")
    current_dir = current_dir.split("\\")
    current_dir = "/".join(current_dir)
    # fmt: off
    command = '''param(
[string]$path
)

$ScriptObj = New-Object -ComObject ("WScript.shell")
$destination = [System.Environment]::GetFolderPath("Desktop") + "/Autoscanner.lnk"
$shortcut = $ScriptObj.CreateShortcut($destination)


$shortcut.TargetPath = $path
$separator = "/"
$workingdir = $path -split $separator
$workingdir = $workingdir[0..($workingdir.Length - 2)] -join "/"
$shortcut.WorkingDirectory = $workingdir
$shortcut.Save()
    
    '''
    # fmt: on
    with open("./shortcut.ps1", "w") as openfile:
        openfile.write(command)
    sleep(2)
    subprocess.Popen(
        [
            "powershell.exe",
            "-Command",
            "&{Set-ExecutionPolicy Bypass -scope CurrentUser -Force}",
        ],
    )
    sleep(1)
    subprocess.run(
        [
            "powershell.exe",
            f"./shortcut.ps1 {current_dir}",
        ],
    )
    sleep(1)
    subprocess.Popen(
        [
            "powershell.exe",
            "-Command",
            "&{Set-ExecutionPolicy Restricted -scope CurrentUser -Force}",
        ],
    )
    return


def clean():
    os.remove("./shortcut.ps1")
    return


def update():
    # compare versions
    check_scanner_folder()
    local_version = CheckDriver.get_local_version(
        "App_Version", filepath="./Scanner/src/versions.json"
    )
    remote_version = CheckDriver.get_webpage_content(LATEST_APP_VERSION)

    if local_version == remote_version:
        return

    # get download link of newest version
    # get zip
    temp_destination = GetLongPathName(tempfile.gettempdir())
    CheckDriver.get_remote_zip(
        get_app_download_link(remote_version), temp_destination + "/app.zip"
    )
    delete_contents()
    CheckDriver.unpack_zip(
        temp_destination + "/app.zip", temp_destination + "/Autoscanner"
    )
    sleep(2)
    move_from_temp()
    CheckDriver.check_file(filepath="./Scanner/src/versions.json")
    CheckDriver.update_version(
        remote_version, "App_Version", filepath="./Scanner/src/versions.json"
    )

    sleep(2)
    create_shortcut()
    sleep(2)
    clean()


try:
    update()
except Exception as e:
    with open("./log.txt", "w") as openfile:
        openfile.write(str(e))
