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
with open("config.json", "r") as file:
    config = json.load(file)

# Define a 'tools' array specifying the tools that can be called within the OpenAI Completion
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


# Define the execute_command function
def execute_command(command):
    try:
        # Execute the command
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        output = result.stdout.strip()
        return {"success": True, "output": output or "done"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# Modify get_response to include tools and handle sending results back
def get_response(client, messages):
    if config.get("debug", False):
        print(f"Dbug: To AI messages = {messages}")
    # Make a request to the OpenAI API, providing the model, messages and tools
    return client.chat.completions.create(
        model=config["openai_model"],
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )


# Define the function 'main' which is the entry point of the script
def main():
    client = OpenAI(api_key=api_key)
    # To store the conversation history
    conversation = [{"role": "system", "content": f"Your operation system is {os.name}" + config["system_message"]}]

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
            response = get_response(client, conversation)
            if config.get("debug", False):
                print(f"Debug: AI RawResponse = {response}")

            if response.choices[0].message.content:
                print(response.choices[0].message.content)
                conversation.append({"role": "assistant", "content": response.choices[0].message.content})

            # Check if 'tool_calls' attribute exists and is not None
            if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls is not None:
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
                                result_message = f"Command execution result: {result['output']}" if result['success'] else f"Error: {result['error']}"

                                # Send the tool result back to the model for further conversation
                                conversation.append({"role": "assistant", "name": "tool", "content": result_message})

                                # TODO conversation.append({"role": "tool", "content": result_message, "tool_call_id": tool_id})
                                print(result_message)
                            else:
                                conversation.append(
                                    {"role": "assistant", "name": "tool", "content": f"Invalid command format.={command}"})
                                print(f"Invalid command format.={command}")
        except Exception as e:
            conversation.append({"role": "user", "name": "Exception", "content": e})
            print(f"Invalid command format.={e}")


# Check if the script is the main module being executed, and if so, call main()
if __name__ == "__main__":
    main()
