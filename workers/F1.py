from workers.base import AdvancedWorkerBase
from utils.xlsx_to_rows import xlsx_to_rows
from config import GLOBAL_TARGET_RULES_FILE, GLOBAL_HEADER_RULES_FILE, HEADER_RULES_FILES
from datetime import datetime
from copy import deepcopy
import os
import time


def load_header_rules(rules_file, origin_rules=None):
    if origin_rules:
        origin_rules = deepcopy(origin_rules)
    else:
        origin_rules = {
            "I": {"key_titles": [], "necessary": {}, "unnecessary": {}},
            "P": {"key_titles": [], "necessary": {}, "unnecessary": {}},
            "S": {"key_titles": [], "necessary": {}, "unnecessary": {}}
        }
    for sheet_name in origin_rules.keys():
        try:
            rows = xlsx_to_rows(rules_file, sheet_name)
        except KeyError:
            raise ValueError(f"规则文件{rules_file}中找不到必要sheet：{sheet_name}")
        title = rows[0]
        for index, i in enumerate(title):
            if i:
                origin_rules[sheet_name]["key_titles"].append(i)
            else:
                sep_post = index
                break
        else:
            raise ValueError(f"规则文件{rules_file}的{sheet_name}中找不到分隔空列，无法区分key值类型")
        origin_rules[sheet_name]["optional_titles"] = title[sep_post + 1:]
        for i in rows[1:]:
            for index, j in enumerate(i):
                if j:
                    if index < sep_post:
                        origin_rules[sheet_name]["necessary"][j] = title[index]
                    else:
                        origin_rules[sheet_name]["unnecessary"][j] = title[index]
    return origin_rules


GLOBAL_HEADER_RULES = load_header_rules(GLOBAL_HEADER_RULES_FILE)


class F1Worker(AdvancedWorkerBase):
    """
    列名匹配模块
    """
    # 载入目标清单规则
    TARGETS = []
    rows = xlsx_to_rows(GLOBAL_TARGET_RULES_FILE)[1:]
    for row in rows:
        if not row[0]:
            break
        if int(datetime.now().strftime("%Y%m")) >= int(row[6]):
            TARGETS.append(row[0].split("_")[1])

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
        if self.customer not in self.TARGETS:
            return False
        exist_keys = []
        if self.file_type not in ["I", "P", "S"]:
            self.error(f"发现命名异常文件：{self.input_file}")
            return False
        rule_info = self.CUSTOMER_HEADER_RULES.get(self.customer, GLOBAL_HEADER_RULES)[self.file_type]
        for index, i in enumerate(self.data[0]):
            if n_key := rule_info["necessary"].get(i):
                self.data[0][index] = n_key
                exist_keys.append(n_key)
            elif un_key := rule_info["unnecessary"].get(i):
                self.data[0][index] = un_key
            else:
                pass
        if lost_keys := [i for i in rule_info["key_titles"] if i not in exist_keys]:
            self.error(f"文件{self.input_file}中，缺少若干关键列：{', '.join(lost_keys)}")
            return False
        self.data[0].extend([i for i in rule_info["optional_titles"] if i not in self.data[0]])
        return True
