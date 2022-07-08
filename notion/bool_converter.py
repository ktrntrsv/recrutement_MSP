def convert(info):
    for prop in info:
        check_does_exists_and_have_passed(prop)
        check_does_exists_and_sth_there(prop)
        check_other_cases(prop)

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
    if prop["ПП: результат ₓ"] and "Пройдена" in prop["ПП: результат ₓ"]:
        prop["ПП: результат ₓ"] = True
    else:
        prop["ПП: результат ₓ"] = False

    if prop["Этап ₓ"] and prop["Этап ₓ"] == "Вышел на занятия":
        prop["Этап ₓ"] = True
    else:
        prop["Этап ₓ"] = False

    prop["Э: пришёл ₓ"] = False
    param = prop["Э: результат ₓ"]
    if param:
        prop["Э: пришёл ₓ"] = True
        if param == ["Пересдача"]:
            prop["Э: пришёл ₓ"] = False
            prop["Э: результат ₓ"] = False
