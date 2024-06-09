import subprocess
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def run_command(command):
    """Executes a given command and returns the output."""
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
        return output
    except subprocess.CalledProcessError as e:
        return e.output

def get_ai_suggestion(prompt):
    """Uses the OpenAI API to get command suggestions based on the user's input."""
    try:
        response = client.completions.create(engine="text-davinci-002",  # Check the latest model on the OpenAI API documentation
        prompt=prompt,
        max_tokens=50)
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error in AI response: {e}"

def main():
    while True:
        cmd_input = input("Command to run: ")
        ai_suggested_command = get_ai_suggestion("Suggest a command for: " + cmd_input)
        print("AI suggests:", ai_suggested_command)
        approval = input("Execute this command? (yes/no): ")
        if approval.lower() == "yes":
            result = run_command(ai_suggested_command)
            print(result)
        else:
            print("Command execution cancelled.")

if __name__ == "__main__":
    main()
