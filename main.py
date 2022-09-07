import sys

import config
import logic
from table_scaner import Table
from subjects_distribution import write_subj_distribution


@logic.add_table_loading_signs
def main(table: Table) -> None:
    row_with_dates = table.read([f"O2:ZZZ2"])[0]["values"][0]
    for column_letter, date in logic.get_sheets_to_write_generator(row_with_dates):
        logic.count_and_write_info_to_column(date, column_letter, table)
    write_subj_distribution(table)


if __name__ == '__main__':
    config.get_spb_flag(sys.argv)
    main()
