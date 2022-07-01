import os
from dotenv import load_dotenv
import string
from loguru import logger

load_dotenv()
NOTION_BOT_TOKEN = os.getenv('NOTION_BOT_TOKEN')

data_sheets_list_name = "Вся школа!"
data_sheets_list_name_spb = "Питер!"
responsible = "Тарасовой Катерине."  # в дательном падеже
CANDIDATES_DB_ID = "88db000781d54a7abadeda91722489db"
loading_with_eyes_table_string_number = "20"
prep_assist_forked_columns_count = 3

spb_flag = False


def get_spb_flag(arguments: list) -> None:
    global spb_flag
    global data_sheets_list_name
    if not len(arguments) >= 2:
        logger.info("Spb_flag = False")

        spb_flag = False
        return
    if arguments[1] == "--spb":
        logger.info("Spb_flag = True")

        spb_flag = True
        data_sheets_list_name = data_sheets_list_name_spb


def get_letters_for_column_names() -> list:
    """
    return ['A', 'B', 'C', 'D', 'E', 'F' ... 'AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG'...]
    """
    s = list(string.ascii_uppercase)

    for i in string.ascii_uppercase:
        for j in string.ascii_uppercase:
            s.append(i + j)
    return s


table_alphabet = get_letters_for_column_names()
first_date_row_ind = table_alphabet.index("H")


order_stages = (
    "gs_invitation_date",
    "gs_date_of_attendance",
    "gs_res",
    "pp_res",
    "is_res",
    "t_taking",
    "t_res",
    "ex_came",

    "ex_res_prep",
    "shsv_res_prep",
    "does_conduct_lessons_prep",

    "ex_res_ass",
    "shsv_res_ass",
    "does_conduct_lessons_ass",
)

field_names = {
    "fio": "ФИО",
    "gs_invitation_date": "ГС: дата приглашения",
    "gs_date_of_attendance": "ГС: дата прихода",
    "gs_res": "Прошел ГС",
    "pp_res": "ПП: результат",
    "is_res": "ИС: результат",
    "t_taking": "Т1",
    "t_res": "Т: пройдены",
    "ex_came": "Э: пришёл",

    "ex_res_prep": "Э: результат",
    "shsv_res_prep": "ШСВ: результат",
    "does_conduct_lessons_prep": "Этап",

    "ex_res_ass": "Э: результат",
    "shsv_res_ass": "ШСВ: результат",
    "does_conduct_lessons_ass": "Этап",

    "self-denial": "Статус"
}
