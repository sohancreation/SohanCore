import logging
from typing import Dict, Any, List
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            "ResearchAgent",
            "Internet Researcher",
            "Search the internet, read multiple sources, and summarize technical findings for the team."
        )

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        task = input_data.get("task")
        
        system_instruction = """
        You are the ResearchAgent, the Technical Scout for SohanCore.
        
        YOUR MISSION: Find concrete implementation details, code boilerplates, and API schemas.
        
        CRITICAL RULES:
        1. Avoid generic 'Best of' or 'Top 10' articles. They are irrelevant for building.
        2. Focus on: 'Github boilerplates', 'documentation snippets', 'CSS layouts', and 'HTML structures'.
        3. If you are searching for a project like a portfolio, search for: 'clean HTML CSS portfolio template code' or 'responsive portfolio boilerplate'.
        4. Your 'summary' MUST contain actionable data (e.g., 'Use this div structure for a grid', 'Here is the link to the CDN').
        
        TOOLS:
        - search_google: Broad search.
        - open_url: Use this on Github or Documentation links to get REAL code.
        - dom_action: Precise DOM automation with Playwright. Params example:
            {{"action": "scrape", "url": "https://site", "selector": "main"}}
            or multi-step: {{"url": "https://site", "steps":[{{"action":"click_text","text":"Docs"}},{{"action":"scrape","selector":"article"}}]}}
        
        Output JSON format:
        {
            "thought": "Focusing on finding raw implementation code for [X]",
            "tool_call": {
                "name": "search_google",
                "params": {"query": "..."}
            },
            "summary": "ACTIONABLE TECHNICAL DATA: [Snippet or specific instruction]"
        }
        """
        
        prompt = f"Research Task: {task}"
        result = await self.call_json_ai(prompt, system_instruction)
        return result
