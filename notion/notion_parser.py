from requests import request

import config
from loguru import logger
from abc import ABC, abstractmethod
from json import dump


class NotionParser:

    def __init__(self):
        self.token: str = config.NOTION_BOT_TOKEN
        self.headers: dict = {
            "Authorization": "Bearer " + self.token,
            "Content-Type": "application/json",
            "Notion-Version": "2021-05-13",
        }
        self.db_info = None
        self.body = {"filter": {}}
        # self.body should look sth like this
        #
        # self.body = {"filter":
        #                  {"property": "Telegram ID", "number": {"equals": self.prep_id}},
        #              }

    def read_database(self, database_id: str) -> None:
        """
        Self.db_info will be like
        [{'object': 'page', <...> 'properties': {'Т1': {'id': '"=A9', 'type': 'relation', 'relation': [{......}]}}}]
        """
        read_url = f"https://api.notion.com/v1/databases/{database_id}/query"

        res = request("POST", read_url, headers=self.headers, json=self.body)
        response = res.json()

        if res.status_code != 200:
            logger.debug(f"{response}")
            self.db_info = []
            return
        if not response["results"]:
            logger.debug("No response result")
            self.db_info = []
            return

        self.db_info = response["results"]

    def find_field_meaning(self, candidate_index: int, field: str) -> any((None, str, int, float, list)):
        """
        Now method can parse
        1. Title
        2. Text
        3. Rollup
            1. Select
            2. Checkbox
            3. Date
            4. Formula (string)
        4. Select
        5. Number
        6. Formula
        """

        info = self.db_info[candidate_index]["properties"]
        # info = {'Т1': {'id': '"=A9', 'type': 'relation', 'relation': [{'id': '0c0382ab-dae0-4e2e-aefb-6929cf4ca3a0'}]}

        if not info:
            logger.debug("No data")
            return None
        if field not in info.keys():
            return None
        field_type = info[field]["type"]

        if field_type == "rollup":  # rollup
            if info[field]["rollup"]["array"]:

                rollup_content = info[field]["rollup"]["array"][0]

                if rollup_content["type"] == "select" and \
                        rollup_content["select"]:  # if field type -- select if field is not empty
                    return rollup_content["select"]["name"]

                elif rollup_content["type"] == "checkbox":  # checkbox check
                    return rollup_content["checkbox"]

                elif rollup_content["type"] == "date":  # date check
                    result = []
                    for i in range(len(info[field]["rollup"]["array"])):
                        if info[field]["rollup"]["array"][i]["date"]:
                            result.append(info[field]["rollup"]["array"][i]["date"]["start"][:10])
                    return result

                elif rollup_content["type"] == "formula":  # formula string
                    if rollup_content["formula"]["type"] == "string":
                        return rollup_content["formula"]["string"].strip()

            return None

        elif field_type == "relation":
            if info[field]["relation"] and len(info[field]["relation"]) > 0:
                return info[field]["relation"][0]["id"]
            else:
                return None

        elif field_type == "rich_text":  # text
            if info[field]["rich_text"] and "plain_text" in \
                    info[field]["rich_text"][0]:
                return info[field]["rich_text"][0]["plain_text"]
            return None

        elif field_type == "title":
            if info[field]["title"]:
                return info[field]["title"][0]["plain_text"]
            return None

        elif field_type == "select":  # select, if field is empty, it will not be sent
            return info[field]["select"]["name"]

        elif field_type == "multi_select" and \
                info[field]["multi_select"]:

            # logger.debug(info[field]["multi_select"])
            multi = []
            for select in info[field]["multi_select"]:
                multi.append(select["name"])
            return multi

        elif field_type == "number":  # number, if field is empty, it will not be sent
            return info[field]["number"]

        if field_type == "formula":  # it works for strings and boolean
            formula_type = info[field][field_type]["type"]
            return info[field][field_type][formula_type]