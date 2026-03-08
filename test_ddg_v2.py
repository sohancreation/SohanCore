from duckduckgo_search import DDGS
import json

def test_search():
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text("newton", max_results=5))
            # Write to a file to avoid console encoding issues
            with open("ddg_results.json", "w", encoding="utf-8") as f:
                json.dump(results, f, indent=4)
            print("Successfully saved results to ddg_results.json")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_search()
