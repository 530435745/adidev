from config import *
from workers import *
from utils.timer import *
import os
import shutil


def unlock_errs():
    # 解锁所有err文件，仅在服务第一次启动时执行
    for dir_name, sub_dirs, files in os.walk(ORDERED_FILES_DIR):
        for filename in files:
            if filename.endswith(".err"):
                shutil.move(os.path.join(dir_name, filename), os.path.join(dir_name, filename[:-4]))


@do_at(interval=300)
def main_worker():
    aim_dirs = []
    rows = xlsx_to_rows(GLOBAL_SPLIT_RULES_FILE)[1:]
    for row in rows:
        if not row[0]:
            break
        aim_dirs.append(row[0])
    # 遍历待分发目录，依次判断所有文件是否符合待分发标准
    for dir_name, sub_dirs, files in os.walk(CHAOS_FILES_DIR):
        if dir_name in aim_dirs:
            for filename in files:
                F0Worker(os.path.join(dir_name, filename)).process()
    # 遍历已分发目录，寻找F0及中间状态文件继续处理
    for dir_name, sub_dirs, files in os.walk(ORDERED_FILES_DIR):
        for filename in files:
            if filename.endswith(".old"):
                continue
            while filename:
                if isinstance(filename, list):
                    filename = filename[0].split(os.sep)[-1]
                if filename.startswith("F3"):
                    MonthlyFinalWorker(os.path.join(dir_name, filename)).process()
                    DailyFinalWorker(os.path.join(dir_name, filename)).process()
                    os.remove(os.path.join(dir_name, filename))
                    break
                elif filename.startswith("F2"):
                    filename = F3Worker(os.path.join(dir_name, filename)).process()
                elif filename.startswith("F1"):
                    filename = F2Worker(os.path.join(dir_name, filename)).process()
                elif filename.startswith("F0"):
                    filename = F1Worker(os.path.join(dir_name, filename)).process()
                else:
                    break


if __name__ == '__main__':
    unlock_errs()
    main_worker()

