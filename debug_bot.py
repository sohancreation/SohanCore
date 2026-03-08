
import requests
import time
import os

token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
if not token:
    raise RuntimeError("Set TELEGRAM_BOT_TOKEN in environment before running debug_bot.py")

url = f"https://api.telegram.org/bot{token}/getUpdates"

print("Monitoring bot with configured TELEGRAM_BOT_TOKEN")
last_update_id = 0

while True:
    try:
        res = requests.get(url, params={"offset": last_update_id + 1, "timeout": 30})
        data = res.json()
        if data.get("ok"):
            for update in data.get("result", []):
                print(f"NEW UPDATE: {update}")
                last_update_id = update["update_id"]
        else:
            print(f"Error: {data}")
    except Exception as e:
        print(f"Exception: {e}")
    time.sleep(1)
