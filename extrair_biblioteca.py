
from playwright.sync_api import sync_playwright
import json, re, time

# URL correcta del nuevo sitio
URL_WIX = "https://www.conectafcm.com/biblioteca-virtual/aea00840-590b-4e56-b96e-4eae57b081a1"

def extrair_links():
    print("Iniciando navegador para extrair links da biblioteca...")
    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=True)
        page = navegador.new_page()
        page.set_extra_http_headers({
            "Accept-Language": "es-AR,es;q=0.9",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

        page.goto(URL_WIX, wait_until="networkidle", timeout=30000)
        time.sleep(5)

        # Obtener todo el HTML renderizado
        html = page.content()

        # Buscar links de archivos wixstatic ugd (PDFs subidos a Wix)
        ugd_links = re.findall(r'https?://[^\s"\'<>]*wixstatic\.com/ugd/[^\s"\'<>]+', html)
        # Buscar links de Google Drive
        drive_links = re.findall(r'https?://drive\.google\.com/[^\s"\'<>]+', html)
        # Buscar links de docs
        docs_links = re.findall(r'https?://docs\.google\.com/[^\s"\'<>]+', html)

        all_file_links = list(set(ugd_links + drive_links + docs_links))

        # Buscar nombres + links en los elementos del widget
        biblioteca = []

        # Intentar encontrar el widget de Wix FileShare (sQHoZUY, sodGpY0, etc.)
        items = page.query_selector_all("[data-hook='file-item'], .sodGpY0, .sHXqSGb, [class*='fileRow'], [class*='FileRow']")
        print(f"Filas de archivo encontradas: {len(items)}")
        for item in items:
            texto = item.inner_text().strip()
            link_el = item.query_selector("a")
            href = link_el.get_attribute("href") if link_el else None
            if texto or href:
                biblioteca.append({"titulo": texto[:100], "url": href or ""})
                print(f"ARCHIVO: {texto[:60]} -> {href}")

        # Si no encontró items, usar los links de archivos
        if not biblioteca and all_file_links:
            for l in all_file_links:
                biblioteca.append({"titulo": l.split("/")[-1][:80], "url": l})
                print(f"LINK: {l[:80]}")

        # Capturar screenshot para ver qué renderizó
        page.screenshot(path="biblioteca_screenshot.png")

        with open("links_biblioteca.json", "w", encoding="utf-8") as f:
            json.dump(biblioteca, f, ensure_ascii=False, indent=4)

        print(f"\nTotal: {len(biblioteca)} archivos encontrados")
        print(f"Links de archivos Wix/Drive encontrados: {len(all_file_links)}")
        for l in all_file_links[:20]:
            print(f"  {l}")

        navegador.close()

if __name__ == "__main__":
    extrair_links()
