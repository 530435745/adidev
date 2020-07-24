from filter.utils.logger import logger
from filter.utils.xlsx_to_rows import xlsx_to_rows
from datetime import datetime
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
        try:
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
                self.error(f"格式未知，需为xlsx, xls或csv")
        except Exception as e:
            self.error(f"解析文件失败：{self.input_file}")

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
        logger.error(f"File : {self.input_file}")
        for c in content.split("\n"):
            logger.error(f"Error: {c}")
        logger.error("---------------------------------------------------------------------------")
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
            self.error(f"文件格式未知")
            return
        self.status, self.transform_type, self.file_type, factory_code, self.customer = infos
        self.customer = f"{factory_code}_{self.customer}"
