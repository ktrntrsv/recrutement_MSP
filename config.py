import os
import string
from dotenv import load_dotenv

load_dotenv()
NOTION_BOT_TOKEN = os.getenv('NOTION_BOT_TOKEN')

responsible = "Бондаревой Даше."  # в дательном падеже
CANDIDATES_DB_ID = "88db000781d54a7abadeda91722489db"
loading_with_eyes_table_string_number = "23"


def get_letters_for_column_names() -> list:
    """
    return ['A', 'B', 'C', 'D', 'E', 'F' ... 'AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG'...]
    """
    s = list(string.ascii_uppercase)

    for i in string.ascii_uppercase:
        for j in string.ascii_uppercase:
            s.append(i + j)
    return s


departments = {"mshp": None,
               "msk": ("Профсоюзная", "Проспект Мира", "ВШЭ", "Яндекс", "Физтехпарк"),
               "spb": ("Санкт-Петербург", "Новочеркасская", "Приморский"),
               "mytishchi": ("Мытищи",),
               "vk": ("Дистанционно",)
               }

table_alphabet = get_letters_for_column_names()

count_of_single_stages = 10
count_of_separated_stages = 4

order_stages = (
    "gs_invitation_date",
    "gs_date_of_attendance",
    "gs_res",
    "pp_came",
    "pp_res",
    "is_came",
    "is_res",
    "t_taking",
    "t_res",
    "ex_came",

    "ex_res_prep",
    "shsv_came_prep",
    "shsv_res_prep",
    "does_conduct_lessons_prep",

    "ex_res_ass",
    "shsv_came_ass",
    "shsv_res_ass",
    "does_conduct_lessons_ass",
)

field_names = {
    "fio": "ФИО",
    "subjects": "ГС: Может вести ₓ",
    "departments": "Отделения ₓ",

    "gs_invitation_date": "ГС: дата приглашения ₓ",
    "gs_date_of_attendance": "ГС: дата прихода ₓ",
    "gs_res": "Прошел ГС ₓ",
    "pp_came": "ПП: пришел",
    "pp_res": "ПП: результат ₓ",
    "is_came": "ИС: пришел",
    "is_res": "ИС: результат ₓ",
    "t_taking": "Т1 ₓ",
    "t_res": "Т: пройдены ₓ",
    "ex_came": "Э: пришёл",

    "ex_res_prep": "Э: результат ₓ",
    "shsv_came_prep": "ШСВ: пришел",
    "shsv_res_prep": "ШСВ: результат ₓ",
    "does_conduct_lessons_prep": "Этап ₓ",

    "ex_res_ass": "Э: результат ₓ",
    "shsv_came_ass": "ШСВ: пришел ₓ",
    "shsv_res_ass": "ШСВ: результат ₓ",
    "does_conduct_lessons_ass": "Этап ₓ",

    "self-denial": "Статус ₓ"
}
