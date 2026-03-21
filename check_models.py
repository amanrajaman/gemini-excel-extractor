import os
from dotenv import load_dotenv
from google import genai

# Load your API key from the .env file
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print("Scanning for available models...")

# Fetch and print all models your key can access
for model in client.models.list():
    print(f"- {model.name}")