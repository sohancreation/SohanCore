import logging
import os
import asyncio
from typing import Dict, Any
from brain.orchestrator import MultiAgentOrchestrator
from executor.desktop_control import open_app

logger = logging.getLogger(__name__)

async def run_agent_loop(goal: str, progress_callback=None) -> Dict[str, Any]:
    orchestrator = MultiAgentOrchestrator()
    goal_lower = goal.lower()
    full_goal = goal          
    
                                           
    is_build_task = any(kw in goal_lower for kw in ["build", "create project", "develop app", "make a game"])
    
    if is_build_task:
        if progress_callback:
            await progress_callback("💻 *Launching VS Code First...*")
        
                                         
        try:
            import subprocess
            subprocess.Popen('code', shell=True)                           
            await asyncio.sleep(1.5)
        except:
            pass

                                            
        words = goal_lower.split("build")[-1].strip().split(" ")
                       
        if words[0] in ["a", "an", "the"]:
            words = words[1:]
        
        project_name = "_".join(words[:2]) or "new_project"                                
        project_name = "".join(c for c in project_name if c.isalnum() or c == "_")
        project_path = f"e:/SohanCore/sohan_ai_agent/projects/{project_name}"
        
        os.makedirs(project_path, exist_ok=True)
        
        if progress_callback:
            await progress_callback(f"📂 *Project Workspace Ready:* `{project_name}`\n🛠️ *Initializing Agents...*")
        
                                                                    
        try:
            full_goal = f"{goal} (Project Directory: {project_path})"
            subprocess.Popen(f'code "{project_path}"', shell=True)
            await asyncio.sleep(1)
        except Exception as e:
            full_goal = goal
            logger.warning(f"Failed to focus VS Code path: {e}")

    try:
        final_result = await orchestrator.run_autonomous_loop(
            user_goal=full_goal,
            progress_callback=progress_callback
        )
        
        return {
            "status": "success" if "Incomplete" not in str(final_result) else "partial",
            "result": final_result
        }
    except Exception as e:
        logger.error(f"Multi-Agent Swarm Failure: {e}")
        return {"status": "error", "message": str(e)}
