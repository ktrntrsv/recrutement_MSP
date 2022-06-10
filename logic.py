from collections import defaultdict
from pprint import pprint
from datetime import datetime
from logger_file import logger
import string

import config


def stages_counter(fields_data):
    reversed_stages = tuple(reversed(config.order_stages))
    counter = dict.fromkeys(reversed_stages, 0)
    self_denial = 0

    if not fields_data:
        return None, None
    for candidate in fields_data:
        # candidate = {'ФИО': 'Андреев Андрей Андреевич', 'ГС: приглашен': True, 'ГС: дата прихода': ['2022-04-24'] ...}
        stage_index = len(config.order_stages)
        if candidate["Статус"] == "Самоотказ" or candidate["Статус"] == "Неизвестен":
            self_denial += 1
            continue
        elif candidate["Статус"] == "На следующий семестр" or \
                candidate["Статус"] == "На следующий год" or \
                candidate["Статус"] == "На весну 2022" or \
                candidate["Статус"] == "На лето 2022":
            continue

        for index, stage in enumerate(reversed_stages):
            if candidate[config.field_names[stage]]:
                stage_index = index
                break
        for i in range(stage_index, len(config.order_stages)):
            counter[reversed_stages[i]] += 1

    return counter, self_denial


def table_date_to_datetime_converter(table_date: str):
    if not table_date:
        return datetime.now(), datetime.now()

    try:
        start, end = table_date.split("-")
        d1, m1 = map(int, start.split("."))
        d2, m2, y = map(int, end.split("."))

        y += 2000

        start = datetime(day=d1, month=m1, year=y)
        end = datetime(day=d2, month=m2, year=y)

        return start, end

    except ValueError:
        return None, None


def get_column_names() -> list:
    """
    get table's table name
    ['A', 'B', 'C', 'D', 'E', 'F' ... 'AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG'...]
    """
    s = list(string.ascii_uppercase)

    for i in string.ascii_uppercase:
        for j in string.ascii_uppercase:
            s.append(i + j)
    return s
