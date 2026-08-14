import requests
from PIL import Image
from io import BytesIO
import os

# --- CONFIGURAÇÕES DE ALVO ---
# Essa é a base do visualizador Zoomify deles para a lâmina de Estômago
# Se mudar a lâmina, tem que atualizar essa URL base
URL_BASE = "https://histologyguide.com/slides/MH-111a-cardioesophageal-junction/"

# Nível de Zoom (0 a 6 geralmente). 
# 4 é HD (Rápido). 5 é Full HD (Lento). 6 é 4K (Demora muito).
ZOOM_LEVEL = 4 

def montar_puzzle():
    print(f"🕵️ Iniciando operação de montagem no Zoom {ZOOM_LEVEL}...")
    
    # 1. Descobrir o tamanho do puzzle (Quantas colunas e linhas?)
    # No Zoomify, isso é tentativa e erro ou leitura de XML. 
    # Para o nível 4, geralmente é uma grade de aproximadamente 16x12 peças.
    # Vamos tentar baixar até dar erro 404 (fim da imagem).
    
    colunas_max = 0
    linhas_max = 0
    
    # Vamos chutar alto e deixar o loop parar quando acabar as imagens
    limit_x = 30
    limit_y = 30
    
    # Tamanho de cada peça (padrão Zoomify é 256x256)
    TILE_SIZE = 256
    
    # Lista para guardar as peças na memória
    tiles = []

    print("⬇️ Baixando peças (Isso pode levar um minuto)...")
    
    headers = {'User-Agent': 'Mozilla/5.0'}

    for x in range(limit_x):
        found_y_in_this_col = False
        for y in range(limit_y):
            # O padrão de URL do Zoomify é: TileGroup{grupo}/{z}-{x}-{y}.jpg
            # O "TileGroup" muda a cada 256 arquivos. Para zoom 4, geralmente cabe no Group0.
            # Se falhar, pode precisar de lógica para calcular o grupo.
            
            grupo = 0 
            # (Simplificação: em zooms muito altos, o grupo muda. No 4 deve funcionar no 0 ou 1)
            
            url = f"{URL_BASE}TileGroup{grupo}/{ZOOM_LEVEL}-{x}-{y}.jpg"
            
            try:
                resp = requests.get(url, headers=headers, timeout=10)
                if resp.status_code == 200:
                    img_tile = Image.open(BytesIO(resp.content))
                    tiles.append({'x': x, 'y': y, 'img': img_tile})
                    
                    # Atualiza os limites máximos encontrados
                    if x > colunas_max: colunas_max = x
                    if y > linhas_max: linhas_max = y
                    
                    found_y_in_this_col = True
                    print(f"   🧩 Peça {x},{y} capturada.", end='\r')
                else:
                    # Se deu 404, acabou a coluna ou a linha
                    break
            except:
                break
        
        # Se não achou nada nesta coluna X, é porque a imagem acabou na largura
        if not found_y_in_this_col and x > 0:
            break

    print(f"\n✅ Download concluído! Grade encontrada: {colunas_max+1} x {linhas_max+1} peças.")

    # 2. Criar a tela em branco do tamanho final
    largura_total = (colunas_max + 1) * TILE_SIZE
    altura_total = (linhas_max + 1) * TILE_SIZE
    
    print(f"🎨 Costurando imagem final de {largura_total}x{altura_total} pixels...")
    
    imagem_final = Image.new('RGB', (largura_total, altura_total))

    # 3. Colar as peças
    for tile in tiles:
        pos_x = tile['x'] * TILE_SIZE
        pos_y = tile['y'] * TILE_SIZE
        imagem_final.paste(tile['img'], (pos_x, pos_y))

    # 4. Salvar
    output_filename = "imagens_laminas/lamina_amiguinho_hd.jpg"
    imagem_final.save(output_filename, quality=90)
    
    print(f"🚀 SUCESSO! Imagem salva em: {output_filename}")
    print(f"📊 Dimensões finais: {largura_total} x {altura_total} pixels")
    print("Agora atualize seu visualizador_pro.html para apontar para este arquivo.")

if __name__ == "__main__":
    montar_puzzle()
