import os
from groq import Groq
from dotenv import load_dotenv

class GroqModel:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('GROQ_API_KEY')
        self.client = Groq(api_key=self.api_key)

    def validate_command(self, command):
        """Validates the command to ensure it is safe and valid to execute."""
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a senior system administrator who must validate shell commands if there are any errors or not and return the proper/fixed version. Also if the input contains anything other than a pure command (e.g. comments, flags, etc.), you must remove them. If the command is already correct, you must return it as is. If the command is in code block, you must remove the code block. Use simple commands and avoid using complex commands for less errors. Anticipate the user's needs and provide the best possible solution."
                },
                {
                    "role": "user",
                    "content": command
                }
            ]
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=messages
            )
            if response.choices:
                validated_command = response.choices[0].message.content.strip()
                return validated_command
            return None
        except Exception as e:
            print(f"Error fetching suggestion from Groq: {e}")
            return None

    def get_command_suggestion(self, context, prompt):
        """Generates shell commands based on the provided context and prompt."""
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that must only output shell commands and nothing else. Anticipate the user's needs and provide the best possible solution. Do not include any comments or flags in the output."
                },
                {
                    "role": "user",
                    "content": context
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=messages
            )
            if response.choices:
                suggested_command = response.choices[0].message.content.strip()
                suggested_command = self.validate_command(suggested_command)
                return suggested_command
            return None
        except Exception as e:
            print(f"Error fetching suggestion from Groq: {e}")
            return None

    def answer_question(self, context, question):
        """Generates answers to questions based on the provided context and question."""
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a knowledgeable assistant who provides detailed answers to questions."
                },
                {
                    "role": "user",
                    "content": context
                },
                {
                    "role": "user",
                    "content": question
                }
            ]
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=messages
            )
            if response.choices:
                answer = response.choices[0].message.content.strip()
                return answer
            return None
        except Exception as e:
            print(f"Error fetching answer from Groq: {e}")
            return None
