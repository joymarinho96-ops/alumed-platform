import asyncio
import os
import sys
import django

# Add project root to sys.path
sys.path.append(r"c:\Users\joyce\Downloads\alumesitemdesenvolvimento-main\alumed-platform")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumed.settings')
django.setup()

from core.models import DigitalBook
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

# We target these files for local download and database link update
TARGET_FILES = [
    {
        "folder_path": ["1ER AÑO", "ANATOMÍA", "LIBROS"],
        "name_in_wix": "Anatomía Cardiológica - San Mauro.pdf",
        "db_title_query": "Anatomía Cardiológica - San Mauro.pdf"
    },
    {
        "folder_path": ["1ER AÑO", "ANATOMÍA", "LIBROS"],
        "name_in_wix": "Anatomía Humana - Rouvière y Delmas 11va Edición Tomo N.° 3.pdf",
        "db_title_query": "Anatomía Humana - Rouvière y Delmas 11va Edición Tomo N.° 3.pdf"
    }
]

async def download_book(page, file_info):
    folder_path = file_info["folder_path"]
    name_in_wix = file_info["name_in_wix"]
    db_title_query = file_info["db_title_query"]
    
    print(f"\n--- Iniciando descarga de: {name_in_wix} ---")
    
    # 1. Navigate folders
    # First, return to MEDICINA root breadcrumb if not there
    try:
        breadcrumb = page.locator("text=MEDICINA").first
        if await breadcrumb.count() > 0:
            await breadcrumb.click()
            await page.wait_for_timeout(3000)
    except Exception:
        pass
        
    for idx, folder in enumerate(folder_path):
        print(f" Navigating into: {folder}")
        elem = page.locator(f"text={folder}").first
        if await elem.count() > 0:
            await elem.click()
            await page.wait_for_timeout(4000)
        else:
            print(f" Folder {folder} not found.")
            return False

    # 2. Wait and find row
    target_selector = f"text={name_in_wix}"
    if await page.locator(target_selector).first.count() == 0:
        # try without extension
        clean_name = name_in_wix.replace(".pdf", "").replace(".PDF", "")
        target_selector = f"text={clean_name}"
        
    if await page.locator(target_selector).first.count() > 0:
        print(" File found in list! Triggering download...")
        try:
            async with page.expect_download(timeout=30000) as download_info:
                await page.locator(target_selector).first.dblclick()
            download = await download_info.value
            
            # Destination path
            dest_dir = os.path.join("media", "library", "pdfs")
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, name_in_wix)
            
            print(f" Downloading to: {dest_path}")
            await download.save_as(dest_path)
            print(" Download completed successfully!")
            
            # Update database
            db_rel_path = f"library/pdfs/{name_in_wix}"
            books_updated = DigitalBook.objects.filter(title__icontains=db_title_query)
            if books_updated.exists():
                for b in books_updated:
                    b.pdf_file = db_rel_path
                    b.save()
                    print(f" Database updated for book ID {b.id}: {b.title} -> pdf_file={db_rel_path}")
                return True
            else:
                # Create if doesn't exist
                b = DigitalBook.objects.create(
                    title=name_in_wix,
                    subject="anato",
                    category="Libro Oficial",
                    year="1º Año",
                    pdf_file=db_rel_path,
                    status="confirmado"
                )
                print(f" Created new book entry in database ID {b.id} with file link.")
                return True
        except Exception as e:
            print(f" Error during download/DB update: {e}")
    else:
        print(f" File {name_in_wix} not found in listing.")
        
    return False

async def main():
    url = "https://secretaria478.wixsite.com/conectafcm/biblioteca-virtual/aea00840-590b-4e56-b96e-4eae57b081a1"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.set_viewport_size({"width": 1280, "height": 800})
        
        print("Navigating to Wix library...")
        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(10000)
        
        for file_info in TARGET_FILES:
            await download_book(page, file_info)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
