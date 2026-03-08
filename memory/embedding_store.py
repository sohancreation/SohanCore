import json
import math
import sqlite3
import logging
import hashlib
from pathlib import Path
import httpx
import config

logger = logging.getLogger(__name__)

MEMORY_DIR = Path("e:/SohanCore/sohan_ai_agent/memory")
MEMORY_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = MEMORY_DIR / "vector_store.sqlite"

def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            label TEXT,
            text TEXT,
            vector TEXT,
            meta TEXT
        )
    """)
    return conn

def _hash_embed(text: str, dims: int = 128):
    vec = [0.0]*dims
    for tok in text.lower().split():
        idx = int(hashlib.md5(tok.encode("utf-8")).hexdigest()[:8], 16) % dims
        vec[idx] += 1.0
    norm = math.sqrt(sum(x*x for x in vec)) or 1.0
    return [x/norm for x in vec]

def embed_text(text: str):
    text = text.strip()
    if not text:
        return None
    if config.OPENAI_API_KEY:
        try:
            headers = {"Authorization": f"Bearer {config.OPENAI_API_KEY}"}
            payload = {"input": text, "model": "text-embedding-3-small"}
            with httpx.Client(timeout=20) as client:
                resp = client.post("https://api.openai.com/v1/embeddings", json=payload, headers=headers)
            if resp.status_code == 200:
                return resp.json()["data"][0]["embedding"]
            else:
                logger.warning(f"OpenAI embedding failed: {resp.status_code} {resp.text}")
        except Exception as e:
            logger.warning(f"OpenAI embedding exception: {e}")
              
    return _hash_embed(text)

def add_memory(label: str, text: str, meta: dict = None):
    vec = embed_text(text)
    if not vec:
        return False
    try:
        conn = _connect()
        conn.execute(
            "INSERT INTO embeddings (label, text, vector, meta) VALUES (?, ?, ?, ?)",
            (label, text, json.dumps(vec), json.dumps(meta or {}))
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Failed to add embedding: {e}")
        return False

def _cosine(a, b):
    dot = sum(x*y for x, y in zip(a, b))
    na = math.sqrt(sum(x*x for x in a)) or 1.0
    nb = math.sqrt(sum(x*x for x in b)) or 1.0
    return dot / (na*nb)

def query_memories(query: str, top_k: int = 3):
    q_vec = embed_text(query)
    if not q_vec:
        return []
    try:
        conn = _connect()
        rows = conn.execute("SELECT id, label, text, vector, meta FROM embeddings").fetchall()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to read embeddings: {e}")
        return []

    scored = []
    for rid, label, text, vec_json, meta_json in rows:
        try:
            vec = json.loads(vec_json)
            score = _cosine(q_vec, vec)
            scored.append({
                "id": rid,
                "label": label,
                "text": text,
                "meta": json.loads(meta_json) if meta_json else {},
                "score": score
            })
        except Exception:
            continue

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]
