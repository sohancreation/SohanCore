"""
test_openrouter.py
Tests the OpenRouter API key directly.
"""
import requests
import json
import os
import sys

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def test():
    key = config.OPENROUTER_API_KEY.strip()
    print(f"Testing key: {key[:10]}...{key[-4:]}")
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "mistralai/mistral-small-3.1-24b-instruct:free",
        "messages": [{"role": "user", "content": "hi"}]
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    test()
