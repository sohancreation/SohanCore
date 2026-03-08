import logging
from typing import Dict, Any, List
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class ExecutorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            "ExecutorAgent",
            "System Operations & Preview Specialist",
            "Execute Python code, start development servers, launch GUI applications, and preview results for the user."
        )

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        task = input_data.get("task")
        cwd = input_data.get("cwd") or "projects/"
        history = input_data.get("full_history", [])
        
        system_instruction = f"""
        You are the ExecutorAgent. Your job is to RUN the code the CoderAgent has built so the USER can see a preview.
        
        PREVIEW PROTOCOL:
        1. ENTRY POINT: Identify the main file (e.g., main.py, index.html, app.py).
        2. RUNTIME: 
           - For Python GUI apps (Tkinter, Pygame) or servers: Use 'launch_command' (e.g., cmd="python main.py").
           - For static scripts: Use 'execute_python'.
           - For web projects: Use 'open_url'.
        4. FEEDBACK: Tell the user the app has been launched for preview.
        5. DESKTOP AUTOMATION: If you need to click buttons, fill forms, or interact with an app:
           - Use 'focus_window' first to make sure the app is active.
           - Use 'mouse_click' (x, y) to click specific coordinates identified by VisionAgent.
           - Use 'keyboard_type' (text) to type sequences.
           - Use 'press_key' (key) for things like 'enter', 'tab', 'esc', 'win'.
        
        Your Working Directory: {cwd}
        
        Tools: run_shell, execute_python, launch_command, open_url, dom_action, list_dir, open_app, send_email, mouse_click, keyboard_type, press_key, focus_window.
        
        Output JSON format:
        {{
            "thought": "The code is ready. I will launch 'main.py' using launch_command so it doesn't block my execution path.",
            "tool_call": {{
                "name": "launch_command",
                "params": {{"cmd": "python main.py", "cwd": "{cwd}"}}
            }}
        }}
        """
        
        prompt = f"System Context: {self.get_context()}\nExecution Task: {task}\nHistory: {history}"
        result = await self.call_json_ai(prompt, system_instruction)
        return result
