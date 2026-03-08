import logging
from typing import Dict, Any, List
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class DebuggerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            "DebuggerAgent",
            "Bug Fixer and Code Reviewer",
            "Analyze stack traces, fix failing code, and suggest architectural improvements to ensure stability."
        )

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        error = input_data.get("error")
        code = input_data.get("code")
        
        system_instruction = """
        You are the DebuggerAgent. Fix the broken code.
        Tools: read_file, write_file, run_shell (to test).
        
        Output JSON format:
        {
            "thought": "Root cause analysis",
            "fix": "Strategy for fixing the bug",
            "tool_call": {
                "name": "write_file",
                "params": {"path": "...", "content": "..."}
            }
        }
        """
        
        prompt = f"Error: {error}\nCode Snippet:\n{code}"
        result = await self.call_json_ai(prompt, system_instruction)
        return result
