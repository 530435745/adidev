from filter.utils.logger import logger
from filter.utils.timer import *
from filter.utils.split_logger import SplitLogger
from filter.workers import *
from filter.config import *
from datetime import datetime
import os
import re
import shutil


# 载入目标清单规则
TARGETS = []
target_rows = xlsx_to_rows(GLOBAL_TARGET_RULES_FILE)[1:]
for target_row in target_rows:
    if not target_row[0]:
        break
    if not target_row[6]:
        raise ValueError("目标清单文件中，有标记为空值。")
    if int(datetime.now().strftime("%Y%m")) >= int(target_row[6]):
        TARGETS.append(os.path.join(ORDERED_FILES_DIR, target_row[0]))


def unlock_errs():
    # 解锁所有err文件，只处理目标清单中的err，仅在服务第一次启动时执行
    pattern = re.compile(r".+\.err\.(xlsx|xls|csv)")
    for target_dir in TARGETS:
        if not os.path.exists(target_dir):
            continue
        files = os.listdir(target_dir)
        for filename in files:
            if re.match(pattern, filename):
                shutil.move(
                    os.path.join(target_dir, filename),
                    os.path.join(target_dir, filename.replace(".err", ""))
                )


@do_at(interval=SPLIT_INTERVAL)
def before_main():
    aim_dirs = {}
    rows = xlsx_to_rows(GLOBAL_SPLIT_RULES_FILE)[1:]
    for row in rows:
        if not row[0]:
            break
        aim_dirs[row[0]] = row[1]
    # 遍历待分发目录，整体判断该目录下文件是否符合分发标准
    pattern = re.compile(r"(FTP|MNL|ADI)_([IPS])_.+")
    with SplitLogger() as s:
        for src_dir, dst_dir in aim_dirs.items():
            if not os.path.exists(src_dir):
                s.data[src_dir]["exception"] = "待分发目录不存在"
                continue
            files = [f for f in os.listdir(src_dir) if re.match(pattern, f)]
            if not files:
                s.data[src_dir]["exception"] = "暂无待分发文件"
                continue
            symbols = [i.split("_")[1] for i in files]
            if len(files) > 3 or len(set(symbols)) != len(symbols):
                info = f"待分发目录{src_dir}中，" \
                       f"发现IPS文件个数分别为: {symbols.count('I')}，{symbols.count('P')}，{symbols.count('S')}，" \
                       f"已忽略。"
                s.data[src_dir]["exception"] = info
                continue
            has_file = False
            for filename in files:
                if ".err" in filename:
                    continue
                if F0Worker(os.path.join(src_dir, filename)).process():
                    s.data[src_dir]["files"].append(filename)
                    has_file = True
            if has_file:
                s.data[src_dir]["exception"] = ""
                s.data[src_dir]["latest"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            else:
                s.data[src_dir]["exception"] = "所有待分发文件均为空或读取出错"


@do_at(interval=INTERVAL)
def after_main():
    # 遍历目标清单指向目录，进行后续操作
    for src_dir in TARGETS:
        if not os.path.exists(src_dir):
            continue
        files = os.listdir(src_dir)
        # 针对目标类型文件过滤，移动旧文件到history
        his_dir = os.path.join(src_dir, "history")
        try:
            os.makedirs(his_dir)
        except FileExistsError:
            pass
        last = {}
        pattern = re.compile(rf"F[0-3]_(FTP|MNL|ADI)_([IPS])_.+\.(xlsx|xls|csv)")
        for filename in files:
            if re.match(pattern, filename):
                status, operator, file_type = filename.split("_")[:3]
                if file_type not in last:
                    last[file_type] = filename
                    continue
                if os.stat(os.path.join(src_dir, filename)) > os.stat(os.path.join(src_dir, last[file_type])):
                    shutil.move(
                        os.path.join(src_dir, last[file_type]),
                        os.path.join(his_dir, last[file_type])
                    )
                    last[file_type] = filename
                else:
                    shutil.move(
                        os.path.join(src_dir, filename),
                        os.path.join(his_dir, filename)
                    )
        # 处理最新的IPS文件
        for filename in last.values():
            if ".err" in filename:
                continue
            if pattern.match(filename):
                while filename:
                    if isinstance(filename, list):
                        filename = filename[0].split(os.sep)[-1]
                    if filename.startswith("F3"):
                        m_result = MonthlyFinalWorker(os.path.join(src_dir, filename)).process()
                        d_result = DailyFinalWorker(os.path.join(src_dir, filename)).process()
                        if m_result and d_result:
                            shutil.move(os.path.join(src_dir, filename), os.path.join(
                                src_dir,
                                "status",
                                f"done{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}_{filename}"
                            ))
                        break
                    elif filename.startswith("F2"):
                        filename = F3Worker(os.path.join(src_dir, filename)).process()
                    elif filename.startswith("F1"):
                        filename = F2Worker(os.path.join(src_dir, filename)).process()
                    elif filename.startswith("F0"):
                        filename = F1Worker(os.path.join(src_dir, filename)).process()
                    else:
                        break
    logger.error("任务结束")
    logger.error("---------------------------------------------------------------------------")
