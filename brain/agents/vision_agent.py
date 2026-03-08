import logging
from typing import Dict, Any
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class VisionAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            "VisionAgent", 
            "Visual Intelligence Specialist",
            "Analyze the screen content, identify UI elements, and extract text to guide the agent loop."
        )

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        task = input_data.get("task", "Describe what is on the screen.")
        goal = input_data.get("goal")
        
        system_instruction = f"""
        You are the VisionAgent for SohanCore. Your job is to be the 'eyes' of the system.
        You will receive a task related to visual analysis. 
        
        TOOLS AT YOUR DISPOSAL:
        - read_screen: Extracts all text from the current display.
        - take_screenshot: Saves a visual snapshot.
        - vision_click: Finds an icon, button, or text label and clicks it.
        
        CRITICAL: If asked to click something specific (icon or text), use 'vision_click'.
        
        When asked to identify a coordinate or click:
        - Use 'vision_click' directly for clearly named targets.
        - Use 'read_screen' if you need to scout for text first.
        
        Output JSON:
        {{
            "thought": "Analysis of why I'm looking at the screen",
            "observation_needed": "Do I need text or an image?",
            "tool_call": {{ "name": "read_screen", "params": {{}} }}
        }}
        """
        
        prompt = f"Goal: {goal}\nCurrent Visual Task: {task}"
        return await self.call_json_ai(prompt, system_instruction)
