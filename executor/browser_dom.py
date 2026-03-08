import asyncio
import logging
from typing import Dict, Any, List, Optional
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
EXTRA_HEADERS = {"Accept-Language": "en-US,en;q=0.9"}

logger = logging.getLogger(__name__)


async def _new_page(headless: bool = True):
    p = await async_playwright().start()
    browser = await p.chromium.launch(headless=headless, args=["--disable-gpu"])
    context = await browser.new_context(user_agent=USER_AGENT, locale="en-US", extra_http_headers=EXTRA_HEADERS)
    page = await context.new_page()
    return p, browser, context, page


async def _close_all(p, browser, context):
    try:
        await context.close()
    except Exception:
        pass
    try:
        await browser.close()
    except Exception:
        pass
    try:
        await p.stop()
    except Exception:
        pass


async def _run_step(page, step: Dict[str, Any]) -> Dict[str, Any]:
    action = (step.get("action") or "").lower()
    selector = step.get("selector")
    text = step.get("text")
    value = step.get("value") or step.get("input") or step.get("text")
    timeout = int(step.get("timeout_ms", 10000))

    try:
        if action == "open_page":
            url = step.get("url")
            await page.goto(url, wait_until="domcontentloaded", timeout=timeout)
            return {"status": "success", "message": f"Opened {url}"}

        if action == "wait_for":
            await page.wait_for_selector(selector, timeout=timeout)
            return {"status": "success", "message": f"wait_for {selector}"}

        if action == "click_selector":
            await page.click(selector, timeout=timeout)
            return {"status": "success", "message": f"Clicked {selector}"}

        if action == "click_text":
            await page.get_by_text(text, exact=step.get("exact", False)).click(timeout=timeout)
            return {"status": "success", "message": f"Clicked text '{text}'"}

        if action == "type":
            await page.fill(selector, value, timeout=timeout)
            return {"status": "success", "message": f"Typed into {selector}"}

        if action == "press":
            await page.press(selector, value, timeout=timeout)
            return {"status": "success", "message": f"Pressed {value} on {selector}"}

        if action == "scrape":
            target = selector or "body"
            content = await page.inner_text(target, timeout=timeout)
            snippet = content[:3000]
            return {"status": "success", "message": f"Scraped {target}", "content": snippet}

        if action == "screenshot":
            path = step.get("path", "dom_capture.png")
            await page.screenshot(path=path, full_page=True)
            return {"status": "success", "message": f"Screenshot saved to {path}"}

        return {"status": "error", "message": f"Unknown DOM action: {action}"}
    except PlaywrightTimeoutError:
        return {"status": "error", "message": f"Timeout on action {action} ({selector or text})"}
    except Exception as e:
        return {"status": "error", "message": f"DOM action failed: {e}"}


async def run_dom_action(params: Dict[str, Any]) -> Dict[str, Any]:
    headless = params.get("headless", True)
    url = params.get("url")
    steps: List[Dict[str, Any]] = params.get("steps") or []

                           
    if not steps and params.get("action"):
        steps = [{
            "action": params.get("action"),
            "selector": params.get("selector"),
            "text": params.get("text"),
            "value": params.get("value"),
            "url": url,
            "timeout_ms": params.get("timeout_ms")
        }]

    p = browser = context = page = None
    results = []
    try:
        p, browser, context, page = await _new_page(headless=headless)
        if url:
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=int(params.get("timeout_ms", 15000)))
            except Exception as e:
                logger.error(f"Initial navigation failed: {e}")
                results.append({"status": "error", "message": f"Failed to open {url}: {e}"})
                return {"status": "error", "message": f"Failed to open {url}: {e}"}

        for step in steps:
            res = await _run_step(page, step)
            results.append(res)
            if res.get("status") == "error":
                break

                            
        overall_status = "success" if all(r.get("status") == "success" for r in results) else "partial"
        return {
            "status": overall_status,
            "message": "; ".join(r.get("message", "") for r in results),
            "results": results
        }
    finally:
        if page:
            await _close_all(p, browser, context)
