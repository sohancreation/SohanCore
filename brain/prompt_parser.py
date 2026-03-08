import json
import logging
import os
import sys
import re
from utils.llm_client import call_llm

                                               
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

logger = logging.getLogger(__name__)

                                               
RE_VOLUME = re.compile(r"(?:volume|vlume|volum|sound|audio)\s+(?:to\s+|at\s+)?(\d+)", re.I)
RE_VOLUME_DELTA = re.compile(r"(?:volume|vlume|volum|sound|audio)\s+(up|down|increase|decrease|louder|quieter|lower|higher)(?:\s+by\s+(\d+))?", re.I)
RE_MUTE = re.compile(r"\b(mute|silence|silent|quiet)\b", re.I)
RE_UNMUTE = re.compile(r"\b(unmute|sound on|audio on|turn on sound|turn sound on)\b", re.I)
RE_GET_VOLUME = re.compile(r"\b(volume level|what.*volume|current.*volume|check.*volume|what.*sound|current.*sound)\b", re.I)
RE_BRIGHTNESS = re.compile(r"(?:brightness|light)\s+(?:to\s+|at\s+)?(\d+)", re.I)
RE_SEARCH = re.compile(r"(?:search|google|find|look up|lookup|info on)\s+(?:for\s+)?(.+)", re.I)
RE_OPEN = re.compile(r"(?:open|start|launch|visit|browse)\s+(?:the\s+)?([^,;.]+)", re.I)
RE_CLICK = re.compile(r"click\s+(?:on\s+)?(?:the\s+)?([^,;.]+)", re.I)
RE_STATS = re.compile(r"(?:system\s+)?(?:stats|health|performance|usage|cpu|ram|battery|disk)", re.I)
RE_PROCESSES = re.compile(r"(?:list|show|active)\s+processes", re.I)
RE_KILL = re.compile(r"(?:kill|terminate|stop|end|shutdown|close)\s+(?:the\s+)?(?:process\s+)?([^,;.]+)", re.I)
RE_WEATHER = re.compile(r"weather\s+(?:in|for|at)\s+([a-zA-Z\s]+)", re.I)
RE_POWER = re.compile(r"(shutdown|restart|lock|sleep)\s+(?:my\s+)?(?:pc|computer|system)", re.I)
RE_FILE_SEARCH = re.compile(r"(?:find|search|look\s+for)\s+(?:file\s+)?([^,;.]+)", re.I)

