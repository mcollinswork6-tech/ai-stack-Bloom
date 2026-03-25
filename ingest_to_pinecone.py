import os
import time
from google import genai
from google.genai import types
from pinecone import Pinecone
from dotenv import load_dotenv
import os

load_dotenv()

# 1. Setup Keys & Clients
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("evidence-to-impact")

folder_path = r'G:\My Drive\Saved from Chrome'

def get_embedding(text):
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
            output_dimensionality=1536
        )
    )
    return result.embeddings[0].values

# 2. Process the Text Files
for filename in os.listdir(folder_path):
    if filename.endswith('.txt'):
        print(f"\n🚀 Processing: {filename}")
        
        with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as f:
            content = f.read()
            # Split by paragraphs, but also filter out empty/tiny ones
            paragraphs = [p.strip() for p in content.split('\n\n') if len(p.strip()) > 100]
            
            for i, para in enumerate(paragraphs):
                try:
                    # Fix 1: Generate Embedding
                    vector = get_embedding(para)
                    
                    # Fix 2: Limit metadata size (Pinecone 40KB limit)
                    # We keep the first 30,000 characters to be safe
                    safe_text = para[:30000] 
                    
                    metadata = {
                        "text": safe_text, 
                        "source": filename,
                        "location": "Texas" if "Texas" in filename or "MMMRC" in filename else "General"
                    }
                    
                    # Upload
                    index.upsert(vectors=[(f"{filename}_{i}", vector, metadata)])
                    print(f"  ✅ Chunk {i} uploaded.")
                    
                    # Fix 3: Rate Limiting (The "Cool Down")
                    # Pause for 1 second so Gemini Free Tier doesn't block us
                    time.sleep(1) 

                except Exception as e:
                    print(f"  ❌ Error on chunk {i}: {e}")
                    # If we hit a rate limit error, wait longer
                    if "429" in str(e):
                        print("  ⏸ Rate limit hit. Waiting 10 seconds...")
                        time.sleep(10)
                    continue

print("\n🎉 Mission Accomplished! Your maternal health data is live in Pinecone.")