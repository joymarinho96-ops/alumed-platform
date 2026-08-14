import requests
from PIL import Image
from io import BytesIO
import os
import time

# --- CONFIGURAÇÕES DE ALVO ---
URL_BASE = "https://histologyguide.com/slides/MH-111a-cardioesophageal-junction/"

# Nível de Zoom: 3 (muito grande), 4 (grande), 5 (HD), 6 (Full HD)
# Vamos tentar o 5 que deve dar um tamanho bom
ZOOM_LEVEL = 5

def montar_puzzle_melhorado():
    print(f"🕵️ Iniciando montagem TURBO no Zoom {ZOOM_LEVEL}...")
    print("⚠️ Isso pode levar alguns minutos. Seja paciente...\n")
    
    # Tamanho padrão de cada tile no Zoomify
    TILE_SIZE = 256
    
    # Vamos tentar descobrir o tamanho real
    tiles = {}
    colunas = 0
    linhas = 0
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    # Limites de busca
    max_x = 50
    max_y = 50
    
    print("⬇️ Fase 1: Descobrindo dimensões da grade...")
    
    # Tenta vários grupos (TileGroup0, TileGroup1, etc)
    for grupo in range(3):
        print(f"   Testando TileGroup{grupo}...")
        encontrou = False
        
        for x in range(max_x):
            for y in range(max_y):
                url = f"{URL_BASE}TileGroup{grupo}/{ZOOM_LEVEL}-{x}-{y}.jpg"
                
                try:
                    resp = requests.get(url, headers=headers, timeout=5)
                    
                    if resp.status_code == 200:
                        img_tile = Image.open(BytesIO(resp.content))
                        chave = (x, y)
                        tiles[chave] = img_tile
                        
                        # Atualiza limites
                        if x > colunas: colunas = x
                        if y > linhas: linhas = y
                        
                        encontrou = True
                        print(f"   ✓ Tile {x},{y} (Grupo {grupo})", end='\r')
                        
                        # Pequena pausa para não sobrecarregar
                        time.sleep(0.1)
                    else:
                        if encontrou and x > colunas + 2:
                            # Se já encontrou e passou do limite, para
                            break
                except requests.Timeout:
                    print(f"   ⏱️ Timeout na leitura de {x},{y}")
                    continue
                except Exception as e:
                    continue
            
            if encontrou and x > colunas + 2:
                break
        
        if encontrou:
            print(f"   ✅ TileGroup{grupo}: {colunas+1} x {linhas+1} tiles")

    if not tiles:
        print("❌ Nenhum tile foi baixado! O servidor pode estar bloqueando.")
        print("💡 Dica: Tente acessar manualmente a URL no navegador para verificar.")
        return

    print(f"\n✅ Download completo! {len(tiles)} tiles capturados")
    print(f"📐 Grade: {colunas+1} colunas x {linhas+1} linhas\n")

    # Montar a imagem final
    largura_total = (colunas + 1) * TILE_SIZE
    altura_total = (linhas + 1) * TILE_SIZE
    
    print(f"🎨 Montando imagem final: {largura_total} x {altura_total} pixels...")
    
    imagem_final = Image.new('RGB', (largura_total, altura_total), color=(255, 255, 255))

    # Colar todos os tiles
    for (x, y), tile_img in tiles.items():
        pos_x = x * TILE_SIZE
        pos_y = y * TILE_SIZE
        
        # Resize tile para garantir 256x256 se necessário
        if tile_img.size != (TILE_SIZE, TILE_SIZE):
            tile_img = tile_img.resize((TILE_SIZE, TILE_SIZE), Image.Resampling.LANCZOS)
        
        imagem_final.paste(tile_img, (pos_x, pos_y))

    # Salvar
    output_path = "imagens_laminas/lamina_amiguinho_ultra_hd.jpg"
    os.makedirs("imagens_laminas", exist_ok=True)
    imagem_final.save(output_path, quality=95)
    
    tamanho_mb = os.path.getsize(output_path) / (1024*1024)
    
    print(f"\n{'='*50}")
    print(f"🚀 SUCESSO!")
    print(f"{'='*50}")
    print(f"📁 Arquivo: {output_path}")
    print(f"📊 Dimensões: {largura_total} x {altura_total} pixels")
    print(f"💾 Tamanho: {tamanho_mb:.2f} MB")
    print(f"{'='*50}")
    print("\n🔄 Agora execute: python atualizar_visualizador.py")

if __name__ == "__main__":
    montar_puzzle_melhorado()
