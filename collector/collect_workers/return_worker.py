from collector.collect_workers.base import CollectorWorkerBase
from collector.config import COLLECTOR_RETURN_FILE
from collector.utils.xlsx_to_rows import xlsx_to_rows
from collector.utils.logger import logger
from datetime import datetime
import os
import re


class ReturnCollector(CollectorWorkerBase):
    RESULT_FILE = COLLECTOR_RETURN_FILE
    TITLES = ["经销商代码", "经销商名称", "收集方式", "收集标记",
              "销售条数", "文件名", "流向最大日期", "进销存类型", "最大返回日期", "状态"]

    @classmethod
    def add_line(cls, current_dir):
        code = current_dir.split(os.sep)[-1]
        return_result = [[code, cls.TARGETS[code]["name"], cls.TARGETS[code]["operation_type"], cls.TARGETS[code]["mark"],
                         "", "", "", i, "", "未返回"] for i in ["P", "S", "I"]]
        today = datetime.now()
        today_pattern = re.compile(
            rf"F1_{cls.TARGETS[code]['operation_type'][:3]}_(?P<file_type>[IPS])_{code}_"
            rf"{today.year}-{today.month}-{today.day}.+")
        date_pattern = re.compile(r"(?P<year>\d{4})[/\s-](?P<month>\d{2})[/\s-](?P<day>\d{2})")
        dirs = [current_dir, os.path.join(current_dir, "status")]
        for current_dir in dirs:
            for file in os.listdir(current_dir):
                if result := today_pattern.search(file):
                    file_data = xlsx_to_rows(os.path.join(current_dir, file))
                    field_to_index = {i: index for index, i in enumerate(file_data[0])}
                    file_type = result.groupdict()["file_type"]
                    date_index = field_to_index["date"] if file_type in "PS" else field_to_index["inventoryReportDate"]
                    qty_index = field_to_index["qty"]
                    if not date_pattern.search(file_data[1][date_index]):
                        if re.search(r"(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})", file_data[1][date_index]):
                            current_date_pattern = re.compile(r"(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})")
                        else:
                            logger.error(f"{os.path.join(current_dir, file)}中，日期列无法匹配到任何规则，已跳过")
                            continue
                    else:
                        current_date_pattern = date_pattern
                    index = ["P", "S", "I"].index(file_type)
                    max_date = None
                    max_num = None
                    for row in file_data[1:]:
                        result = current_date_pattern.search(row[date_index])
                        if not result:
                            continue
                        if not max_date:
                            max_date = row[date_index]
                            max_num = int(result.groupdict()["year"]) * 10000 + \
                                      int(result.groupdict()["month"]) * 100 + \
                                      int(result.groupdict()["day"])
                        else:
                            if current_num := int(result.groupdict()["year"]) * 10000 + \
                                              int(result.groupdict()["month"]) * 100 + \
                                              int(result.groupdict()["day"]) > max_num:
                                max_date = row[date_index]
                                max_num = current_num
                    return_result[index][4] = sum([int(row[qty_index]) for row in file_data[1:]])
                    return_result[index][5] = os.path.join(current_dir, file)
                    return_result[index][6] = max_date
                    return_result[index][8] = datetime.now().strftime("%Y%m%d")
                    return_result[index][9] = "已返回"
        return return_result



