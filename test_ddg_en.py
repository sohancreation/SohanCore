from duckduckgo_search import DDGS
import json

def test_search():
    try:
        with DDGS() as ddgs:
            # Forcing US English region
            results = list(ddgs.text("newton", region="us-en", max_results=5))
            with open("ddg_results_en.json", "w", encoding="utf-8") as f:
                json.dump(results, f, indent=4)
            print("Successfully saved English results to ddg_results_en.json")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_search()
