from filter.workers.base import AdvancedWorkerBase
from filter.utils.xlsx_to_rows import xlsx_to_rows
from filter.config import GLOBAL_HEADER_RULES_FILE, HEADER_RULES_FILES
from datetime import datetime
from copy import deepcopy
import os
import re


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
                continue
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
            self.error(f"存在未能匹配到的关键列：{', '.join(lost_keys)}")
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
        if self.transform_type != "ADI":
            for index in range(1, len(self.data)):
                self.data[index].extend(["" for _ in range(len(lost_keys))])
            date_pattern = re.compile(r"(?P<year>\d{4})[/\s-]*(?P<month>\d{1,2})[/\s-]*(?P<day>\d{1,2})")
            field_to_index = {i: index for index, i in enumerate(self.data[0])}
            date_index = field_to_index["date"] if self.file_type in "PS" else field_to_index["inventoryReportDate"]
            control_date_index = field_to_index["controlDate"]
            for index, row in enumerate(self.data):
                if index == 0:
                    continue
                result = date_pattern.search(row[date_index])
                if not result:
                    if self.data[1][date_index]:
                        self.error(f"第{index + 1}行发现不合法的日期时间格式: \"{self.data[1][date_index]}\"")
                    else:
                        self.error(f"第{index + 1}行日期时间为空")
                    return False
                self.data[index][control_date_index] = \
                    result.groupdict()["year"] + result.groupdict()["month"] + result.groupdict()["day"]

        return True
