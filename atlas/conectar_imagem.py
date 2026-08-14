import re
import os

def conectar_imagem_ao_site():
    caminho_html = 'index.html'
    caminho_imagem = 'imagens_laminas/lamina_0.jpg'

    # Verifica se a imagem e o site existem
    if not os.path.exists(caminho_html):
        print("❌ Erro: Não encontrei o arquivo index.html")
        return
    
    if not os.path.exists(caminho_imagem):
        print(f"⚠️ Aviso: A imagem '{caminho_imagem}' não foi encontrada na pasta.")
        print("Mas vou atualizar o código mesmo assim, assumindo que você vai colocar ela lá.")

    print("🔍 Lendo o código do site...")
    
    with open(caminho_html, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # A MÁGICA (REGEX):
    # Procura por: url: '...qualquer coisa...',
    # E substitui pelo caminho da nossa lâmina
    
    padrao = r"url:\s*['\"].*?['\"],"
    nova_linha = f"url:  '{caminho_imagem}',"
    
    # Verifica se encontrou algo antes de substituir
    if re.search(padrao, conteudo):
        novo_conteudo = re.sub(padrao, nova_linha, conteudo, count=1)
        
        with open(caminho_html, 'w', encoding='utf-8') as f:
            f.write(novo_conteudo)
            
        print("✅ SUCESSO! O código foi atualizado.")
        print(f"🔗 Imagem conectada: {caminho_imagem}")
        print("🚀 Pode abrir o site no navegador agora!")
    else:
        print("❌ Não encontrei a linha 'url:' no seu index.html.")
        print("Verifique se o código do OpenSeadragon está lá certinho.")

if __name__ == "__main__":
    conectar_imagem_ao_site()
