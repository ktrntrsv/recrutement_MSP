import sys

from datetime import datetime
import config
import logic
from loguru import logger


@logic.add_table_loading_signs
def main(table) -> str:
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
