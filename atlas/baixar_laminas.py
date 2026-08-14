import json
import requests
from PIL import Image
from io import BytesIO
import os

def baixar_laminas():
    # 1. Carregar os dados que raspamos
    print("📂 Lendo arquivo 'laminas_banco_dados.json'...")
    
    try:
        with open('laminas_banco_dados.json', 'r', encoding='utf-8') as f:
            dados = json.load(f)
            
            # Se o JSON for apenas um objeto (uma lâmina), transforma em lista
            if isinstance(dados, dict):
                laminas = [dados]
            else:
                laminas = dados
    except FileNotFoundError:
        print("❌ Erro: Arquivo 'laminas_banco_dados.json' não encontrado.")
        return

    print(f"🎯 Encontrei {len(laminas)} lâminas para baixar.")

    # 2. Criar pasta para salvar as imagens
    if not os.path.exists('imagens_laminas'):
        os.makedirs('imagens_laminas')

    # 3. Loop para baixar cada uma
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    for i, lamina in enumerate(laminas):
        nome_arquivo = f"lamina_{i}.jpg"
        caminho_final = os.path.join('imagens_laminas', nome_arquivo)
        
        print(f"\n🔬 Processando: {lamina.get('titulo', 'Sem Título')}")
        
        # TRUQUE HACKER:
        # A URL original é algo como: .../slideview/MH-111a.../14-slide-2.html
        # A imagem de capa geralmente fica em: .../slideview/MH-111a.../imgs/slide.png
        # Vamos tentar deduzir a URL da imagem baseada na URL da página.
        
        url_origem = lamina.get('url', '')
        if not url_origem:
            print("   ⚠️ Pulei: URL de origem não encontrada.")
            continue
            
        # Tenta achar o diretório base da imagem
        # De: .../14-slide-2.html -> Para: .../imgs/slide.png
        base_url = url_origem.rsplit('/', 1)[0]
        url_imagem = f"{base_url}/imgs/slide.png"
        
        print(f"   ⬇️ Baixando de: {url_imagem}")
        
        try:
            response = requests.get(url_imagem, headers=headers)
            if response.status_code == 200:
                # Salva a imagem
                img = Image.open(BytesIO(response.content))
                # Converte para RGB se necessário (para salvar como JPEG)
                if img.mode in ('RGBA', 'P', 'LA'):
                    bg = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    bg.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = bg
                img.save(caminho_final, 'JPEG', quality=95)
                print(f"   ✅ Sucesso! Salva em '{caminho_final}'")
            else:
                print(f"   ❌ Falha (Erro {response.status_code}). O site pode ter bloqueado.")
        except Exception as e:
            print(f"   ❌ Erro técnico: {e}")

if __name__ == "__main__":
    baixar_laminas()
