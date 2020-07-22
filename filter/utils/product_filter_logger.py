from filter.config import PRODUCT_FILTER_RESULT_FILE
from filter.utils.xlsx_to_rows import xlsx_to_rows
import openpyxl
import os


class ProductFilterLogger:
    def __init__(self):
        self.data = {}
        self.rows = [["原始产品名称", "原始产品规格", "进销存类型", "经销商代码"]]

    def __enter__(self):
        self.file_name = PRODUCT_FILTER_RESULT_FILE()
        if os.path.exists(self.file_name):
            self.rows = xlsx_to_rows(self.file_name)
            for row in self.rows[1:]:
                self.data[f"{row[0]}|{row[1]}"] = {
                    "file_type": row[2],
                    "customer": row[3]
                }
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        wb = openpyxl.Workbook()
        ws = wb.active
        for row in self.rows[1:]:
            del self.data[f"{row[0]}|{row[1]}"]
        for key, info in self.data.items():
            self.rows.append([key.split("|")[0], key.split("|")[1], info["file_type"], info["customer"]])
        for i_index, i in enumerate(self.rows):
            for j_index, j in enumerate(i):
                ws.cell(i_index + 1, j_index + 1).value = j
        wb.save(self.file_name)
