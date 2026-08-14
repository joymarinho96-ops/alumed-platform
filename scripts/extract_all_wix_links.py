import asyncio
import os
import json
import sys
import django

# Add project root to sys.path
sys.path.append(r"c:\Users\joyce\Downloads\alumesitemdesenvolvimento-main\alumed-platform")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumed.settings')
django.setup()

from core.models import DigitalBook
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

# Output file path
MAPPING_FILE = "wix_links_mapping.json"

# Store mapping: {filename: download_url}
mapping_data = {}
if os.path.exists(MAPPING_FILE):
    try:
        with open(MAPPING_FILE, "r", encoding="utf-8") as f:
            mapping_data = json.load(f)
    except Exception:
        pass

async def extract_links_from_current_folder(page, folder_name):
    print(f"\n📁 --- Explorando carpeta: {folder_name} ---")
    await page.wait_for_timeout(4000)
    
    # Dump visible text to find files/folders
    rows = page.locator("[role='row']")
    row_count = await rows.count()
    if row_count == 0:
        # try simple list items
        rows = page.locator(".sMGIOw0") # Wix fileshare list items
        row_count = await rows.count()
        
    print(f"Filas detectadas en la vista: {row_count}")
    
    # We will identify folders and files
    items_to_process = []
    
    # Extract names and info of all rows first
    for i in range(row_count):
        try:
            row = rows.nth(i)
            text = await row.inner_text()
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            if not lines:
                continue
                
            name = lines[0]
            is_folder = "ítem" in text.lower() or "item" in text.lower()
            
            items_to_process.append({
                "index": i,
                "name": name,
                "is_folder": is_folder,
                "full_text": text
            })
        except Exception as e:
            print(f"Error leyendo fila {i}: {e}")
            
    print(f"Items estructurados para procesar: {len(items_to_process)}")
    
    # Process files in current folder
    for item in items_to_process:
        name = item["name"]
        if not item["is_folder"]:
            # It's a file! Let's double-click to capture link
            if name in mapping_data:
                print(f" Skipping file (already mapped): {name}")
                continue
                
            print(f" 📄 Procesando archivo: {name}")
            try:
                target_selector = page.locator(f"text={name}").first
                
                # Double click and intercept download
                async with page.expect_download(timeout=10000) as download_info:
                    await target_selector.dblclick()
                download = await download_info.value
                
                url = download.url
                await download.cancel() # Cancel to save bandwidth
                print(f"   Link extraído: {url[:100]}...")
                
                # Save to mapping
                mapping_data[name] = url
                with open(MAPPING_FILE, "w", encoding="utf-8") as f:
                    json.dump(mapping_data, f, ensure_ascii=False, indent=4)
                    
                # Update DB record synchronously
                # Since we are in async, we can do it because Django setup was loaded
                # Django allows database queries in async context if we wrap or if it runs successfully
                try:
                    books = DigitalBook.objects.filter(title__icontains=name)
                    if books.exists():
                        for b in books:
                            b.pdf_url = url
                            b.save()
                            print(f"   BD actualizada para ID {b.id}")
                except Exception as db_e:
                    print(f"   Error BD: {db_e}")
                    
            except Exception as e:
                print(f"   Error procesando archivo {name}: {e}")
                
    # Process subfolders recursively
    for item in items_to_process:
        name = item["name"]
        if item["is_folder"]:
            print(f" 📂 Entrando a subcarpeta: {name}")
            try:
                folder_selector = page.locator(f"text={name}").first
                await folder_selector.click()
                await page.wait_for_timeout(5000)
                
                # Recursion
                await extract_links_from_current_folder(page, name)
                
                # Go back up
                print(f" ⬅ Volviendo de subcarpeta: {name}")
                breadcrumb = page.locator("text=MEDICINA").first
                if await breadcrumb.count() > 0:
                    await breadcrumb.click()
                    await page.wait_for_timeout(4000)
            except Exception as e:
                print(f"   Error navegando subcarpeta {name}: {e}")

async def main():
    url = "https://secretaria478.wixsite.com/conectafcm/biblioteca-virtual/aea00840-590b-4e56-b96e-4eae57b081a1"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.set_viewport_size({"width": 1280, "height": 800})
        
        print("Navigating to Wix library...")
        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(10000)
        
        # Start crawling from MEDICINA root
        await extract_links_from_current_folder(page, "MEDICINA")
        
        await browser.close()
        print("\n🎉 --- Proceso completado! ---")
        print(f"Total de links en mapping: {len(mapping_data)}")

if __name__ == "__main__":
    asyncio.run(main())
