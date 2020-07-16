from workers.base import WorkerBase
from workers.F3 import F3Worker
from config import GLOBAL_PRODUCT_RULES_FILE, PRODUCT_RULES_FILES
from copy import deepcopy
import openpyxl


def load_product_rules(rules_file, origin_rules=None):
    if origin_rules:
        origin_rules = deepcopy(origin_rules)
    else:
        origin_rules = {}
    wb = openpyxl.load_workbook(rules_file)
    ws = wb.worksheets[0]
    rows = [[str(j.value).strip() if j.value else "" for j in i] for i in ws.rows][1:]
    for row in rows:
        origin_rules[f"{row[0]}-{row[1]}"] = {
            "name": row[2],
            "size": row[3],
            "unit": row[4],
            "multi": int(row[6]) if row[5] == "是" else 1
        } if row[7] == "是" else {}
    return origin_rules


class F2Worker(WorkerBase):
    """
    产品规格过滤模块
    """
    NEXT = F3Worker
    GLOBAL_PRODUCT_RULES = load_product_rules(GLOBAL_PRODUCT_RULES_FILE)
    CUSTOMER_PRODUCT_RULES = {
        customer: load_product_rules(file_name, GLOBAL_PRODUCT_RULES)
        for customer, file_name in PRODUCT_RULES_FILES.items()
    }

    def _process(self):
        title = self.data[0]
        current_rule = self.CUSTOMER_PRODUCT_RULES.get(self.customer, GLOBAL_PRODUCT_RULES_FILE)
        name_pos = title.index("productName")
        spec_pos = title.index("productSpec")
        qty_pos = title.index("qty")
        self.data.extend(["originProductName", "originProductSpec"])
        to_delete = []
        for index, i in enumerate(self.data):
            if index == 0:
                continue
            if result := current_rule.get(f"{i[name_pos]}-{i[spec_pos]}") is not None:
                if result != {}:
                    self.data[index].extend([i[name_pos], i[spec_pos]])
                    self.data[index][name_pos], self.data[index][spec_pos] = result["name"], result["size"]
                    self.data[index][qty_pos] = result["multi"] * int(self.data[index][qty_pos])
                else:
                    to_delete.append(self.data[index])
            else:
                self.error(f"文件{self.input_file}中，第{index}行未能匹配到规则")
                return False
        self.data = [i for index, i in enumerate(self.data) if index not in to_delete]
        return True
