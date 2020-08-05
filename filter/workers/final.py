from filter.workers.base import AdvancedWorkerBase
from filter.utils.xlsx_to_rows import xlsx_to_rows
from filter.config import *
from datetime import datetime
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
            cond1 = data_value <= top if top else True
            cond2 = data_value >= bottom if bottom else True
            return data_row if all([cond1, cond2]) else []
    else:
        print(filter_type, field, value)
        raise Exception
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
    rows = xlsx_to_rows(filename)
    field_to_index = {i: index for index, i in enumerate(rows[0])}
    result = {}
    for row in rows[1:]:
        key = "-".join([row[field_to_index[key]] for key in key_fields.split("&")])
        value = [row[field_to_index[key]] for key in value_fields.split("&")]
        result[key] = value

    def _wrapper(data_row, data_field_to_index):
        data_key = "-".join([data_row[data_field_to_index[k]] for k in key_fields.split("&")])
        data_row.extend(result.get(data_key, []))
        return data_row
    return _wrapper


sheet_name_to_transform = {
    "单列过滤": transform_filter,
    "替换": transform_replace,
    "添加列": transform_add_list
}


def get_rules(rules_files):
    rules = {}
    for customer, rules_file in rules_files.items():
        wb = openpyxl.load_workbook(rules_file)
        rules[customer] = []
        for ws in wb.worksheets:
            rows = [i for i in ws.rows][1:]
            for i in rows:
                try:
                    rules[customer].append(
                        sheet_name_to_transform[ws.title](
                            *[str(j.value).strip() if j.value is not None else "" for j in i]
                        )
                    )
                except KeyError:
                    raise ValueError(f"{rules_file}中存在不合法的表名: {ws.title}")
                except FileNotFoundError:
                    raise ValueError(f"{rules_file}中，指定的映射表文件不存在")
    return rules


class FinalWorker(AdvancedWorkerBase):
    TYPE_DICT = {
        "日特殊规则": get_rules(DAILY_RULES_FILES),
        "月特殊规则": get_rules(MONTHLY_RULES_FILES)
    }
    # 子类覆盖此参数
    USED_RULE = None

    def real_process(self):
        print(f"Final: {self.input_file}")
        if self.customer not in self.TYPE_DICT[self.USED_RULE]:
            return True
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
        return True

    def process(self):
        if super().process():
            return True
        else:
            return False


class MonthlyFinalWorker(FinalWorker):
    USED_RULE = "月特殊规则"

    def get_output_files(self):
        return [
            os.path.join(
                os.path.split(self.input_file)[0],
                "month",
                f"final_{os.path.split(self.input_file)[1].split('_')[1]}_"
                f"{os.path.split(self.input_file)[1].split('_')[2]}_"
                f"{datetime.now().strftime('%Y%m')}.xlsx"
            )
        ]


class DailyFinalWorker(FinalWorker):
    USED_RULE = "日特殊规则"

    def get_output_files(self):
        return [
            os.path.join(
                os.path.split(self.input_file)[0],
                f"final_{os.path.split(self.input_file)[1].split('_')[1]}_"
                f"{os.path.split(self.input_file)[1].split('_')[2]}.xlsx"
            )
        ]
