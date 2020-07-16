from config import ERROR_LOG
import logging

fh = logging.FileHandler(ERROR_LOG)
formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d]: %(message)s')
fh.setFormatter(formatter)
fh.setLevel(logging.DEBUG)
logger = logging.getLogger()
logger.addHandler(fh)

