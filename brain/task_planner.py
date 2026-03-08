import json
import logging
import os
import sys
import re
from utils.llm_client import call_llm
from ai_engineer.content_generator import generate_text

                                               
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

logger = logging.getLogger(__name__)

def _sync_fallback_plan(parsed_task: dict) -> list[dict]:
                                                    
    pass

async def fallback_plan(parsed_task: dict) -> list[dict]:
    intent = parsed_task.get('intent', 'unknown')
    params = parsed_task.get('parameters', {})
    original_prompt = parsed_task.get('original_prompt', '')
    original_prompt_lower = original_prompt.lower()
    
                             
    if intent == "software_engineering":
        return [{"action": "build_software", "prompt": original_prompt}]
        
                         
    if intent == "agent_execution":
        return [{"action": "run_agentic_loop", "prompt": original_prompt}]
        
                                      
    if intent == "messaging_action":
        if "action" not in params:
            if "whatsapp" in original_prompt_lower: params["action"] = "send_whatsapp"
            elif "email" in original_prompt_lower or "mail" in original_prompt_lower: params["action"] = "send_email"
            else: params["action"] = "reply"
            
                                           
        text_val = params.get("text") or params.get("body") or ""
        elaboration_triggers = ["elaborate", "generate", "write a", "compose", "draft", "professional", "detail", "about", "regarding"]
        
        if any(tr in original_prompt_lower for tr in elaboration_triggers) or len(text_val) > 5:
            try:
                logger.info("Generating automated professional message content...")
                system_instruction = "You are a world-class personal assistant. Draft a highly professional, well-formatted, and detailed message. Output ONLY the raw message string, nothing else. No surrounding quotes."
                user_query = f"User Intent: {original_prompt}\nSubject/Topic: {text_val}\nPlease draft the full message to send:"
                draft = await call_llm(user_query, system_instruction)
                
                if draft and len(draft) > 10:
                    if "text" in params: params["text"] = draft.strip()
                    if "body" in params: params["body"] = draft.strip()
                else:
                    raise Exception("LLM returned insufficient text")
            except Exception as e:
                logger.error(f"AI Elaboration failed using rule-based fallback: {e}")
                                                
                topic = text_val if text_val else "the requested matter"
                if "bangladesh economy" in original_prompt_lower:
                    topic_text = "The economy of Bangladesh is currently in a transformative phase, showing significant resilience and growth potential in the South Asian region. Key sectors like garments and textiles continue to lead exports, while infrastructure development and digital expansion are creating new opportunities for trade and investment."
                else:
                    topic_text = f"the current status and relevant details regarding {topic}"
                
                fallback_draft = f"Dear recipient,\n\nI hope this message finds you well. I am writing to provide you with a detailed update and elaborate on {topic_text}.\n\nIt is important to note that recent developments have highlighted several key areas of interest. We are closely monitoring the situation to ensure all objectives are met effectively and that you remain informed of any significant progression.\n\nPlease let me know if you would like to discuss this further or if you require additional specifics on any particular aspect.\n\nWarm regards,\nSohan's Personal AI Assistant"
                
                if "text" in params: params["text"] = fallback_draft
                if "body" in params: params["body"] = fallback_draft
                
        return [params]
    
                                             
                                                                                               
                                                                               
    research_triggers = ["research", "deep dive into", "google for"]
    search_keywords = ["search google for", "find online", "look up on web"]
    
    if any(tr in original_prompt_lower for tr in research_triggers) or \
       any(word in original_prompt_lower for word in search_keywords):
        
        query = params.get("query")
        if not query:
             for word in research_triggers + search_keywords:
                  if word in original_prompt_lower:
                      parts = original_prompt_lower.split(word, 1)
                      if len(parts) > 1:
                          query = parts[1].strip()
                          break
        if not query: query = original_prompt
        query = re.sub(r"^(?:for|about|the|web|google|info|me)\s+", "", query, flags=re.IGNORECASE).strip()
        
        return [
            {"action": "search_google", "query": query},
            {"action": "wait", "seconds": 2},
            {"action": "read_screen"},
            {"action": "reply", "message": f"I'm researching '{query}' for you. I'll read the results and provide an elaborated summary."}
        ]
    
                                
    if "open" in original_prompt_lower and ("." in original_prompt or "www" in original_prompt or "http" in original_prompt):
        url = params.get("url") or original_prompt
        url = url.lower().replace("open", "").strip()
        return [{"action": "open_url", "url": url}]

                        
    if intent == "desktop_action" or "open" in original_prompt_lower:
        target = params.get("target") or original_prompt_lower.replace("open", "").strip()
        if target:
            return [{"action": "open_app", "target": target}, {"action": "wait", "seconds": 3}]

                        
    if any(k in original_prompt_lower for k in ["volume", "vlume", "volum", "sound", "audio"]):
        level_match = re.search(r"(\d+)", original_prompt_lower)
        return [{"action": "set_volume", "level": int(level_match.group(1)) if level_match else 50}]
        
    if "brightness" in original_prompt_lower:
        level_match = re.search(r"(\d+)", original_prompt_lower)
        return [{"action": "set_brightness", "level": int(level_match.group(1)) if level_match else 50}]

                       
    if intent == "vision_action" or "click" in original_prompt_lower:
        action = params.get("action")
        if "click" in original_prompt_lower:
            target = original_prompt_lower.split("click", 1)[1].replace("on", "").replace("the", "").strip()
            if not target and params.get("text"): target = params["text"]
            if target:
                return [{"action": "vision_click", "text": target}]
        
        if action == "read_screen": return [{"action": "read_screen"}]
        if action == "vision_click": return [{"action": "vision_click", "text": params.get("text")}]
        if action == "take_screenshot": return [{"action": "take_screenshot", "file": "screenshot.png"}]

                          
    if intent == "system_monitor":
        action = params.get("action")
        if action == "get_stats": return [{"action": "get_stats"}]
        if action == "list_procs": return [{"action": "list_procs"}]
        if action == "kill_proc": return [{"action": "kill_proc", "target": params.get("target")}]

                                 
    if intent == "system_control":
        action = params.get("action")
        if "bluetooth" in original_prompt_lower:
            state = "off" not in original_prompt_lower
            return [{"action": "toggle_bluetooth", "state": state}]
        if "wifi" in original_prompt_lower:
            state = "off" not in original_prompt_lower
            return [{"action": "toggle_wifi", "state": state}]
        if action == "power_action":
            return [{"action": "power_action", "sub_action": params.get("sub_action")}]
            
                     
    if intent == "file_action":
        action = params.get("action")
        if action == "search_files":
            return [{"action": "search_files", "query": params.get("query")}]

                
    if action == "get_weather":
        return [{"action": "get_weather", "city": params.get("city")}]

    return []                                      

