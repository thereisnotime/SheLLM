import os
import shlex
import subprocess
import sys
import pty
import select
import signal
import logging

logger = logging.getLogger(__name__)

def change_directory(tokens):
    """Handles the 'cd' command."""
    try:
        if len(tokens) > 1:
            os.chdir(tokens[1])
        else:
            os.chdir(os.path.expanduser('~'))
        logger.info(f"Changed directory to {os.getcwd()}")
    except FileNotFoundError as e:
        logger.error(f"cd: {e}")

def run_command_with_pty(command):
    """Runs commands in a pseudo-terminal to support interactive commands."""
    def read(fd):
        output = ""
        while True:
            r, _, _ = select.select([fd], [], [])
            if fd in r:
                try:
                    data = os.read(fd, 1024)
                    if not data:
                        break
                    decoded_data = data.decode()
                    sys.stdout.write(decoded_data)
                    sys.stdout.flush()
                    output += decoded_data
                except OSError:
                    break
        return output

    def signal_handler(sig, frame):
        if pid:
            os.kill(pid, sig)

    pid, fd = pty.fork()
    if pid == 0:
        os.execvp("/bin/bash", ["/bin/bash", "-c", command])
    else:
        signal.signal(signal.SIGINT, signal_handler)
        try:
            output = read(fd)
        except Exception as e:
            logger.error(f"An error occurred: {e}")
        finally:
            os.close(fd)
            signal.signal(signal.SIGINT, signal.SIG_DFL)  # Reset signal handler to default

    return output
