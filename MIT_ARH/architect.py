from expert import GPTExpert
import openai
import json


class GPTArchitect:
    def __init__(self, api_key, model):
        self.api_key = api_key
        self.model = model
        self.client = openai.OpenAI(api_key=api_key)

    def analyze_task(self, task):
        # Запрос к OpenAI для анализа задачи
        conversation = [
            {"role": "system", "content": "Побудь архитектором. Мне нужно, чтобы ты собрал команду в виде списка экспертов не более 3, которые могут создать Техническое задание для задачи. От тебя требуется только список JSON. Больше ничего писать не нужно. [{\"expert\": \"научный сотрудник\", \"task\": \"тут должна быть описана задача для него\", \"mainTask\": \"Тут должно быть краткое описание финальной задачи от пользователя\"}, {\"expert\": \"психолог\", \"task\": \"тут должна быть описана задача для него\", \"mainTask\": \"Тут должно быть краткое описание финальной задачи от пользователя\"}] и так далее для задачи."},
            {"role": "user", "content": task}
        ]
        response = self.client.chat.completions.create(model=self.model, messages=conversation)
        answer = response.choices[0].message.content
        print(answer)
        # Парсинг ответа и возврат списка экспертов
        try:
            experts_list = json.loads(answer)
            return experts_list
        except json.JSONDecodeError:
            print("Error JSON")
            return []

    def assemble_team(self, expertise_areas):
        team = []
        for area in expertise_areas:
            expert = GPTExpert(self.api_key, self.model, area)
            team.append(expert)
        return team

    def synthesize_solutions(self, solutions):
        # Формируем текст со всеми решениями экспертов
        solutions_text = "\n\n".join([f"Эксперт {solution['expert']}: {solution['solution']}" for solution in solutions])

        # Запрос к GPT для синтеза решений
        conversation = [
            {"role": "system", "content": "Проанализируйте следующие решения и предоставьте совместное решение:"},
            {"role": "user", "content": solutions_text}
        ]
        print(conversation)
        response = self.client.chat.completions.create(model=self.model, messages=conversation)
        synthesized_solution = response.choices[0].message.content

        return synthesized_solution

    def solve_task(self, task):
        experts_list = self.analyze_task(task)

        if not experts_list:
            return "Не удалось сформировать команду экспертов для задачи."

        solutions = []
        for expert_info in experts_list:
            expert = GPTExpert(self.api_key, self.model, expert_info["expert"])
            expert_task = expert_info["task"]
            main_task = expert_info["mainTask"]
            solution = expert.solve(expert_task, {"mainTask": main_task})
            solutions.append({"expert": expert_info["expert"], "solution": solution})

        final_solution = self.synthesize_solutions(solutions)
        return final_solution
