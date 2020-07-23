from filter.utils.os_tools import remove_dir
import os
import shutil

if __name__ == '__main__':
    os.chdir("/home/adidev/adidev")
    os.system("git pull")
    origin_path = "/home/adidev/adidev"
    for filename in os.listdir("/home/adidev"):
        if filename.startswith("adidev_"):
            factory_code = filename.split("_")[1]
            new_path = f"/home/adidev/adidev_{factory_code}"
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
            with open(f"/home/adidev/{filename}/deploy/filter.bash", "w") as w:
                with open(f"/home/adidev/adidev/deploy/filter.bash.sample", "r") as r:
                    w.write(r.read().format(factory_code=factory_code))
            os.system(f"chmod +x {new_path}/deploy/filter.bash")
    os.system("supervisorctl reload")
