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
            full_prompt = f"Given the terminal history:\n{context}\nUser asks: {prompt}\nSuggest a command:"
            # Correct method call using the client instance
            response = self.client.completions.create(
                model="gpt-4o",
                prompt=full_prompt,
                max_tokens=150
            )
            # Properly access the choices and text
            return response['choices'][0]['text'].strip() if 'choices' in response else None
        except Exception as e:
            print(f"Error fetching suggestion from OpenAI: {e}")
            return None
