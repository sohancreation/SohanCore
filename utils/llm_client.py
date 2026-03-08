import asyncio
import hashlib
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

                              
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

logger = logging.getLogger(__name__)

CACHE_PATH = Path("e:/SohanCore/sohan_ai_agent/memory/llm_cache.json")
CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
_CACHE_LOCK = asyncio.Lock()
_OLLAMA_MODEL_LOCK = asyncio.Lock()
_OLLAMA_MODEL_CACHE: Dict[str, Any] = {"ts": 0.0, "models": []}


def _build_messages(prompt: str, system_instruction: str = "", history: list = None) -> List[Dict[str, str]]:
    messages: List[Dict[str, str]] = []
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})
    if history:
        for msg in history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": prompt})
    return messages


def _is_coding_task(prompt: str, system_instruction: str) -> bool:
    text = (prompt + " " + system_instruction).lower()
    code_words = [
        "code", "script", "build software", "create app", "refactor", "debug",
        "stack trace", "bug", "python", "javascript", "api", "function", "class"
    ]
    return any(word in text for word in code_words)


def _cache_key(messages: List[Dict[str, str]], response_format: str) -> str:
    payload = {"messages": messages, "response_format": response_format}
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


async def _load_cache() -> Dict[str, Any]:
    async with _CACHE_LOCK:
        if not CACHE_PATH.exists():
            return {}
        try:
            return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}


async def _save_cache(cache: Dict[str, Any]) -> None:
    async with _CACHE_LOCK:
        try:
            CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=True), encoding="utf-8")
        except Exception as e:
            logger.warning(f"LLM cache write failed: {e}")


async def _cache_get(key: str) -> Optional[str]:
    cache = await _load_cache()
    item = cache.get(key)
    if not item:
        return None
    if time.time() - item.get("ts", 0) > config.LLM_CACHE_TTL_SECONDS:
        return None
    return item.get("text")


async def _cache_set(key: str, text: str, provider: str, model: str) -> None:
    cache = await _load_cache()
                                     
    if len(cache) > 2000:
                         
        ordered = sorted(cache.items(), key=lambda kv: kv[1].get("ts", 0))
        for k, _ in ordered[:400]:
            cache.pop(k, None)
    cache[key] = {"text": text, "provider": provider, "model": model, "ts": time.time()}
    await _save_cache(cache)


async def _request_openrouter(messages: List[Dict[str, str]], response_format: str, is_coding: bool, timeout: int) -> str:
    if not config.OPENROUTER_API_KEY:
        return ""
    model = "google/gemini-2.0-flash-001" if is_coding else "google/gemma-3-27b-it"
    payload: Dict[str, Any] = {"model": model, "messages": messages}
    if response_format == "json":
        payload["response_format"] = {"type": "json_object"}
    headers = {
        "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://sohan.ai",
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=timeout,
        )
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    raise RuntimeError(f"OpenRouter {response.status_code}: {response.text[:250]}")


async def _request_openai(messages: List[Dict[str, str]], response_format: str, is_coding: bool, timeout: int) -> str:
    if not config.OPENAI_API_KEY:
        return ""
    model = "gpt-4o" if is_coding else "gpt-4o-mini"
    payload: Dict[str, Any] = {"model": model, "messages": messages}
    if response_format == "json":
        payload["response_format"] = {"type": "json_object"}
    headers = {"Authorization": f"Bearer {config.OPENAI_API_KEY}"}
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=timeout,
        )
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    raise RuntimeError(f"OpenAI {response.status_code}: {response.text[:250]}")


async def _request_gemini(messages: List[Dict[str, str]], is_coding: bool) -> str:
    if not config.GEMINI_API_KEY:
        return ""
    import google.generativeai as genai
    genai.configure(api_key=config.GEMINI_API_KEY)
    model_name = "gemini-2.0-flash" if is_coding else "gemini-2.0-flash-lite"
    model = genai.GenerativeModel(model_name)
    context = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
    response = await asyncio.to_thread(model.generate_content, context)
    if response and response.text:
        return response.text.strip()
    raise RuntimeError("Gemini empty response")


