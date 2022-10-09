import config
from config import order_stages, count_of_separated_stages, count_of_single_stages, table_alphabet
from datetime import datetime

from notion.notion_parser_recruitment import \
    NotionParserRecruitment
from subjects_distribution import SubjCounter
from logger_file import logger

cut_table_alphabet = []


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
    return cut_table_alphabet[cut_table_alphabet.index(letter) + 1]


def get_distribution_for_all_departments(data):
    for city in config.departments.keys():
        department = config.departments[city]
        SubjCounter().get_subj_distribution(data, department, city)


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


