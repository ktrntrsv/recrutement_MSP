from table_scaner import Table
from logger_file import logger
from collections import Counter, defaultdict


class SubjCounter:
    _instance = None

    def __new__(cls):  # singleton
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)
            cls.__init(cls._instance)
        return cls._instance

    def __init(self):
        self.distribution = {"mshp": {"preps": Counter(), "assists": Counter()},
                             "msk": {"preps": Counter(), "assists": Counter()},
                             "spb": {"preps": Counter(), "assists": Counter()},
                             "mytishchi": {"preps": Counter(), "assists": Counter()},
                             "vk": {"preps": Counter(), "assists": Counter()}
                             }
        self.main_subjects = (
            "Python 1 год", "Python 2 год", "C++ 1 год", "C++ 2 год", "C#", "Scratch", "Компьютерные сети",
            "Дискретная математика",
            "ЕГЭ по математике", "ЕГЭ по информатике")

        self.junior_subjects = (
            "MarkOnline", "Алгоритмика", "Micro:bit", "Математика (младшие классы)",
            "Базовая компьютерная подготовка",
            "Scratch")
        self.middle_subjects = (
            "Figma", "Python 1 год", "Python 2 год", "PyGame", "Основы олимпиадной математики",
            "Форматы данных")
        self.senior_subjects = (
            "C++ 1 год", "C++ 2 год", "ЕГЭ по информатике", "ЕГЭ по математике", "ОГЭ по информатике",
            "ОГЭ по математике", "C#",
            "Компьютерные сети",
            "Дискретная математика", "Machine Learning")

    def get_subj_distribution(self, data, departments: str, city: str):
        subjs_preps = []
        subjs_assists = []

        if not data:
            return

        for prep in data:
            if not prep["ГС: Может вести ₓ"]:
                continue
            if departments and prep["Отделения ₓ"] and (not set(prep["Отделения ₓ"]) & set(departments)):
                continue
            # logger.info(prep["ГС: Может вести ₓ"])
            if not prep["Э: результат ₓ"] or \
                    prep["Э: результат ₓ"] == ["Отказ"] or \
                    prep["ШСВ: результат ₓ"] == "Не прошел" or \
                    prep["Статус ₓ"] == "Самоотказ" or \
                    prep["Статус ₓ"] == "Отказ":
                continue
            if "+ Преподаватель" in prep["Э: результат ₓ"] or "+ Тьютор" in prep["Э: результат ₓ"]:
                subjs_preps.append(prep["ГС: Может вести ₓ"])
            elif "+ Ассистент" in prep["Э: результат ₓ"]:
                subjs_assists.append(prep["ГС: Может вести ₓ"])

        self.count_subjects(subjs_preps, subjs_assists, city)
        self.count_grades(subjs_preps, subjs_assists, city)

    def count_subjects(self, subjs_preps, subjs_assists, city):

        for subj in self.main_subjects:
            for subj_prep in subjs_preps:
                if subj_prep and subj in subj_prep:
                    self.distribution[city]["preps"][subj] += 1
                    logger.info(f"[added subj] {city} - {subj} - {subj_prep}")
            for subj_assist in subjs_assists:
                if subj_assist and subj in subj_assist:
                    self.distribution[city]["assists"][subj] += 1
                    logger.info(f"[added subj] {city} - {subj} - {subj_assist}")

    def count_grades(self, subjs_preps, subjs_assists, city):
        self.count("preps", subjs_preps, city)
        self.count("assists", subjs_assists, city)

    def count(self, job_title: str, subjects, city):
        for prep in subjects:
            if not prep:
                continue

            current_jun, current_mid, current_sen, current_spec = (None,) * 4
            for s in prep:
                if prep != current_jun and s in self.junior_subjects:
                    self.distribution[city][job_title]["junior"] += 1
                    current_jun = prep
                    continue
                elif prep != current_mid and s in self.middle_subjects:
                    self.distribution[city][job_title]["middle"] += 1
                    current_mid = prep
                    continue
                elif prep != current_sen and s in self.senior_subjects:
                    self.distribution[city][job_title]["senior"] += 1
                    current_sen = prep
                    continue
                elif prep != current_spec:
                    self.distribution[city][job_title]["spec_courses"] += 1
                    current_spec = prep

    def write_subj_distribution(self, table: Table):

        subjs = (
            "Python 1 год", "Python 2 год", "C++ 1 год", "C++ 2 год", "C#", "Scratch", "Компьютерные сети",
            "Дискретная математика", "ЕГЭ по математике",
            "ЕГЭ по информатике", "spec_courses")

        logger.info(self.distribution)

        sorted_sections = defaultdict(list)
        for section in ("junior", "middle", "senior") + subjs:
            for city in self.distribution.keys():
                for title in "preps", "assists":
                    sorted_sections[section].append(self.distribution[city][title][section])

        logger.info(f"{sorted_sections=}")

        sorted_sections = list(sorted_sections.values())
        table.write("DM5:DV18", sorted_sections)
