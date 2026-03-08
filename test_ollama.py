import requests
try:
    response = requests.get("http://127.0.0.1:11434/api/tags")
    print(response.json())
except Exception as e:
    print(f"Error: {e}")