async def _request_ollama(messages: List[Dict[str, str]], is_coding: bool, timeout: int) -> str:
    model = await _resolve_ollama_model(is_coding, timeout)
    payload = {"model": model, "messages": messages, "stream": False}
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{config.OLLAMA_BASE_URL}/api/chat",
            json=payload,
            timeout=timeout,
        )
    if response.status_code == 200:
        data = response.json()
        msg = data.get("message", {})
        return (msg.get("content") or "").strip()
    raise RuntimeError(f"Ollama {response.status_code}: {response.text[:250]}")


async def _fetch_ollama_models(timeout: int) -> List[str]:
    now = time.time()
    async with _OLLAMA_MODEL_LOCK:
        if now - _OLLAMA_MODEL_CACHE["ts"] < 30:
            return list(_OLLAMA_MODEL_CACHE["models"])
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=timeout)
            if response.status_code != 200:
                logger.warning(f"Ollama tags fetch failed: {response.status_code}")
                return []
            data = response.json()
            models = [m.get("name", "").strip() for m in data.get("models", []) if m.get("name")]
            _OLLAMA_MODEL_CACHE["ts"] = now
            _OLLAMA_MODEL_CACHE["models"] = models
            return list(models)
        except Exception as e:
            logger.warning(f"Ollama tags fetch error: {e}")
            return []


async def _resolve_ollama_model(is_coding: bool, timeout: int) -> str:
    preferred = config.OLLAMA_MODEL_CODE if is_coding else config.OLLAMA_MODEL_FAST
    models = await _fetch_ollama_models(timeout)
    if not models:
        return preferred
    if preferred in models:
        return preferred
    fallback = models[0]
    logger.warning(f"Ollama model '{preferred}' not installed. Falling back to '{fallback}'.")
    return fallback


async def _request_with_backoff(provider: str, messages: List[Dict[str, str]], response_format: str, is_coding: bool, timeout: int) -> str:
    for attempt in range(3):
        try:
            if provider == "openrouter":
                return await _request_openrouter(messages, response_format, is_coding, timeout)
            if provider == "openai":
                return await _request_openai(messages, response_format, is_coding, timeout)
            if provider == "gemini":
                return await _request_gemini(messages, is_coding)
            if provider == "ollama":
                return await _request_ollama(messages, is_coding, timeout)
            return ""
        except Exception as e:
            delay = min(8, 2 ** attempt)
            logger.warning(f"{provider} attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                await asyncio.sleep(delay)
    return ""


async def call_llm(prompt: str, system_instruction: str = "", response_format: str = "text", history: list = None) -> str:
    messages = _build_messages(prompt, system_instruction, history)
    is_coding = _is_coding_task(prompt, system_instruction)
    timeout = 120 if is_coding else 50

    key = _cache_key(messages, response_format)
    cached = await _cache_get(key)
    if cached:
        logger.info("LLM cache hit")
        return cached

    order = [p.strip().lower() for p in config.LLM_PROVIDER_ORDER.split(",") if p.strip()]
    if not order:
        order = ["openrouter", "openai", "gemini", "ollama"]

    for provider in order:
        text = await _request_with_backoff(provider, messages, response_format, is_coding, timeout)
        if text:
            await _cache_set(key, text, provider=provider, model=("code" if is_coding else "fast"))
            return text

    return ""


async def call_vision_llm(prompt: str, image_path: str) -> str:
    if not config.GEMINI_API_KEY:
        logger.error("Vision requires a Gemini API Key.")
        return ""

    try:
        import google.generativeai as genai
        from PIL import Image
        import pyautogui

        w, h = pyautogui.size()
        full_prompt = f"The screen resolution is {w}x{h}. {prompt}"

        genai.configure(api_key=config.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.0-flash")

        img = Image.open(image_path)
        response = await asyncio.to_thread(model.generate_content, [full_prompt, img])
        if response and response.text:
            return response.text.strip()
    except Exception as e:
        logger.warning(f"Direct Gemini Vision failed (quota?), trying OpenRouter failover: {e}")
        
                                    
    if config.OPENROUTER_API_KEY:
        try:
            import base64
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            headers = {
                "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://sohan.ai",
            }
            payload = {
                "model": "google/gemini-2.0-flash-001",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ]
            }
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=60,
                )
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"].strip()
                logger.error(f"OpenRouter Vision failover failed: {response.text}")
        except Exception as ve:
            logger.error(f"Ultimate Vision failure: {ve}")

    return ""
