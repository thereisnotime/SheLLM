import os
import pty
import sys
import select
import logging
from .prompt import get_prompt

logger = logging.getLogger(__name__)

def run_interactive_ssh(tokens, shellm):
    """Runs an interactive SSH session."""
    try:
        pid, fd = pty.fork()
        if pid == 0:
            os.execvp(tokens[0], tokens)
        else:
            shellm.ssh_session = fd  # Set the ssh_session file descriptor
            interactive_ssh(fd, shellm)
    except Exception as e:
        logger.error(f"SSH session error: {e}")

def interactive_ssh(fd, shellm):
    """Handles interactive SSH session."""
    while True:
        rlist, _, _ = select.select([fd, sys.stdin], [], [])
        
        if fd in rlist:
            data = os.read(fd, 1024)
            if data:
                sys.stdout.buffer.write(data)
                sys.stdout.flush()
            else:
                break

        if sys.stdin in rlist:
            command = input(get_prompt())
            if command.strip().startswith('##'):
                shellm.answer_question(command[2:].strip())
            elif command.strip().startswith('#'):
                shellm.handle_lm_command(command[1:].strip(), remote=True)
            else:
                os.write(fd, (command + '\n').encode())
