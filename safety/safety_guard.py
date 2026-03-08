import logging
import re
import os
from pathlib import Path

logger = logging.getLogger(__name__)

                              
BLOCKLIST_COMMANDS = [
    r"rm\s+-rf\s+/",                                  
    r"del\s+/s\s+/q\s+c:\\windows",                          
    r"format\s+[a-z]:",                           
    r"mkfs",                                          
    r"dd\s+if=/dev/zero",                     
    r"shutdown\s+/s",                             
    r"reg\s+delete",                                
    r"powershell\s+.*-executionpolicy\s+bypass",                    
    r":\(\)\{ :\|:& \};:",                 
]

SENSITIVE_PATHS = [
    r"c:\\windows",
    r"c:\\program files",
    r"c:\\users\\[^\\]+\\appdata",
    r"/etc/",
    r"/usr/bin/",
]

                                                                     
ALLOWED_PROJECT_ROOT = Path("e:/SohanCore/sohan_ai_agent")

def validate_task(task_dict: dict) -> tuple[bool, str]:
    action = task_dict.get("action", "unknown")
    params = {k: v for k, v in task_dict.items() if k != "action"}
    
                                 
    if action in ["run_command", "build_software"]:
        cmd_text = str(params.get("command", "")) or str(params.get("prompt", ""))
        for pattern in BLOCKLIST_COMMANDS:
            if re.search(pattern, cmd_text, re.IGNORECASE):
                _log_violation(action, cmd_text, "Dangerous command pattern detected.")
                return False, f"DANGEROUS COMMAND BLOCKED: {pattern}"

                               
    paths_to_check = []
    if "path" in params: paths_to_check.append(params["path"])
    if "target" in params: paths_to_check.append(params["target"])
    if "url" in params and "file://" in str(params["url"]): 
        paths_to_check.append(params["url"].replace("file://", ""))

    for p in paths_to_check:
        p_str = str(p).lower()
        
                                              
        for sensitive in SENSITIVE_PATHS:
            if re.search(sensitive, p_str, re.IGNORECASE):
                _log_violation(action, p_str, "Access to sensitive system path blocked.")
                return False, f"PERMISSION DENIED: Cannot access {sensitive}"

                                                                          
        if action in ["delete_file", "write_file", "create_folder"]:
            try:
                target_path = Path(p).resolve()
                base_path = ALLOWED_PROJECT_ROOT.resolve()
                if not str(target_path).startswith(str(base_path)):
                    _log_violation(action, p_str, "Directory traversal / Escape attempt.")
                    return False, "WORKSPACE ESCAPE BLOCKED: You are not allowed to touch files outside SohanCore."
            except:
                pass                                                       

                   
    if action == "open_url":
        url = str(params.get("url", "")).lower()
        if "localhost" in url or "127.0.0.1" in url:
            _log_violation(action, url, "Local network access blocked.")
            return False, "SAFETY BLOCK: Localhost access is restricted."

    return True, "Safe"

def _log_violation(action: str, data: str, reason: str):
    logger.error(f"⚠️ SAFETY VIOLATION ⚠️ | Action: {action} | Reason: {reason} | Data: {data}")
                                                                                         

                             
if __name__ == "__main__":
    dangerous_task = {"action": "run_command", "command": "del /s /q C:\\Windows"}
    safe, msg = validate_task(dangerous_task)
    print(f"Simple Task: {safe} - {msg}")
    
    escape_task = {"action": "write_file", "path": "C:\\Users\\Admin\\Desktop\\virus.txt", "content": "hello"}
    safe, msg = validate_task(escape_task)
    print(f"Escape Task: {safe} - {msg}")
