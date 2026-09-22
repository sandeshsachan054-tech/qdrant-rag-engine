# Audio RAG Search Engine 

An intelligent Retrieval-Augmented Generation (RAG) system built with FastAPI, Qdrant Vector Database, and Groq Cloud API. This project transcribes audio files, generates semantic embeddings using Sentence Transformers, and enables fast semantic querying and intelligent context-aware responses over transcribed content.

---

##  Features

- Audio Transcription & Chunking : Extracts and structures audio transcripts for vector search.
- Vector Storage with Qdrant : High-performance vector embeddings storage and similarity search.
- Fast Embeddings : Uses `sentence-transformers` for dense semantic search.
- FastAPI Backend : Clean and fast RESTful API endpoints for querying and retrieving context.
- Groq LLM Acceleration : Lightning-fast inference for generative question answering based on audio context.

---

##  Tech Stack

- Backend: FastAPI, Uvicorn
- Vector Database: Qdrant
- LLM / Inference: Groq API
- Embeddings: Sentence-Transformers
- Language: Python 3.11+

---

##  Project Structure

```text
├── audios/                     # Raw audio files
├── qdrant_db/                  # Local Qdrant vector database storage
├── transcribed_chunks.json     # Processed transcriptions with timestamps/metadata
├── convert_playlist_in_rag.py  # Audio processing & embedding generation pipeline
├── app.py                      # FastAPI server & query endpoints
├── main.py                     # Entry point / workflow runner
├── requirements.txt            # Project dependencies
├── .env.example                # Template for environment variables
└── README.md
```

## Installation & Setup
1.clone the Repository:
```bash
git clone https://github.com/sandeshsachan054-tech/audio-rag-search-engine.git
cd audio-rag-search-engine
```

2.Set Up a Virtual Environment:
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate
```

3.Install Dependencies:
```bash
pip install -r requirements.txt
```

4. Configure Environment Variables
env
GROQ_API_KEY=your_groq_api_key_here

## Running Application
1. Process and Index Audio Files:
```bash
python convert_playlist_in_rag.py
```

2. Start the FastAPI Server:
```bash
python app.py
```
The server runs locally at:
http://127.0.0.1:8000


