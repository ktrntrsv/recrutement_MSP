from loguru import logger

from config import order_stages, count_of_separated_stages
from logic import _table_date_to_datetime_converter, get_period_info_from_notion, get_distribution_for_all_departments, \
    get_next_alph_letter, get_list_for_zero_table_column
from process_visualisation import visualize_loading
from stages_counter import StagesCounter
from table_scaner import Table


@visualize_loading
def count_and_write_info_to_column(info, column_letter, table: Table):
    start_date, end_date = _table_date_to_datetime_converter(info)
    logger.info(f"[date] {str(start_date)[:10]} - {str(end_date)[:10]}")

    data = get_period_info_from_notion(start_date, end_date)
    get_distribution_for_all_departments(data)

    counted_single_stages, counted_separated_stages, self_denial = StagesCounter(data).count_for_all()

    data = glue_single_separated_self_denial_numbers(counted_single_stages, counted_separated_stages, self_denial)

    cell_range = f"{column_letter}5:{get_next_alph_letter(column_letter)}{5 + len(order_stages)}"
    table.write(cell_range, data)


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
