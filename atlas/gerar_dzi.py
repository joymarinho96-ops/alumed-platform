#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de arquivos DZI (Deep Zoom Image) a partir de imagens histológicas
Converte imagens PNG/JPG para formato DZI compatível com OpenSeadragon
"""

from PIL import Image
import os
import json
from pathlib import Path
import math

def gerar_lamina_dzi(arquivo_entrada, nome_saida):
    """
    Converte uma imagem para formato DZI (Deep Zoom Image)
    
    Args:
        arquivo_entrada: Caminho da imagem de entrada (PNG, JPG, etc)
        nome_saida: Nome do arquivo de saída (sem extensão)
    """
    try:
        print(f"🔄 Carregando imagem: {arquivo_entrada}")
        
        # Carregar imagem com Pillow
        img = Image.open(arquivo_entrada)
        img_rgb = img.convert('RGB')  # Garantir RGB
        
        width, height = img_rgb.size
        print(f"   ✓ Dimensões: {width} x {height} pixels")
        
        # Criar diretórios
        output_base = f"imagens_laminas/{nome_saida}"
        output_dir = f"{output_base}_files"
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"🎯 Gerando DZI: {output_base}.dzi")
        
        # Parâmetros DZI
        tile_size = 256
        overlap = 1
        
        # Calcular profundidade (número de níveis)
        max_dim = max(width, height)
        depth = math.ceil(math.log2(max_dim / tile_size)) + 1
        
        # Gerar cada nível de zoom
        for level in range(depth):
            # Calcular dimensões deste nível
            scale = 2 ** (depth - level - 1)
            level_width = max(1, width // scale)
            level_height = max(1, height // scale)
            
            # Redimensionar imagem para este nível
            level_img = img_rgb.resize((level_width, level_height), Image.Resampling.LANCZOS)
            
            # Criar diretório para este nível
            level_dir = os.path.join(output_dir, str(level))
            os.makedirs(level_dir, exist_ok=True)
            
            # Gerar tiles para este nível
            tile_count = 0
            for y in range(0, level_height, tile_size - overlap):
                for x in range(0, level_width, tile_size - overlap):
                    # Extrair tile
                    tile_box = (
                        x,
                        y,
                        min(x + tile_size, level_width),
                        min(y + tile_size, level_height)
                    )
                    tile = level_img.crop(tile_box)
                    
                    # Salvar tile
                    tile_col = x // (tile_size - overlap)
                    tile_row = y // (tile_size - overlap)
                    tile_path = os.path.join(level_dir, f"{tile_col}_{tile_row}.jpg")
                    tile.save(tile_path, quality=85)
                    tile_count += 1
            
            print(f"   Level {level}: {tile_count} tiles ({level_width}x{level_height})")
        
        # Gerar arquivo DZI XML
        dzi_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<Image xmlns="http://schemas.microsoft.com/deep-zoom/2008"
       TileSize="256"
       Overlap="1"
       Format="jpg">
    <Size Width="{width}" Height="{height}"/>
</Image>'''
        
        dzi_path = f"{output_base}.dzi"
        with open(dzi_path, 'w') as f:
            f.write(dzi_content)
        
        print(f"✅ Sucesso! Arquivo gerado: {output_base}.dzi")
        print(f"   📁 Pasta de tiles: {output_dir}/")
        print(f"   🎨 Profundidade: {depth} níveis de zoom")
        print(f"\n📝 Para usar no OpenSeadragon, configure:")
        print(f'   tileSources: "imagens_laminas/{nome_saida}.dzi"')
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao processar {arquivo_entrada}")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*60)
    print("🔬 Gerador de Deep Zoom Images (DZI)")
    print("="*60)
    
    # Convertendo lamina_0.jpg como exemplo
    arquivo_origem = "imagens_laminas/lamina_0.jpg"
    
    if os.path.exists(arquivo_origem):
        gerar_lamina_dzi(arquivo_origem, "Lamina15")
    else:
        print(f"❌ Arquivo não encontrado: {arquivo_origem}")
        print("\nArquivos disponíveis:")
        for arquivo in os.listdir("imagens_laminas"):
            if arquivo.lower().endswith(('.jpg', '.jpeg', '.png')):
                print(f"   - {arquivo}")
