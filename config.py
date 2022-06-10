import os
from dotenv import load_dotenv
import logic

load_dotenv()

data_sheets_list_name = "Actual!"

responsible = "Тарасовой К."  # в дательном падеже

NOTION_BOT_TOKEN = os.getenv('NOTION_BOT_TOKEN')

# databases ids
CANDIDATES_DB_ID = "88db000781d54a7abadeda91722489db"
GROUP_INTERVIEWS_DB_ID = "15019c70586a413b80e174e789d4599f"
SUBJECT_CHECK_DB_ID = "3c47f3ff156547cdb578dbf916173ec4"
INDIVIDUAL_INTERVIEW_DB_ID = "e397cd52ab23448ca63bd703cddb61bd"
TRAININGS_DB_ID = "3d7e64da3c0d4932bda78288d3f765e5"
EXAMS_DB_ID = "5df8f2d398e945e5b542a8ba1d7a3073"

loading_str = "17"
table_alphabet = logic.get_column_names()
first_date_row_ind = table_alphabet.index("H")

order_stages = (
    "gs_date",
    "gs_res",
    "pp_res",
    "is_res",
    "t_taking",
    "t_res",
    "ex_res",
    "shsv_res",
    "etap_res",
)


field_names = {
    "fio": "ФИО",
    "gs_date": "ГС: дата приглашения",
    "gs_res": "Прошел ГС",
    "pp_res": "ПП: результат",
    "is_res": "ИС: результат",
    "t_taking": "Т1",
    "t_res": "Т: пройдены",
    "ex_res": "Э: прошёл?",
    "shsv_res": "ШСВ: результат",
    "etap_res": "Этап",
    "self-denial": "Статус"
}
