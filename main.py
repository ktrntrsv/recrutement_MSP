import logic
from table_scaner import Table
from subjects_distribution import SubjCounter
from functools import partial
from list_name import get_list_name
from datetime import datetime
from logger_file import logger


def update_list(table: Table) -> None:
    row_with_dates = table.read([f"O2:ZZZ2"])[0]["values"][0]
    for column_letter, date in logic.get_sheets_to_write_generator(row_with_dates):
        logic.count_and_write_info_to_column(date, column_letter, table)
    SubjCounter().write_subj_distribution(table)


if __name__ == '__main__':
    check_prev_sem = False
    repeats = 1
    if 10 <= datetime.now().month <= 12 or 4 <= datetime.now().month <= 6:
        repeats = 2
    for _ in range(repeats):
        list_name = get_list_name(prev_sem=check_prev_sem)
        logger.info(f"Updating list {list_name}")
        loading_decorator = partial(logic.add_table_loading_signs, list_name=list_name)
        update_list_wrapped = loading_decorator(update_list)
        update_list_wrapped()
        check_prev_sem = not check_prev_sem
