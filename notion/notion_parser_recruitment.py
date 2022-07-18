from collections import namedtuple
from datetime import datetime, timedelta
from pprint import pprint

import config
from notion.notion_parser import NotionParser
import notion.bool_converter as bool_converter
from loguru import logger


class NotionParserRecruitment(NotionParser):
    def __init__(self, start_day: datetime, end_day: datetime):
        super(NotionParserRecruitment, self).__init__()

        self.start_day: datetime = start_day
        self.end_day: datetime = end_day

        self.apply_filter_by_start_and_end_dates()

    def apply_filter_by_start_and_end_dates(self) -> None:

        self.body["filter"]["and"] = [
            {
                "property": "ГС: дата приглашения ₓ", "rollup": {
                "any": {
                    "date": {"on_or_after": str(self.start_day)}
                }
            }
            },
            {
                "property": "ГС: дата приглашения ₓ", "rollup": {
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
            "property": "Тип ₓ",
            "multi_select": {"contains": "Очный Санкт-Петербург"}
        }
        self.body["filter"]["and"].append(prop_dict)

    def get_filtered_fields_meaning(self) -> any((list, None)):
        """
        Get from self.db_info fields (which specified in config.field_names)
        and process the data in two filters (second_filter and bool_treatment).

        :return: list of dicts of candidates if there is something in self.db_info
                 None if no info in the field,
        """

        if not self.db_info:
            return []

        result = self.get_fields_meaning_for_every_candidate()
        result = self.apply_filter_by_date_of_gs_invitation(result)
        result = bool_converter.convert(result)
        return result

    def get_fields_meaning_for_every_candidate(self):
        result = [{} for _ in range(len(self.db_info))]

        for candidate_ind in range(len(self.db_info)):
            for field in config.field_names.values():
                filed_meaning = self.find_field_meaning(candidate_ind, field)
                result[candidate_ind][field] = filed_meaning
            logger.debug(f"[{result[candidate_ind]['ФИО']}]: {result[candidate_ind]}")
        return result

    def apply_filter_by_date_of_gs_invitation(self, info: list) -> list:
        """
        :param: list info like
                [{'ГС: дата приглашения': ['2022-03-23'], 'ИС: результат': 'Прошел',
                'ФИО': 'Поповченко Поп Поповович', ...} {},]
        """

        ind_to_pop = self.get_indexes_of_popped_preps(info)
        self.fix_coming_date(info)

        for ind in ind_to_pop[::-1]:
            info.pop(ind)

        return info

    def get_indexes_of_popped_preps(self, prep_list):
        ind_to_pop = []

        for i, prep in enumerate(prep_list):
            # logger.debug(prep["ФИО"])  # sometimes ФИО is "", it's ok, do not pop candidate
            date = self.get_max_date(date=prep["ГС: дата приглашения ₓ"])
            prep["ГС: дата приглашения ₓ"] = [date]
            date = datetime.strptime(date, "%Y-%m-%d")  # from string to datetime

            if (date - self.end_day).days > 0 or (self.start_day - date).days > 0:
                ind_to_pop.append(i)
        return ind_to_pop

    @staticmethod
    def get_max_date(date: list) -> any((None, str)):
        if not date:
            return None
        for ind, day in enumerate(date):
            date[ind] = datetime.fromisoformat(day)
        return str(max(date))[:10]

    @staticmethod
    def fix_coming_date(prep_list):
        for i, prep in enumerate(prep_list):
            if prep["ГС: дата прихода ₓ"] and \
                    prep["ГС: дата прихода ₓ"] != prep["ГС: дата приглашения ₓ"]:
                prep["ГС: дата прихода ₓ"] = []
