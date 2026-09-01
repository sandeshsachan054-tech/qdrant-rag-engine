import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
from groq import Groq

app = FastAPI()

# Frontend se request allow karne ke liye CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Candidate Profile Data
CANDIDATE_DATA = {
    "name": "Sandesh Kumar",
    "education": "B.Tech in Computer Science (Artificial intelligence and machine learning(2023-2027)",
    "cgpa": "7.8",
    "skills": ["Python", "FastAPI", "React", "LangChain", "LLMs", "SQL"],
    "projects": [
        {
            "title": "AI Personal Assistant",
            "tech": "FastAPI, Groq, React",
            "description": "An AI chatbot that answers questions based on personal candidate data with zero hallucination."
        },
        {
            "title": "E-commerce Recommendation System",
            "tech": "Python, Scikit-learn",
            "description": "Collaborative filtering recommendation engine for online stores."
        }
    ],
    "experience": "AI Intern at TechCorp (6 Months) - Built LLM wrappers and prompt pipelines.",
    "certifications": ["DeepLearning.AI Prompt Engineering", "AWS Certified Cloud Practitioner"],
    "links": {
        "github": "https://github.com/example",
        "linkedin": "https://linkedin.com/in/example"
    }
}

# 2. System Prompt Engineering
SYSTEM_PROMPT = f"""
You are the official AI Portfolio Assistant for {CANDIDATE_DATA['name']}.
Your task is to answer recruiters and visitors professionally and honestly using ONLY the information provided below.

RULES:
1. Do NOT make up any information (No Hallucinations).
2. If the user asks something not present in the data, politely say: "I don't have that information in my profile."
3. Be professional, concise, and helpful.

Candidate Profile Data:
{CANDIDATE_DATA}
"""

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

@app.post("/chat")
async def chat_stream(request: ChatRequest):
    try:
        # History ke saath system prompt attach karna (Memory support)
        full_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in request.messages:
            full_messages.append({"role": msg.role, "content": msg.content})

        def generate():
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=full_messages,
                stream=True,
            )
            for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    yield content

        return StreamingResponse(generate(), media_type="text/plain")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)