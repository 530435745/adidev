from utils.logger import logger
from datetime import datetime
import shutil
import openpyxl
import traceback
import csv
import os


def now_str():
    return datetime.now().strftime("%Y-%m-%d-%H-%M-%S")


class WorkerBase(object):
    # 下一个处理模块
    NEXT = None

    def __init__(self, input_file, output_files, backup_file):
        self.input_file = input_file
        self.status, self.file_type, self.customer = self.input_file.split(os.sep)[-1].split("_")[:3]
        self.output_files = output_files
        self.backup_file = backup_file
        if input_file.endswith(".xls") or input_file.endswith(".xlsx"):
            wb = openpyxl.load_workbook(input_file)
            ws = wb.worksheets[0]
            self.data = [[str(j.value).strip() if j.value else "" for j in i] for i in ws.rows]
        elif input_file.endswith(".csv"):
            reader = csv.reader(self.input_file)
            self.data = [i for i in reader]
        elif input_file.endswith(".err"):
            self.data = None
        else:
            self.data = None
            shutil.move(self.input_file, self.input_file + ".err")
            logger.error(f"发现未知格式文件{self.input_file}，已移动到{self.input_file}.err")

    def error(self, content):
        """
        出错时移动问题文件到.err并记录日志
        :param content:
        :return:
        """
        logger.error(content)
        logger.error(f"移动出错文件{self.input_file}至{self.input_file}.err")
        shutil.move(self.input_file, self.input_file + ".err")

    def _process(self):
        """
        实际工作内容
        :return: 执行成功时返回True，失败时返回False
        """
        return True

    def process(self):
        """
        调用执行函数
        :return:
        """
        try:
            result = self._process()
        except Exception as e:
            self.error(f"程序执行出错，请联系开发人员：\n{traceback.format_exc()}")
            return
        if result:
            wb = openpyxl.Workbook()
            ws = wb.active
            for i_index, i in enumerate(self.data):
                for j_index, j in enumerate(i):
                    ws.cell(i_index + 1, j_index + 1).value = j
            map(wb.save, self.output_files)
            shutil.move(self.input_file, self.backup_file)
