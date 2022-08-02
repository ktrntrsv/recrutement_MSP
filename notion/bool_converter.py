def convert(info):
    for prop in info:
        check_other_cases(prop)
        check_does_exists_and_have_passed(prop)
        check_does_exists_and_sth_there(prop)

    return info


def check_does_exists_and_have_passed(prop):
    for field_name in ("ИС: результат ₓ",
                       "ШСВ: результат ₓ",
                       ):
        if prop[field_name] and prop[field_name] == "Прошел":
            prop[field_name] = True
        else:
            prop[field_name] = False


def check_does_exists_and_sth_there(prop):
    for field_name in ("Т1 ₓ",
                       "Т: пройдены ₓ",
                       "ГС: дата приглашения ₓ",
                       "ГС: дата прихода ₓ",
                       ):
        if prop[field_name]:
            prop[field_name] = True
        else:
            prop[field_name] = False


def check_other_cases(prop):
    check_is_come(prop)
    check_shsv_come(prop)
    check_pp_come(prop)
    check_pp_res(prop)
    check_exam(prop)
    check_stage(prop)


def check_is_come(prop):
    prop["ИС: пришел"] = False
    if prop["ИС: результат ₓ"]:
        prop["ИС: пришел"] = True


def check_shsv_come(prop):
    prop["ШСВ: пришел"] = False
    if prop["ШСВ: результат ₓ"]:
        prop["ШСВ: пришел"] = True


def check_pp_come(prop):
    prop["ПП: пришел"] = False
    if prop["ПП: результат ₓ"] and prop["ПП: результат ₓ"] != "⚠️ Не проверено":
        prop["ПП: пришел"] = True


def check_pp_res(prop):
    if prop["ПП: результат ₓ"] and "🟢" in prop["ПП: результат ₓ"]:
        prop["ПП: результат ₓ"] = True
    else:
        prop["ПП: результат ₓ"] = False


def check_exam(prop):
    prop["Э: пришёл"] = False
    param = prop["Э: результат ₓ"]
    if param:
        prop["Э: пришёл"] = True
        if param == ["Пересдача"]:
            prop["Э: пришёл"] = False
            prop["Э: результат ₓ"] = False


def check_stage(prop):
    if prop["Этап ₓ"] and prop["Этап ₓ"] == "Вышел на занятия":
        prop["Этап ₓ"] = True
    else:
        prop["Этап ₓ"] = False