from memory.memory_manager import get_chat_history, add_chat_message
from memory.experience_learning import suggest_solution

async def plan_task(parsed_task: dict, user_id: int = None) -> list[dict]:
    intent = parsed_task.get('intent', 'unknown')
    original_prompt = parsed_task.get('original_prompt', '')
    logger.info(f"Asynchronous planning for: {original_prompt}")

                                                           
    if intent == "general_request":
        history = get_chat_history(user_id) if user_id else []
        system_instruction = f"You are {config.AGENT_NAME}, a helpful, friendly, and highly capable personal assistant. You now have 'OpenClaw Mode' enabled â€“ a super-advanced autonomous reasoning engine. You can control the user's computer, look at the screen (Vision), search the web, and build software. Respond naturally. If the user has a complex goal, suggest using your 'Autonomous mode' by asking for it."
        
        ai_response = await call_llm(original_prompt, system_instruction, history=history)
        if user_id: add_chat_message(user_id, "user", original_prompt)
        if user_id: add_chat_message(user_id, "assistant", ai_response)
        
        return [{"action": "reply", "message": ai_response}]

    learned_solution = suggest_solution(original_prompt)
    if learned_solution:
        is_valid_match = True
        prompt_lower = original_prompt.lower()
        prompt_level_match = re.search(r"(\d+)", prompt_lower)
        prompt_level = int(prompt_level_match.group(1)) if prompt_level_match else None

        wants_brightness = any(k in prompt_lower for k in ["brightness", "light"])
        wants_volume = any(k in prompt_lower for k in ["volume", "sound", "audio", "vlume", "volum"])
        has_brightness_step = any(step.get("action") == "set_brightness" for step in learned_solution)
        has_volume_step = any(step.get("action") == "set_volume" for step in learned_solution)

        for step in learned_solution:
            if step.get("action") == "search_google":
                query = step.get("query", "").lower()
                if query not in original_prompt.lower():
                    is_valid_match = False
                    break
            if step.get("action") == "open_app":
                target = step.get("target", "").lower()
                if target not in original_prompt.lower():
                    is_valid_match = False
                    break
            if step.get("action") == "send_email":
                target_to = step.get("to", "").lower()
                if target_to not in original_prompt.lower():
                    is_valid_match = False
                    break
            if step.get("action") == "send_whatsapp":
                target_phone = str(step.get("phone", "")).lower()
                if target_phone not in original_prompt.lower():
                    is_valid_match = False
                    break
            if step.get("action") == "set_brightness" and prompt_level is not None:
                if int(step.get("level", -1)) != prompt_level:
                    is_valid_match = False
                    break
            if step.get("action") == "set_volume" and prompt_level is not None:
                if int(step.get("level", -1)) != prompt_level:
                    is_valid_match = False
                    break

        if is_valid_match and wants_brightness and not has_brightness_step:
            is_valid_match = False
        if is_valid_match and wants_volume and not has_volume_step:
            is_valid_match = False

        if is_valid_match:
            logger.info(f"Using verified learned solution for: {original_prompt}")
            return learned_solution
        else:
            logger.warning(f"Rejecting weak memory match for: {original_prompt}")

    web_keywords = ["search", "google", "find", "open", "visit", "browse", "look up", "lookup", "read screen", "click on", "click", "build", "create", "develop", "whatsapp", "message", "email", "send"]
    sys_keywords = ["volume", "sound", "brightness", "light"]
    
    if any(word in original_prompt.lower() for word in web_keywords + sys_keywords) or intent in ["vision_action", "software_engineering", "agent_execution", "messaging_action"]:
        return await fallback_plan(parsed_task)

                 
    try:
        system_instruction = "Plan execution steps as JSON array. Output ONLY JSON."
        response_text = await call_llm(json.dumps(parsed_task), system_instruction, response_format="json")
        data = json.loads(response_text)
        if isinstance(data, list) and len(data) > 0: return data
        return await fallback_plan(parsed_task)
    except:
        return await fallback_plan(parsed_task)

