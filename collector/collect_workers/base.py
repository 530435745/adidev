from collector.config import COLLECTOR_TARGETS_LIST, COLLECTOR_ORDERED_DIR_LIST
from collector.utils.xlsx_to_rows import xlsx_to_rows
import openpyxl
import os


class CollectorWorkerBase:
    # 指定收集结果文件
    RESULT_FILE = None
    # 指定表头
    TITLES = []

    TARGETS = {}
    for target in COLLECTOR_TARGETS_LIST:
        TARGETS.update({
            row[0]: {
                "name": row[1],
                "province": row[2],
                "city": row[3],
                "level": row[4],
                "operation_type": row[5],
                "mark": row[6],
                "manual_mark": row[7],
                "sub_company": row[8],
                "history": row[9]
            } for row in xlsx_to_rows(target)[1:]
        })

    @classmethod
    def add_line(cls, current_dir):
        """
        处理单行数据方法，在子类中覆盖
        :param current_dir: 当前目录
        :return: 单行数据
        """

    @staticmethod
    def get_dir(code):
        for target_dir in COLLECTOR_ORDERED_DIR_LIST:
            for sub_dir in os.listdir(target_dir):
                if sub_dir == code:
                    return os.path.join(target_dir, sub_dir)

    @classmethod
    def process(cls):
        """
        单次任务，刷新当前类指向的汇总文件
        :return:
        """
        data = [cls.TITLES]
        for code, info in cls.TARGETS.items():
            if not (current_dir := cls.get_dir(code)):
                continue
            data.extend(cls.add_line(current_dir))
        wb = openpyxl.Workbook()
        ws = wb.active
        for i_index, i in enumerate(data):
            for j_index, j in enumerate(i):
                ws.cell(i_index + 1, j_index + 1).value = j
        wb.save(cls.RESULT_FILE())





