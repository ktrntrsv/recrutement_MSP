from table_scaner import Table
from pprint import pprint
from datetime import datetime, timedelta
from notion.notion_parser_recrutement import NotionParserRecrutement
import config
import logic
from logger_file import logger


def notion_scan(start, end):
    n = NotionParserRecrutement(start_day=start, end_day=end)
    n.read_database(config.CANDIDATES_DB_ID)
    fields_data = n.get_fields_meaning()
    if not fields_data:
        logger.debug("No fields data")
        return
    return fields_data


def count_stages(fields_data) -> list:
    counted_stages, self_denial = logic.stages_counter(fields_data=fields_data)
    if not counted_stages:
        return [["0"]] * (len(config.order_stages) + 1)
    pre_final_numbers = list(sorted(counted_stages.values(), reverse=True))
    logger.debug(f"{pre_final_numbers=}")
    final_numbers = []
    for i in pre_final_numbers:
        final_numbers.append([i])
    final_numbers.append([self_denial])
    # logger.debug(final_numbers)
    return final_numbers


def table_warning(func):
    def wrapper():
        t = Table()

        warning_cell = "A20:A21"
        t.write(warning_cell,
                [["Внимание, таблица обновляется."],
                 ["Пожалуйста, не совершайте резких движений."]])
        last_row_char = "G"
        try:
            last_row_char = func(t)
            t.write("A18:A19", [["Последнее обновление:"], [f"{datetime.now()}"[:-7]]])
            logger.info("Done.")
        except Exception:
            t.write(warning_cell,
                    [["Произошла какая-то ошибка."],
                     [f"Пожалуйста, сообщите об этом {config.responsible}"]])
            logger.error(Exception.args)
            raise Exception
        finally:
            t.write(warning_cell, [[""], [""]])
            print(f"{config.first_date_row_ind=}")
            print(f"{config.table_alphabet.index(last_row_char)=}")

            t.write(f"{config.table_alphabet[config.first_date_row_ind]}{config.loading_str}:"
                    f"{last_row_char}{config.loading_str}",

                    [[""] * (config.table_alphabet.index(last_row_char) - config.first_date_row_ind + 1)])

    return wrapper


@table_warning
def main(table):
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
                logger.debug(f"[get] {start_date}-{end_date}")

                data = notion_scan(start_date, end_date)
                logger.info(f"{data=}")
                cell_range = config.table_alphabet[char_ind + 1] + "4:" + \
                             config.table_alphabet[char_ind + 1] + f"{4 + len(config.order_stages)}"
                table.write(cell_range, count_stages(data))
                table.write(loading_cell, [["✅"]])

        else:
            break
    return last_row_char


if __name__ == '__main__':
    main()
