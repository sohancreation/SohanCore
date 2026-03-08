from duckduckgo_search import DDGS

def test_search():
    with DDGS() as ddgs:
        results = ddgs.text("newton", max_results=5)
        for i, r in enumerate(results):
            print(f"{i+1}. {r['title']} - {r['href']}")

if __name__ == "__main__":
    test_search()
