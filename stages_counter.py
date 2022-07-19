import config


class StagesCounter:
    def __init__(self, fields_data):
        self.fields_data = fields_data

        self.reversed_single_stages = tuple(reversed(config.order_stages[:config.count_of_single_stages]))
        self.single_counter = dict.fromkeys(self.reversed_single_stages, 0)

        self.separated_stages = tuple(config.order_stages[config.count_of_single_stages:])
        self.separated_counter = dict.fromkeys(self.separated_stages, 0)

        self.self_denial = 0

    def count_for_all(self):
        if not self.fields_data:
            return None, None, None

        for candidate in self.fields_data:
            # candidate = {'ФИО': 'Андреев Андрей Андреевич', 'ГС: приглашен': True, 'ГС: дата прихода': ['2022-04-24']}

            if candidate["Статус ₓ"] and candidate["Статус ₓ"] == "Самоотказ" \
                    or candidate["Статус ₓ"] == "Неизвестен":
                self.self_denial += 1
                continue

            if candidate["Статус ₓ"] and candidate["Статус ₓ"].startswith("На "):
                # Check, if "На следующий год", "На лето 2022" etc
                continue

            self.calculate_for_singles(candidate)
            self.calculate_for_separated(candidate)

        return self.single_counter, self.separated_counter, self.self_denial

    def calculate_for_singles(self, candidate):
        stage_index = len(self.reversed_single_stages) - 1

        for index, stage in enumerate(self.reversed_single_stages):
            if candidate[config.field_names[stage]]:
                stage_index = index
                break

        for i in range(stage_index, len(self.reversed_single_stages)):
            self.single_counter[self.reversed_single_stages[i]] += 1

    def calculate_for_separated(self, candidate) -> None:
        candidate_role = self.get_candidate_role(candidate)

        if not candidate_role:
            return None

        stage_index = len(self.separated_counter) - 1
        stages_for_role = self.get_role_stages(candidate_role)
        reversed_stages_for_role = tuple(reversed(stages_for_role))

        for index, stage in enumerate(reversed_stages_for_role):
            if candidate[config.field_names[stage]]:
                stage_index = index
                break

        for i in range(stage_index, len(stages_for_role)):
            self.separated_counter[reversed_stages_for_role[i]] += 1

    def get_role_stages(self, role: str) -> list:
        stages = []
        for stage in self.separated_stages:
            if stage.endswith(role):
                stages.append(stage)
        return stages

    @staticmethod
    def get_candidate_role(candidate) -> str:
        if candidate["Э: результат ₓ"] and \
                "+ Преподаватель" in candidate["Э: результат ₓ"]:
            return "prep"

        if candidate["Э: результат ₓ"] and \
                "+ Ассистент" in candidate["Э: результат ₓ"]:
            return "ass"
        return ""
