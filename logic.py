from typing import Callable, List
from datetime import datetime, timedelta

import config
from config import order_stages, count_of_separated_stages, count_of_single_stages, table_alphabet
from notion.notion_parser_recruitment import \
    NotionParserRecruitment
from subjects_distribution import get_subj_distribution
from table_scaner import Table
from stages_counter import StagesCounter
from logger_file import logger


def get_sheets_to_write_generator(row_content: list):
    start_ind = config.table_alphabet.index("O")
    global cut_table_alphabet
    cut_table_alphabet = table_alphabet[start_ind:len(row_content) + start_ind]
    rows_to_content = dict(zip(cut_table_alphabet, row_content))
    for column_letter, date in rows_to_content.items():
        if date \
                and "TOTAL" not in date \
                and _table_date_to_datetime_converter(date):
            yield get_next_alph_letter(column_letter), date


def get_next_alph_letter(letter):
    global cut_table_alphabet
    return cut_table_alphabet[cut_table_alphabet.index(letter) + 1]


def visualize_loading(func):
    def wrapped(info, column_letter, table):
        loading_cell = column_letter + config.loading_with_eyes_table_string_number
        table.write(loading_cell, [["👀"]])

        func(info, column_letter, table)

        table.write(loading_cell, [["✔️"]])

    return wrapped


@visualize_loading
def count_and_write_info_to_column(info, column_letter, table: Table):
    start_date, end_date = _table_date_to_datetime_converter(info)
    logger.info(f"[date] {str(start_date)[:10]} - {str(end_date)[:10]}")

    data = get_period_info_from_notion(start_date, end_date)
    get_subj_distribution(data)
    counted_single_stages, counted_separated_stages, self_denial = StagesCounter(data).count_for_all()

    data = glue_single_separated_self_denial_numbers(counted_single_stages, counted_separated_stages, self_denial)

    cell_range = f"{column_letter}5:{get_next_alph_letter(column_letter)}{5 + len(order_stages)}"
    table.write(cell_range, data)


def _table_date_to_datetime_converter(date: str) -> any((tuple, None)):
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


def glue_single_separated_self_denial_numbers(counted_single_stages, counted_separated_stages, self_denial) -> list:
    if not counted_single_stages:
        return get_list_for_zero_table_column()
    pre_final_numbers = list(sorted(counted_single_stages.values(), reverse=True))
    final_numbers = []
    for i in pre_final_numbers:
        final_numbers.append([i])

    append_doubled_stages(final_numbers, counted_separated_stages)

    final_numbers.append([self_denial])
    return final_numbers


def get_list_for_zero_table_column() -> list:
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


def add_table_loading_signs(func: Callable) -> Callable:
    def wrapper() -> None:
        t = Table()

        warning_cell = "A24:A25"

        t.write("A26:A27", [[""], [""]])  # request limit google warning was logged here
        t.write(warning_cell, [[""], [""]])
        try:
            func(t)
            t.write(warning_cell, [["Последнее обновление:"], [f"{datetime.now() + timedelta(hours=3)}"[:-10]]])
            logger.info("Success.")
        except Exception as ex:
            t.write(warning_cell,
                    [[f"Произошла ошибка {ex}."],
                     [f"Пожалуйста, сообщите об этом {config.responsible}"]])
            logger.error(Exception.args)
            raise Exception
        finally:
            global cut_table_alphabet
            t.write(
                f"{cut_table_alphabet[0]}{config.loading_with_eyes_table_string_number}:"
                f"{cut_table_alphabet[-1]}{config.loading_with_eyes_table_string_number}",

                [[""] * len(cut_table_alphabet)])

    return wrapper
