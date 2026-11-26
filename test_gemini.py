import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("Gemini API key not found in .env!")

client = genai.Client(api_key=api_key)

print("Connecting to Gemini...")

response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents="Explain Retrieval-Augmented Generation in 3 simple sentences."
)

print("\nGEMINI RESPONSE")
print("=" * 50)
print(response.text)
