import shutil

shutil.copytree("./dist/Autoscanner/", "./dist/release/")
shutil.move("./dist/Updater.exe", "./dist/release")
shutil.make_archive("./dist/Autoscanner", "zip", "./dist/release")
