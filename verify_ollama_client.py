import asyncio
import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.llm_client import call_llm

async def main():
    print("Testing LLM call via Ollama (as prioritized in config)...")
    prompt = "Hello, what is your name?"
    response = await call_llm(prompt)
    print(f"\nPrompt: {prompt}")
    print(f"Response: {response}")

if __name__ == "__main__":
    asyncio.run(main())
