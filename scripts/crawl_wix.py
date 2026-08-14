import asyncio
from playwright.async_api import async_playwright

async def crawl():
    url = "https://secretaria478.wixsite.com/conectafcm/biblioteca-virtual/aea00840-590b-4e56-b96e-4eae57b081a1"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.set_viewport_size({"width": 1280, "height": 800})
        print(f"Navigating to {url}...")
        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(10000)
        
        # Look for elements containing folder names
        folders = ["1ER AÑO", "2DO AÑO", "3ER AÑO", "4to y 5to AÑO"]
        for f in folders:
            # Let's find selector for this folder
            try:
                elem = page.locator(f"text={f}").first
                if await elem.count() > 0:
                    print(f"Found folder: {f}. Attempting click...")
                    await elem.click()
                    await page.wait_for_timeout(5000)
                    
                    # Dump the text to see what is shown now
                    body_text = await page.inner_text("body")
                    print(f"--- Screen content after clicking {f} (first 800 chars) ---")
                    print(body_text[:800])
                    
                    # Take a screenshot to inspect
                    await page.screenshot(path=f"screenshot_after_{f.replace(' ', '_')}.png")
                    print(f"Saved screenshot for {f}")
                    
                    # Back to main MEDICINA folder by clicking the breadcrumb
                    breadcrumb = page.locator("text=MEDICINA").first
                    if await breadcrumb.count() > 0:
                        await breadcrumb.click()
                        await page.wait_for_timeout(4000)
                else:
                    print(f"Folder {f} not found on page.")
            except Exception as e:
                print(f"Error handling folder {f}: {e}")
                
        await browser.close()

asyncio.run(crawl())
