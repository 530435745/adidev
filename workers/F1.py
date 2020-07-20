from workers.base import AdvancedWorkerBase
from utils.xlsx_to_rows import xlsx_to_rows
from config import GLOBAL_HEADER_RULES_FILE, HEADER_RULES_FILES
from datetime import datetime
from copy import deepcopy
import os


def load_header_rules(rules_file, origin_rules=None):
    if origin_rules:
        origin_rules = deepcopy(origin_rules)
    else:
        origin_rules = {
            "I": {"key_titles": {}, "optional_titles": {}},
            "P": {"key_titles": {}, "optional_titles": {}},
            "S": {"key_titles": {}, "optional_titles": {}}
        }
    for sheet_name in origin_rules.keys():
        try:
            rows = xlsx_to_rows(rules_file, sheet_name)
        except KeyError:
            raise ValueError(f"规则文件{rules_file}中找不到必要sheet：{sheet_name}")
        current = "key_titles"
        for index, i in enumerate(rows[0]):
            if not i:
                current = "optional_titles"
            if origin := origin_rules[sheet_name][current].get(i):
                origin_rules[sheet_name][current][i] = [row[index] for row in rows] + origin
            else:
                origin_rules[sheet_name][current][i] = [row[index] for row in rows]
    return origin_rules


GLOBAL_HEADER_RULES = load_header_rules(GLOBAL_HEADER_RULES_FILE)


class F1Worker(AdvancedWorkerBase):
    """
    列名匹配模块
    """
    # 载入列名匹配规则
    CUSTOMER_HEADER_RULES = {}
    for customer, file_name in HEADER_RULES_FILES.items():
        CUSTOMER_HEADER_RULES[customer] = load_header_rules(file_name, GLOBAL_HEADER_RULES)

    def get_output_files(self):
        return [self.input_file.replace("F0_", "F1_")]

    def get_backup_file(self):
        return os.path.join(
            os.path.split(self.input_file)[0],
            "status",
            f"done{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}_{os.path.split(self.input_file)[1]}"
        )

    def real_process(self):
        print(f"F1: {self.input_file}")
        if self.file_type not in ["I", "P", "S"]:
            self.error(f"发现命名异常文件：{self.input_file}")
            return False
        rule_info = self.CUSTOMER_HEADER_RULES.get(self.customer, GLOBAL_HEADER_RULES)[self.file_type]
        lost_keys = []
        for key, values in rule_info["key_titles"].items():
            for value in values:
                try:
                    index = self.data[0].index(value)
                except ValueError:
                    continue
                self.data[0][index] = key
                break
            else:
                lost_keys.append(key)
        if lost_keys:
            self.error(f"文件{self.input_file}中，存在未能匹配到的关键列：{', '.join(lost_keys)}")
            return False
        lost_keys = []
        for key, values in rule_info["optional_titles"].items():
            for value in values:
                try:
                    index = self.data[0].index(value)
                except ValueError:
                    continue
                self.data[0][index] = key
                break
            else:
                lost_keys.append(key)
        self.data[0].extend(lost_keys)
        return True
