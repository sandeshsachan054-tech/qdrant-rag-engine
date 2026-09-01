#============================
# PART 1 - IMPORTS AND ENVIRONVENT
#============================

import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams,PointStruct
from sentence_transformers import SentenceTransformer
from groq import Groq

#Load variables from .env

load_dotenv()
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

#=================================
#PART 2 - CONNECT TO QDRANT
#=================================

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)
print("Connected to Qdrant Cloud!")

#==================================
#PART 3 - CREATE QDRANT COLLECTION
#==================================

COLLECTION_NAME="knowledge"
EMBEDDING_SIZE=384

#DELETE COLLECTION IF IT ALREADY EXISTS
if client.collection_exists(COLLECTION_NAME):
    print(f"Deleting existing collection:(COLLECTION_NAME)")
    client.delete_collection(COLLECTION_NAME)

#CREATE COLLECTION
client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(
        size=EMBEDDING_SIZE,
        distance=Distance.COSINE,
    ),
)
print(f"Created collection: {COLLECTION_NAME}")
print("Distance:COSINE")

#===================================
# PART 4- LOAD OUR KNOWLEDGE
#===================================

with open("knowledge.txt", "r", encoding="utf-8") as f:
    documents = [
        line.strip()
        for line in f
        if line.strip()
    ]
    print(f"Loaded{len(documents)}documents)")

#================================
# PART 5 - CREATE EMBEDDINGS
#================================

print("Loading embedding model...")
model=SentenceTransformer("all-MiniLM-L6-V2")
print("Embedding model ready!")
embeddings = model.encode(documents)
print(f"Generated{len(embeddings)}embeddings")
print(f"Embedding size:{len(embeddings[0])}")

#=================================
#PART 6 - CREATE QDRANT POINTS
#=================================

points = []
for i,embedding in enumerate(embeddings):
    point = PointStruct(
        id = i+1, #id=1
        vector = embedding.tolist(),
        payload={
            "text":documents[i]

        }
    )
    points.append(point)

#==================================
#PART 7 - UPLOAD TO QDRANT
#==================================

client.upsert( #upload+insert
    collection_name=COLLECTION_NAME,
    points=points
    )
print(f"uploaded{len(points)}documents to Qdrant!")

#===================================
# PART 8- SEARCH QDRANT
#===================================

def search(query, top_k=3):

    #convert the question into an embedding
    query_vector = model.encode(query).tolist()
    #SEARCH QDRANT FOR SIMILAR VECTORS
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        with_payload =True,
    ).points
    return results

#===================================
# PART 9- TEST SEARCH
#===================================

query = "How many vacation days do i get?"
results = search(query,top_k=3)
print("\nSearch results:")
for result in results:
    print(f"Score:{result.score:.3f}")
    print(result.payload["text"])
    print()

#====================================
# PART 10 - CONNECT TO GROQ
#====================================

groq_client =Groq(
    api_key=GROQ_API_KEY
)

#====================================
#PART 11- ASK THE LLM
#====================================

def ask_llm(question, context):
    prompt = f"""
Answer the question using only the information provided below.
Context:
{context}
Question:
{question}
If the answer is not present in the context, say:
"I do not know based on the provided information."
"""

    
    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-safeguard-20b",
        messages=[
            {
                "role":"user",
                "content": prompt,
            }
        ],
    )
    return response.choices[0].message.content

#========================================
# PART 12- COMPLETE RAG PIPELINE
#========================================

question="Howmany vacation days do I get?"
results = search(question,top_k=3)

#EXTRACT TEXT FROM THE SEARCH RESULTS
context = "\n".join(
    result.payload["text"]
    for result in results
)
answer = ask_llm(question,context)
print ("\nFinal Answer:")
print(answer)