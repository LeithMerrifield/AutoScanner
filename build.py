import shutil

shutil.copytree("./dist/Autoscanner/", "./dist/release/Scanner")
shutil.make_archive("./dist/Autoscanner", "zip", "./dist/release")
