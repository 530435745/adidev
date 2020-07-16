from workers.base import WorkerBase
from config import *
import openpyxl
import json


def transform_filter(field, value, filter_type):
    if filter_type == "定值":
        def _wrapper(data_row, data_field_to_index):
            return data_row if data_row[data_field_to_index[field]] == value else []
    elif filter_type == "包含":
        def _wrapper(data_row, data_field_to_index):
            return data_row if value in data_row[data_field_to_index[field]] else []
    elif filter_type == "不包含":
        def _wrapper(data_row, data_field_to_index):
            return data_row if value not in data_row[data_field_to_index[field]] else []
    elif filter_type == "区间":
        bottom = float(value.split("-")[0]) if value.split("-")[0] else None
        top = float(value.split("-")[1]) if value.split("-")[1] else None

        def _wrapper(data_row, data_field_to_index):
            try:
                data_value = float(data_row[data_field_to_index[field]])
            except ValueError:
                return "该列存在非法元素无法进行区间比对"
            cond1 = data_value < top if top else True
            cond2 = data_value > bottom if bottom else True
            return data_row if all([cond1, cond2]) else []
    else:
        raise
    return _wrapper


def transform_replace(filter_info, replace_info):
    def _wrapper(data_row, data_field_to_index):
        keys = json.loads(filter_info)
        if all([data_row[data_field_to_index[key]] == value for key, value in keys.items()]):
            values = json.loads(replace_info)
            for k, v in values:
                data_row[data_field_to_index[k]] = v
        return data_row
    return _wrapper


def transform_add_list(filename, key_fields, value_fields):
    wb = openpyxl.load_workbook(filename)
    ws = wb.worksheets[0]
    rows = [[str(j.value).strip() if j.value else "" for j in i] for i in ws.rows]
    field_to_index = {i: index for index, i in enumerate(rows[0])}
    result = {}
    for row in rows[1:]:
        key = "-".join([row[field_to_index[key]] for key in key_fields.split("&")])
        value = [row[field_to_index[key]] for key in value_fields.split("&")]
        result[key] = value

    def _wrapper(data_row, data_field_to_index):
        data_key = "-".join([data_row[data_field_to_index[key]] for key in key_fields.split("&")])
        data_row.extend(result.get(data_key, []))
        return data_row
    return _wrapper


sheet_name_to_transform = {
    "筛选": transform_filter,
    "替换": transform_replace,
    "加列": transform_add_list
}


def get_rules(rules_files):
    rules = {}
    for customer, rules_file in rules_files.items():
        wb = openpyxl.load_workbook(rules_file)
        rules[customer] = []
        for ws in wb.worksheets:
            rows = [i for i in ws.rows][1:]
            for i in rows:
                rules[customer].append(sheet_name_to_transform[ws.title](*[str(j.value).strip() if j.value else "" for j in i]))
    return rules


class FinalWorker(WorkerBase):
    TYPE_DICT = {
        "日特殊规则": get_rules(DAILY_RULES_FILES),
        "月特殊规则": get_rules(MONTHLY_RULES_FILES)
    }
    # 子类覆盖此参数
    USED_RULE = None

    def _process(self):
        field_to_index = {i: index for index, i in enumerate(self.data[0])}
        for index, row in enumerate(self.data):
            if index == 0:
                continue
            for rule_wrapper in self.TYPE_DICT[self.USED_RULE][self.customer]:
                if isinstance(row, str):
                    self.error(row)
                if row:
                    row = rule_wrapper(row, field_to_index)
                else:
                    break
            self.data[index] = row
        self.data = [i for i in self.data if i]


class MonthlyFinalWorker(FinalWorker):
    USED_RULE = "月特殊规则"


class DailyFinalWorker(FinalWorker):
    USED_RULE = "日特殊规则"
