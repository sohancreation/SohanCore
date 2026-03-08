import logging
import os
import sys
from utils.llm_client import call_llm

                                               
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

logger = logging.getLogger(__name__)

async def generate_text(prompt: str, context: str = "general") -> str:
    logger.info(f"Generating content for: '{prompt}'")
    
    instruction = f"""
    You are an expert content creator AI. 
    Task: {prompt}
    Context: {context}
    
    Rule: Output ONLY the content. No preamble, no 'Here is your essay'.
    """

    try:
        content = await call_llm(prompt, instruction)
        return str(content).strip()
    except Exception as e:
        logger.error(f"Content Generator Error: {e}")
        return f"Error generating content: {str(e)}"

async def generate_code(prompt: str, language: str = "python") -> str:
    instruction = f"Generate clean, functional {language} code. Output RAW code ONLY."
    return await generate_text(prompt, context=instruction)
