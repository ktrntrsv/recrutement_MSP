import os
from dotenv import load_dotenv
import string

load_dotenv()
NOTION_BOT_TOKEN = os.getenv('NOTION_BOT_TOKEN')


data_sheets_list_name = "Actual!"
responsible = "Тарасовой К."  # в дательном падеже
loading_str = "20"  # string with eyes  👀 during loading
forked_columns_count = 3  # how many parameters with an assistant/prep separation


def get_column_names() -> list:
    """
    Get table's table name
    ['A', 'B', 'C', 'D', 'E', 'F' ... 'AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG'...]

    :return words list
    """
    s = list(string.ascii_uppercase)

    for i in string.ascii_uppercase:
        for j in string.ascii_uppercase:
            s.append(i + j)
    return s


table_alphabet = get_column_names()
first_date_row_ind = table_alphabet.index("H")  # first row with date


# databases ids
CANDIDATES_DB_ID = "88db000781d54a7abadeda91722489db"
GROUP_INTERVIEWS_DB_ID = "15019c70586a413b80e174e789d4599f"
SUBJECT_CHECK_DB_ID = "3c47f3ff156547cdb578dbf916173ec4"
INDIVIDUAL_INTERVIEW_DB_ID = "e397cd52ab23448ca63bd703cddb61bd"
TRAININGS_DB_ID = "3d7e64da3c0d4932bda78288d3f765e5"
EXAMS_DB_ID = "5df8f2d398e945e5b542a8ba1d7a3073"


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
    "etap_res_prep",

    "ex_res_ass",
    "shsv_res_ass",
    "etap_res_ass",  # вышел ли на занятия
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
    "etap_res_prep": "Этап",

    "ex_res_ass": "Э: результат",
    "shsv_res_ass": "ШСВ: результат",
    "etap_res_ass": "Этап",

    "self-denial": "Статус"
}
