import logging
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from utils.llm_client import call_llm

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    def __init__(self, name: str, role: str, goal: str):
        self.name = name
        self.role = role
        self.goal = goal
        self.short_term_memory: List[Dict[str, Any]] = []

    def log_step(self, thought: str, action: str, result: str):
        self.short_term_memory.append({
            "thought": thought,
            "action": action,
            "result": result
        })

    def get_context(self) -> str:
        context = f"You are {self.name}, the {self.role}.\nYour overarching mission: {self.goal}\n\nRecent History:\n"
        for i, step in enumerate(self.short_term_memory[-10:], 1):
            context += f"Action {i}: {step.get('action')}\nResult: {step.get('result')[:500]}\n"
        return context

    @abstractmethod
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    async def speak(self, prompt: str, system_instruction: str = None) -> str:
        if not system_instruction:
            system_instruction = self.get_context()
        return await call_llm(prompt, system_instruction)

    async def call_json_ai(self, prompt: str, system_instruction: str) -> Dict[str, Any]:
        full_system = f"{system_instruction}\n\nIMPORTANT: Respond ONLY with a valid JSON object."
        response = await call_llm(prompt, full_system, response_format="json")
        try:
                          
            import re
            json_match = re.search(r"(\{.*\})", response, re.DOTALL)
            if json_match:
                clean_res = json_match.group(1).strip()
                data = json.loads(clean_res)
            else:
                                  
                clean_res = response.strip()
                if clean_res.startswith("```json"): clean_res = clean_res[7:]
                elif clean_res.startswith("```"): clean_res = clean_res[3:]
                if clean_res.endswith("```"): clean_res = clean_res[:-3]
                data = json.loads(clean_res.strip())
            
                                                                                      
            if isinstance(data, list):
                if len(data) > 0:
                    first = data[0] if isinstance(data[0], dict) else {}
                    first["all_results"] = data                          
                    return first
                return {"error": "Empty list from AI"}
            
            return data if isinstance(data, dict) else {"error": "Not a dict", "raw": str(data)}
            
        except Exception as e:
            logger.error(f"Agent {self.name} JSON failure: {e}. Raw: {response}")
            return {"error": "Invalid JSON", "thought": "I returned bad JSON. I need to retry with raw braces only."}
