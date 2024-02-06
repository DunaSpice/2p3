import sqlite3
import json

# Создание или подключение к базе данных config.db
conn = sqlite3.connect('config.db')

# Создание курсора для выполнения SQL команд
cursor = conn.cursor()

# Создание таблицы config
cursor.execute('''
CREATE TABLE IF NOT EXISTS config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
)
''')

# Конфигурационные данные, включая tool_arg как строку JSON
config_items = [
    ('debug', 'true'),
    ('openai_model', 'gpt-3.5-turbo'),
    ('exit_command', 'exit'),
    ('system_message', 'You mast find and do command shell only this OS.'),
    ('tool_import', 'import subprocess'),
    ('tool_function', "def execute_command(arguments):\n    return subprocess.run(json.loads(arguments).get('command', ''), shell=True, capture_output=True, text=True, check=True).stdout.strip()"),
    ('tool_arg', json.dumps({
        "type": "function",
        "function": {
            "name": "execute_command",
            "description": "Execute a system command line with shell subprocess module",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The command to execute"
                    }
                },
                "required": ["command"]
            }
        }
    }))
]

# Вставка конфигурационных данных в таблицу config
for key, value in config_items:
    # Для tool_arg используется сериализация в JSON
    cursor.execute('INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)', (key, value))

# Сохранение изменений и закрытие соединения с базой данных
conn.commit()
conn.close()
