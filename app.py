import click
from models.openai_model import OpenAIModel

class TerminalWrapper:
    def __init__(self):
        self.context = ""
        self.model = OpenAIModel()

    # def execute_system_command(self, command):
    #     """Execute system commands and capture output."""
    #     try:
    #         result = subprocess.run(command, shell=True, text=True, capture_output=True, check=True)
    #         output = result.stdout
    #         error = result.stderr
    #         self.context += f"\n$ {command}\n{output}{error}"
    #         print(output)
    #         if error:
    #             print(f"Error: {error}", file=sys.stderr)
    #     except subprocess.CalledProcessError as e:
    #         print(f"An error occurred: {e}", file=sys.stderr)

    def execute_system_command(self, command):
        """Executes system commands and captures output."""
        import subprocess
        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        output = result.stdout + result.stderr
        self.context += f"\n$ {command}\n{output}"
        print(output)

    def handle_lm_command(self, command):
        suggestion = self.model.get_suggestion(self.context, command)
        if suggestion and click.confirm(f'Execute this command? {suggestion}'):
            self.execute_system_command(suggestion)

@click.command()
def main():
    click.echo("Welcome to the Terminal Wrapper. Type 'exit' to quit.")
    wrapper = TerminalWrapper()
    while True:
        cmd = input(">")
        if cmd == "exit":
            break
        elif cmd.startswith('#'):
            wrapper.handle_lm_command(cmd[1:])  # Remove the '#' and pass the command
        else:
            wrapper.execute_system_command(cmd)

if __name__ == "__main__":
    main()
