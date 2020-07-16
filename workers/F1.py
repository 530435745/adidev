from workers.base import WorkerBase
from config import GLOBAL_TARGET_RULES_FILE, GLOBAL_HEADER_RULES_FILE, HEADER_RULES_FILES
from workers.F2 import F2Worker
import openpyxl
from datetime import datetime
from copy import deepcopy


def load_header_rules(rules_file, origin_rules=None):
    if origin_rules:
        origin_rules = deepcopy(origin_rules)
    else:
        origin_rules = {
            "I": {"key_titles": [], "necessary": {}, "unnecessary": {}},
            "P": {"key_titles": [], "necessary": {}, "unnecessary": {}},
            "S": {"key_titles": [], "necessary": {}, "unnecessary": {}}
        }
    wb = openpyxl.load_workbook(rules_file)
    for sheet_name in origin_rules.keys():
        try:
            ws = wb[sheet_name]
        except KeyError:
            raise ValueError(f"规则文件{rules_file}中找不到必要sheet：{sheet_name}")
        rows = [[str(j.value).strip() if j.value else "" for j in i] for i in ws.rows]
        title = rows[0]
        for index, i in enumerate(title):
            if i:
                origin_rules[sheet_name]["key_titles"].append(i)
            else:
                break
        else:
            raise ValueError(f"规则文件{rules_file}的{sheet_name}中找不到分隔空列，无法区分key值类型")
        for i in rows[1:]:
            for index, j in enumerate(i):
                if j:
                    if index in origin_rules[sheet_name]["key_titles"]:
                        origin_rules[sheet_name]["necessary"][j] = title[index]
                    else:
                        origin_rules[sheet_name]["unnecessary"][j] = title[index]
    return origin_rules


class F1Worker(WorkerBase):
    """
    列名匹配模块
    """
    NEXT = F2Worker
    # 载入目标清单规则
    TARGETS = []
    wb = openpyxl.load_workbook(GLOBAL_TARGET_RULES_FILE)
    ws = wb.worksheets[0]
    rows = [[str(j.value).strip() if j.value else "" for j in i] for i in ws.rows][1:]
    for row in rows:
        if int(datetime.now().strftime("%Y%m")) >= int(row[6]):
            TARGETS.append(rows[1])

    # 载入列名匹配规则
    GLOBAL_HEADER_RULES = load_header_rules(GLOBAL_HEADER_RULES_FILE)
    CUSTOMER_HEADER_RULES = {
        customer: load_header_rules(file_name, GLOBAL_HEADER_RULES)
        for customer, file_name in HEADER_RULES_FILES.items()
    }

    def _process(self):
        if self.customer not in self.TARGETS:
            return False
        exist_keys = []
        if self.file_type not in ["I", "P", "S"]:
            self.error(f"发现命名异常文件：{self.input_file}")
            return False
        if customer_info := self.CUSTOMER_HEADER_RULES.get(self.customer):
            rule_info = customer_info[self.file_type]
        else:
            rule_info = self.GLOBAL_HEADER_RULES[self.file_type]
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
        self.data[0].extend([i for i in rule_info["unnecessary"].keys() if i not in self.data[0]])
        return True
