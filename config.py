import os
from dotenv import load_dotenv
import string
from logger_file import logger

load_dotenv()
NOTION_BOT_TOKEN = os.getenv('NOTION_BOT_TOKEN')

data_sheets_list_name = "Actual!"
data_sheets_list_name_spb = "Питер!"
responsible = "Тарасовой К."  # в дательном падеже
loading_str = "20"  # string with eyes  👀 during loading
forked_columns_count = 3  # how many parameters with an assistant/prep separation

spb_flag = False


def get_spb_flag(arguments: list) -> None:
    """
    :param arguments: list like ['test.py', '--sbp']
    :return: True if it is a running for Sbp (there is an --sbp arg in terminal)
    """
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
    "etap_res_ass",  # does he conduct his lessons
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
