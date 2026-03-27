import os
from google import genai
from google.genai import types
from pinecone import Pinecone
from groq import Groq
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

# --- Clients ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# Initialize Clients
gemini_client = genai.Client(api_key=GEMINI_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)
tavily = TavilyClient(api_key=TAVILY_API_KEY)

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("evidence-to-impact")

def get_query_embedding(text):
    """Converts user question into a vector using a stable model ID."""
    try:
        result = gemini_client.models.embed_content(
            # FIX: Use the string name directly, no 'models/' prefix
            model="text-embedding-004", 
            contents=text,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_QUERY",
                # Ensure this matches your Pinecone index settings
                output_dimensionality=1536 
            )
        )
        return result.embeddings[0].values
    except Exception as e:
        st.error(f"Embedding Error: {e}")
        # Return a zero-vector or re-raise to prevent the 404 from crashing the app
        raise e
def ask_ai(question):
    # 1. SEARCH PINECONE
    query_vector = get_query_embedding(question)
    search_results = index.query(vector=query_vector, top_k=3, include_metadata=True)
    
    # 2. CHECK SIMILARITY THRESHOLD
    # Safety check: Get score of the top match, or 0 if no matches found
    best_score = search_results['matches'][0]['score'] if search_results.get('matches') else 0
    sources = []
    context_text = ""
    
    # THRESHOLD: 0.7 
    if best_score > 0.7:
        print("✅ Found high-quality evidence in Bloom database.")
        for match in search_results['matches']:
            context_text += f"\n---\n{match['metadata'].get('text', 'No text found')}"
            sources.append(f"📄 {match['metadata'].get('source', 'Unknown Source')}")
        validation_tag = "✅ **Validated by Bloom Health Evidence Base.**"
    else:
        # 3. SEARCH THE WEB (Agentic Fallback)
        print("🌐 Low confidence in local files. Searching open internet...")
        try:
            web_search = tavily.search(query=question, search_depth="advanced")
            for result in web_search.get('results', []):
                context_text += f"\n---\n{result.get('content', '')}"
                sources.append(f"🌐 {result.get('url', 'External Link')}")
            validation_tag = "🌍 **Note: Information retrieved from verified web sources (Outside Bloom Internal Base).**"
        except Exception as e:
            context_text = "No relevant information found in internal database or web search."
            validation_tag = "⚠️ **No validated evidence found.**"

    # 4. GENERATE FINAL RESPONSE
    prompt = f"""
    You are a Maternal Health Policy Expert. 
    Use the provided context to answer the question accurately and professionally. 
    
    At the very start of your response, you MUST include this exact tag: {validation_tag}
    
    CONTEXT:
    {context_text}
    
    QUESTION:
    {question}
    """

    completion = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return completion.choices[0].message.content, sources