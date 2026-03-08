import requests
import config

def list_all_free_models():
    url = "https://openrouter.ai/api/v1/models"
    headers = {"Authorization": f"Bearer {config.OPENROUTER_API_KEY}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        models = response.json().get('data', [])
        free_models = [m['id'] for m in models if ':free' in m['id']]
        print("Free Models found:", len(free_models))
        for m in free_models:
            print(f" - {m}")
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    list_all_free_models()
