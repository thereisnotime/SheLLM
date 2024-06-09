import click
import subprocess
import sys
import os
import getpass
from datetime import datetime
from colorama import Fore, Style, init
from models.openai_model import OpenAIModel
from models.groq_model import GroqModel
import shlex
import pty

def get_git_info():
    """Returns the current git branch and status if in a git repository."""
    try:
        # Check if the current directory is a git repository
        if subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).returncode == 0:
            branch = subprocess.check_output(['git', 'branch', '--show-current'], text=True).strip()
            status = subprocess.check_output(['git', 'status', '--porcelain'], text=True)
            changes = len(status.split('\n')) - 1 if status else 0
            return f"{branch} | {changes} changes" if branch else ""
        return ""
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
        prompt_parts.append(f"{Fore.CYAN}({git_info}){Style.RESET_ALL}")
    if venv:
        prompt_parts.append(f"{Fore.MAGENTA}(venv:{venv}){Style.RESET_ALL}")
    return ' '.join(prompt_parts) + "\n>"

class SheLLM:
    def __init__(self, llm_api):
        self.context = ""
        self.history = []
        if llm_api == 'groq':
            self.model = GroqModel()
        else:
            self.model = OpenAIModel()
        self.ssh_session = None

    def execute_system_command(self, command):
        """Executes system commands and captures output."""
        tokens = shlex.split(command)
        if tokens[0] == 'cd':
            self.change_directory(tokens)
        elif tokens[0] == 'history':
            self.show_history()
        elif tokens[0] == 'ssh':
            self.run_interactive_ssh(tokens)
        else:
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
                print(f"An error occurred: {e}", file.sys.stderr)

    def change_directory(self, tokens):
        """Handles the 'cd' command."""
        try:
            if len(tokens) > 1:
                os.chdir(tokens[1])
            else:
                os.chdir(os.path.expanduser('~'))
        except FileNotFoundError as e:
            print(f"cd: {e}", file=sys.stderr)

    def run_interactive_ssh(self, tokens):
        """Runs an interactive SSH session."""
        try:
            pid, fd = pty.fork()
            if pid == 0:
                os.execvp(tokens[0], tokens)
            else:
                self.ssh_session = fd
                self.interactive_ssh()
        except Exception as e:
            print(f"SSH session error: {e}", file=sys.stderr)

    def interactive_ssh(self):
        """Handles interactive SSH session."""
        while self.ssh_session:
            try:
                data = os.read(self.ssh_session, 1024).decode()
                if data:
                    print(data, end='', flush=True)
                command = input(get_prompt())
                if command.strip().startswith('##'):
                    self.answer_question(command[2:].strip())
                elif command.strip().startswith('#'):
                    self.handle_lm_command(command[1:].strip(), remote=True)
                else:
                    os.write(self.ssh_session, (command + '\n').encode())
            except OSError:
                break

    def handle_lm_command(self, command, remote=False):
        suggestion = self.model.get_command_suggestion(self.context, command)
        if suggestion:
            current_time = datetime.now().strftime('%H:%M:%S')
            print(f"{Fore.RED}[SheLLM]{Style.RESET_ALL} {Fore.BLUE}[{current_time}]{Style.RESET_ALL} Execute command: {Fore.RED}{suggestion}{Style.RESET_ALL}")
            if click.confirm(''):
                if remote and self.ssh_session:
                    os.write(self.ssh_session, (suggestion + '\n').encode())
                else:
                    self.execute_system_command(suggestion)

    def answer_question(self, question):
        answer = self.model.answer_question(self.context, question)
        current_time = datetime.now().strftime('%H:%M:%S')
        print(f"{Fore.RED}[SheLLM]{Style.RESET_ALL} {Fore.BLUE}[{current_time}]{Style.RESET_ALL} Answer: {Fore.GREEN}{answer}{Style.RESET_ALL}")
        return answer

    # TODO: Hook this with the shell history and implement SheLLM custom history with session support.
    def show_history(self):
        current_time = datetime.now().strftime('%H:%M:%S')
        print(f"{Fore.RED}[SheLLM]{Style.RESET_ALL} {Fore.BLUE}[{current_time}]{Style.RESET_ALL} Command History:")
        for i, cmd in enumerate(self.history, 1):
            print(f"{i}: {cmd}")

@click.command()
@click.option('--llm-api', type=click.Choice(['openai', 'groq']), default='openai', help="Choose the language model API to use.")
def main(llm_api):
    init(autoreset=True)
    click.echo(f"Welcome to the {Fore.RED}SheLLM{Style.RESET_ALL} Model: {Fore.BLUE}{llm_api.capitalize()}{Style.RESET_ALL}. Prefix with '#' to generate a command or '##' to ask a question. Type 'exit' to quit.")
    wrapper = SheLLM(llm_api=llm_api)
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
