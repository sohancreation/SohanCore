from typing import Dict, Any, List


def reflect(history: List[Dict[str, Any]], last_observation: str) -> str:
    if not history:
        return "First iteration; nothing to reflect on."
    last = history[-1]
    agent = last.get("agent")
    obs = last_observation or last.get("observation", "")

    if isinstance(obs, str) and any(k in obs.lower() for k in ["error", "failed", "exception"]):
        return f"Observation shows failure from {agent}; try different tool/params next."
    if "success" in str(obs).lower():
        return f"{agent} step succeeded; proceed or escalate complexity."
    return f"{agent} produced neutral output; consider adding verification or deeper inspection."
