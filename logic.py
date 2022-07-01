from notion.notion_parser_recruitment import \
    NotionParserRecruitment
# from pprint import pprint
from datetime import datetime
from loguru import logger
import config


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
    fields_data = n.get_fields_meaning()
    if not fields_data:
        logger.debug("No fields data")
        return
    return fields_data


def is_self_denial(candidate):
    return candidate["Статус"] and candidate["Статус"] == "Самоотказ" or candidate["Статус"] == "Неизвестен"


def stages_counter(fields_data):  # TODO: REWRITE
    """
    Count all numbers from fields_data.

    :param fields_data: candidates dictionaries with all needed fields.
    :return: tuple(counter, self_denial). Counter is a dict with numbers and self_denial is an int number.
    """

    reversed_stages = tuple(reversed(config.order_stages[:8]))
    counter = dict.fromkeys(reversed_stages, 0)

    separated_stages = tuple(reversed(config.order_stages[8:]))
    separated_counter = dict.fromkeys(separated_stages, 0)

    self_denial = 0

    if not fields_data:
        return None, None, None
    for candidate in fields_data:
        # candidate = {'ФИО': 'Андреев Андрей Андреевич', 'ГС: приглашен': True, 'ГС: дата прихода': ['2022-04-24'] ...}
        stage_index = len(reversed_stages) - 1

        if is_self_denial(candidate):
            self_denial += 1
            continue
        if candidate["Статус"] and candidate["Статус"].startswith("На "):  # "На следующий год", "На лето 2022" etc
            continue

        logger.info(candidate)

        for index, stage in enumerate(reversed_stages):
            if candidate[config.field_names[stage]]:
                stage_index = index
                break

        for i in range(stage_index, len(reversed_stages)):
            counter[reversed_stages[i]] += 1

        if not candidate["Э: пришёл"]:
            continue

        for i, k in ("+ Ассистент", "ass"), ("+ Преподаватель", "prep"):
            if candidate["Э: результат"] == i and candidate["Этап"]:
                separated_counter[f"does_conduct_lessons_{k}"] += 1
                separated_counter[f"shsv_res_{k}"] += 1
                separated_counter[f"ex_res_{k}"] += 1
                break
            if candidate["Э: результат"] == i and candidate["ШСВ: результат"]:
                separated_counter[f"shsv_res_{k}"] += 1
                separated_counter[f"ex_res_{k}"] += 1
                break
            if candidate["Э: результат"] == i:
                separated_counter[f"ex_res_{k}"] += 1

    logger.info(f"{counter=}, {separated_counter=}")
    return counter, separated_counter, self_denial


def append_doubled_stages(final_numbers, counted_separated_stages):
    for prp_stage, ass_stage in (("ex_res_prep", "ex_res_ass"),
                                 ("shsv_res_prep", "shsv_res_ass"),
                                 ("does_conduct_lessons_prep", "does_conduct_lessons_ass")):
        final_numbers.append([counted_separated_stages[prp_stage],
                              counted_separated_stages[ass_stage]])


def get_list_for_zero_table_column():
    zero_list = []
    for _ in range(len(config.order_stages) - config.prep_assist_forked_columns_count + 1):
        zero_list.append(["0"])
    for i in 8, 9, 10:
        zero_list[i].append("0")
    return zero_list


def form_final_stages_numbers(fields_data) -> list:
    """
    :param fields_data:
    :return: list with final numbers
    """
    counted_single_stages, counted_separated_stages, self_denial = stages_counter(fields_data=fields_data)
    if not counted_single_stages:
        return get_list_for_zero_table_column()
    pre_final_numbers = list(sorted(counted_single_stages.values(), reverse=True))
    logger.debug(f"{pre_final_numbers=}")
    final_numbers = []
    for i in pre_final_numbers:
        final_numbers.append([i])

    append_doubled_stages(final_numbers, counted_separated_stages)

    final_numbers.append([self_denial])
    logger.info(final_numbers)
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

    data = get_period_info_from_notion(start_date, end_date)
    logger.info(f"{data=}")
    cell_range = config.table_alphabet[char_ind + 1] + "5:" + \
                 config.table_alphabet[char_ind + 2] + f"{5 + len(config.order_stages)}"
    table.write(cell_range, form_final_stages_numbers(data))

# start = datetime(day=15, month=4, year=2022)
# end = datetime(day=28, month=4, year=2022)
# logger.info(form_final_stages_numbers(notion_scan(start, end)))
