import logging
import asyncio
import json
import time
from typing import Dict, Any, List

from .agents.manager_agent import ManagerAgent
from .agents.planner_agent import PlannerAgent
from .agents.research_agent import ResearchAgent
from .agents.coder_agent import CoderAgent
from .agents.debugger_agent import DebuggerAgent
from .agents.executor_agent import ExecutorAgent
from .agents.vision_agent import VisionAgent

from executor.code_runner import run_command
from executor.file_manager import read_file, write_file, list_dir
from executor.browser_control import search_google, open_url
from executor.desktop_control import open_app, take_screenshot
from executor.screen_vision import extract_text_from_screen, capture_screen_state
from executor.messaging import send_email
from executor.browser_dom import run_dom_action
from executor.environment_observer import get_environment_snapshot
from memory.embedding_store import query_memories
from brain.goal_interpreter import interpret_goal
from brain.reflection import reflect
from memory.embedding_store import query_memories

logger = logging.getLogger(__name__)

class MultiAgentOrchestrator:
    def __init__(self):
        self.manager = ManagerAgent()
        self.planner = PlannerAgent()
        self.researcher = ResearchAgent()
        self.coder = CoderAgent()
        self.debugger = DebuggerAgent()
        self.executor = ExecutorAgent()
        self.vision = VisionAgent()
        
        self.agent_map = {
            "ManagerAgent": self.manager,
            "PlannerAgent": self.planner,
            "ResearchAgent": self.researcher,
            "CoderAgent": self.coder,
            "DebuggerAgent": self.debugger,
            "ExecutorAgent": self.executor,
            "VisionAgent": self.vision
        }
        
        self.global_context = []                                             

    async def execute_tool(self, action: Dict[str, Any]) -> str:
        if not action: return "No tool call."
        name = action.get("name")
        params = action.get("params", {})
        cwd = params.get("cwd") or params.get("path")                           
        
        try:
            if name == "run_shell":
                res = await run_command(params.get("cmd", ""), cwd=cwd)
                return f"STDOUT: {res.get('stdout')}\nSTDERR: {res.get('stderr')}"
            elif name == "execute_python":
                from executor.code_runner import run_python
                res = await run_python(params.get("file", ""), cwd=cwd)
                return f"STDOUT: {res.get('stdout')}\nSTDERR: {res.get('stderr')}"
            elif name == "write_file":
                res = write_file(params.get("path"), params.get("content"))
                return res.get("message", "File written.")
            elif name == "read_file":
                res = read_file(params.get("path"))
                return res.get("content", "Error reading file.")
            elif name == "list_dir":
                res = list_dir(params.get("path", "."))
                return f"Contents: {json.dumps(res)}"
            elif name == "search_google":
                res = await search_google(params.get("query"))
                return "\n".join(res.get("results", []))
            elif name == "open_url":
                res = await open_url(params.get("url"))
                return res.get("content", "Error loading URL.")
            elif name == "open_app":
                res = open_app(params.get("target"))
                return res.get("message", "App launched.")
            elif name == "dom_action":
                res = await run_dom_action(params)
                return json.dumps(res) if isinstance(res, dict) else str(res)
            elif name == "send_email":
                res = await send_email(
                    to=params.get("to") or params.get("recipient", ""),
                    subject=params.get("subject", ""),
                    body=params.get("body", "")
                )
                return res.get("message", "Email action triggered.")
            elif name == "read_screen":
                text = await extract_text_from_screen()
                return f"Text Extracted from Screen: {text[:2000]}..."
            elif name == "take_screenshot":
                filename = params.get("filename", "agent_snapshot.png")
                res = take_screenshot(filename)
                return f"Screenshot saved to: {res.get('path')}"
            elif name == "launch_command":
                from executor.code_runner import launch_command
                res = await launch_command(params.get("cmd", ""), cwd=cwd)
                return res.get("message", "App launched in background.")
            elif name == "mouse_click":
                from executor.desktop_control import click_position
                res = click_position(params.get("x"), params.get("y"), clicks=params.get("clicks", 1))
                return res.get("message", "Mouse clicked.")
            elif name == "keyboard_type":
                from executor.desktop_control import type_text
                res = type_text(params.get("text", ""))
                return res.get("message", "Text typed.")
            elif name == "press_key":
                from executor.desktop_control import press_key
                res = press_key(params.get("key", ""))
                return res.get("message", f"Key {params.get('key')} pressed.")
            elif name == "focus_window":
                from executor.desktop_control import focus_window
                res = focus_window(params.get("title", ""))
                return res.get("message", "Window focused.")
            elif name == "toggle_bluetooth":
                from executor.desktop_control import toggle_bluetooth
                res = toggle_bluetooth(params.get("state", True))
                return res.get("message")
            elif name == "toggle_wifi":
                from executor.desktop_control import toggle_wifi
                res = toggle_wifi(params.get("state", True))
                return res.get("message")
            elif name == "vision_click":
                from executor.screen_vision import super_click
                res = await super_click(params.get("text") or params.get("target", ""), double=params.get("double", True))
                return res.get("message", "Visual click performed.")
            return f"Error: Tool '{name}' not found."
        except Exception as e:
            return f"Exception during tool execution: {e}"

    async def run_autonomous_loop(self, user_goal: str, progress_callback=None):
        iteration = 0
        max_iterations = 25
        max_failures = 5
        time_budget_sec = 300
        failure_count = 0
        start_time = time.time()
        
        if progress_callback:
            await progress_callback(f"[AUTO] SohanCore swarm online | Goal: `{user_goal}`")

        while iteration < max_iterations:
                           
            elapsed = time.time() - start_time
            if elapsed > time_budget_sec:
                if progress_callback:
                    await progress_callback(f"[AUTO] Halted: exceeded {time_budget_sec}s budget")
                return f"Stopped: time budget {time_budget_sec}s exceeded."
            if failure_count >= max_failures:
                if progress_callback:
                    await progress_callback(f"[AUTO] Halted: {failure_count} tool failures")
                return f"Stopped: too many failures ({failure_count})."

            iteration += 1
            
                                                                             
            memories = query_memories(user_goal, top_k=3)
            env_snapshot = get_environment_snapshot()
            screen_state = await capture_screen_state()
            env_snapshot["screen_text"] = screen_state.get("text") if isinstance(screen_state, dict) else ""
            env_snapshot["screen_image"] = screen_state.get("path") if isinstance(screen_state, dict) else ""
            goal_spec = interpret_goal(user_goal).to_dict()

                                                                                          
            manager_decision = await self.manager.run({
                "user_goal": user_goal,
                "agent_results": self.global_context,                                           
                "memories": memories,
                "environment": env_snapshot,
                "goal_spec": goal_spec
            })
            
            thought = manager_decision.get("thought", "Thinking...")
            is_complete = manager_decision.get("is_complete", False)
            
            if is_complete:
                final = manager_decision.get("final_answer", "Goal achieved.")
                if progress_callback:
                    await progress_callback(f"[AUTO] Mission accomplished | {final}")
                return final
            
            target_agent_name = manager_decision.get("next_agent")
            task_desc = manager_decision.get("task_description")
            
            if not target_agent_name or target_agent_name not in self.agent_map:
                target_agent_name = "PlannerAgent"
                task_desc = user_goal

            if progress_callback:
                await progress_callback(f"[AUTO] Manager: {thought} | DEPLOY: {target_agent_name}")

                                                                           
            agent = self.agent_map[target_agent_name]
            agent_input = {
                "task": task_desc, 
                "goal": user_goal,
                "full_history": self.global_context[-5:],
                "memories": memories,
                "environment": env_snapshot,
                "goal_spec": goal_spec
            }
            agent_output = await agent.run(agent_input)
            
                                                        
            tool_call = agent_output.get("tool_call")
            observation = "No tool call requested."
            if tool_call:
                if progress_callback:
                    await progress_callback(f"[TOOL] {target_agent_name} -> {tool_call.get('name')}")
                observation = await self.execute_tool(tool_call)

                                                                    
                obs_lower = str(observation).lower()
                error_triggered = False
                if "error" in obs_lower or "exception" in obs_lower or '"status": "error"' in obs_lower:
                    error_triggered = True
                if error_triggered:
                    failure_count += 1
                    if progress_callback:
                        await progress_callback(f"[REFLEX] Tool error -> DebuggerAgent ({failure_count}/{max_failures})")
                    debug_result = await self.debugger.run({
                        "error": str(observation),
                        "code": agent_output
                    })
                                                       
                    self.global_context.append({
                        "iteration": iteration,
                        "agent": "DebuggerAgent",
                        "thought": debug_result.get("thought"),
                        "agent_full_output": debug_result,
                        "observation": debug_result.get("fix") or debug_result.get("tool_call") or "Debugger response recorded."
                    })
                                                                                  
                    continue
                else:
                    failure_count = 0                    

                                                             
            result_entry = {
                "iteration": iteration,
                "agent": target_agent_name,
                "thought": agent_output.get("thought"),
                "agent_full_output": agent_output,                             
                "observation": observation
            }
            self.global_context.append(result_entry)
                                  
            reflection = reflect(self.global_context, observation)
            self.global_context.append({
                "iteration": iteration,
                "agent": "Reflection",
                "thought": reflection,
                "agent_full_output": {"reflection": reflection},
                "observation": reflection
            })
            
            if progress_callback:
                                                                                 
                obs_disp = observation if len(observation) <= 1500 else observation[:1500] + " ... [TRUNCATED]"
                obs_disp = obs_disp.replace("_", "\\_").replace("*", "").replace("`", "'")
                await progress_callback(f"[OBS] {target_agent_name}: {obs_disp}")

        if progress_callback:
            await progress_callback(f"[AUTO] Halted: reached max iterations")
        return "Incomplete: Max iterations."






