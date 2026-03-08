import json
import logging
import datetime
import difflib
import os
from pathlib import Path
from .embedding_store import add_memory

                   
logger = logging.getLogger(__name__)

                                 
MEMORY_DIR = Path("e:/SohanCore/sohan_ai_agent/memory")
MEMORY_DIR.mkdir(parents=True, exist_ok=True)
EXP_DB_FILE = MEMORY_DIR / "experience_db.json"

def _load_db():
    if not EXP_DB_FILE.exists():
        return []
    try:
        with open(EXP_DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading experience DB: {e}")
        return []

def _save_db(db):
    try:
        with open(EXP_DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving experience DB: {e}")

def store_experience(task, steps, result, errors=None, solution=None):
    db = _load_db()
    entry = {
        "task": task.lower().strip(),
        "steps": steps,
        "result": result,                         
        "errors": errors or [],
        "solution": solution or steps,                                        
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    db.append(entry)
    _save_db(db)
    logger.info(f"Experience stored for task: '{task}' (Result: {result})")
    try:
        summary_text = f"Task: {task}\nResult: {result}\nSteps: {steps}\nErrors: {errors or []}"
        add_memory(label=f"task:{task}", text=summary_text, meta={"result": result})
    except Exception as e:
        logger.warning(f"Embedding store update failed: {e}")

def search_similar_tasks(task_description, threshold=0.95):
    db = _load_db()
    if not db:
        return None

                                                
    past_tasks = [entry["task"] for entry in db if entry["result"] == "success"]
    if not past_tasks:
        return None

                                           
    matches = difflib.get_close_matches(task_description.lower().strip(), past_tasks, n=1, cutoff=threshold)
    
    if matches:
        best_match = matches[0]
                                                 
        for entry in db:
            if entry["task"] == best_match and entry["result"] == "success":
                logger.info(f"Found similar past task: '{best_match}'")
                return entry
    return None

def suggest_solution(task_description):
    similar_exp = search_similar_tasks(task_description)
    if similar_exp:
        logger.info(f"Suggesting learned solution for: '{task_description}'")
        return similar_exp.get("solution") or similar_exp.get("steps")
    return None

def update_experience_with_fix(task, error, fix):
    db = _load_db()
                                                
    for entry in reversed(db):
        if entry["task"] == task.lower().strip():
            entry["errors"].append(error)
            entry["solution"] = fix                                     
            entry["result"] = "success"                                 
            _save_db(db)
            logger.info(f"Learned fix for error in task '{task}': {error[:50]}...")
            return True
    
                                                                 
    store_experience(task, [], "success", errors=[error], solution=fix)
    return True

                                     
                                             
                                                                                                        

                                       
                                                  
                                              
