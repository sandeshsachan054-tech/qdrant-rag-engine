import os
import yt_dlp
import whisper
import json

# 1. Download Audio from Playlist
def download_playlist_audio(playlist_url, output_dir="audios"):
    os.makedirs(output_dir, exist_ok=True)
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_dir}/%(id)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=True)
        return [entry['id'] for entry in info['entries'] if entry]

# 2. Transcribe Audio using Whisper GPU
def transcribe_and_chunk(video_ids, audio_dir="audios"):
    model = whisper.load_model("base") # ya 'small' / 'medium' GPU ke hisaab se
    all_chunks = []

    for vid in video_ids:
        audio_path = f"{audio_dir}/{vid}.mp3"
        if not os.path.exists(audio_path):
            continue
            
        print(f"Transcribing: {vid}...")
        result = model.transcribe(audio_path, verbose=False)
        
        # Segment chunking (whisper timestamps provide karta hai)
        for seg in result['segments']:
            start_time = int(seg['start'])
            text = seg['text'].strip()
            
            # YouTube timestamp link format: https://youtu.be/<id>?t=<seconds>
            chunk_data = {
                "video_id": vid,
                "text": text,
                "start_time": start_time,
                "timestamp_url": f"https://youtu.be/{vid}?t={start_time}"
            }
            all_chunks.append(chunk_data)

    # Save to JSON
    with open("transcribed_chunks.json", "w") as f:
        json.dump(all_chunks, f, indent=2)
    return all_chunks

import json
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct

def setup_vector_db():
    # Model: mini LM (all-MiniLM-L6-v2)
    embed_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Local In-Memory Qdrant DB ya Docker instance
    client = QdrantClient(path="./qdrant_db_new")
    collection_name = "dsa_playlist"

    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

    with open("transcribed_chunks.json", "r") as f:
        chunks = json.load(f)

    points = []
    for idx, chunk in enumerate(chunks):
        vector = embed_model.encode(chunk['text']).tolist()
        points.append(
            PointStruct(
                id=idx,
                vector=vector,
                payload={
                    "video_id": chunk['video_id'],
                    "text": chunk['text'],
                    "start_time": chunk['start_time'],
                    "url": chunk['timestamp_url']
                }
            )
        )

    # Batch upload
    client.upsert(collection_name=collection_name, points=points)
    print("All chunks successfully uploaded to Qdrant!")

# setup_vector_db()
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from openai import OpenAI

# Initialize
embed_model = SentenceTransformer('all-MiniLM-L6-v2')
qdrant = QdrantClient(path="./qdrant_db")
openai_client = OpenAI(api_key="YOUR_OPENAI_OR_CLAUDE_API_KEY")

def ask_rag_pipeline(user_query):
    # 1. Convert user query to vector
    query_vector = embed_model.encode(user_query).tolist()

    # 2. Search Top 3 relevant matches in Qdrant
    search_results = qdrant.search(
        collection_name="dsa_playlist",
        query_vector=query_vector,
        limit=3
    )

    # 3. Format context with timestamps
    context = ""
    for hit in search_results:
        context += f"\n- Text: {hit.payload['text']}\n  Video Link: {hit.payload['url']}\n"

    # 4. LLM Prompting
    prompt = f"""
    You are an AI assistant helping students navigate a DSA playlist.
    Answer the user's question based strictly on the provided video context.
    Always provide the exact video link with the timestamp so the user can watch it.

    Context:
    {context}

    User Question: {user_query}
    """

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

# Example Run:
# print(ask_rag_pipeline("Where is binary search explained?"))