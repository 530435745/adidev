from collector.collect_workers.base import CollectorWorkerBase
from collector.config import COLLECTOR_TOTAL_FILE
from datetime import datetime
import os
import re


class TotalCollector(CollectorWorkerBase):
    RESULT_FILE = COLLECTOR_TOTAL_FILE
    TITLES = ["经销商代码", "经销商名称", "数据采集方式",
              "采购交付物差异时间", "销售交付物差异时间", "库存交付物差异时间",
              "历史平均销量", "加权评分",
              "直连采购最新状态", "直连销售最新状态", "直连库存最新状态",
              "手工采购最新状态", "手工销售最新状态", "手工库存最新状态"]

    @staticmethod
    def get_days(file_time):
        return (datetime.now().date() - datetime.fromtimestamp(file_time).date()).days

    @staticmethod
    def get_newest(status):
        if not status:
            return "na"
        for s in ["final", "F3", "F2", "F1", "F0"]:
            if s in status:
                return s

    @classmethod
    def add_line(cls, current_dir):
        code = current_dir.split(os.sep)[-1]
        files = os.listdir(current_dir)
        result = [code, cls.TARGETS[code]["name"], cls.TARGETS[code]["operation_type"],
                  9999, 9999, 9999, int(cls.TARGETS[code]["history"]) if cls.TARGETS[code]["history"] else 0,
                  9999, [], [], [], [], [], []]
        pattern = re.compile(r"(F0|F1|F2|F3|final)_(FTP|MNL|ADI)_[IPS].+")
        final_pos = {"P": 3, "S": 4, "I": 5}
        adi_pos = {"P": 8, "S": 9, "I": 10}
        mnl_pos = {"P": 11, "S": 12, "I": 13}
        for file in files:
            if re.match(pattern, file):
                if file.split("_")[0] == "final" and file.split("_")[1] == cls.TARGETS[code]["operation_type"][:3]:
                    result[final_pos[file.split(".")[0].split("_")[2]]] = cls.get_days(
                        os.stat(os.path.join(current_dir, file)).st_ctime
                    )
                if file.split("_")[1] == "ADI":
                    result[adi_pos[file.split(".")[0].split("_")[2]]].append(file.split("_")[0])
                if file.split("_")[1] == "MNL":
                    result[mnl_pos[file.split(".")[0].split("_")[2]]].append(file.split("_")[0])
        for i in range(8, 14):
            result[i] = cls.get_newest(result[i])
        result[7] = result[3]*0.1+result[4]*0.4+result[5]*0.2+result[6]*0.3
        return [result]
