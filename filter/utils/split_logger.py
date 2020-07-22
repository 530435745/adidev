from filter.config import GLOBAL_SPLIT_RULES_FILE, SPLIT_RESULT_FILE
from filter.utils.xlsx_to_rows import xlsx_to_rows
import openpyxl
import os


class SplitLogger:
    def __init__(self):
        self.rows = xlsx_to_rows(GLOBAL_SPLIT_RULES_FILE)
        self.data = {row[0]: {
            "latest": "",
            "files": [],
            "exception": ""
        } for row in self.rows}

    def __enter__(self):
        self.file_name = SPLIT_RESULT_FILE()
        if os.path.exists(self.file_name):
            rows = xlsx_to_rows(self.file_name)
            for row in rows:
                self.data[row[0]] = {
                    "latest": row[5],
                    "files": row[6].split(", "),
                    "exception": row[7]
                }
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        wb = openpyxl.Workbook()
        ws = wb.active
        self.rows[0].extend(["最近分发完成时间", "已分发文件", "异常记录"])
        for index, row in enumerate(self.rows):
            if index == 0:
                continue
            self.rows[index].extend([
                self.data[row[0]]["latest"],
                ", ".join(self.data[row[0]]["files"]),
                self.data[row[0]]["exception"]
            ])
        for i_index, i in enumerate(self.rows):
            for j_index, j in enumerate(i):
                ws.cell(i_index + 1, j_index + 1).value = j
        wb.save(self.file_name)
