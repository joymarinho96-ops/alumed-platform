from playwright.sync_api import sync_playwright
import json

URL_WIX = "https://secretaria478.wixsite.com/conectafcm/biblioteca-virtual/aea00840-590b-4e56-b96e-4eae57b081a1"

def extrair_links():
    print("🚀 Iniciando o navegador fantasma para invadir o Wix...")
    with sync_playwright() as p:
        # Abre o navegador invisível (mude headless=False se quiser ver a tela abrindo)
        navegador = p.chromium.launch(headless=True)
        pagina = navegador.new_page()
        
        # Vai até a sua biblioteca virtual
        pagina.goto(URL_WIX)
        
        print("⏳ Esperando o widget do Wix carregar os livros...")
        # O robô espera até que as tags de link (<a>) do widget apareçam na tela
        pagina.wait_for_selector("a") 
        
        # Puxa todos os links da página
        elementos = pagina.query_selector_all("a")
        
        biblioteca = []
        for el in elementos:
            nome_livro = el.inner_text().strip()
            link = el.get_attribute("href")
            
            # Filtra apenas os links que parecem ser arquivos do Wix (PDFs, docs)
            if link and ("media" in link or "files" in link or "wixstatic" in link):
                biblioteca.append({"titulo": nome_livro, "url": link})
                print(f"📖 Encontrado: {nome_livro} -> {link}")
        
        # Salva a lista estruturada em um arquivo JSON
        with open("links_biblioteca.json", "w", encoding="utf-8") as f:
            json.dump(biblioteca, f, ensure_ascii=False, indent=4)
            
        print(f"\n✅ SUCESSO! {len(biblioteca)} livros extraídos e salvos em 'links_biblioteca.json'.")
        navegador.close()

if __name__ == "__main__":
    extrair_links()
