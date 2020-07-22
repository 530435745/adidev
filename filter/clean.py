from filter.utils.timer import do_at
from filter.utils.xlsx_to_rows import xlsx_to_rows
from filter.config import SPLIT_RESULT_FILE
import os
import shutil
import time


def mkdir(dir_name):
    try:
        os.mkdir(dir_name)
    except FileExistsError:
        pass


@do_at(hour=21)
def clean():
    rows = xlsx_to_rows(SPLIT_RESULT_FILE)
    for row in rows[1:]:
        mkdir(os.path.join(row[0], "history"))
        for filename in os.listdir(row[0]):
            if filename.startswith("done"):
                shutil.move(
                    os.path.join(row[0], filename),
                    os.path.join(row[0], "history", filename)
                )
        for filename in os.listdir(os.path.join(row[0], "history")):
            now = time.time()
            if now - os.stat(os.path.join(row[0], "history", filename)).st_ctime > 30 * 24 * 60 * 60:
                os.remove(os.path.join(row[0], "history", filename))
