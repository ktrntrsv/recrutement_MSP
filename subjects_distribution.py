from table_scaner import Table
from logger_file import logger
from collections import Counter

distribution = {"preps": Counter(), "assists": Counter()}

main_subjects = (
    "Python", "Python (младшие классы)", "C++", "Scratch", "C#", "Компьютерные сети", "Дискретная математика")

junior_subjects = (
    "MarkOnline", "Алгоритмика", "Micro:bit", "Математика (младшие классы)", "Базовая компьютерная подготовка",
    "Scratch")
middle_subjects = (
    "Figma", "Python", "Python (младшие классы)", "PyGame", "Основы олимпиадной математики", "Форматы данных")
senior_subjects = (
    "C++", "ЕГЭ по информатике", "ЕГЭ по математике", "ОГЭ по информатике", "ОГЭ по математике", "C#",
    "Компьютерные сети",
    "Дискретная математика", "Machine Learning")


def get_subj_distribution(data):
    # for prep in data:
    #     if prep["Э: результат ₓ"]:
    #         logger.error(prep)

    passed_exam_preps = []
    passed_exam_assists = []
    if not data:
        return
    for prep in data:
        if not prep["Э: результат ₓ"] or prep["Э: результат ₓ"] == ["Отказ"]:
            continue
        if "+ Преподаватель" in prep["Э: результат ₓ"] and prep["ШСВ: результат ₓ"] != "Не прошел" and prep[
            "Статус ₓ"] != "Самоотказ" and prep["Статус ₓ"] != "Отказ":
            passed_exam_preps.append(prep["ГС: Может вести ₓ"])
            logger.error(prep["ФИО"])
        elif "+ Ассистент" in prep["Э: результат ₓ"] and prep["ШСВ: результат ₓ"] != "Не прошел" and prep[
            "Статус ₓ"] != "Самоотказ" and prep["Статус ₓ"] != "Отказ":
            passed_exam_assists.append(prep["ГС: Может вести ₓ"])
            logger.error(prep["ФИО"], prep["ГС: Может вести ₓ"])

    count_subjects(passed_exam_preps, passed_exam_assists)
    count_grades(passed_exam_preps, passed_exam_assists)


def count_subjects(preps_subj, assists_subj):
    global distribution

    for subj in main_subjects:
        for prep in preps_subj:
            if prep and subj in prep:
                distribution["preps"][subj] += 1
        for assist in assists_subj:
            if assist and subj in assist:
                distribution["assists"][subj] += 1

    for i in "preps", "assists":
        distribution[i]["Python"] += distribution[i]["Python (младшие классы)"]
        distribution[i]["Python (младшие классы)"] = 0


def count_grades(preps_subj, assists_subj):
    count("preps", preps_subj)
    count("assists", assists_subj)


def count(job_title: str, subjects):
    global distribution
    for prep in subjects:
        if not prep:
            continue

        cache_jun, cache_mid, cache_sen = None, None, None

        for s in prep:
            if prep != cache_jun and s in junior_subjects:
                distribution[job_title]["junior"] += 1
                logger.error(f"{prep} -- jun")
                cache_jun = prep
                continue
            elif prep != cache_mid and s in middle_subjects:
                distribution[job_title]["middle"] += 1
                logger.error(f"{prep} -- miiddle")
                cache_mid = prep
                continue
            elif prep != cache_sen and s in senior_subjects:
                distribution[job_title]["senior"] += 1
                logger.error(f"{prep} -- senior")
                cache_sen = prep
                continue


def write_subj_distribution(table: Table):
    result = []

    for grade in "junior", "middle", "senior":
        result.append([distribution["preps"][grade],
                       distribution["assists"][grade]])

    subjs = ("Python", "C++", "C#", "Scratch", "Компьютерные сети", "Дискретная математика")
    for subj in subjs:
        result.append([distribution["preps"][subj],
                       distribution["assists"][subj]])
    table.write("DO9:DP17", result)
