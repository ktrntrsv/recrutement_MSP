from logger_file import logger

import sys
from datetime import datetime, timedelta


def get_semester_name(prev_sem):
    if prev_sem:
        half_year_ago = datetime.now() - timedelta(days=180)
        curr_year = half_year_ago.year
        curr_month = half_year_ago.month
    else:
        curr_year = datetime.now().year
        curr_month = datetime.now().month

    if curr_month >= 10:
        semester = "I"
        y1 = str(curr_year)[-2:]
        y2 = str(curr_year + 1)[-2:]
    elif curr_month <= 3:
        semester = "I"
        y1 = str(curr_year - 1)[-2:]
        y2 = str(curr_year)[-2:]
    else:
        semester = "II"
        y1 = str(curr_year - 1)[-2:]
        y2 = str(curr_year)[-2:]

    result = f"{y1}/{y2}-{semester}"
    return result


def get_list_name(prev_sem: bool = False):
    semester = get_semester_name(prev_sem)
    if is_spb_flag():
        return f"Питер - набор {semester}!"
    else:
        return f"Школа - набор {semester}!"


def is_spb_flag() -> bool:
    arguments = sys.argv
    if not len(arguments) >= 2:
        logger.info("Spb_flag = False")
        return False
    if arguments[1] == "--spb":
        logger.info("Spb_flag = True")
        return True


