import json
import logging
import re
from utils.llm_client import call_llm

logger = logging.getLogger(__name__)

async def plan_project(prompt: str) -> dict:
    logger.info(f"Planning software project for: {prompt}")
    
    system_instruction = """
    You are a Senior Project Architect. 
    Analyze the user prompt and return a structured JSON plan for a software project.
    
    The JSON must include:
    1. "project_name": A unique, descriptive, multi-word slug (e.g., 'flappy_bird_pro', 'weather_dashboard', 'ai_chatbot'). 
       DO NOT use generic names like 'project' or 'app'.
    2. "files": A list of files to be created (e.g., ["main.py", "utils.py"]).
    3. "dependencies": A list of pip packages required.
    4. "development_steps": A list of tasks.
    
    Output ONLY JSON.
    """

    try:
        response = await call_llm(prompt, system_instruction, response_format="json")
                                                                            
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            plan = json.loads(json_match.group())
        else:
            plan = json.loads(response)
            
                                                  
        if not plan.get("project_name") or plan.get("project_name") in ["project", "new_project", "gen_project"]:
             words = re.sub(r'[^a-z0-9\s]', '', prompt.lower()).split()
             plan["project_name"] = "_".join(words[:3]) or "generated_app"

        logger.info(f"Project plan generated: {plan['project_name']}")
        return plan
    except Exception as e:
        logger.error(f"Project planning failed: {e}")
                                                     
        words = re.sub(r'[^a-z0-9\s]', '', prompt.lower()).split()
        fallback_name = "_".join(words[:3]) if words else "standalone_project"
        return {
            "project_name": f"fallback_{fallback_name}",
            "files": ["main.py"],
            "dependencies": [],
            "development_steps": [{"task": "error in planning"}]
        }
