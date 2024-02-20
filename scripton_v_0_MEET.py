import json
import os
import platform
from dotenv import load_dotenv
from openai import OpenAI

# Load configuration from JSON file
config = json.load(open('config.json'))
exec(config["tool_import"])
exec(config["tool_function"])
# Load .env file
load_dotenv()
# Load OpenAI API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")


# Define the function 'main' which is the entry point of the script
def main():
    client = OpenAI(api_key=api_key)
    main_arh_system = [{"role": "system", "content": "Побудь архиткетором. Твоя задача расписать задачи для других как можно понятнее"}]
    help_arh_system = [{"role": "system", "content": f"Побудть помошником уточняй моменти которие могут бить непоняты"}]
    count_msgs = 5

    user_content = input("Enter your request (or type '" + config["exit_command"] + "' to quit): ")
    # Break out of the prompt loop to stop the program
    if user_content.lower() == config["exit_command"]:
        return

    conversation = [{"role": "user", "content": user_content}]
    # Append user message to conversation history

    while count_msgs > 0:
        try:
            res_main_message = get_response(client, main_arh_system + conversation).choices[0].message
            if res_main_message.content:
                print(res_main_message.content)
                conversation.append({"role": "assistant", "content": res_main_message.content})

            res_help_message = get_response(client, help_arh_system + conversation).choices[0].message
            if res_help_message.content:
                print(res_help_message.content)
                conversation.append({"role": "user", "content": res_help_message.content})

            if config.get("debug", False):
                print(f"Debug: To AI messages = {conversation}\n"
                      f"Debug: AI RawResponse = {res_main_message}\n" 
                      f"Debug: AI RawResponse = {res_help_message}\n")

        except Exception as e:
            conversation.append({"role": "user", "name": "Exception", "content": f"{e}"})
            print(f"Exception: {e}")

        count_msgs -= 1


def get_response(client, conversation):
    return client.chat.completions.create(
        model=config["openai_model"],
        messages=conversation
    )


# Check if the script is the main module being executed, and if so, call main()
if __name__ == "__main__":
    main()
