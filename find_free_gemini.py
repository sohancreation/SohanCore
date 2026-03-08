import requests
import config

def find_gemini_free():
    url = "https://openrouter.ai/api/v1/models"
    headers = {"Authorization": f"Bearer {config.OPENROUTER_API_KEY}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        models = response.json().get('data', [])
        for m in models:
            if 'gemini' in m['id'].lower() and ':free' in m['id']:
                print(f"Found free Gemini: {m['id']}")
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    find_gemini_free()
