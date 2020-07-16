from workers.base import WorkerBase
from config import GLOBAL_SPLIT_RULES_FILE
from workers.F1 import F1Worker
import openpyxl
import os


class F0Worker(WorkerBase):
    """
    文件从待分发到F0，只执行文件移动和备份
    """
    NEXT = F1Worker
    RULES = {}
    wb = openpyxl.load_workbook(GLOBAL_SPLIT_RULES_FILE)
    ws = wb.worksheets[0]
    rows = [[str(j.value).strip() if j.value else "" for j in i] for i in ws.rows][1:]
    for row in rows:
        RULES[row[0]] = {
            "targets": [i for i in row[1].split("|")],
            "sign": row[2],
            "sep": row[3],
            "pos": row[4]
        }

    def _process(self):
        file_path, file_name = os.path.split(self.input_file)
        if path_info := self.RULES.get(file_path):
            if file_name.split(path_info["sep"])[path_info["pos"]] == path_info["sign"]:
                return True
        return False
