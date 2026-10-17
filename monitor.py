import asyncio
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from playwright.async_api import async_playwright

URL = os.getenv("TICKET_URL", "https://vasco.eleventickets.com/#!/apresentacao/5cd8c7b86342e60220038fe6c296712b12724622")
INTERVAL = float(os.getenv("CHECK_INTERVAL", "20"))
HEADLESS = os.getenv("HEADLESS", "true").lower() != "false"

# We start in detection-only mode. Do NOT put passwords, cookies or payment data here.
SECTORS = [
    "Norte", "Sul", "Leste Superior", "Leste Inferior", "Oeste Inferior", "Maracanã Mais"
]

async def snapshot(page):
    """Collect visible text plus basic DOM state for later comparison.
    This intentionally avoids guessing the site's internal API or CSS selectors.
    """
    text = await page.locator("body").inner_text(timeout=10000)
    # Capture elements that look like sectors, availability, seats or ticket categories.
    candidates = await page.locator("[class], [id], svg, path, g").evaluate_all(
        """els => els.slice(0, 5000).map(e => ({
            tag:e.tagName, id:e.id || '', cls:typeof e.className === 'string' ? e.className : '',
            aria:e.getAttribute('aria-label') || '', role:e.getAttribute('role') || '',
            text:(e.innerText || e.textContent || '').trim().slice(0,120)
        })).filter(x => /norte|sul|leste|oeste|maracanã|maracana|meia|inteira|dispon|esgot|ingresso|setor/i.test(
            [x.id,x.cls,x.aria,x.role,x.text].join(' ')))"""
    )
    return {"text": text, "candidates": candidates}


def meaningful_change(old, new):
    if old is None:
        return True
    old_text = old["text"]
    new_text = new["text"]
    if old_text != new_text:
        # Ignore timestamps/random counters where possible.
        a = re.sub(r"\b\d{1,2}:\d{2}:\d{2}\b", "", old_text)
        b = re.sub(r"\b\d{1,2}:\d{2}:\d{2}\b", "", new_text)
        if a != b:
            return True
    return old["candidates"] != new["candidates"]


async def main():
    print(f"Starting monitor: {URL}")
    print(f"Interval: {INTERVAL}s | detection-only mode")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        page = await browser.new_page(viewport={"width": 1440, "height": 1200})
        try:
            await page.goto(URL, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(5000)
            previous = None
            while True:
                try:
                    current = await snapshot(page)
                    now = datetime.now(timezone.utc).isoformat()
                    if meaningful_change(previous, current):
                        print(f"[{now}] PAGE/DOM CHANGE DETECTED")
                        print(current["text"][:3000])
                        Path("last_snapshot.txt").write_text(current["text"], encoding="utf-8")
                        previous = current
                    else:
                        print(f"[{now}] no meaningful change")
                    await asyncio.sleep(INTERVAL)
                    await page.reload(wait_until="domcontentloaded", timeout=60000)
                    await page.wait_for_timeout(3000)
                except Exception as e:
                    print(f"monitor error: {type(e).__name__}: {e}")
                    await asyncio.sleep(INTERVAL)
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
