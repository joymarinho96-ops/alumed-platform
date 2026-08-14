"""
extrair_biblioteca.py
---------------------
Extrai todos os links de PDFs e arquivos da Biblioteca Virtual do Conecta FCM
(hospedada no Wix com carregamento assíncrono via FileShareOoiViewerWidget).

Uso:
    python scripts/extrair_biblioteca.py

Resultado:
    Gera/atualiza o arquivo 'scripts/links_biblioteca.json' com estrutura:
    [{"titulo": "...", "url": "...", "materia": "..."}]

Requisitos:
    pip install playwright
    playwright install chromium
"""

import asyncio
import json
import os
import sys

# Garante encoding UTF-8 no terminal Windows
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from playwright.async_api import async_playwright

# URL pública da biblioteca do Conecta FCM
URL_BIBLIOTECA = (
    "https://secretaria478.wixsite.com/conectafcm"
    "/biblioteca-virtual/aea00840-590b-4e56-b96e-4eae57b081a1"
)

# Arquivo de saída (relativo à raiz do projeto)
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "links_biblioteca.json")


def deduzir_materia(titulo: str) -> str:
    """Categoriza automaticamente o arquivo pela palavra-chave do título."""
    t = titulo.lower()
    if any(k in t for k in ["histo", "tejido", "epitelio", "lamina", "tinción"]):
        return "Histología"
    if any(k in t for k in ["anato", "arteria", "musculo", "nervio", "hueso"]):
        return "Anatomía"
    if any(k in t for k in ["embrio", "derivado", "desarrollo", "fetal"]):
        return "Embriología"
    if any(k in t for k in ["bio", "celular", "karp", "molecular"]):
        return "Biología"
    if any(k in t for k in ["fisio", "fisiolog"]):
        return "Fisiología"
    if any(k in t for k in ["bioquim", "bioquímic"]):
        return "Bioquímica"
    return "General"


async def extrair_biblioteca() -> list[dict]:
    """Abre a biblioteca com Playwright e extrai todos os links de arquivos."""
    biblioteca_data: list[dict] = []
    vistos: set[str] = set()

    # Carrega dados já extraídos anteriormente (modo incremental)
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            try:
                existentes = json.load(f)
                for item in existentes:
                    biblioteca_data.append(item)
                    vistos.add(item["url"])
                print(f"📂 Carregados {len(existentes)} registros existentes.")
            except json.JSONDecodeError:
                pass

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.set_viewport_size({"width": 1280, "height": 800})

        print(f"🌐 Navegando até: {URL_BIBLIOTECA}")
        await page.goto(URL_BIBLIOTECA, wait_until="networkidle", timeout=30000)

        print("⏳ Aguardando carregamento do widget Wix FileShare...")
        try:
            await page.wait_for_selector("a[href]", timeout=20000)
        except Exception:
            print("⚠️  Seletor não encontrado a tempo. Continuando com o que renderizou.")

        # Aguarda mais um pouco para garantir renderização completa
        await page.wait_for_timeout(5000)

        # Extrai todos os links do DOM
        links = await page.query_selector_all("a[href]")
        print(f"🔍 {len(links)} elementos <a> encontrados no DOM.")

        novos = 0
        for link_element in links:
            try:
                titulo = (await link_element.inner_text()).strip().replace("\n", " ")
                url = await link_element.get_attribute("href")

                if not url or not titulo:
                    continue

                # Filtra apenas links de arquivos hospedados no Wix ou Google Drive
                eh_arquivo = (
                    "wixstatic.com/media/" in url
                    or "drive.google.com" in url
                    or url.endswith(".pdf")
                    or url.endswith(".docx")
                    or url.endswith(".pptx")
                )

                if eh_arquivo and url not in vistos:
                    item = {
                        "titulo": titulo,
                        "url": url,
                        "materia": deduzir_materia(titulo),
                    }
                    biblioteca_data.append(item)
                    vistos.add(url)
                    novos += 1
                    print(f"  ✅ [{item['materia']}] {titulo[:60]}")

            except Exception as e:
                print(f"  ⚠️  Erro ao processar link: {e}")

        await browser.close()
        print(f"\n🎉 Extração concluída! {novos} novos links encontrados.")

    # Salva o resultado
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(biblioteca_data, f, ensure_ascii=False, indent=4)

    print(f"💾 Total salvo em '{OUTPUT_FILE}': {len(biblioteca_data)} recursos.")
    return biblioteca_data


if __name__ == "__main__":
    asyncio.run(extrair_biblioteca())
