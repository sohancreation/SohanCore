import logging
from typing import Dict, Any, List
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class ManagerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            "ManagerAgent", 
            "Orchestrator and Supervisor",
            "Receive the user's goal, assign tasks to specialized agents, and monitor overall progress."
        )

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        goal = input_data.get("user_goal")
        history = input_data.get("agent_results", [])
        memories = input_data.get("memories", [])
        environment = input_data.get("environment", {})
        goal_spec = input_data.get("goal_spec", {})
        mem_summary = "\n".join([f"- ({m.get('score',0):.2f}) {m.get('label')}: {m.get('text')[:160]}" for m in memories]) or "None"
        
        system_instruction = f"""
        You are the ManagerAgent, the supreme orchestrator of SohanCore.
        Your goal: {goal}
        
        AGENTS: PlannerAgent, ResearchAgent, CoderAgent, DebuggerAgent, ExecutorAgent, VisionAgent.
        
        STRICT OPERATING PROTOCOL (FULL AUTONOMY):
        1. NO LIMITS: You can perform ANY task requested (clicks, typing, settings, installs, sign-ups).
        2. REVIEW: Analyze previous agent_results to see if the last action worked.
        3. DESKTOP INTERACTION (Action Mode): If the task requires interacting with an app or website:
           - STEP 1 (LOOK): Use VisionAgent to see the screen and get coordinates for buttons or text boxes.
           - STEP 2 (ACT): Use ExecutorAgent (mouse_click, keyboard_type, press_key) to perform the interaction.
           - STEP 3 (VERIFY): Use VisionAgent again to see the result and decide the next move.
        4. COMPLEX AUTOMATION: If the user says "Create an account" or "Change settings":
           - Open the browser or settings app (ExecutorAgent).
           - Cycle through Vision -> Click -> Type until the form is filled.
        5. DEVELOPER MODE: If the user goal is to 'build' something, proceed as normal but include previews.
        6. PROACTIVE: If something is blocked, try a different path (e.g., if a click fails, try keyboard shortcuts).
        7. TERMINATE: Set 'is_complete' to true ONLY when you can see the success state on the screen or in logs.
        
        Recent History: {history}
        Goal Spec: {goal_spec}
        Environment Snapshot: {environment}
        Relevant Long-Term Memories:\n{mem_summary}
        
        Output JSON format:
        {{
            "thought": "Direct critique of last action and logic for the next",
            "is_complete": false,
            "final_answer": "Summary of what was built",
            "next_agent": "AgentName",
            "task_description": "Specific, actionable command for the specialist agent"
        }}
        """
        
        prompt = f"Goal: {goal}\nStatus: {history}\nWhat is the next step?"
        result = await self.call_json_ai(prompt, system_instruction)
        return result
