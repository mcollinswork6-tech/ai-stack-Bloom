import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

print("--- Listing Models ---")
try:
    for m in client.models.list():
        if "embedContent" in m.supported_generate_methods:
            print(f"Model ID: {m.name}, Name: {m.display_name}")
except Exception as e:
    print(f"Error listing models: {e}")

print("\n--- Testing text-embedding-004 ---")
try:
    res = client.models.embed_content(
        model="text-embedding-004",
        contents="Hello world",
    )
    print("text-embedding-004 success!")
except Exception as e:
    print(f"text-embedding-004 failed: {e}")

print("\n--- Testing gemini-embedding-001 ---")
try:
    res = client.models.embed_content(
        model="gemini-embedding-001",
        contents="Hello world",
    )
    print("gemini-embedding-001 success!")
except Exception as e:
    print(f"gemini-embedding-001 failed: {e}")
