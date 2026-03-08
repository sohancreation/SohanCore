import logging
import os
import asyncio
import webbrowser
import subprocess
import urllib.parse
from playwright.async_api import async_playwright
from duckduckgo_search import DDGS
from pathlib import Path

                   
logger = logging.getLogger(__name__)

                              
DOWNLOADS_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "projects" / "downloads"

async def _ensure_downloads_dir():
    if not DOWNLOADS_DIR.exists():
        DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

                        
EXTRA_HEADERS = {
    "Accept-Language": "en-US,en;q=0.9",
}

                               

async def open_url_on_desktop(url: str):
    if url.startswith("mailto:"):
        logger.info(f"Forcing native Mail app for mailto link: {url}")
                                                                         
        to_part = url.replace("mailto:", "").split("?")[0]
        params = url.split("?")[-1] if "?" in url else ""
        new_uri = f"outlookmail:compose?to={to_part}&{params}"
        subprocess.Popen(f'start {new_uri}', shell=True)
        return {"status": "success", "message": f"📬 Opened your native Mail app for {to_part}"}

    if not url.startswith(("http://", "https://", "file://")):
                                        
        if ":" in url or url.startswith(("/", "\\")):
             url = f"file:///{os.path.abspath(url).replace('\\', '/')}"
        else:
             url = f"https://{url}"
    
    logger.info(f"FORCING desktop URL: {url}")
    try:
                                   
        webbrowser.open(url)
                                                                         
                                                                 
        subprocess.Popen(f'start "" "{url}"', shell=True)
        
        return {"status": "success", "message": f"🌐 OK! I have opened {url} on your PC screen."}
    except Exception as e:
        logger.error(f"Failed to open desktop browser: {e}")
        return {"status": "error", "message": f"❌ Error launching browser: {str(e)}"}

async def search_on_desktop(query: str):
    logger.info(f"FORCING desktop search for: {query}")
    try:
                               
        query = query.strip()
        safe_query = urllib.parse.quote(query)
        url = f"https://www.google.com/search?q={safe_query}&hl=en"
        
                                                                                
        subprocess.Popen(f'start "" "{url}"', shell=True)
                                            
        webbrowser.open(url)
        
        return {"status": "success", "message": f"🔍 OK! I've launched a search for '{query}' on your computer."}
    except Exception as e:
        logger.error(f"Failed to search on desktop: {e}")
        return {"status": "error", "message": f"❌ Error performing search: {str(e)}"}

                                                      

async def open_url(url: str):
    if not url.startswith(("http://", "https://", "file://")):
        if ":" in url or url.startswith(("/", "\\")):
             url = f"file:///{os.path.abspath(url).replace('\\', '/')}"
        else:
             url = f"https://{url}"
        
    logger.info(f"Background opening URL: {url}")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--disable-gpu"])
            context = await browser.new_context(
                user_agent=USER_AGENT,
                locale="en-US",
                extra_http_headers=EXTRA_HEADERS
            )
            page = await context.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=45000)
            title = await page.title()
            content = await page.inner_text("body")
            content = content[:2500].strip()
            await browser.close()
            return {"status": "success", "message": f"Read content from {url}", "title": title, "content": content}
    except Exception as e:
        logger.error(f"Failed to open URL {url}: {e}")
        return {"status": "error", "message": f"Web access failed: {str(e)}"}

async def search_google(query: str):
    logger.info(f"Background search for: '{query}'")
    try:
        results = []
        with DDGS() as ddgs:
            ddgs_results = list(ddgs.text(f"{query}", region="wt-wt", max_results=5))
            for r in ddgs_results:
                results.append(f"{r['title']} ({r['href']})\nSnippet: {r['body']}\n")
        
        if results:
            return {"status": "success", "message": f"Found results for '{query}'", "results": results}
    except Exception as e:
        logger.error(f"Search failure: {e}")
    return {"status": "error", "message": "Search results unavailable."}

async def download_file(url: str, filename: str = None):
    await _ensure_downloads_dir()
    if not filename:
        filename = url.split("/")[-1] or "downloaded_file"
    save_path = DOWNLOADS_DIR / filename
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            response = await page.request.get(url, timeout=60000)
            if response.status == 200:
                body = await response.body()
                with open(save_path, "wb") as f: f.write(body)
                await browser.close()
                return {"status": "success", "message": f"Downloaded: {filename}"}
                
            await browser.close()
    except: pass
    return {"status": "error", "message": "Download failed."}

async def get_weather(city: str):
    logger.info(f"Checking weather for: {city}")
    query = f"weather in {city}"
    try:
                                                
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=1))
            if results:
                info = results[0]['body']
                return {"status": "success", "message": f"🌤️ *Weather in {city}:*\n{info}"}
        return {"status": "error", "message": "Could not find weather info."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
