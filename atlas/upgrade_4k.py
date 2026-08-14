import requests
import os

def upgrade_para_4k():
    print("🚀 Iniciando Upgrade de Definição (4K)...")
    
    # URL de uma lâmina de histologia de alta resolução
    url_hd = "https://libimages1.princeton.edu/loris/pudl0001%2F4609321%2Fs42%2F00000001.jp2/full/full/0/default.jpg"
    
    caminho_arquivo = "imagens_laminas/lamina_0.jpg"
    
    # Cabeçalhos para não sermos bloqueados
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0'
    }

    try:
        print(f"⬇️ Baixando imagem de alta fidelidade (pode demorar um pouco, é grande!)...")
        response = requests.get(url_hd, headers=headers, stream=True)
        
        if response.status_code == 200:
            with open(caminho_arquivo, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("✅ SUCESSO! A imagem foi atualizada para HD.")
            print("🔄 Vá no navegador e aperte Ctrl + F5 (Limpar Cache) para ver a diferença.")
        else:
            print(f"❌ Erro no download: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro técnico: {e}")

if __name__ == "__main__":
    upgrade_para_4k()
