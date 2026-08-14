#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script otimizado para baixar lâminas histológicas da UFRJ.
Estrategia: Baixar apenas as imagens principais, não toda a pirâmide.
"""

import os
import json
import sys
import requests
from pathlib import Path
from time import sleep

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')

class DescargarLaminasUFRJ:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0'
        })
        self.base_dir = Path(__file__).parent / 'imagens_laminas'
        self.base_dir.mkdir(exist_ok=True)
        self.laminas_descargadas = 0
        self.total_intentos = 0
        
    def cargar_laminas_datos(self):
        """Carga datos de laminas_ufrj_dados.json"""
        json_path = Path(__file__).parent / 'laminas_ufrj_dados.json'
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Si es un array, ya está bien formateado
            if isinstance(data, list):
                return data
            # Si es dict, extraer la lista de laminas
            elif 'laminas' in data:
                return data['laminas']
            return []
    
    def descargar_imagen(self, url, ruta_local, reintentos=3):
        """Descarga una imagen con reintentos"""
        self.total_intentos += 1
        
        for intento in range(reintentos):
            try:
                respuesta = self.session.get(url, timeout=10)
                respuesta.raise_for_status()
                
                # Crear directorio si no existe
                ruta_local.parent.mkdir(parents=True, exist_ok=True)
                
                with open(ruta_local, 'wb') as f:
                    f.write(respuesta.content)
                
                tamaño = len(respuesta.content) / (1024 * 1024)  # MB
                print(f"  [OK] {ruta_local.name} ({tamaño:.1f} MB)")
                return True
                
            except Exception as e:
                if intento < reintentos - 1:
                    print(f"  [RETRY] Intento {intento + 1}/{reintentos}...")
                    sleep(1)
        
        print(f"  [SKIP] No se pudo descargar")
        return False
    
    def descargar_lamina(self, lamina_id, url_base):
        """
        Descarga una lámina intentando varios niveles de zoom.
        Estrategia: Probar niveles 5, 4, 3, 2 (no todos)
        """
        print(f"\n[*] {lamina_id}")
        
        # Niveles a probar (de mayor a menor zoom)
        niveles_a_probar = [5, 4, 3, 2, 1, 0]
        directorio_lamina = self.base_dir / f"lamina_{lamina_id}"
        
        descargado = False
        for nivel in niveles_a_probar:
            # Intentar URLs comunes
            urls_nivel = [
                f"{url_base}{nivel}/0_0.jpg",
                f"{url_base}{nivel}/0_0.png",
                f"{url_base}l{nivel}.jpg",
                f"{url_base}{nivel}.jpg",
            ]
            
            for url in urls_nivel:
                ruta_local = directorio_lamina / f"nivel_{nivel}_0_0.jpg"
                
                # No descargar de nuevo si ya existe
                if ruta_local.exists():
                    print(f"  [SKIP] Nivel {nivel} ya existe")
                    descargado = True
                    break
                
                try:
                    respuesta = self.session.head(url, timeout=5)
                    if respuesta.status_code == 200:
                        print(f"  Descargando nivel {nivel}...", end=" ", flush=True)
                        if self.descargar_imagen(url, ruta_local, reintentos=2):
                            descargado = True
                            break
                except:
                    pass
            
            if descargado:
                break
        
        if descargado:
            self.laminas_descargadas += 1
        else:
            # Si no se descargó nada, al menos crear la carpeta
            directorio_lamina.mkdir(parents=True, exist_ok=True)
        
        return descargado
    
    def actualizar_json_con_urls_locales(self):
        """Actualiza el JSON con URLs locales"""
        json_path = Path(__file__).parent / 'laminas_ufrj_datos.json'
        
        with open(json_path, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        # Asegurar que sea una lista
        if not isinstance(datos, list):
            if 'laminas' in datos:
                datos = datos['laminas']
            else:
                return
        
        # Agregar URL local a cada lámina
        for lamina in datos:
            lamina['url_local'] = f"/imagens_laminas/lamina_{lamina['id']}/nivel_0_0.jpg"
        
        # Guardar actualizado
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
        
        print(f"\n[OK] Metadatos actualizados en {json_path}")
    
    def ejecutar(self):
        """Ejecuta el descargador"""
        print("=" * 60)
        print("DESCARGADOR DE LAMINAS HISTOLOGICAS UFRJ (Optimizado)")
        print("=" * 60)
        
        # Cargar datos
        print("\n[*] Cargando datos...")
        laminas = self.cargar_laminas_datos()
        total = len(laminas)
        print(f"[OK] {total} laminas encontradas")
        
        # Descargar cada lámina
        print("\n[*] Descargando laminas...")
        for i, lamina in enumerate(laminas, 1):
            print(f"\n[{i}/{total}] {lamina['nombre']}")
            self.descargar_lamina(
                lamina['id'],
                lamina['url_base']
            )
        
        # Actualizar metadatos
        print("\n[*] Actualizando metadatos...")
        self.actualizar_json_con_urls_locales()
        
        # Resumen
        print("\n" + "=" * 60)
        print("[DONE] Proceso completado!")
        print("=" * 60)
        print(f"\nResultados:")
        print(f"  Laminas descargadas: {self.laminas_descargadas}/{total}")
        print(f"  Intentos de descarga: {self.total_intentos}")
        print(f"  Ubicacion: {self.base_dir}")
        print(f"\n[NEXT] Inicia el servidor:")
        print(f"  python -m http.server 8000")
        print(f"\n[BROWSER] Abre:")
        print(f"  http://localhost:8000/microscopio_virtual.html")

if __name__ == '__main__':
    try:
        descargador = DescargarLaminasUFRJ()
        descargador.ejecutar()
    except KeyboardInterrupt:
        print("\n\n[!] Descarga cancelada por el usuario")
    except Exception as e:
        print(f"\n[ERROR] {e}")
