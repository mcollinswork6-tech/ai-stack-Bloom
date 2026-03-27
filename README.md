# 🌸 Bloom Health: Evidence-to-Impact

Bloom Health AI is a specialized platform designed to provide validated maternal health guidelines and policy information, specifically focusing on the Texas Maternal Health Plan. It leverages a Retrieval-Augmented Generation (RAG) architecture to ensure responses are grounded in official documentation.

## 🚀 The Bloom-ai-stack Process

The core process follows an "Evidence-First" approach:
1.  **User Inquiry**: A user submits a query through the Streamlit interface.
2.  **Semantic Search**: The system converts the query into a high-dimensional vector and searches a curated internal database (Pinecone).
3.  **Validation Check**: 
    *   If a high-confidence match (>70%) is found, the system uses internal evidence.
    *   If confidence is low, the system performs a real-time web search (Tavily) to gather current information.
4.  **Expert Reasoning**: The retrieved context is passed to a Large Language Model (Groq Llama 3) with a "Maternal Health Expert" persona.
5.  **Validated Response**: The AI generates a response including source citations and a validation tag indicating the evidence source.

## ⚙️ Data Processing Pipeline

### 📥 Ingestion (`ingest_to_pinecone.py`)
- **Extraction**: Text is extracted from official reports and guidelines.
- **Chunking**: Documents are split into meaningful paragraphs to preserve context.
- **Embedding**: Each chunk is transformed into a 1536-dimensional vector using **Google Gemini (gemini-embedding-001)**.
- **Storage**: Chunks and their vectors are stored in a **Pinecone** index (`evidence-to-impact`) with source metadata.

### 🔍 Retrieval & Retrieval-Augmented Generation (`query_pinecone.py`)
- **Query Embedding**: The user's question is embedded using **Google Gemini (gemini-embedding-001)**.
- **Vector Matching**: Pinecone's vector search identifies the most relevant evidence chunks.
- **Fallback Mechanism**: When internal data is insufficient, **Tavily API** provides a secondary layer of real-time web-based evidence.

## 🏗️ Core Components & Interactions

| Component | Responsibility | Technology |
| :--- | :--- | :--- |
| **Frontend UI** | User interaction & Chat Interface | [Streamlit](https://streamlit.io/) |
| **Vector Database**| Long-term memory & semantic search | [Pinecone](https://www.pinecone.io/) |
| **Embeddings** | Converting text to mathematical vectors | [Google Gemini API](https://ai.google.dev/) |
| **Reasoning Engine**| Generating human-like expert responses | [Groq](https://groq.com/) (Llama 3.3 70B) |
| **Web Research** | Real-time external data verification | [Tavily](https://tavily.com/) |
| **Reporting** | Generating exportable `.docx` reports | [Python-docx](https://python-docx.readthedocs.io/) |

## 🛠️ Setup & Local Development

1.  **Clone the Repository**:
    ```bash
    git clone [repository-url]
    cd bloom-health
    ```
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure Environment**:
    Create a `.env` file with the following keys:
    - `GEMINI_API_KEY`
    - `GROQ_API_KEY`
    - `TAVILY_API_KEY`
    - `PINECONE_API_KEY`
4.  **Run the Application**:
    ```bash
    streamlit run app.py
    ```

---
*Created with ❤️ for Maternal Health Advocacy.*
