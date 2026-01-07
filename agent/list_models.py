import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("GOOGLE_API_KEY not found")
    exit(1)

client = genai.Client(api_key=api_key)
for model in client.models.list(config={"page_size": 100}):
    print(model.name)
