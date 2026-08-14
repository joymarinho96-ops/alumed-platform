import asyncio
from playwright.async_api import async_playwright

async def debug():
    url = "https://secretaria478.wixsite.com/conectafcm/biblioteca-virtual/aea00840-590b-4e56-b96e-4eae57b081a1"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print(f"Navigating to {url}...")
        await page.goto(url, wait_until="networkidle")
        await page.wait_for_timeout(8000)
        
        # 1. Print title
        title = await page.title()
        print(f"Page Title: {title}")
        
        # 2. Check frames
        frames = page.frames
        print(f"Total Frames: {len(frames)}")
        for idx, frame in enumerate(frames):
            print(f" Frame {idx}: Name={frame.name}, URL={frame.url}")
            
        # 3. Save html
        content = await page.content()
        with open("debug_playwright.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("Saved page content to debug_playwright.html")
        
        # 4. Search for links in all frames
        total_links = 0
        wix_links = []
        for frame in frames:
            try:
                elements = await frame.query_selector_all("a")
                for el in elements:
                    href = await el.get_attribute("href")
                    text = await el.inner_text()
                    if href:
                        total_links += 1
                        if "wixstatic.com" in href or ".pdf" in href.lower() or "drive.google.com" in href:
                            wix_links.append((text.strip(), href))
            except Exception as e:
                print(f"  Error reading frame: {e}")
                
        print(f"Total links found across all frames: {total_links}")
        print(f"Wix/PDF/Drive links found: {len(wix_links)}")
        for text, href in wix_links[:10]:
            print(f" - {text}: {href}")
            
        await browser.close()

asyncio.run(debug())
