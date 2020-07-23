from filter.utils.os_tools import remove_dir
import os
import shutil

if __name__ == '__main__':
    os.chdir("/home/adidev/adidev")
    os.system("git pull")
    for filename in os.listdir("/home/adidev"):
        if filename.startswith("adidev_"):
            shutil.move(
                f"/home/adidev/{filename}/filter/config.py",
                f"/home/adidev/config_{filename.split('_')[1]}.py"
            )
            remove_dir(f"/home/adidev/{filename}")
            shutil.copytree("/home/adidev/adidev", f"/home/adidev/{filename}")
            shutil.move(
                f"/home/adidev/config_{filename.split('_')[1]}.py",
                f"/home/adidev/{filename}/filter/config.py"
            )
    os.system("supervisorctl reload")