def fallback_parse(user_text: str) -> dict:
    user_text_lower = user_text.lower()
    
                                     
    whatsapp_keywords = ["whatsapp", "message", "msg", "text"]
    email_keywords = ["email", "mail", "send mail"]
    
                                   
                                                                
    if any(k in user_text_lower for k in email_keywords):
        target_email = re.search(r"([\w\.-]+@[\w\.-]+\.\w+)", user_text)
        if target_email:
            to = target_email.group(1).strip()
                                                            
            subject = ""
            if "subject" in user_text_lower:
                sub_part = re.split(r"subject[:\s]+", user_text, flags=re.I)[-1]
                subject = re.split(r"\s+(?:and\s+)?body", sub_part, flags=re.I)[0].strip(" ,-:;")
            
            body = ""
                                                
            if "body" in user_text_lower:
                body = re.split(r"body[:\s]+", user_text, flags=re.I)[-1].strip(" ,-:;")
                                                                                
            elif any(kw in user_text_lower for kw in ["elaborate on", "about", "regarding", "telling him", "telling her"]):
                body = re.split(r"(?:elaborate on|about|regarding|telling him|telling her)\s+", user_text, flags=re.I)[-1].strip(" ,-:;")
                                                    
            elif "saying" in user_text_lower or "say" in user_text_lower:
                body = re.split(r"(?:saying|say)\s+", user_text, flags=re.I)[-1].strip(" ,-:;")
            
                                                                        
            if not subject and not body:
                parts = user_text.split(to, 1)
                if len(parts) > 1:
                    body = parts[1].strip(" ,-:;?")
            
            return {"intent": "messaging_action", "parameters": {"action": "send_email", "to": to, "subject": subject, "body": body}}

                                      
    if any(k in user_text_lower for k in whatsapp_keywords):
        phone_match = re.search(r"(\+?[\d\s\-]{8,})", user_text)
                                    
        name_match = re.search(r"(?:to\s+)([a-zA-Z\s]+?)\s*(?:saying|say|tell|with|message|elaborate|about|$)", user_text, re.I)
        
        phone_val = ""
        if phone_match: phone_val = phone_match.group(1).strip()
        elif name_match: phone_val = name_match.group(1).strip()
        
        if phone_val:
            text_part = user_text.split(phone_val)[-1].strip(" ,-:;?")
            text_part = re.sub(r"^(?:saying|say|tell|with message|message|write|about|generate|draft|elaborate|send|and)\s+", "", text_part, flags=re.I).strip()
            if not text_part: text_part = "Hello!"
            return {"intent": "messaging_action", "parameters": {"action": "send_whatsapp", "phone": phone_val, "text": text_part}}

                              
    if "read" in user_text_lower and "screen" in user_text_lower:
        return {"intent": "vision_action", "parameters": {"action": "read_screen"}}
        
                              
    if any(word in user_text_lower for word in ["screenshot", "screnshot", "screnshoot", "screen shot"]):
        return {"intent": "vision_action", "parameters": {"action": "take_screenshot"}}
    
                        
    click_match = RE_CLICK.search(user_text)
    if click_match:
        return {"intent": "vision_action", "parameters": {"action": "vision_click", "text": click_match.group(1).strip()}}

                                      
                       
    unmute_match = RE_UNMUTE.search(user_text)
    if unmute_match:
        return {"intent": "system_control", "parameters": {"action": "unmute_volume"}}
    
    if RE_MUTE.search(user_text) and not RE_VOLUME.search(user_text):
        return {"intent": "system_control", "parameters": {"action": "mute_volume"}}
    
    vol_match = RE_VOLUME.search(user_text)
    if vol_match: return {"intent": "system_control", "parameters": {"action": "set_volume", "level": int(vol_match.group(1))}}
    
    vol_delta = RE_VOLUME_DELTA.search(user_text)
    if vol_delta:
        direction = vol_delta.group(1).lower()
        amount = int(vol_delta.group(2)) if vol_delta.group(2) else 10
        delta = amount if direction in ("up", "increase", "louder", "higher") else -amount
        return {"intent": "system_control", "parameters": {"action": "adjust_volume", "delta": delta}}
    
    if RE_GET_VOLUME.search(user_text):
        return {"intent": "system_control", "parameters": {"action": "get_volume"}}
    
    bri_match = RE_BRIGHTNESS.search(user_text)
    if bri_match: return {"intent": "system_control", "parameters": {"action": "set_brightness", "level": int(bri_match.group(1))}}

                         
    search_match = RE_SEARCH.search(user_text)
    if search_match:
        query = search_match.group(1).strip()
        query = re.sub(r"^(?:google|web|internet|about|me|the|for|info on|info)\s+", "", query, flags=re.I)
        return {"intent": "web_automation", "parameters": {"action": "search_google", "query": query.strip()}}

                                                                    
    build_triggers = ["build ", "create ", "develop ", "code ", "write a program", "make an app", "make a game"]
    if any(trigger in user_text_lower for trigger in build_triggers) and any(kw in user_text_lower for kw in ["a ", "an ", "project", "software", "app", "game", "program", "tool", "script"]):
        return {"intent": "software_engineering", "parameters": {"action": "build_software", "prompt": user_text}}
        
                                                             
    agent_triggers = ["advanced agent", "figure out", "solve", "auto agent", "openclaw", "autonomous", "super agent", "agentic"]
    if any(trigger in user_text_lower for trigger in agent_triggers) or (len(user_text.split()) > 8 and "I want" in user_text):
        return {"intent": "agent_execution", "parameters": {"action": "run_agentic_loop", "prompt": user_text}}
        
                       
    open_match = RE_OPEN.search(user_text)
    if open_match:
        target = open_match.group(1).split(" and ")[0].strip()
        if "." in target or "http" in target or "www" in target:
            return {"intent": "web_automation", "parameters": {"action": "open_url", "url": target}}
        return {"intent": "desktop_action", "parameters": {"action": "open_app", "target": target}}

                                 
    stats_match = RE_STATS.search(user_text)
    if stats_match: return {"intent": "system_monitor", "parameters": {"action": "get_stats"}}
    
    proc_match = RE_PROCESSES.search(user_text)
    if proc_match: return {"intent": "system_monitor", "parameters": {"action": "list_procs"}}
    
    power_match = RE_POWER.search(user_text)
    if power_match: return {"intent": "system_control", "parameters": {"action": "power_action", "sub_action": power_match.group(1).lower()}}

    file_match = RE_FILE_SEARCH.search(user_text)
    if file_match and "file" in user_text_lower:
        return {"intent": "file_action", "parameters": {"action": "search_files", "query": file_match.group(1).strip()}}

    weather_match = RE_WEATHER.search(user_text)
    if weather_match:
        return {"intent": "web_automation", "parameters": {"action": "get_weather", "city": weather_match.group(1).strip()}}

    kill_match = RE_KILL.search(user_text)
    if kill_match:
        target_proc = kill_match.group(1).strip()
        if target_proc and not any(kw in target_proc.lower() for kw in ["task", "operation", "bot", "agent"]):
            return {"intent": "system_monitor", "parameters": {"action": "kill_proc", "target": target_proc}}

    return {"intent": "general_request", "parameters": {}}

async def parse_prompt(user_text: str, history: list = None) -> dict:
                             
    fast_result = fallback_parse(user_text)
    if fast_result.get("intent") != "general_request":
        fast_result["original_prompt"] = user_text
        return fast_result

                                                
    try:
        system_instruction = "Extract intent (desktop_action, complex_task, system_control, web_automation, vision_action, messaging_action) as JSON. If messaging_action, provide action ('send_email' or 'send_whatsapp') and relevant parameters like 'to', 'subject', 'body' or 'phone', 'text'. Consider the shared chat history if the current prompt is a follow-up."
        response_text = await call_llm(user_text, system_instruction, response_format="json", history=history)
        if not response_text: return {"original_prompt": user_text, "intent": "general_request"}
        data = json.loads(response_text)
        data["original_prompt"] = user_text
        return data
    except:
        return {"original_prompt": user_text, "intent": "general_request"}
