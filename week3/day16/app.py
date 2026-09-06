import os
import glob
import json
import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.responses import HTMLResponse
# import whisper
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from groq import Groq
load_dotenv()

# ================= CONFIGURATION =================
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
COLLECTION_NAME = "dsa_playlist"
AUDIO_DIR = "audios"
# =================================================

def transcribe_downloaded_audios():
    if os.path.exists("transcribed_chunks.json"):
        print("transcribed_chunks.json pehle se maujood hai. Use load kar rahe hain...")
        with open("transcribed_chunks.json", "r", encoding="utf-8") as f:
            return json.load(f)

    print("--- 1. Whisper se Audio Transcribe ho raha hai ---")
    model = whisper.load_model("base")
    audio_files = glob.glob(f"{AUDIO_DIR}/*.mp3")
    all_chunks = []
    if os.path.exists("transcribed_chunks.json"):
        with open("transcribed_chunks.json", "r", encoding="utf-8") as f:
            all_chunks = json.load(f)
    
    # Jo video IDs pehle hi process ho chuke hain unka set
    processed_vids = {chunk["video_id"] for chunk in all_chunks}

    print(f"Total files: {len(audio_files)}")

    for idx, audio_path in enumerate(audio_files):
        filename = os.path.basename(audio_path)
        vid = os.path.splitext(filename)[0]

        # --- YEH CHECK ADD KIYA HAI (Line 36 ke aas-paas) ---
        if vid in processed_vids:
            print(f"[{idx+1}/{len(audio_files)}] Skipping (Already done): {vid}")
            continue

        print(f"[{idx+1}/{len(audio_files)}] Processing: {vid}")
        try:
            result = model.transcribe(audio_path, verbose=False)
            for seg in result.get('segments', []):
                start_sec = int(seg['start'])
                text = seg['text'].strip()
                if len(text) < 5:
                    continue
                all_chunks.append({
                    "video_id": vid,
                    "text": text,
                    "start_time": start_sec,
                    "timestamp_url": f"https://youtu.be/{vid}?t={start_sec}"
                })
            
            # --- HAR VIDEO KE BAAD SAVE KAREGA ---
            with open("transcribed_chunks.json", "w", encoding="utf-8") as f:
                json.dump(all_chunks, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Error in {vid}: {e}")

    return all_chunks

def build_vector_db(chunks):
    print("--- 2. Qdrant Vector Database ban raha hai ---")
    embed_model = SentenceTransformer('all-MiniLM-L6-v2')
    client = QdrantClient(path="./qdrant_db_new")

    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

    points = []
    for idx, chunk in enumerate(chunks):
        vector = embed_model.encode(chunk['text']).tolist()
        points.append(
            PointStruct(
                id=idx,
                vector=vector,
                payload=chunk
            )
        )

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print("Database indexing complete!")

app = FastAPI()
embed_model = SentenceTransformer('all-MiniLM-L6-v2')
qdrant = QdrantClient(path="./qdrant_db_new")

HTML_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Lecture Search - Padho with RAG</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: sans-serif; }
        body { background-color: #0f1117; color: #e1e4ea; display: flex; flex-direction: column; height: 100vh; }
        .top-nav { height: 50px; background: #161822; border-bottom: 1px solid #232738; display: flex; align-items: center; padding: 0 25px; gap: 20px; font-size: 13px; color: #8f96a3; }
        .container { display: flex; flex: 1; padding: 20px; gap: 20px; height: calc(100vh - 50px); }
        .left-col { flex: 1.2; display: flex; flex-direction: column; gap: 15px; }
        .right-col { flex: 1.2; background: #000; border-radius: 12px; overflow: hidden; border: 1px solid #232738; display: flex; }
        .search-bar { display: flex; gap: 10px; }
        .search-bar input { flex: 1; padding: 14px 18px; border-radius: 8px; border: 1px solid #2e3449; background: #1a1d29; color: #fff; font-size: 15px; outline: none; }
        .search-bar button { padding: 0 24px; border-radius: 8px; border: none; background: #ff7a00; color: #fff; font-weight: bold; cursor: pointer; }
        .results-box { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; }
        .card { background: #161822; border: 1px solid #232738; padding: 14px 18px; border-radius: 8px; cursor: pointer; }
        .card:hover { border-color: #ff7a00; background: #1c202d; }
        .card-header { display: flex; justify-content: space-between; margin-bottom: 6px; }
        .card-idx { font-weight: bold; color: #ff7a00; }
        .card-time { background: #ff7a00; color: #000; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .card-text { font-size: 13px; color: #a0a6b5; line-height: 1.4; }
        .llm-summary { background: #1a1d29; border: 1px solid #2e3449; padding: 12px; border-radius: 8px; font-size: 14px; margin-bottom: 5px; }
        iframe { width: 100%; height: 100%; border: none; }
    </style>
</head>
<body>
    <div class="top-nav">
        <span>● Active Playlist Indexed</span>
        <span>⚡ Instant Moment Search</span>
    </div>
    <div class="container">
        <div class="left-col">
            <div class="search-bar">
                <input type="text" id="query" placeholder="Topic search karein (e.g. sliding window, binary search)..." onkeypress="if(event.key==='Enter') doSearch()">
                <button onclick="doSearch()">Search</button>
            </div>
            <div id="llmBox" class="llm-summary" style="display:none;"></div>
            <div class="results-box" id="results"></div>
        </div>
        <div class="right-col">
            <iframe id="videoPlayer" src="" allowfullscreen allow="autoplay"></iframe>
        </div>
    </div>
   <script>
    async function doSearch() {
        const query = document.getElementById('query').value.trim();
        if (!query) return;
        document.getElementById('llmBox').style.display = 'block';
        document.getElementById('llmBox').innerText = 'Generating answer...';
        
        const res = await fetch('/api/search?q=' + encodeURIComponent(query));
        const data = await res.json();
        document.getElementById('llmBox').innerText = data.answer;
        
        const list = document.getElementById('results');
        list.innerHTML = '';
        
        data.results.forEach((item, idx) => {
            const mins = Math.floor(item.start_time / 60);
            const secs = item.start_time % 60;
            const timeStr = mins + ':' + (secs < 10 ? '0' : '') + secs;
            const card = document.createElement('div');
            card.className = 'card';
            card.innerHTML = '<div class="card-header"><span class="card-idx">Match ' + (idx + 1) + '</span><span class="card-time">' + timeStr + '</span></div><div class="card-text">' + item.text + '</div>';
            card.onclick = () => {
                document.getElementById('videoPlayer').src = 'https://www.youtube.com/embed/' + item.video_id + '?start=' + item.start_time + '&autoplay=1';
            };
            list.appendChild(card);
        });

        if (data.results.length > 0) {
            document.getElementById('videoPlayer').src = 'https://www.youtube.com/embed/' + data.results[0].video_id + '?start=' +data.results[0].start_time + '&autoplay=1';
        }
    }
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def get_index():
    return HTML_UI

@app.get("/api/search")
def api_search(q: str):
    query_vector = embed_model.encode(q).tolist()
    response = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=5
    )
    hits = response.points
    results = []
    context = ""
    for hit in hits:
        results.append(hit.payload)
        context += f"\\n- [{hit.payload['start_time']}s]: {hit.payload['text']}"

    prompt = f"Answer clearly in Hinglish where this topic is explained based on context:\\nContext:{context}\\nQuestion:{q}"
    resp = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}]
    )
    return {
        "answer": resp.choices[0].message.content,
        "results": results
    }

if __name__ == "__main__":
    with open("transcribed_chunks.json", "r", encoding="utf-8") as f:
        import json
        chunks = json.load(f)
    #build_vector_db(chunks)
    print("\n🚀 UI Server Live: http://127.0.0.1:8000\n")
    uvicorn.run(app, host="127.0.0.1", port=8000)