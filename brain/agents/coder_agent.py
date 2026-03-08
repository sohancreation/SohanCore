import logging
from typing import Dict, Any, List
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class CoderAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            "CoderAgent",
            "Software Engineer",
            "Generate source code, modify files, and create complex project structures with high quality."
        )

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        task = input_data.get("task")
        context = input_data.get("context", "")
        
        system_instruction = """
        You are the CoderAgent, the master engineer.
        
        YOUR TASK: Implement high-quality, functional code. 
        
        CRITICAL RULE: NEVER use placeholders. NEVER say 'add logic here' or '// implementation goes here'. 
        You MUST provide the ENTIRE working content of the file every time.
        
        CONTEXTUAL AWARENESS:
        1. Always look at the 'full_history' provided in the input.
        2. If the ResearchAgent has provided a 'summary' of documentation or code snippets, you MUST use that information.
        3. Follow best practices for the specific technology found during research.
        
        Tools: write_file, read_file, list_dir.
        
        Output JSON format:
        {
            "thought": "Architecture and implementation logic based on research findings",
            "tool_call": {
                "name": "write_file",
                "params": {"path": "...", "content": "..."}
            }
        }
        """
        
        prompt = f"Task: {task}\nProject Context: {context}"
        result = await self.call_json_ai(prompt, system_instruction)
        return result
