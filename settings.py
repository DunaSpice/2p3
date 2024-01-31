import os
import json
from dotenv import load_dotenv

load_dotenv()

class Settings:

    api_key = os.getenv("OPENAI_API_KEY")

    with open("config.json", "r") as file:
        config = json.load(file)

    tools = [
        {
            "type": "function",
            "function": {
                "name": "execute_command",
                "description": "Execute a system command line with shell subprocess module",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The command to execute",
                        }
                    },
                    "required": ["command"],
                },
            }
        }
    ]


settings = Settings()


try:
    from local_settings import api_key
    settings.api_key = api_key
except ImportError:
    pass
