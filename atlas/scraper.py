import requests
from bs4 import BeautifulSoup
import json

# URL da lâmina que você mandou o print (Estômago)
url = "https://histologyguide.com/slideview/MH-111a-cardioesophageal-junction/14-slide-2.html"

print(f"🕵️ Acessando: {url}...")

# Fingindo ser um navegador comum para não ser bloqueado
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # 1. Pegar o Título da Lâmina
    titulo = soup.find('h2').text.strip() if soup.find('h2') else "Título não encontrado"
    
    # 2. Pegar a Descrição (Texto lateral)
    # No HTML deles, a descrição está dentro de uma div com id 'sidebar'
    sidebar = soup.find('div', id='sidebar')
    descricao = sidebar.find('p').text.strip() if sidebar and sidebar.find('p') else "Sem descrição"

    # 3. Extrair os botões/marcações (As estruturas anatômicas)
    marcacoes = []
    # Eles usam botões dentro de listas <ul> com 'onclick' para o zoom
    botoes = sidebar.find_all('button') if sidebar else []
    
    for botao in botoes:
        nome_estrutura = botao.text.strip()
        acao_zoom = botao.get('onclick') # Ex: zZoomAndPanToView(28273, 10367, 3.6)
        
        if acao_zoom and 'zZoomAndPanToView' in acao_zoom:
            # Limpando o texto para pegar só os números
            numeros = acao_zoom.replace('zZoomAndPanToView(', '').replace(')', '').split(',')
            if len(numeros) >= 3:
                x = int(numeros[0].strip())
                y = int(numeros[1].strip())
                zoom = float(numeros[2].strip())
                
                marcacoes.append({
                    "nome": nome_estrutura,
                    "x_original": x,
                    "y_original": y,
                    "zoom": zoom
                })

    # Criando o objeto final
    lamina_data = {
        "titulo": titulo,
        "url_origem": url,
        "descricao": descricao,
        "estruturas_identificadas": marcacoes
    }

    # Salvando em um arquivo JSON
    with open('laminas_coletadas.json', 'w', encoding='utf-8') as f:
        json.dump(lamina_data, f, indent=4, ensure_ascii=False)

    print("✅ Sucesso! Dados salvos em 'laminas_coletadas.json'")
    print(f"Título: {titulo}")
    print(f"Estruturas encontradas: {len(marcacoes)}")

except Exception as e:
    print(f"❌ Erro ao acessar: {e}")
