from workers.base import AdvancedWorkerBase
from utils.xlsx_to_rows import xlsx_to_rows
from config import GLOBAL_PRODUCT_RULES_FILE, PRODUCT_RULES_FILES
from copy import deepcopy
from datetime import datetime
import os


def load_product_rules(rules_file, origin_rules=None):
    if origin_rules:
        origin_rules = deepcopy(origin_rules)
    else:
        origin_rules = {}
    rows = xlsx_to_rows(rules_file)[1:]
    for row in rows:
        origin_rules[f"{row[0]}-{row[1]}"] = {
            "name": row[2],
            "size": row[3],
            "unit": row[4],
            "multi": int(row[6]) if row[5] == "是" else 1
        } if row[7] == "是" else {}
    return origin_rules


class F2Worker(AdvancedWorkerBase):
    """
    产品规格过滤模块
    """
    GLOBAL_PRODUCT_RULES = load_product_rules(GLOBAL_PRODUCT_RULES_FILE)
    CUSTOMER_PRODUCT_RULES = {
        customer: load_product_rules(file_name, GLOBAL_PRODUCT_RULES)
        for customer, file_name in PRODUCT_RULES_FILES.items()
    }

    def get_output_files(self):
        return [self.input_file.replace("F1_", "F2_")]

    def get_backup_file(self):
        return os.path.join(
            os.path.split(self.input_file)[0],
            "status",
            f"done{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}_{os.path.split(self.input_file)[1]}"
        )

    def real_process(self):
        print(f"F2: {self.input_file}")
        title = self.data[0]
        current_rule = self.CUSTOMER_PRODUCT_RULES.get(self.customer, self.GLOBAL_PRODUCT_RULES)
        name_pos = title.index("productName")
        spec_pos = title.index("productSpec")
        qty_pos = title.index("qty")
        self.data[0].extend(["originProductName", "originProductSpec"])
        to_delete = []
        for index, i in enumerate(self.data):
            if index == 0:
                continue
            if (result := current_rule.get(f"{i[name_pos]}-{i[spec_pos]}")) is not None:
                if result != {}:
                    self.data[index].extend([i[name_pos], i[spec_pos]])
                    self.data[index][name_pos], self.data[index][spec_pos] = result["name"], result["size"]
                    self.data[index][qty_pos] = result["multi"] * int(float(self.data[index][qty_pos]))
                else:
                    self.data[index] = []
            else:
                self.error(f"第{index + 1}行未能匹配到规则，产品规格为: {i[name_pos]}-{i[spec_pos]}")
                return False
        self.data = [i for i in self.data if i]
        return True
