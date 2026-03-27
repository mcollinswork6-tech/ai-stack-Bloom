import streamlit as st
import time
from query_pinecone import get_query_embedding, index 
from google import genai
from groq import Groq
from tavily import TavilyClient
from docx import Document 
from io import BytesIO
from dotenv import load_dotenv
import os

load_dotenv()

# --- 1. SETUP & CLIENTS ---
st.set_page_config(page_title="Bloom Health AI", page_icon="🌸", layout="centered")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

@st.cache_resource
def get_clients():
    return {
        "gemini": genai.Client(api_key=os.getenv(GEMINI_API_KEY)),
        "groq": Groq(api_key=os.getenv(GROQ_API_KEY)),
        "tavily": TavilyClient(api_key=os.getenv(TAVILY_API_KEY))
    }

clients = get_clients()

# --- 2. HELPER FUNCTIONS ---

def generate_report(messages):
    doc = Document()
    doc.add_heading('Bloom Health: Evidence-to-Impact Report', 0)
    for msg in messages:
        role = "USER" if msg["role"] == "user" else "BLOOM AI"
        doc.add_heading(role, level=1)
        doc.add_paragraph(msg["content"])
        doc.add_paragraph("_" * 20)
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

def ask_bloom_ai(question):
    # 1. Search Pinecone (Fixed model ID from our previous 404 error)
    query_vector = get_query_embedding(question) 
    search_results = index.query(vector=query_vector, top_k=3, include_metadata=True)
    
    best_score = search_results['matches'][0]['score'] if search_results['matches'] else 0
    context_text = ""
    detailed_sources = [] 
    
    if best_score >= 0.7:
        status_tag = f"✅ **Validated by Bloom Health Evidence Base.** (Confidence: {best_score:.1%})"
        for match in search_results['matches']:
            # Use metadata directly instead of making a second API call for a 'gist'
            source_name = match['metadata'].get('source', 'Internal Document')
            text_chunk = match['metadata'].get('text', '')[:2000]
            context_text += f"\n---\n{text_chunk}"
            
            detailed_sources.append({
                "title": source_name,
                "summary": "Verified internal documentation." # Static text saves 3 API calls
            })
    else:
        # Agentic Fallback via Tavily
        status_tag = "🌍 **Note: Retrieved via Real-Time Web Search.**"
        web_results = tavily.search(query=question, search_depth="basic", max_results=2)
        for res in web_results['results']:
            context_text += f"\n---\n{res['content'][:1500]}"
            detailed_sources.append({
                "title": res['url'],
                "summary": "External web resource."
            })

    # 2. Generate Response
    system_prompt = f"Maternal Health Expert. Start with: {status_tag}. Use context ONLY."
    try:
        chat_completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context: {context_text}\n\nQ: {question}"}
            ],
            temperature=0.2
        )
        return chat_completion.choices[0].message.content, detailed_sources
    except Exception as e:
        return f"⚠️ API Error: {e}", []