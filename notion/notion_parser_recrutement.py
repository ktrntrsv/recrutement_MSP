from collections import namedtuple
from datetime import datetime, timedelta
from pprint import pprint

import config
from notion.notion_parser import NotionParser
from logger_file import logger


class NotionParserRecrutement(NotionParser):
    def __init__(self, start_day: datetime, end_day: datetime):
        super(NotionParserRecrutement, self).__init__()

        self.start_day: datetime = start_day
        self.end_day: datetime = end_day

        self.body: dict = {}
        self.get_week_filter()

        self.params_tuple = namedtuple("params_tuple",
                                       ("fio", "gs_done", "pp_done", "is_done", "t_done", "ex_done", "shsv_done"))

    def get_week_filter(self) -> None:
        """
        Create filter for request to Notion
        dict self.body: the body of request
        :return: None
        """

        self.body = {
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

        if config.spb_flag:
            self.append_spb_filter()


    def append_spb_filter(self):
        prop_dict = {
            "property": "Тип",
            "multi_select": {"contains": "Очный Санкт-Петербург"}
        }
        self.body["filter"]["and"].append(prop_dict)

    def second_filter(self, info: list) -> list:  # TODO: TEST!
        """
        Return list with only suitable by date of invitation candidates.

        There are two and more dates in "ГС: дата приглашения" sometimes.
        We should take only last of them.
        The method takes info, takes the last date and leave only this one in "ГС: дата приглашения".
        If the date not in required time range, func pop this candidate

        :param: list info like
                [{'ГС: дата приглашения': ['2022-03-20'], 'ИС: результат': 'Прошел',
                'ФИО': 'Блажиевский Артём Александрович', ...} {},]
        :return: list info (filtered)
        """
        ind_to_pop = []
        for i, prep in enumerate(info):
            logger.debug(prep["ФИО"])  # sometimes ФИО is "", it's ok, do not pop candidate
            date = prep["ГС: дата приглашения"]
            for ind, day in enumerate(date):
                date[ind] = datetime.fromisoformat(day)
            date = str(max(date))[:10]

            prep["ГС: дата приглашения"] = [date]
            date = datetime.strptime(date, "%Y-%m-%d")  # from string to datetime

            if (date - self.end_day).days > 0 or (self.start_day - date).days > 0:
                ind_to_pop.append(i)
                logger.info(f'{prep["ФИО"]}, {date=}')

            # prep.pop("ГС: дата прихода", None)
        for ind in ind_to_pop[::-1]:
            info.pop(ind)
        return info

    def get_fields_meaning(self) -> any((list, None)):
        """
        Get from self.db_info fields (which specified in config.field_names)
        and process the data in two filters (second_filter and bool_treatment).

        :return: list of dicts of candidates if there is something in self.db_info
                 None if no info in the field,
        """

        if not self.db_info:
            logger.error(f"{self.db_info=}")
            return
        result = [{} for _ in range(len(self.db_info))]

        for i in range(len(self.db_info)):
            for field in config.field_names.values():
                filed_meaning = self.find_field_meaning(i, field)
                result[i][field] = filed_meaning
        result = self.second_filter(result)
        result = self.bool_treatment(result)
        return result

    @staticmethod
    def bool_treatment(info):
        """
        Convert properties to bool.

        :param: list[dict] info different means
        :return: list[dict] info bool means
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

            if prop["ГС: дата прихода"]:
                prop["ГС: дата прихода"] = True
            else:
                prop["ГС: дата прихода"] = False

            param = prop["Э: результат"]
            if param:
                prop["Э: пришёл"] = True
                if param == "Пересдача":
                    prop["Э: пришёл"] = False
                    prop["Э: результат"] = False

        return info


if __name__ == '__main__':
    start = datetime(day=15, month=8, year=2021)
    end = datetime(day=31, month=8, year=2021)

    n = NotionParserRecrutement(start, end)
    n.read_database(config.CANDIDATES_DB_ID)
    print(n.get_fields_meaning())
