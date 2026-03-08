import os
import shutil
import logging
from pathlib import Path

                   
logger = logging.getLogger(__name__)

                                                                 
BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "projects"

def _get_safe_path(requested_path: str) -> Path:
    try:
        req_path = Path(requested_path)
        
                                
        if not BASE_DIR.exists():
            BASE_DIR.mkdir(parents=True, exist_ok=True)
            
                      
        if not req_path.is_absolute():
            target = (BASE_DIR / req_path).resolve()
        else:
            target = req_path.resolve()
            
        base = BASE_DIR.resolve()
        
                                                                  
        if base in target.parents or target == base:
            return target
            
                                                                                   
        logger.warning(f"Path escape attempt blocked: {requested_path}. Forcing to projects.")
        return base / req_path.name
    except Exception as e:
        logger.error(f"Path resolution error: {e}")
        return BASE_DIR / "error_file.txt"

def create_folder(path: str):
    try:
        target_path = _get_safe_path(path)
        os.makedirs(target_path, exist_ok=True)
        logger.info(f"Directory created: {target_path}")
        return {"status": "success", "message": f"Folder created at {target_path}"}
    except Exception as e:
        logger.error(f"Failed to create directory {path}: {e}")
        return {"status": "error", "message": str(e)}

def write_file(file_path: str, content: str):
    try:
        target_path = _get_safe_path(file_path)
                                         
        os.makedirs(target_path.parent, exist_ok=True)
        
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"File written successfully: {target_path}")
        return {"status": "success", "message": f"File written to {target_path}"}
    except Exception as e:
        logger.error(f"Failed to write file {file_path}: {e}")
        return {"status": "error", "message": str(e)}

def read_file(file_path: str):
    try:
        target_path = _get_safe_path(file_path)
        if not target_path.exists():
            return {"status": "error", "message": "File not found."}
            
        with open(target_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"status": "success", "content": content}
    except Exception as e:
        logger.error(f"Failed to read file {file_path}: {e}")
        return {"status": "error", "message": str(e)}

def list_dir(directory_path: str = "."):
    try:
        target_path = _get_safe_path(directory_path)
        if not target_path.exists():
            return {"status": "error", "message": "Directory not found."}
        
        items = os.listdir(target_path)
        return {"status": "success", "items": items}
    except Exception as e:
        logger.error(f"Failed to list directory {directory_path}: {e}")
        return {"status": "error", "message": str(e)}

def delete_file(file_path: str):
    try:
        target_path = _get_safe_path(file_path)
        if target_path.is_file():
            os.remove(target_path)
            logger.info(f"File deleted: {target_path}")
        elif target_path.is_dir():
            shutil.rmtree(target_path)
            logger.info(f"Directory deleted: {target_path}")
        else:
            return {"status": "error", "message": "Target does not exist."}
            
        return {"status": "success", "message": f"Deleted {target_path}"}
    except Exception as e:
        logger.error(f"Failed to delete {file_path}: {e}")
        return {"status": "error", "message": str(e)}

def search_files(query: str):
    try:
        results = []
                                              
        for path in BASE_DIR.rglob(f"*{query}*"):
            results.append(str(path.relative_to(BASE_DIR)))
        
        if results:
            return {"status": "success", "message": f"Found {len(results)} matches.", "files": results[:20]}
        else:
            return {"status": "error", "message": "No matching files found."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
