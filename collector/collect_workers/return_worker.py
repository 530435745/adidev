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
              "销售数量", "文件名", "流向最大日期", "进销存类型", "最大返回日期", "状态"]

    @classmethod
    def add_line(cls, current_dir):
        code = current_dir.split(os.sep)[-1]
        return_result = [[code, cls.TARGETS[code]["name"], cls.TARGETS[code]["operation_type"], cls.TARGETS[code]["mark"],
                         "", "", "", i, "", "未返回"] for i in ["P", "S", "I"]]
        today = datetime.now()
        today_pattern = re.compile(
            rf"F1_{cls.TARGETS[code]['operation_type'][:3]}_(?P<file_type>[IPS])_{code}_"
            rf"{today.year}-{str(today.month).zfill(2)}-{str(today.day).zfill(2)}.+")
        date_pattern = re.compile(r"(?P<year>\d{4})[/\s-](?P<month>\d{2})[/\s-](?P<day>\d{2})")
        dirs = [current_dir]
        if os.path.exists(status_dir := os.path.join(current_dir, "status")):
            dirs.append(status_dir)
        for current_dir in dirs:
            for file in os.listdir(current_dir):
                if result := today_pattern.search(file):
                    file_data = xlsx_to_rows(os.path.join(current_dir, file))
                    file_type = result.groupdict()["file_type"]
                    index = ["P", "S", "I"].index(file_type)
                    if len(file_data) >= 2:
                        field_to_index = {i: index for index, i in enumerate(file_data[0])}
                        control_date_index = field_to_index["controlDate"]
                        qty_index = field_to_index["qty"]
                        max_date = 0
                        for row in file_data[1:]:
                            try:
                                if current_num := int(row[control_date_index]) > max_date:
                                    max_date = current_num
                            except ValueError:
                                break
                        return_result[index][4] = sum([int(float(row[qty_index])) for row in file_data[1:]])
                        return_result[index][6] = str(max_date)
                    return_result[index][5] = os.path.join(current_dir, file)
                    return_result[index][8] = datetime.now().strftime("%Y%m%d")
                    return_result[index][9] = "已返回"
        return return_result



