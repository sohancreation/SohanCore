import logging
from utils.llm_client import call_llm

logger = logging.getLogger(__name__)

async def suggest_fix(file_name: str, code: str, error_msg: str) -> dict:
    logger.info(f"Analyzing error in: {file_name}")
    
    system_instruction = """
    You are a Debugging Expert AI. 
    Analyze the provided code and the error message.
    Provide a solution in JSON format:
    {
      "action": "install_dependency" | "modify_code" | "other",
      "command": "pip install ...", (if action is install_dependency)
      "new_code": "...", (if action is modify_code)
      "explanation": "Why it failed"
    }
    Output ONLY JSON.
    """

    prompt = f"File: {file_name}\nError: {error_msg}\nCurrent Code:\n{code}"

    try:
        response = await call_llm(prompt, system_instruction, response_format="json")
        import json
        return json.loads(response)
    except Exception as e:
        logger.error(f"Error analysis failed: {e}")
        return {"action": "other", "explanation": "Failed to analyze error."}
