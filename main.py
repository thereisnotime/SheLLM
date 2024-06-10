import os
import click
import signal
import readline
import logging
from colorama import init, Fore, Style
from config.logger_setup import setup_logging
from core.shellm import SheLLM
from core.prompt import get_prompt

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

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
