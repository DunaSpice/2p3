import os
import platform
import sqlite3
import json  # Добавлен для десериализации JSON
from dotenv import load_dotenv
from openai import OpenAI

def load_config_from_db():
    """Загружает конфигурацию из базы данных SQLite."""
    conn = sqlite3.connect('config.db')
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM config")
    config = {}
    for row in cursor.fetchall():
        key, value = row
        if key == "tool_arg":  # Особая обработка для 'tool_arg'
            value = json.loads(value)  # Десериализация из строки JSON в объект Python
        config[key] = value
    conn.close()
    return config

# Загрузка конфигурации из базы данных
config = load_config_from_db()

# Загрузка .env файла для доступа к переменным окружения
load_dotenv()
# Загрузка OpenAI API ключа из переменной окружения
api_key = os.getenv("OPENAI_API_KEY")

# Определение основной функции, которая является точкой входа в скрипт
def main():
    client = OpenAI(api_key=api_key)
    # История разговора
    conversation = [{"role": "system", "content": f"You are assistant only in operating system {platform.system()}, it important. {config['system_message']}"}]

    while True:
        # Запрос ввода от пользователя
        user_content = input("Enter your request (or type '" + config["exit_command"] + "' to quit): ")
        # Выход из цикла по команде пользователя
        if user_content.lower() == config["exit_command"]:
            break
        # Добавление сообщения пользователя в историю разговора
        conversation.append({"role": "user", "content": user_content})

        try:
            # Получение ответа от ChatGPT OpenAI
            response = client.chat.completions.create(
                model=config["openai_model"],
                messages=conversation,
                tools=[config["tool_arg"]],  # Используется уже десериализованный объект
                tool_choice="auto",
            )
            if config.get("debug", False):
                print(f"Debug: To AI messages = {conversation}\nDebug: AI RawResponse = {response}")

            res_message = response.choices[0].message

            if res_message.content:
                print(res_message.content)
                conversation.append({"role": "assistant", "content": res_message.content})
        except Exception as e:
            conversation.append({"role": "user", "name": "Exception", "content": f"{e}"})
            print(f"Exception: {e}")

# Проверка, является ли скрипт основным модулем, и, в таком случае, выполнение main()
if __name__ == "__main__":
    main()
