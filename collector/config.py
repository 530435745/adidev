from datetime import datetime
import os


BASE_DIR = "/demo"
# 汇总报告目录
REPORT_DIR = os.path.join(BASE_DIR, 'report')
# 汇总错误日志
COLLECTOR_ERROR_LOG = os.path.join(BASE_DIR, "collector_error.log")
# 汇总间隔
COLLECTOR_INTERVAL = 600
# 总量跟踪表文件
COLLECTOR_TOTAL_FILE = lambda: os.path.join(REPORT_DIR, f"总量跟踪表-{datetime.now().strftime('%Y-%m-%d')}.xlsx")
# 返回情况表文件
COLLECTOR_RETURN_FILE = lambda: os.path.join(REPORT_DIR, f"返回情况表-{datetime.now().strftime('%Y-%m-%d')}.xlsx")
# 所有厂商目标清单文件列表
COLLECTOR_TARGETS_LIST = [os.path.join(BASE_DIR, "rules", "L_target_list.xlsx")]
# 所有厂商已分发文件目录
COLLECTOR_ORDERED_DIR_LIST = [os.path.join(BASE_DIR, "spld")]
