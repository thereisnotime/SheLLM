import os
import pty
import sys
import select
import logging
from .prompt import get_prompt

logger = logging.getLogger(__name__)

def run_interactive_ssh(tokens):
    """Runs an interactive SSH session."""
    try:
        pid, fd = pty.fork()
        if pid == 0:
            os.execvp(tokens[0], tokens)
        else:
            interactive_ssh(fd)
    except Exception as e:
        logger.error(f"SSH session error: {e}")

def interactive_ssh(fd):
    """Handles interactive SSH session."""
    while True:
        try:
            data = os.read(fd, 1024).decode()
            if data:
                sys.stdout.write(data)
                sys.stdout.flush()
            command = input(get_prompt())
            os.write(fd, (command + '\n').encode())
        except OSError:
            break
