import click
import subprocess
import sys
import os
import getpass
from datetime import datetime
from colorama import Fore, Style, init
from models.openai_model import OpenAIModel

def get_git_info():
    """Returns the current git branch and status if in a git repository."""
    try:
        branch = subprocess.check_output(['git', 'branch', '--show-current'], text=True).strip()
        status = subprocess.check_output(['git', 'status', '--porcelain'], text=True)
        changes = len(status.split('\n')) - 1 if status else 0
        return f"{branch} | {changes} changes" if branch else ""
    except subprocess.CalledProcessError:
        return ""

def get_prompt():
    """Constructs a customized prompt with user, host, path, git and venv info."""
    user = getpass.getuser()
    host = os.uname().nodename
    path = os.getcwd()
    git_info = get_git_info()
    venv = os.environ.get('VIRTUAL_ENV', '').split('/')[-1] if os.environ.get('VIRTUAL_ENV') else ""
    current_time = datetime.now().strftime('%H:%M:%S')
    prompt_parts = [
        f"{Fore.RED}[SheLLM]{Style.RESET_ALL}",
        f"{Fore.BLUE}[{current_time}]{Style.RESET_ALL}",
        f"{Fore.GREEN}{user}{Style.RESET_ALL}@{host}:",
        f"{Fore.GREEN}{path}{Style.RESET_ALL}"
    ]
    if git_info:
        prompt_parts.append(f"{Fore.CYAN}{git_info}{Style.RESET_ALL}")
    if venv:
        prompt_parts.append(f"{Fore.MAGENTA}(venv:{venv}){Style.RESET_ALL}")
    return ' '.join(prompt_parts) + "\n>"

class SheLLM:
    def __init__(self):
        self.context = ""
        self.history = []
        self.model = OpenAIModel()

    def execute_system_command(self, command):
        """Executes system commands and captures output."""
        if command == "history":
            self.show_history()
            return
        try:
            result = subprocess.run(command, shell=True, text=True, capture_output=True, check=True)
            output = result.stdout
            error = result.stderr
            self.context += f"\n$ {command}\n{output}{error}"
            self.history.append(command)
            print(output)
            if error:
                print(f"Error: {error}", file=sys.stderr)
        except subprocess.CalledProcessError as e:
            print(f"An error occurred: {e}", file=sys.stderr)

    def handle_lm_command(self, command):
        suggestion = self.model.get_command_suggestion(self.context, command)
        if suggestion:
            current_time = datetime.now().strftime('%H:%M:%S')
            print(f"{Fore.RED}[SheLLM]{Style.RESET_ALL} {Fore.BLUE}[{current_time}]{Style.RESET_ALL} Execute command: {Fore.RED}{suggestion}{Style.RESET_ALL}")
            if click.confirm(''):
                self.execute_system_command(suggestion)

    def answer_question(self, question):
        answer = self.model.answer_question(self.context, question)
        current_time = datetime.now().strftime('%H:%M:%S')
        print(f"{Fore.RED}[SheLLM]{Style.RESET_ALL} {Fore.BLUE}[{current_time}]{Style.RESET_ALL} Answer: {Fore.GREEN}{answer}{Style.RESET_ALL}")
        return answer

    def show_history(self):
        current_time = datetime.now().strftime('%H:%M:%S')
        print(f"{Fore.RED}[SheLLM]{Style.RESET_ALL} {Fore.BLUE}[{current_time}]{Style.RESET_ALL} Command History:")
        for i, cmd in enumerate(self.history, 1):
            print(f"{i}: {cmd}")

@click.command()
def main():
    init(autoreset=True)  # Initialize Colorama
    click.echo("Welcome to the SheLLM. Prefix with '#' to generate a command or '##' to ask a question. Type 'exit' to quit.")
    wrapper = SheLLM()
    while True:
        cmd = input(get_prompt())
        if cmd.lower() == "exit":
            break
        elif cmd.strip().startswith('##'):
            wrapper.answer_question(cmd[2:].strip())
        elif cmd.strip().startswith('#'):
            wrapper.handle_lm_command(cmd[1:].strip())
        else:
            wrapper.execute_system_command(cmd)

if __name__ == "__main__":
    main()
