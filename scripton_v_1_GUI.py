import json
import os
import subprocess
from dotenv import load_dotenv
from openai import OpenAI

# Load .env file
load_dotenv()
# Load OpenAI API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
# Load configuration from JSON file
config = json.load(open('config.json'))


# Define the execute_command function
def execute_command(*args):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True).stdout.strip()
        return {"success": True, "output": result or "done"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# Define the function 'main' which is the entry point of the script
def main():
    client = OpenAI(api_key=api_key)
    # To store the conversation history
    conversation = [{"role": "system", "content": config["system_message"]},
                    {"role": "user", "content": f"Your operation system is {os.name}."}]

    while True:
        # User for input
        user_content = input("Enter your request (or type '" + config["exit_command"] + "' to quit): ")
        # Break out of the prompt loop to stop the program
        if user_content.lower() == config["exit_command"]:
            break

        # Append user message to conversation history
        conversation.append({"role": "user", "content": user_content})

        try:
            # Get response from OpenAI's ChatGPT
            response = client.chat.completions.create(
                model=config["openai_model"],
                messages=conversation,
                tools=[config["tool"]],
                tool_choice="auto",
            )
            if config.get("debug", False):
                print(f"Debug: To AI messages = {conversation}\nDebug: AI RawResponse = {response}")

            if response.choices[0].message.content:
                print(response.choices[0].message.content)
                conversation.append({"role": "assistant", "content": response.choices[0].message.content})

            # Check if 'tool_calls' attribute exists and is not None
            if hasattr(response.choices[0].message, 'tool_calls') and response.choices[
                0].message.tool_calls is not None:
                for tool_call in response.choices[0].message.tool_calls:
                    if getattr(tool_call, 'type', None) == 'function':
                        function_name = getattr(tool_call.function, 'name', None)
                        arguments = getattr(tool_call.function, 'arguments', "{}")

                        if function_name == 'execute_command':
                            # Ensure that arguments are properly formatted as a string
                            command = json.loads(arguments).get('command', '')
                            if isinstance(command, str):
                                # Execute the command and print the result
                                result = execute_command(command)
                                result_message = f"Command execution result: {result['output']}" if result[
                                    'success'] else f"Error: {result['error']}"
                                # Send the tool result back to the model for further conversation
                                conversation.append({"role": "assistant", "name": "tool", "content": result_message})
                                # TODO conversation.append({"role": "tool", "content": result_message, "tool_call_id": tool_id})
                                print(result_message)
                            else:
                                conversation.append({"role": "assistant", "name": "tool",
                                                     "content": f"Invalid command format.={command}"})
                                print(f"Invalid command format.={command}")
                        else:
                            raise Exception(f"function {function_name} not exist")
        except Exception as e:
            conversation.append({"role": "user", "name": "Exception", "content": e})
            print(f"Invalid command format.={e}")


import tkinter as tk
from tkinter import scrolledtext


# Функция для отправки запроса к OpenAI API
def handle_query(query):
    result = OpenAI(api_key=api_key).chat.completions.create(
        model=config["openai_model"],
        messages=query,
        tools=[config["tool_arg"]],
        tool_choice="auto",
    )
    return result.choices[0].message.content


# Функция, вызываемая при нажатии кнопки отправки
def send_query():
    user_input = query_entry.get("1.0", tk.END).strip()
    if user_input:  # Проверяем, не пустой ли запрос
        # Формируем массив сообщений
        messages = [
            {"role": "user", "content": user_input}
        ]
        response = handle_query(messages)
        response_text.configure(state='normal')
        response_text.insert(tk.END, "User: " + user_input + "\nGPT: " + str(response) + "\n")
        response_text.configure(state='disabled')
        query_entry.delete("1.0", tk.END)  # Очищаем поле ввода после отправки


# Создание GUI
root = tk.Tk()
root.title("GPT Chat Interface")

query_label = tk.Label(root, text="Введите ваш запрос:")
query_label.pack(pady=5)

query_entry = scrolledtext.ScrolledText(root, height=5, wrap=tk.WORD)
query_entry.pack(padx=10, pady=5)

send_button = tk.Button(root, text="Отправить", command=send_query)
send_button.pack(pady=5)

response_label = tk.Label(root, text="Ответы:")
response_label.pack(pady=5)

response_text = scrolledtext.ScrolledText(root, height=10, wrap=tk.WORD, state='disabled')
response_text.pack(padx=10, pady=5)

root.mainloop()
