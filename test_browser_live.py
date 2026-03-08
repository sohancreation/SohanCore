import asyncio
from playwright.async_api import async_playwright

async def test_open():
    try:
        async with async_playwright() as p:
            print("Launching browser...")
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            print("Navigating to google.com...")
            await page.goto("https://www.google.com/ncr", timeout=30000)
            title = await page.title()
            print(f"Success! Title: {title}")
            await browser.close()
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_open())
