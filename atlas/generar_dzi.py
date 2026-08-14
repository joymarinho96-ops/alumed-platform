#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de Láminas DZI (Deep Zoom Image)
Convierte imágenes PNG/JPG a formato DZI compatible con OpenSeadragon
"""

from PIL import Image
import os
import json
from pathlib import Path
import math

def generar_lamina_dzi(archivo_entrada, nombre_salida):
    """
    Convierte una imagen a formato DZI (Deep Zoom Image)
    
    Args:
        archivo_entrada: Ruta de la imagen de entrada (PNG, JPG, etc)
        nombre_salida: Nombre del archivo de salida (sin extensión)
    """
    try:
        print(f"🔄 Cargando imagen: {archivo_entrada}")
        
        # Cargar imagen con Pillow
        img = Image.open(archivo_entrada)
        img_rgb = img.convert('RGB')  # Garantizar RGB
        
        width, height = img_rgb.size
        print(f"   ✓ Dimensiones: {width} x {height} píxeles")
        
        # Crear directorios
        output_base = f"imagens_laminas/{nombre_salida}"
        output_dir = f"{output_base}_files"
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"🎯 Generando DZI: {output_base}.dzi")
        
        # Parámetros DZI
        tile_size = 256
        overlap = 1
        
        # Calcular profundidad (número de niveles)
        max_dim = max(width, height)
        depth = math.ceil(math.log2(max_dim / tile_size)) + 1
        
        # Generar cada nivel de zoom
        for level in range(depth):
            # Calcular dimensiones de este nivel
            scale = 2 ** (depth - level - 1)
            level_width = max(1, width // scale)
            level_height = max(1, height // scale)
            
            # Redimensionar imagen para este nivel
            level_img = img_rgb.resize((level_width, level_height), Image.Resampling.LANCZOS)
            
            # Crear directorio para este nivel
            level_dir = os.path.join(output_dir, str(level))
            os.makedirs(level_dir, exist_ok=True)
            
            # Generar tiles para este nivel
            tile_count = 0
            for y in range(0, level_height, tile_size - overlap):
                for x in range(0, level_width, tile_size - overlap):
                    # Extraer tile
                    tile_box = (
                        x,
                        y,
                        min(x + tile_size, level_width),
                        min(y + tile_size, level_height)
                    )
                    tile = level_img.crop(tile_box)
                    
                    # Guardar tile
                    tile_col = x // (tile_size - overlap)
                    tile_row = y // (tile_size - overlap)
                    tile_path = os.path.join(level_dir, f"{tile_col}_{tile_row}.jpg")
                    tile.save(tile_path, quality=85)
                    tile_count += 1
            
            print(f"   Nivel {level}: {tile_count} tiles ({level_width}x{level_height})")
        
        # Generar archivo DZI XML
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
        
        print(f"✅ ¡Éxito! Archivo generado: {output_base}.dzi")
        print(f"   📁 Carpeta de tiles: {output_dir}/")
        print(f"   🎨 Profundidad: {depth} niveles de zoom")
        print(f"\n📝 Para usar en OpenSeadragon, configura:")
        print(f'   tileSources: "imagens_laminas/{nombre_salida}.dzi"')
        
        return True
        
    except Exception as e:
        print(f"❌ Error al procesar {archivo_entrada}")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*70)
    print("🔬 Generador de Imágenes Deep Zoom (DZI)")
    print("="*70)
    
    # Convirtiendo lamina_0.jpg como ejemplo
    archivo_origen = "imagens_laminas/lamina_0.jpg"
    
    if os.path.exists(archivo_origen):
        generar_lamina_dzi(archivo_origen, "Lamina15")
    else:
        print(f"❌ Archivo no encontrado: {archivo_origen}")
        print("\nArchivos disponibles:")
        for archivo in os.listdir("imagens_laminas"):
            if archivo.lower().endswith(('.jpg', '.jpeg', '.png')):
                print(f"   - {archivo}")
