class PropertiesConverterToBool:

    def __init__(self, info):
        self.info = info
        self.prop = None

    def convert(self):
        for self.prop in self.info:
            self.check_does_exists_and_have_passed()
            self.check_does_exists_and_sth_there()
            self.check_other_cases()

        return self.info

    def check_does_exists_and_have_passed(self):
        for field_name in ("ИС: результат",
                           "ШСВ: результат",
                           ):
            if self.prop[field_name] and self.prop[field_name] == "Прошел":
                self.prop[field_name] = True
            else:
                self.prop[field_name] = False

    def check_does_exists_and_sth_there(self):
        for field_name in ("Т1",
                           "Т: пройдены",
                           "ГС: дата приглашения",
                           "ГС: дата прихода",
                           ):
            if self.prop[field_name]:
                self.prop[field_name] = True
            else:
                self.prop[field_name] = False

    def check_other_cases(self):
        if self.prop["ПП: результат"] and "Пройдена" in self.prop["ПП: результат"]:
            self.prop["ПП: результат"] = True
        else:
            self.prop["ПП: результат"] = False

        if self.prop["Этап"] and self.prop["Этап"] == "Вышел на занятия":
            self.prop["Этап"] = True
        else:
            self.prop["Этап"] = False

        param = self.prop["Э: результат"]
        if param:
            self.prop["Э: пришёл"] = True
            if param == "Пересдача":
                self.prop["Э: пришёл"] = False
                self.prop["Э: результат"] = False
