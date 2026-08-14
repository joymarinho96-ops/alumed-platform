import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin

# Lista de URLs das lâminas histológicas
urls_laminas = [
    "https://histologyguide.com/slideview/MH-111a-cardioesophageal-junction/14-slide-2.html",
    "https://histologyguide.com/slideview/MH-111-stomach-fundus/8-slide-2.html",
    "https://histologyguide.com/slideview/MH-112-stomach-pylorus/8-slide-2.html",
]

# Headers para não ser bloqueado
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

laminas_completas = []

for url in urls_laminas:
    print(f"\n🕵️ Processando: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 1. Título da Lâmina
        titulo = soup.find('h2')
        titulo_texto = titulo.text.strip() if titulo else "Sem título"
        
        # 2. Descrição
        sidebar = soup.find('div', id='sidebar')
        descricao = ""
        if sidebar:
            paragrafo = sidebar.find('p')
            descricao = paragrafo.text.strip() if paragrafo else ""

        # 3. Extrair estruturas identificadas
        marcacoes = []
        if sidebar:
            botoes = sidebar.find_all('button')
            for botao in botoes:
                nome = botao.text.strip()
                onclick = botao.get('onclick', '')
                
                if 'zZoomAndPanToView' in onclick:
                    try:
                        # Extrair números: zZoomAndPanToView(x, y, zoom)
                        numeros = onclick.replace('zZoomAndPanToView(', '').replace(')', '').split(',')
                        if len(numeros) >= 3:
                            x = int(numeros[0].strip())
                            y = int(numeros[1].strip())
                            zoom = float(numeros[2].strip())
                            
                            marcacoes.append({
                                "nome": nome,
                                "x": x,
                                "y": y,
                                "zoom": zoom
                            })
                    except:
                        pass

        # 4. Criar objeto da lâmina
        lamina = {
            "titulo": titulo_texto,
            "url": url,
            "descricao": descricao,
            "total_estruturas": len(marcacoes),
            "estruturas": marcacoes
        }
        
        laminas_completas.append(lamina)
        print(f"✅ {titulo_texto} - {len(marcacoes)} estruturas encontradas")
        
        # Pequena pausa para não sobrecarregar o servidor
        time.sleep(1)

    except Exception as e:
        print(f"❌ Erro ao processar {url}: {e}")

# Salvar em JSON
with open('laminas_banco_dados.json', 'w', encoding='utf-8') as f:
    json.dump(laminas_completas, f, indent=4, ensure_ascii=False)

print(f"\n{'='*50}")
print(f"📊 RESUMO DA COLETA")
print(f"{'='*50}")
print(f"Total de lâminas coletadas: {len(laminas_completas)}")
print(f"Total de estruturas: {sum(l['total_estruturas'] for l in laminas_completas)}")
print(f"✅ Dados salvos em 'laminas_banco_dados.json'")
