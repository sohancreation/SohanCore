import json
import os
import logging
from datetime import datetime
from pathlib import Path
import difflib
from typing import Any, Dict, List
from .embedding_store import add_memory, query_memories

                   
logger = logging.getLogger(__name__)

                                 
MEMORY_DIR = Path("e:/SohanCore/sohan_ai_agent/memory")
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

            
HISTORY_FILE = MEMORY_DIR / "task_history.json"
PREFS_FILE = MEMORY_DIR / "preferences.json"
LONG_TERM_FILE = MEMORY_DIR / "long_term_memory.json"

def _load_json(file_path):
                                              
    is_list = any(k in str(file_path).lower() for k in ["history", "long", "chat", "experience"])
    default = [] if is_list else {}
    
    if not file_path.exists():
        return default
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            val = json.load(f)
            return val if val is not None else default
    except Exception as e:
        logger.error(f"Error loading {file_path}: {e}")
        return default

def _save_json(file_path, data):
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        logger.error(f"Error saving {file_path}: {e}")
        return False

                         

def store_memory(key_concept: str, data: Any, type: str = "solution"):
    memories = _load_json(LONG_TERM_FILE)
    entry = {
        "id": len(memories) + 1,
        "timestamp": datetime.now().isoformat(),
        "concept": key_concept,
        "data": data,
        "type": type
    }
    memories.append(entry)
    _save_json(LONG_TERM_FILE, memories)
    logger.info(f"Long-term memory stored: {key_concept}")
    try:
        add_memory(label=f"memory:{key_concept}", text=f"{key_concept}\n{data}", meta={"type": type})
    except Exception as e:
        logger.warning(f"Embedding store update failed for long-term memory: {e}")

def retrieve_memory(concept_id: int):
    memories = _load_json(LONG_TERM_FILE)
    for m in memories:
        if m.get("id") == concept_id:
            return m
    return None

def search_similar_tasks(query: str, threshold: float = 0.6) -> list:
    memories = _load_json(LONG_TERM_FILE)
    results = []
    
    query_lower = query.lower()
    for m in memories:
        concept = m.get("concept", "").lower()
                              
        if query_lower in concept or concept in query_lower:
            results.append(m)
            continue
            
                     
        ratio = difflib.SequenceMatcher(None, query_lower, concept).ratio()
        if ratio >= threshold:
            m["relevance"] = ratio
            results.append(m)
            
                       
    return sorted(results, key=lambda x: x.get("relevance", 1.0), reverse=True)

                         

def save_task(prompt, intent, plan, status="success"):
    history = _load_json(HISTORY_FILE)
    entry = {
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt,
        "intent": intent,
        "plan": plan,
        "status": status
    }
    history.append(entry)
    _save_json(HISTORY_FILE, history[-500:])
    
                                                               
    if status == "success" and len(plan) > 2:
        store_memory(prompt, plan, type="learned_plan")

def load_history(limit=10):
    history = _load_json(HISTORY_FILE)
    return history[-limit:] if history else []

def save_preference(key, value):
    prefs = _load_json(PREFS_FILE)
    prefs[key] = value
    _save_json(PREFS_FILE, prefs)

def get_preference(key, default=None):
    prefs = _load_json(PREFS_FILE)
    return prefs.get(key, default)

def get_chat_history(user_id: int, limit: int = 10) -> List[Dict]:
    chat_file = MEMORY_DIR / f"chat_{user_id}.json"
    history = _load_json(chat_file)
    return history[-limit:] if history else []

def add_chat_message(user_id: int, role: str, message: str):
    chat_file = MEMORY_DIR / f"chat_{user_id}.json"
    history = _load_json(chat_file)
    history.append({
        "timestamp": datetime.now().isoformat(),
        "role": role,
        "content": message
    })
                                       
    _save_json(chat_file, history[-20:])
