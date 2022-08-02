from notion.notion_parser_recruitment import \
    NotionParserRecruitment
from typing import Callable
from datetime import datetime, timedelta

import config
from config import order_stages, count_of_separated_stages, count_of_single_stages
from table_scaner import Table
from stages_counter import StagesCounter
from logger_file import logger


def add_table_loading_signs(func: Callable) -> Callable:
    def wrapper() -> None:
        t = Table()

        warning_cell = "A24:A25"

        t.write("A26:A27", ["", ""])  # request limit google warning was logged here
        t.write(warning_cell,
                [["Внимание, таблица обновляется"],
                 ["Пожалуйста, не совершайте резких движений"]])
        last_row_char = "G"
        try:
            last_row_char = func(t)
            t.write(warning_cell, [["Последнее обновление:"], [f"{datetime.now() + timedelta(hours=3)}"[:-10]]])
            logger.info("Success.")
        except Exception as ex:
            t.write(warning_cell,
                    [[f"Произошла ошибка {ex}."],
                     [f"Пожалуйста, сообщите об этом {config.responsible}"]])
            logger.error(Exception.args)
            raise Exception
        finally:
            t.write(f"{config.table_alphabet[config.first_date_row_ind]}{config.loading_with_eyes_table_string_number}:"
                    f"{last_row_char}{config.loading_with_eyes_table_string_number}",

                    [[""] * (config.table_alphabet.index(last_row_char) - config.first_date_row_ind + 1)])

    return wrapper


def table_date_to_datetime_converter(date: str):
    """
    Parse table string date (ex: "12.03-19.03.22") to two datetime variables

    :param str date: date string from table "dd.mm-dd.mm.yy"
    :return: tuple(datetime[start], datetime[end])
             or datetime.now(), datetime.now()
    """

    if not date:
        return datetime.now(), datetime.now()

    try:
        start, end = date.split("-")
        d1, m1 = map(int, start.split("."))
        d2, m2, y = map(int, end.split("."))

        y += 2000

        start = datetime(day=d1, month=m1, year=y)
        end = datetime(day=d2, month=m2, year=y)

        return start, end

    except ValueError:
        return None


def get_period_info_from_notion(start: datetime, end: datetime) -> any((list, None)):
    n = NotionParserRecruitment(start_day=start, end_day=end)
    n.read_database(config.CANDIDATES_DB_ID)
    fields_data = n.get_filtered_fields_meaning()
    if not fields_data:
        logger.debug("No fields data")
        return
    return fields_data


def append_doubled_stages(final_numbers, counted_separated_stages):
    separated_couples = tuple(zip(
        order_stages[-count_of_separated_stages * 2:-count_of_separated_stages],
        order_stages[-count_of_separated_stages:]
    ))
    """
    Example:
    (("ex_res_prep", "ex_res_ass"),
    ("shsv_came_prep", "shsv_came_ass"),
    ("shsv_res_prep", "shsv_res_ass"),
    ("does_conduct_lessons_prep", "does_conduct_lessons_ass"))
    """

    for prp_stage, ass_stage in separated_couples:
        final_numbers.append([counted_separated_stages[prp_stage],
                              counted_separated_stages[ass_stage]])


def get_list_for_zero_table_column():
    zero_list = []
    for _ in range(len(order_stages) - count_of_separated_stages + 1):
        zero_list.append(["0"])

    separated_stages_indexes = tuple(
        range(
            count_of_single_stages + count_of_separated_stages))[count_of_single_stages:

                                                                 count_of_single_stages +
                                                                 count_of_separated_stages]

    for i in separated_stages_indexes:
        zero_list[i].append("0")
    return zero_list


def glue_single_separated_self_denial_numbers(fields_data: list) -> list:
    counted_single_stages, counted_separated_stages, self_denial = StagesCounter(fields_data).count_for_all()
    if not counted_single_stages:
        return get_list_for_zero_table_column()
    pre_final_numbers = list(sorted(counted_single_stages.values(), reverse=True))
    final_numbers = []
    for i in pre_final_numbers:
        final_numbers.append([i])

    append_doubled_stages(final_numbers, counted_separated_stages)

    final_numbers.append([self_denial])
    return final_numbers


def check_data_and_write_info_to_spreadsheets(table_data, char_ind, table):
    if table_data and \
            table_data[0] and \
            "values" in table_data[0].keys() and \
            table_data[0]["values"][0][0] and \
            table_date_to_datetime_converter(table_data[0]["values"][0][0]):
        write_info_to_spreadsheets(table_data, char_ind, table)


def visualize_loading(func):
    def wrapped(table_data, char_ind, table):
        loading_cell = config.table_alphabet[char_ind + 1] + config.loading_with_eyes_table_string_number
        table.write(loading_cell, [["👀"]])

        func(table_data, char_ind, table)

        table.write(loading_cell, [["✔️"]])

    return wrapped


@visualize_loading
def write_info_to_spreadsheets(table_data, char_ind, table):
    start_date, end_date = table_date_to_datetime_converter(table_data[0]["values"][0][0])
    logger.info(f"[date] {str(start_date)[:10]} - {str(end_date)[:10]}")

    cell_range = config.table_alphabet[char_ind + 1] + "5:" + \
                 config.table_alphabet[char_ind + 2] + f"{5 + len(order_stages)}"

    data = get_period_info_from_notion(start_date, end_date)
    data = glue_single_separated_self_denial_numbers(data)

    table.write(cell_range, data)

