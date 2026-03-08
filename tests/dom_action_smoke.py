"""
Quick smoke test for the new DOM automation helper.
Steps:
1) Open https://example.com
2) Click the "More information..." link
3) Scrape the main body text
Run: python tests/dom_action_smoke.py
"""
import asyncio
import json
from executor.browser_dom import run_dom_action


async def main():
    res = await run_dom_action({
        "url": "https://example.com",
        "steps": [
            {"action": "click_text", "text": "More information"},
            {"action": "scrape", "selector": "body"}
        ],
    })
    print(json.dumps(res, indent=2)[:4000])


if __name__ == "__main__":
    asyncio.run(main())
