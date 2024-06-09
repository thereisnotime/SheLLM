# models/openai_model.py
import openai
from dotenv import load_dotenv
import os

class OpenAIModel:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('OPENAI_API_KEY')
        openai.api_key = self.api_key

    def get_suggestion(self, context, prompt):
        try:
            full_prompt = f"Given the terminal history:\n{context}\nUser asks: {prompt}\nSuggest a command:"
            response = openai.Completion.create(
                engine="text-davinci-002",
                prompt=full_prompt,
                max_tokens=150
            )
            return response.choices[0].text.strip()
        except Exception as e:
            print(f"Error fetching suggestion from OpenAI: {e}")
            return None
