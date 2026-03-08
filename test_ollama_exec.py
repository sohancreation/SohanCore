import requests
import json

url = "http://127.0.0.1:11434/api/generate"
data = {
    "model": "gpt-oss:120b-cloud",
    "prompt": "Why is the sky blue? Answer in one sentence.",
    "stream": False
}

try:
    response = requests.post(url, json=data)
    print(response.json())
except Exception as e:
    print(f"Error: {e}")
