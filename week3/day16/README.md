# Qdrant RAG Engine - Local Setup Guide

Yeh guide aapko is project ko *VS Code* me setup aur run karne me madad karegi.

---

## 🛠️ Prerequisites
- [VS Code](https://code.visualstudio.com/) installed hona chahiye.
- Python (v3.10 ya upar) installed hona chahiye.
- Git installed hona chahiye.

---

## 🚀 VS Code Setup Steps

### 1. Repository Clone Karein
VS Code open karein aur built-in terminal (Ctrl + ~) me run karein:
git clone https://github.com/sandeshsachan054-tech/qdrant-rag-engine.git
cd qdrant-rag-engine/week3/day16

### 2. Python Virtual Environment Banayein
Terminal me run karein:
python -m venv venv

Virtual environment activate karein:
- *Windows:* venv\Scripts\activate
- *Mac/Linux:* source venv/bin/activate

### 3. Required Libraries Install Karein
pip install fastapi uvicorn qdrant-client sentence-transformers groq

(Agar pyproject.toml ya requirements.txt hai, toh pip install -e . ya pip install -r requirements.txt use karein)

### 4. API Keys Setup (.env)
Project folder me ek .env file banayein aur apni keys add karein:
GROQ_API_KEY=your_groq_api_key_here
QDRANT_API_KEY=your_qdrant_api_key_here

### 5. Application Run Karein
Terminal me command run karein:
python app.py

Ab browser me http://127.0.0.1:8000 open karein.