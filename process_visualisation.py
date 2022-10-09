from datetime import datetime, timedelta
from functools import wraps
from typing import Callable

from loguru import logger

import config
from table_scaner import Table


class Updater:
    __slots__ = ("table",)

    warning_cell = "A24:A25"

    def __init__(self, table):
        self.table = table

    def __enter__(self):
        self.table.write("A26:A27", [[""], [""]])
        self.table.write(self.warning_cell, [[""], [""]])
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        from logic import cut_table_alphabet
        self.table.write(
            f"{cut_table_alphabet[0]}{config.loading_with_eyes_table_string_number}:"
            f"{cut_table_alphabet[-1]}{config.loading_with_eyes_table_string_number}",

            [[""] * len(cut_table_alphabet)])
        if exc_type:
            self._log_exception(exc_val)

    def log_last_update(self):
        self.table.write(self.warning_cell,
                         [["Последнее обновление:"], [f"{datetime.now() + timedelta(hours=3)}"[:-10]]])
        logger.info("Success.")

    def _log_exception(self, exc_val):
        self.table.write(self.warning_cell,
                         [[f"Произошла ошибка {exc_val}."],
                          [f"Пожалуйста, сообщите об этом {config.responsible}"]])
        logger.error(Exception.args)
        raise Exception


def add_table_loading_signs(func: Callable, list_name) -> Callable:
    @wraps(func)
    def wrapper() -> None:
        t = Table(list_name)

        with Updater(table=t) as upd:
            func(t)
            upd.log_last_update()

    return wrapper


def visualize_loading(func: Callable):
    @wraps(func)
    def wrapped(info, column_letter, table):
        loading_cell = column_letter + config.loading_with_eyes_table_string_number
        table.write(loading_cell, [["👀"]])

        func(info, column_letter, table)

        table.write(loading_cell, [["✔️"]])

    return wrapped
