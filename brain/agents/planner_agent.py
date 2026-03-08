import logging
from typing import Dict, Any, List
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            "PlannerAgent",
            "Strategist and Architect",
            "Break complex goals into structured, actionable steps and produce prioritized task lists."
        )

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        goal = input_data.get("goal")
        memories = input_data.get("memories", [])
        environment = input_data.get("environment", {})
        goal_spec = input_data.get("goal_spec", {})
        mem_summary = "\n".join([f"- ({m.get('score',0):.2f}) {m.get('label')}: {m.get('text')[:160]}" for m in memories]) or "None"
        
        system_instruction = """
        You are the PlannerAgent, the chief strategist.
        
        TASK: Break complex goals into a structured, technical roadmap.
        
        GUIDELINES:
        - FOR BUILDS: Specify exactly which files need to be created in which directories (e.g., 'src/main.py', 'css/style.css').
        - Step 1: Create directories and skeleton files.
        - Step 2: Implement full logic.
        - Step 3: PREVIEW the application (launch main.py or open index.html).
        - WEB AUTOMATION: Prefer DOM-first actions using the Playwright tool 'dom_action' (click selectors/text, type, wait_for, scrape) before vision-based clicks. Use clear selectors/text targets.
        - Avoid ResearchAgent unless the user asks for something rare or complex.
        - USE CONTEXT: If relevant memories exist, incorporate them directly to skip redundant work.\n{mem_summary}
        - ENVIRONMENT: Current snapshot -> {environment}
        - GOAL SPEC: {goal_spec}
        
        Output JSON format:
        {
            "thought": "Deep technical analysis and strategy",
            "steps": [
                {"step_id": 1, "task": "Search for [Technology] documentation and code examples", "agent": "ResearchAgent"},
                {"step_id": 2, "task": "...", "agent": "CoderAgent"}
            ]
        }
        """
        
        prompt = f"Decompose this goal: {goal}"
        result = await self.call_json_ai(prompt, system_instruction)
        return result
