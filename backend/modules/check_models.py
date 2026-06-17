import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

print("Listing available models...")
try:
    for m in client.models.list():
        print(f" > {m.name}")
except Exception as e:
    print(f"Error: {e}")