import os
import subprocess
from openai import OpenAI
from settings import settings


class Client:

    def __init__(self):
        self.client = OpenAI(api_key=settings.api_key)

    # Define the execute_command function
    def execute_command(self, command):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
            output = result.stdout.strip()
            return {"success": True, "output": output or "done"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # Modify get_response to include tools and handle sending results back
    def get_response(self, messages):
        return self.client.chat.completions.create(
            model=settings.config["openai_model"],
            messages=messages,
            tools=settings.tools,
            tool_choice="auto",
        )

    def client_response(self, user_content: str):

        # To store the conversation history
        conversation = [{"role": "system", "content": f"Your operation system is {os.name}" +
                                                      settings.config["system_message"]},
                        {"role": "user", "content": user_content}]

        # Get response from OpenAI's ChatGPT
        response = self.get_response(conversation)

        return response
