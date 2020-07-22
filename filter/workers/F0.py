from filter.workers.base import WorkerBase
from filter.config import GLOBAL_SPLIT_RULES_FILE
from filter.utils.MD5 import get_md5
from filter.utils.xlsx_to_rows import xlsx_to_rows
from datetime import datetime
import os


class F0Worker(WorkerBase):
    """
    文件从待分发到F0，只执行文件移动和备份
    """
    RULES = {}
    rows = xlsx_to_rows(GLOBAL_SPLIT_RULES_FILE)[1:]
    for row in rows:
        if not row[0]:
            break
        RULES[row[0]] = {
            "targets": [i for i in row[1].split("|")],
            "sign": row[2],
            "sep": row[3],
            "pos": row[4]
        }

    def __init__(self, input_file):
        super().__init__(input_file)

    def new_file_name(self, customer):
        md5_str = get_md5(self.input_file)
        file_path, file_name = os.path.split(self.input_file)
        return f"F0_" \
               f"{file_name.split('_')[0]}_" \
               f"{file_name.split('_')[1]}_" \
               f"{customer}_" \
               f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}_" \
               f"{md5_str}.xlsx"

    def get_backup_file(self):
        return os.path.join(
            os.path.split(self.input_file)[0],
            "history",
            f"done{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}_{get_md5(self.input_file)}_"
            f"{os.path.split(self.input_file)[1]}"
        )

    def real_process(self):
        print(f"F0: {self.input_file}")
        if not self.data:
            return False
        file_path, file_name = os.path.split(self.input_file)
        if file_name.split(self.RULES[file_path]["sep"])[int(self.RULES[file_path]["pos"])] \
                == self.RULES[file_path]["sign"]:
            customer = file_path.split(os.path.sep)[-1]
            new_file_name = self.new_file_name(customer)
            self.output_files = []
            for target in self.RULES[file_path]["targets"]:
                self.output_files.append(os.path.join(target, new_file_name))
            return True
        return False
