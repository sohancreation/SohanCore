import logging
import re
from utils.llm_client import call_llm

logger = logging.getLogger(__name__)

async def generate_file_content(filename: str, project_description: str, file_context: str = "") -> str:
    logger.info(f"Generating COMPLETE source code for: {filename}")
    
                                                                          
    system_instruction = f"""
    You are a Highly Skilled Professional Software Engineer.
    
    TASK: Write the ABSOLUTE COMPLETE source code for the file named '{filename}'.
    PROJECT: {project_description}
    
    CONTEXT (Other files in project):
    {file_context}
    
    COMPLETENESS RULES:
    1. You MUST provide every single line of code. No summaries, no comments like 'rest of code goes here'.
    2. Start from the very first import and end with the very last closing parenthesis.
    3. If the file is a game (like Flappy Bird), you MUST include:
       - All Pygame/GUI initialization.
       - The full Game Loop (while True...).
       - Full event handling (keyboard/mouse).
       - Full rendering logic and asset management (use polygons if images aren't provided).
    4. NO PLACEHOLDERS. NO TODOs. 
    5. Output ONLY the code. DO NOT wrap in markdown (No ```python).
    """

    prompt = f"Write the full production-ready Python code for '{filename}' to build {project_description}. Make the file complete and self-contained."

    try:
                       
        code = await call_llm(prompt, system_instruction)
        
                                                                                             
        if len(code.split('\n')) < 15 and "main.py" in filename:
            logger.warning(f"Generated code for {filename} seems way too short. Retrying with 'Max Output' force.")
            code = await call_llm(f"STRICT: The previous code was too short. REWRITE THE ENTIRE {filename} FILE COMPLETELY. NO TRUNCATION.", system_instruction)

                                           
        if code.strip().startswith("```"):
            code = re.sub(r'^```[\w]*\n', '', code)
            code = re.sub(r'\n```$', '', code)
            
        return code.strip()
    except Exception as e:
        logger.error(f"Full code generation failed for {filename}: {e}")
        return f"# Critical Error: Could not generate complete logic for {filename}"
