import openai


class Expert:
    def solve(self, task):
        raise NotImplementedError("This method should be implemented by subclasses.")


class GPTExpert(Expert):
    def __init__(self, api_key, model, expertise_area):
        self.api_key = api_key
        self.model = model
        self.expertise_area = expertise_area
        self.client = openai.OpenAI(api_key=api_key)

    def solve(self, task, additional_params=None):
        conversation = [{"role": "system", "content": f"Решите задачу в области {self.expertise_area}."},
                        {"role": "user", "content": task}]
        if additional_params:
            for key, value in additional_params.items():
                conversation.append({"role": "system", "content": f"{key}: {value}"})
        response = self.client.chat.completions.create(model=self.model, messages=conversation)
        print(response)
        return response.choices[0].message.content
