import json
from dotenv import load_dotenv
import os
from architect import GPTArchitect

# Load .env file
load_dotenv()
# Load OpenAI API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")


def main():
    architect = GPTArchitect(api_key, "gpt-3.5-turbo")

    while True:
        user_task = input("Enter your task): ")

        solution = architect.solve_task(user_task)
        print("Solution:", solution)


if __name__ == "__main__":
    main()
