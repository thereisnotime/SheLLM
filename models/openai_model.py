# models/openai_model.py
import openai
from dotenv import load_dotenv
import os

class OpenAIModel:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('OPENAI_API_KEY')
        # Create an instance of the OpenAI client
        self.client = openai.OpenAI(api_key=self.api_key)

    def get_suggestion(self, context, prompt):
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that must only output shell commands and nothing else."
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
            # Use the chat completions endpoint with proper formatting
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=4000
            )
            # Print the response for debugging purposes
            print(response)
            # Properly extract the response text
            if response.choices:
                suggested_command = response.choices[0].message.content.strip()  # Access content directly
                return suggested_command
            return None
        except Exception as e:
            print(f"Error fetching suggestion from OpenAI: {e}")
            return None