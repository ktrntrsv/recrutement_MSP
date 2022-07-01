import sys
from typing import Callable

from table_scaner import Table
from datetime import datetime
import config
import logic
from loguru import logger


def add_table_loading_signs(func: Callable) -> Callable:
    def wrapper() -> None:
        t = Table()

        warning_cell = "A20:A21"
        t.write(warning_cell,
                [["Внимание, таблица обновляется"],
                 ["Пожалуйста, не совершайте резких движений"]])
        last_row_char = "G"
        try:
            last_row_char = func(t)
            t.write("A22:A23", [["Последнее обновление:"], [f"{datetime.now()}"[:-7]]])
            logger.info("Success.")
        except Exception as ex:
            t.write("A25:A26",
                    [[f"Произошла ошибка {ex}."],
                     [f"Пожалуйста, сообщите об этом {config.responsible}"]])
            logger.error(Exception.args)
            raise Exception
        finally:
            t.write(warning_cell, [[""], [""]])
            t.write(f"{config.table_alphabet[config.first_date_row_ind]}{config.loading_with_eyes_table_string_number}:"
                    f"{last_row_char}{config.loading_with_eyes_table_string_number}",

                    [[""] * (config.table_alphabet.index(last_row_char) - config.first_date_row_ind + 1)])

    return wrapper


@add_table_loading_signs
def main(table: Table) -> str:
    char_ind = "G"

    for char_ind in range(config.first_date_row_ind, len(config.table_alphabet)):
        cell_date = f"{config.table_alphabet[char_ind]}2:{config.table_alphabet[char_ind]}2"
        table_data = table.read([cell_date])
        if not table_data:
            break
        logic.check_data_and_write_info_to_spreadsheets(table_data, char_ind, table)

    last_using_row_char = config.table_alphabet[char_ind]
    return last_using_row_char


if __name__ == '__main__':
    config.get_spb_flag(sys.argv)
    main()
