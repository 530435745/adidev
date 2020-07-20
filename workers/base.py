from utils.logger import logger
from datetime import datetime
from config import FACTORY_CODE
from utils.xlsx_to_rows import xlsx_to_rows
import openpyxl
import shutil
import csv
import os


def now_str():
    return datetime.now().strftime("%Y-%m-%d-%H-%M-%S")


class WorkerBase(object):
    def __init__(self, input_file):
        self.data = None
        self.input_file = input_file
        self.output_files = self.get_output_files()
        self.backup_file = self.get_backup_file()
        if input_file.endswith(".xls") or input_file.endswith(".xlsx"):
            self.data = xlsx_to_rows(input_file)
        elif input_file.endswith(".csv"):
            with open(self.input_file, 'rb') as csv_in:
                with open(self.input_file, "w", encoding="utf-8") as csv_temp:
                    for line in csv_in:
                        if not line:
                            break
                        else:
                            line = line.decode("utf-8", "ignore")
                            csv_temp.write(str(line).rstrip() + '\n')
            with open(self.input_file) as f:
                reader = csv.reader(f)
                self.data = [i for i in reader]
        elif input_file.endswith(".err"):
            pass
        else:
            self.error(f"发现未知格式文件{self.input_file}")

    def get_output_files(self):
        """
        生成返回文件列表
        :return:
        """

    def get_backup_file(self):
        """
        生成备份文件位置
        :return:
        """

    def error(self, content):
        """
        出错时移动问题文件到.err并记录日志
        :param content:
        :return:
        """
        logger.error(content)
        shutil.move(self.input_file, self.input_file.split(".")[0] + ".err." + self.input_file.split(".")[1])

    def real_process(self):
        """
        实际工作内容
        :return: 执行成功时返回True，失败时返回False
        """
        return True

    @staticmethod
    def mkdir(filename):
        path = os.path.split(filename)[0]
        try:
            os.makedirs(path)
        except FileExistsError:
            pass

    def process(self):
        """
        调用执行函数
        :return:
        """
        # try:
        result = self.real_process()
        # except Exception as e:
        #     self.error(f"程序执行出错，请联系开发人员：\n{traceback.format_exc()}")
        #     return
        if result:
            wb = openpyxl.Workbook()
            ws = wb.active
            for i_index, i in enumerate(self.data):
                for j_index, j in enumerate(i):
                    ws.cell(i_index + 1, j_index + 1).value = j
            for output in self.output_files:
                self.mkdir(output)
                wb.save(output)
            if self.backup_file:
                self.mkdir(self.backup_file)
                shutil.move(self.input_file, self.backup_file)
            return self.output_files


class AdvancedWorkerBase(WorkerBase):
    def __init__(self, input_file):
        super().__init__(input_file)
        if len(infos := self.input_file.split(os.sep)[-1].split("_")[:5]) < 5:
            self.error(f"发现未知格式文件{self.input_file}")
            return
        self.status, self.transform_type, self.file_type, self.factory_code, self.customer = infos

    def process(self):
        if self.input_file.split(os.sep)[-1].split("_")[3] != FACTORY_CODE:
            self.error(f"文件{self.input_file}命名不符合规则，或不属于当前厂商")
            return
        return super().process()
