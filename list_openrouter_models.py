import requests
import config

def list_models():
    url = "https://openrouter.ai/api/v1/models"
    headers = {"Authorization": f"Bearer {config.OPENROUTER_API_KEY}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        models = response.json().get('data', [])
        free_models = [m['id'] for m in models if ':free' in m['id']]
        print("Free Models:", free_models)
        
        # Check for any gemini 2.0
        gemini_2 = [m['id'] for m in models if 'gemini-2.0' in m['id'].lower()]
        print("Gemini 2.0 Models:", gemini_2)
    else:
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    list_models()