import sys

from table_scaner import Table
from pprint import pprint
from datetime import datetime, timedelta
import config
import logic
from logger_file import logger


def table_warning(func):
    """
    Decorator implements loading signs on the Google Table.

    :param func: main
    :return: func
    """

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
            t.write(f"{config.table_alphabet[config.first_date_row_ind]}{config.loading_str}:"
                    f"{last_row_char}{config.loading_str}",

                    [[""] * (config.table_alphabet.index(last_row_char) - config.first_date_row_ind + 1)])

    return wrapper


@table_warning
def main(table: Table) -> str:
    """
    Walking through the lines, checking if a writing is needed and writing if needed.
    Also added eyes for loading tracking.

    :param table for reading and writing
    :return: str last_row_char
    """
    end_date = datetime.now() - timedelta(weeks=1000)

    last_row_char = "G"

    for char_ind in range(config.first_date_row_ind, len(config.table_alphabet)):
        if (datetime.now() - end_date).days > 0:

            cell_date = f"{config.table_alphabet[char_ind]}2:{config.table_alphabet[char_ind]}2"
            table_data = table.read([cell_date])

            if not table_data:
                break

            if table_data and \
                    table_data[0] and \
                    "values" in table_data[0].keys() and \
                    table_data[0]["values"][0][0] and \
                    logic.table_date_to_datetime_converter(table_data[0]["values"][0][0]):
                loading_cell = config.table_alphabet[char_ind + 1] + config.loading_str
                table.write(loading_cell, [["👀"]])
                last_row_char = config.table_alphabet[char_ind + 1]

                start_date, end_date = logic.table_date_to_datetime_converter(table_data[0]["values"][0][0])
                # logger.info(f"[date] {str(start_date)[:10]} - {str(end_date)[:10]}")

                data = logic.notion_scan(start_date, end_date)
                # logger.info(f"{data=}")
                cell_range = config.table_alphabet[char_ind + 1] + "5:" + \
                             config.table_alphabet[char_ind + 2] + f"{5 + len(config.order_stages)}"
                # pprint(logic.form_final_stages_numbers(data))
                table.write(cell_range, logic.form_final_stages_numbers(data))
                table.write(loading_cell, [["✔️"]])
        else:
            break
    return last_row_char


if __name__ == '__main__':
    config.get_spb_flag(sys.argv)
    main()
