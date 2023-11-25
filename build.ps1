./venv/Scripts/Activate
python.exe -m PyInstaller ./Updater.spec
python.exe -m PyInstaller ./Autoscanner.spec

python.exe ./build.py

