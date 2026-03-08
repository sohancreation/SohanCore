from dataclasses import dataclass, asdict
from typing import List


@dataclass
class GoalSpec:
    goal_type: str
    components: List[str]
    complexity: str
    raw_goal: str

    def to_dict(self):
        return asdict(self)


def interpret_goal(text: str) -> GoalSpec:
    t = (text or "").lower()
    goal_type = "general"
    components: List[str] = []
    complexity = "medium"

    if any(k in t for k in ["build", "create", "develop", "app", "project", "software"]):
        goal_type = "software_project"
        if any(k in t for k in ["frontend", "ui", "react", "html", "css", "vue"]):
            components.append("frontend")
        if any(k in t for k in ["api", "backend", "server", "django", "flask", "fastapi", "node"]):
            components.append("backend")
        if "database" in t or "db" in t or "postgres" in t or "mongo" in t:
            components.append("database")
    elif any(k in t for k in ["research", "investigate", "look up", "find info"]):
        goal_type = "research"
    elif any(k in t for k in ["automate", "workflow", "script", "batch"]):
        goal_type = "automation"
    elif any(k in t for k in ["shutdown", "restart", "brightness", "volume", "process", "bluetooth", "wifi", "network", "display", "audio"]):
        goal_type = "system_control"
    elif any(k in t for k in ["click", "find", "scan", "read screen", "screenshot"]):
        goal_type = "vision_action"

                         
    if not components:
        components = ["task"]

                                
    words = len(t.split())
    if words < 8:
        complexity = "low"
    elif words > 40:
        complexity = "high"

    return GoalSpec(goal_type=goal_type, components=components, complexity=complexity, raw_goal=text)
