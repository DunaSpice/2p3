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
    # Conversation history
    conversation = [{"role": "system", "content": f"You are assistant only in operating system {platform.system()}, "
                                                  f"it important. {config['system_message']}"}]

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
                tools=[config["tool_arg"]],
                tool_choice="auto",
            )
            if config.get("debug", False):
                print(f"Debug: To AI messages = {conversation}\nDebug: AI RawResponse = {response}")

            res_message = response.choices[0].message

            if res_message.content:
                print(res_message.content)
                conversation.append({"role": "assistant", "content": res_message.content})

            # Check if 'tool_calls' attribute exists and is not None
            if hasattr(res_message, 'tool_calls') and res_message.tool_calls is not None:
                for tool_call in res_message.tool_calls:
                    if getattr(tool_call, 'type', None) == 'function':
                        function_name = getattr(tool_call.function, 'name', None)
                        arguments = getattr(tool_call.function, 'arguments', "{}")

                        if function_name in globals():
                            # Execute the function
                            result_func = f"Function result: {globals()[function_name](arguments)}"
                            # Send the tool result back to the model for further conversation
                            conversation.append({"role": "user", "content": result_func})
                            # TODO tool answer now not work conversation.append({"role": "tool", "content": result_func, "tool_call_id": tool_id})
                            print(result_func)
                        else:
                            raise Exception(f"function {function_name} not exist")
        except Exception as e:
            conversation.append({"role": "user", "name": "Exception", "content": f"{e}"})
            print(f"Exception: {e}")


# Check if the script is the main module being executed, and if so, call main()
if __name__ == "__main__":
    main()
