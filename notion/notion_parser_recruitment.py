from collections import namedtuple
from datetime import datetime, timedelta
from pprint import pprint

import config
from notion.notion_parser import NotionParser
from notion.bool_converter import PropertiesConverterToBool
from loguru import logger


class NotionParserRecruitment(NotionParser):
    def __init__(self, start_day: datetime, end_day: datetime):
        super(NotionParserRecruitment, self).__init__()

        self.start_day: datetime = start_day
        self.end_day: datetime = end_day

        self.apply_filter_by_start_and_end_dates()
        logger.info(self.body)

        self.params_tuple = namedtuple("params_tuple",
                                       ("fio", "gs_done", "pp_done", "is_done", "t_done", "ex_done", "shsv_done"))

    def apply_filter_by_start_and_end_dates(self) -> None:

        self.body["filter"]["and"] = [
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

        if config.spb_flag:
            self.apply_filter_by_spb()

    def apply_filter_by_spb(self) -> None:
        prop_dict = {
            "property": "Тип",
            "multi_select": {"contains": "Очный Санкт-Петербург"}
        }
        self.body["filter"]["and"].append(prop_dict)

    def apply_filter_by_date_of_gs_invitation(self, info: list) -> list:  # TODO: TEST!
        """
        :param: list info like
                [{'ГС: дата приглашения': ['2022-03-20'], 'ИС: результат': 'Прошел',
                'ФИО': 'Блажиевский Артём Александрович', ...} {},]
        """

        ind_to_pop = self.get_indexes_of_popped_preps(info)

        for ind in ind_to_pop[::-1]:
            info.pop(ind)

        return info

    def get_indexes_of_popped_preps(self, prep_list):
        ind_to_pop = []

        for i, prep in enumerate(prep_list):
            logger.debug(prep["ФИО"])  # sometimes ФИО is "", it's ok, do not pop candidate
            date = self.get_max_date(date=prep["ГС: дата приглашения"])
            prep["ГС: дата приглашения"] = [date]
            date = datetime.strptime(date, "%Y-%m-%d")  # from string to datetime

            if (date - self.end_day).days > 0 or (self.start_day - date).days > 0:
                ind_to_pop.append(i)
                logger.info(f'{prep["ФИО"]}, {date=}')
        return ind_to_pop

    @staticmethod
    def get_max_date(date: list) -> str:
        for ind, day in enumerate(date):
            date[ind] = datetime.fromisoformat(day)
        return str(max(date))[:10]

    def get_fields_meaning(self) -> any((list, None)):
        """
        Get from self.db_info fields (which specified in config.field_names)
        and process the data in two filters (second_filter and bool_treatment).

        :return: list of dicts of candidates if there is something in self.db_info
                 None if no info in the field,
        """

        if not self.db_info:
            logger.error(f"{self.db_info=}")
            return []

        result = self.match_values_to_field_names_from_config_field_names()
        result = self.apply_filter_by_date_of_gs_invitation(result)
        result = PropertiesConverterToBool(result).convert()
        return result

    def match_values_to_field_names_from_config_field_names(self):
        result = [{} for _ in range(len(self.db_info))]

        for i in range(len(self.db_info)):
            for field in config.field_names.values():
                filed_meaning = self.find_field_meaning(i, field)
                result[i][field] = filed_meaning
        return result


if __name__ == '__main__':
    start = datetime(day=15, month=8, year=2021)
    end = datetime(day=31, month=8, year=2021)

    n = NotionParserRecruitment(start, end)
    n.read_database(config.CANDIDATES_DB_ID)
    print(n.get_fields_meaning())
