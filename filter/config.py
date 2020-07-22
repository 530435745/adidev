import os
from datetime import datetime

# BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "adidev")
BASE_DIR = "/demo"

SEARCH_DOMAIN = "mdmapileo.qtdatas.com"
NEW_QUERY_URL = f"http://{SEARCH_DOMAIN}/x1/newquery"
GET_RESULT_URL = f"http://{SEARCH_DOMAIN}/x1/getresult"
INTERVAL = 300
ERROR_LOG = os.path.join(BASE_DIR, "error.log")

# 待分发目录
CHAOS_FILES_DIR = os.path.join(BASE_DIR, "pds")
# 已分发目录
ORDERED_FILES_DIR = os.path.join(BASE_DIR, "spld")

RULES_DIR = os.path.join(BASE_DIR, "rules")
# 全局目标清单文件
GLOBAL_TARGET_RULES_FILE = os.path.join(RULES_DIR, "L_target_list.xlsx")
# 全局分发规则文件
GLOBAL_SPLIT_RULES_FILE = os.path.join(RULES_DIR, "L_split_rules.xlsx")
# 全局字段匹配规则文件
GLOBAL_HEADER_RULES_FILE = os.path.join(RULES_DIR, "L_name_list.xlsx")
# 全局产品过滤规则文件
GLOBAL_PRODUCT_RULES_FILE = os.path.join(RULES_DIR, "L_product_list.xlsx")
# 当天分发记录文件
SPLIT_RESULT_FILE = lambda: os.path.join(RULES_DIR, f"分发记录-{datetime.now().strftime('%Y-%m-%d')}.xlsx")
# 当天产品未识别清单
PRODUCT_FILTER_RESULT_FILE = lambda: os.path.join(RULES_DIR, f"产品未识别清单-{datetime.now().strftime('%Y-%m-%d')}.xlsx")

# 经销商字段匹配规则文件（根据已分发目录自动扫描添加）
HEADER_RULES_FILES = {}
# 经销商产品过滤规则文件（根据已分发目录自动扫描添加）
PRODUCT_RULES_FILES = {}
# 经销商日总结规则文件（根据已分发目录自动扫描添加）
DAILY_RULES_FILES = {}
# 经销商月总结规则文件（根据已分发目录自动扫描添加）
MONTHLY_RULES_FILES = {}
# 经销商匹配规则文件（根据已分发目录自动扫描添加）
MATCH_RULES_FILES = {}
# 扫描经销商配置文件
for _dir_name, _sub_dirs, _files in os.walk(ORDERED_FILES_DIR):
    for _filename in _files:
        target = None
        if _filename == "name_list.xlsx":
            target = HEADER_RULES_FILES
        if _filename == "product_list.xlsx":
            target = PRODUCT_RULES_FILES
        if _filename == "日数据特殊规则.xlsx":
            target = DAILY_RULES_FILES
        if _filename == "月数据特殊规则.xlsx":
            target = MONTHLY_RULES_FILES
        if _filename == "customer_list.xlsx":
            target = MATCH_RULES_FILES
        if target is not None:
            target[_dir_name.split(os.sep)[-1].split("_")[1]] = os.path.join(_dir_name, _filename)


if __name__ == '__main__':
    print(BASE_DIR)
