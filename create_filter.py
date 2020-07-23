from filter.utils.os_tools import remove_dir
import os
import sys
import shutil

if __name__ == '__main__':
    try:
        factory_code = sys.argv[1]
    except IndexError:
        print("执行此命令请携带厂商代码参数。")
        sys.exit(0)
    origin_path = "/home/adidev/adidev"
    new_path = f"/home/adidev/adidev_{factory_code}"
    if os.path.exists(new_path):
        remove_dir(new_path)
    print("正在停止supervisor...（如有任务正在进行，此过程可能会持续很长时间）")
    result = os.system("supervisorctl stop all")
    print("supervisor已停止")
    shutil.copytree(origin_path, new_path)
    print(f"项目已复制到: {new_path}")
    with open(f"/etc/supervisor/conf.d/supervisor_{factory_code}.conf", "w") as w:
        with open(f"{origin_path}/deploy/supervisor.conf.sample", "r") as r:
            w.write(r.read().format(factory_code=factory_code))
    with open(f"{new_path}/deploy/filter.bash", "w") as w:
        with open(f"{origin_path}/deploy/filter.bash.sample", "r") as r:
            w.write(r.read().format(factory_code=factory_code))
    os.system(f"chmod +x {new_path}/deploy/filter.bash")
    print(f"针对新项目的执行脚本与supervisor配置文件已就位")
    print("---------注意---------")
    print(f"请打开{new_path}/filter/config.py进行{factory_code}厂商相关配置")
    print("配置完成后，执行supervisorctl reload即可重载配置并重启服务")
    print("---------------------")
