from collections import namedtuple
from datetime import datetime, timedelta
from pprint import pprint

import config
from notion.notion_parser import NotionParser
from logger_file import logger


class NotionParserRecrutement(NotionParser):
    def __init__(self, start_day, end_day):
        self.body = None
        self.start_day = start_day
        self.end_day = end_day
        super(NotionParserRecrutement, self).__init__()
        self.body = self.get_week_filter()
        self.params_tuple = namedtuple("params_tuple",
                                       ("fio", "gs_done", "pp_done", "is_done", "t_done", "ex_done", "shsv_done"))

    def get_week_filter(self):
        body = {
            "filter": {
                "and": [
                    {
                        "property": "ГС: дата приглашения", "rollup": {
                        "any": {
                            "date": {"on_or_after": str(self.start_day)}
                        }
                    }
                    },
                    {
                        "property": "ГС: дата приглашения", "rollup": {
                        "any": {
                            "date": {
                                "on_or_before": str(self.end_day + timedelta(days=1))}
                        }
                    }
                    },
                ]
            }
        }
        return body

    def second_filter(self, info):
        """
        There are two dates in "ГС: дата прихода" sometimes.
        We should take only last of them.

        :param: info like
        [{'ГС: дата прихода': ['2022-03-20'],
        'ИС: результат': 'Прошел',
        'ПП: результат': '❌ Не пройдена Junior ✅ Пройдена Middle ❌ Не пройдена Senior',
        'Прошел ГС': True,
        'Т: пройдены': True,
        'ФИО': 'Блажиевский Артём Александрович',
        'ШСВ: результат': 'Прошел',
        'Э: прошёл?': True}, ...
        {},
        {}]
        """
        # logger.debug(info)
        ind_to_pop = []
        for i, prep in enumerate(info):
            logger.debug(prep["ФИО"])
            date = prep["ГС: дата приглашения"]
            for ind, day in enumerate(date):
                date[ind] = datetime.fromisoformat(day)
            date = str(max(date))[:10]

            prep["ГС: дата приглашения"] = [date]
            date = datetime.strptime(date, "%Y-%m-%d")  # from string to datetime

            if (date - self.start_day).days > 7:
                ind_to_pop.append(i)
                logger.info(f'{prep["ФИО"]}, {date=}')
            # prep.pop("ГС: дата прихода", None)
        for ind in ind_to_pop[::-1]:
            info.pop(ind)
        return info

    def get_fields_meaning(self):
        """
        fields_list: list ["field_name 1", "field_name 2"...]
        """
        if not self.db_info:
            logger.error(f"{self.db_info=}")
            return
        result = [{} for i in range(len(self.db_info))]

        for i in range(len(self.db_info)):
            for field in config.field_names.values():
                filed_meaning = self.find_field_meaning(i, field)
                result[i][field] = filed_meaning
        result = self.second_filter(result)
        result = self.bool_treatment(result)
        return result

    def bool_treatment(self, info):
        """
        convert properties to bool
        """

        for prop in info:
            if prop["ИС: результат"] and prop["ИС: результат"] == "Прошел":
                prop["ИС: результат"] = True
            else:
                prop["ИС: результат"] = False

            if prop["ПП: результат"] and "Пройдена" in prop["ПП: результат"]:
                prop["ПП: результат"] = True
            else:
                prop["ПП: результат"] = False

            if prop["ШСВ: результат"] and prop["ШСВ: результат"] == "Прошел":
                prop["ШСВ: результат"] = True
            else:
                prop["ШСВ: результат"] = False

            if prop["Этап"] and prop["Этап"] == "Вышел на занятия":
                prop["Этап"] = True
            else:
                prop["Этап"] = False

            if prop["Т1"]:
                prop["Т1"] = True
            else:
                prop["Т1"] = False

            if prop["Т: пройдены"]:
                prop["Т: пройдены"] = True
            else:
                prop["Т: пройдены"] = False

            if prop["ГС: дата приглашения"]:
                prop["ГС: дата приглашения"] = True
            else:
                prop["ГС: дата приглашения"] = False

        return info

#
# start = datetime(day=6, month=3, year=2022)
# end = datetime(day=6, month=3, year=2022)

# n = NotionParserRecrutement(start, end)
# n.read_database(config.CANDIDATES_DB_ID)
# print(n.get_fields_meaning())
