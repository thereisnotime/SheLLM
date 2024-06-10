import click
import subprocess
import sys
import os
import getpass
import logging
import shlex
import pty
import readline
import select
import signal
from utils.logger_setup import setup_logging
from datetime import datetime
from colorama import Fore, Style, init
from models.openai_model import OpenAIModel
from models.groq_model import GroqModel

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

def get_git_info():
    """Returns the current git branch and status if in a git repository."""
    try:
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
    if len(path) > 42:
        path = "../" + os.path.basename(path)
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
        self.current_process_pid = None
        if llm_api == 'groq':
            self.model = GroqModel()
        else:
            self.model = OpenAIModel()
        self.ssh_session = None
        logger.info(f"SheLLM initialized with {llm_api} model.")

    def execute_system_command(self, command):
        """Executes system commands and captures output."""
        if not command.strip():
            logger.info("No command entered. Please enter a valid command.")
            return
        
        tokens = shlex.split(command)
        if tokens[0] == 'cd':
            self.change_directory(tokens)
        elif tokens[0] == 'history':
            self.show_history()
        elif tokens[0] == 'ssh':
            self.run_interactive_ssh(tokens)
        else:
            self.run_command_with_pty(command)

    def change_directory(self, tokens):
        """Handles the 'cd' command."""
        try:
            if len(tokens) > 1:
                os.chdir(tokens[1])
            else:
                os.chdir(os.path.expanduser('~'))
        except FileNotFoundError as e:
            logger.error(f"cd: {e}")

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
            logger.error(f"SSH session error: {e}")

    def interactive_ssh(self):
        """Handles interactive SSH session."""
        while self.ssh_session:
            try:
                data = os.read(self.ssh_session, 1024).decode()
                if data:
                    sys.stdout.write(data)
                    sys.stdout.flush()
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
        while True:
            suggestion = self.model.get_command_suggestion(self.context, command)
            if suggestion:
                current_time = datetime.now().strftime('%H:%M:%S')
                logger.info(f"Execute command: {Fore.RED}{suggestion}{Style.RESET_ALL}")
                response = click.prompt(f"{Fore.RED}[SheLLM]{Style.RESET_ALL} Confirm execution (Y/n/r)", type=str, default='Y').lower()
                if response == 'y':
                    if remote and self.ssh_session:
                        os.write(self.ssh_session, (suggestion + '\n').encode())
                    else:
                        self.execute_system_command(suggestion)
                    break
                elif response == 'n':
                    break
                elif response == 'r':
                    continue

    def answer_question(self, question):
        answer = self.model.answer_question(self.context, question)
        current_time = datetime.now().strftime('%H:%M:%S')
        logger.info(f"{Fore.RED}[SheLLM]{Style.RESET_ALL} {Fore.BLUE}[{current_time}]{Style.RESET_ALL} Answer: {Fore.GREEN}{answer}{Style.RESET_ALL}")
        return answer

    def show_history(self):
        current_time = datetime.now().strftime('%H:%M:%S')
        if not self.history:
            logger.info(f"{Fore.RED}[SheLLM]{Style.RESET_ALL} {Fore.BLUE}[{current_time}]{Style.RESET_ALL} No command history.")
        else:
            logger.info(f"{Fore.RED}[SheLLM]{Style.RESET_ALL} {Fore.BLUE}[{current_time}]{Style.RESET_ALL} Command History:")
            for i, cmd in enumerate(self.history, 1):
                logger.info(f"{i}: {cmd}")

    def run_command_with_pty(self, command):
        """Runs commands in a pseudo-terminal to support interactive commands."""
        def read(fd):
            while True:
                r, _, _ = select.select([fd], [], [])
                if fd in r:
                    try:
                        data = os.read(fd, 1024)
                        if not data:
                            break
                        sys.stdout.write(data.decode())
                        sys.stdout.flush()
                    except OSError:
                        break

        pid, fd = pty.fork()
        if pid == 0:
            os.execvp("/bin/bash", ["/bin/bash", "-c", command])
        else:
            self.current_process_pid = pid
            try:
                read(fd)
            except Exception as e:
                logger.error(f"An error occurred: {e}")
            finally:
                os.close(fd)
                self.current_process_pid = None

def signal_handler(sig, frame):
    """Signal handler for SIGINT to stop the current command."""
    if shellm.current_process_pid:
        os.kill(shellm.current_process_pid, signal.SIGINT)
    else:
        logger.info("\nUse 'exit' to quit SheLLM.")

@click.command()
@click.option('--llm-api', type=click.Choice(['openai', 'groq']), default='openai', help="Choose the language model API to use.")
def main(llm_api):
    global shellm
    init(autoreset=True)
    readline.parse_and_bind('tab: complete')
    readline.parse_and_bind('set editing-mode vi')
    history_file = os.path.expanduser("~/.shellm_history")
    try:
        readline.read_history_file(history_file)
    except FileNotFoundError:
        pass

    shellm = SheLLM(llm_api=llm_api)
    signal.signal(signal.SIGINT, signal_handler)

    logger.info(f"Welcome to the {Fore.RED}SheLLM{Style.RESET_ALL} Model: {Fore.BLUE}{llm_api.capitalize()}{Style.RESET_ALL}. Prefix with '#' to generate a command or '##' to ask a question. Type 'exit' to quit.")
    
    while True:
        try:
            cmd = input(get_prompt())
            if cmd.lower() == "exit":
                break
            elif cmd.strip().startswith('##'):
                shellm.answer_question(cmd[2:].strip())
            elif cmd.strip().startswith('#'):
                shellm.handle_lm_command(cmd[1:].strip())
            else:
                shellm.execute_system_command(cmd)
        except (EOFError, KeyboardInterrupt):
            logger.info("\nExiting...")
            break

    readline.write_history_file(history_file)

if __name__ == "__main__":
    main()
