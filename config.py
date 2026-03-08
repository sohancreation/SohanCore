import os

from dotenv import load_dotenv

load_dotenv()

AGENT_NAME = os.getenv("AGENT_NAME", "SohanCore")
AGENT_LOGGER_NAME = os.getenv("AGENT_LOGGER_NAME", f"{AGENT_NAME}-Core")


def _parse_allowed_ids(raw: str) -> list[int]:
    if not raw.strip():
        return []
    values = []
    for part in raw.split(","):
        token = part.strip()
        if token.isdigit():
            values.append(int(token))
    return values


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
ALLOWED_USER_IDS = _parse_allowed_ids(os.getenv("ALLOWED_USER_IDS", ""))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
GROK_API_KEY = os.getenv("GROK_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

LLM_PROVIDER_ORDER = os.getenv("LLM_PROVIDER_ORDER", "ollama,openrouter,openai,gemini")
LLM_CACHE_TTL_SECONDS = int(os.getenv("LLM_CACHE_TTL_SECONDS", "900"))

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL_FAST = os.getenv("OLLAMA_MODEL_FAST", "gpt-oss:120b-cloud")
OLLAMA_MODEL_CODE = os.getenv("OLLAMA_MODEL_CODE", "gpt-oss:120b-cloud")
