#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para baixar lâminas histológicas da UFRJ localmente.
Evita problema de CORS no navegador.
Estrutura: imagens_laminas/lamina_{id}/nivel/x_y.jpg
"""

import os
import json
import sys
import requests
from pathlib import Path
from time import sleep
from urllib.parse import urljoin

# Configurar encoding UTF-8 para console
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')

class DescargarLaminasUFRJ:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.base_dir = Path(__file__).parent / 'imagens_laminas'
        self.base_dir.mkdir(exist_ok=True)
        
    def cargar_laminas_datos(self):
        """Carga datos de laminas_ufrj_datos.json"""
        json_path = Path(__file__).parent / 'laminas_ufrj_dados.json'
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Si es un array, convertir a dict por sistema
            if isinstance(data, list):
                laminas_dict = {}
                for lamina in data:
                    sistema = lamina.get('sistema', 'Sin clasificar')
                    if sistema not in laminas_dict:
                        laminas_dict[sistema] = []
                    laminas_dict[sistema].append(lamina)
                return laminas_dict
            return data
    
    def descargar_imagen(self, url, ruta_local, reintentos=3):
        """Descarga una imagen con reintentos"""
        for intento in range(reintentos):
            try:
                respuesta = self.session.get(url, timeout=10)
                respuesta.raise_for_status()
                
                # Crear directorio si no existe
                ruta_local.parent.mkdir(parents=True, exist_ok=True)
                
                with open(ruta_local, 'wb') as f:
                    f.write(respuesta.content)
                
                return True
            except Exception as e:
                print(f"  [!] Intento {intento + 1}/{reintentos} fallo: {e}")
                if intento < reintentos - 1:
                    sleep(2)  # Esperar antes de reintentar
        
        return False
    
    def descargar_piramide_lamina(self, lamina_id, url_base):
        """
        Descarga una pirámide de Deep Zoom de una lámina.
        
        Estructura UFRJ: url_base + "{nivel}/{x}_{y}.jpg"
        Ejemplo: http://www.histo.ufrj.br/LIB/Lamina%2002_files/0/0_0.jpg
                                                       ↑
                                              Estructura Deep Zoom Legacy
        """
        print(f"\n[*] Descargando {lamina_id}...")
        
        # Estructura de zoom típica (adjust según sea necesario)
        niveles = [12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
        
        # Para cada nivel, descargamos el thumbnail (0_0.jpg)
        # Esto es más rápido y evita descargar miles de tiles
        directorio_lamina = self.base_dir / f"lamina_{lamina_id}"
        
        imgenes_descargadas = 0
        
        for nivel in niveles:
            # Intentar descargar el tile central de cada nivel
            # Formato UFRJ: nivel/x_y.jpg
            url = f"{url_base}{nivel}/0_0.jpg"
            
            # Guardar como: lamina_02/nivel_0_0.jpg
            ruta_local = directorio_lamina / f"nivel_{nivel}_0_0.jpg"
            
            print(f"  Descargando nivel {nivel}...", end="")
            
            if self.descargar_imagen(url, ruta_local):
                print(" [OK]")
                imgenes_descargadas += 1
                sleep(0.5)  # Respetar servidor
            else:
                # Si falla el 0_0, intentar el primer tile disponible
                urls_alternativas = [
                    f"{url_base}{nivel}/1_0.jpg",
                    f"{url_base}{nivel}/0_1.jpg",
                    f"{url_base}{nivel}/1_1.jpg",
                ]
                
                encontrado = False
                for url_alt in urls_alternativas:
                    if self.descargar_imagen(url_alt, ruta_local):
                        print(f" [OK] (alternativa)")
                        imgenes_descargadas += 1
                        encontrado = True
                        break
                
                if not encontrado:
                    print(" [FAIL]")
        
        return imgenes_descargadas
    
    def actualizar_laminas_metadata(self, laminas_data):
        """
        Actualiza el JSON con rutas locales de las imágenes descargadas.
        Permite fallback: primero trata local, luego UFRJ.
        """
        # Si es dict por categoría
        if isinstance(laminas_data, dict) and 'laminas' not in laminas_data:
            for categoria, laminas in laminas_data.items():
                for lamina in laminas:
                    # Agregar URL local de fallback
                    lamina['url_local'] = f"/imagens_laminas/lamina_{lamina['id']}/nivel_0_0.jpg"
        # Si es array (formato original)
        elif isinstance(laminas_data, list):
            for lamina in laminas_data:
                lamina['url_local'] = f"/imagens_laminas/lamina_{lamina['id']}/nivel_0_0.jpg"
        # Si es dict con key 'laminas'
        elif 'laminas' in laminas_data:
            for lamina in laminas_data['laminas']:
                lamina['url_local'] = f"/imagens_laminas/lamina_{lamina['id']}/nivel_0_0.jpg"
        
        return laminas_data
    
    def ejecutar(self):
        """Ejecuta el descargador completo"""
        print("=" * 60)
        print("DESCARGADOR DE LAMINAS HISTOLOGICAS UFRJ")
        print("=" * 60)
        
        # Cargar datos
        print("\n[*] Cargando datos de laminas...")
        laminas_data = self.cargar_laminas_datos()
        
        # Contar láminas (compatible con array y dict)
        if isinstance(laminas_data, list):
            total_laminas = len(laminas_data)
            laminas_a_procesar = laminas_data
        else:
            total_laminas = sum(len(items) for items in laminas_data.values())
            laminas_a_procesar = [l for items in laminas_data.values() for l in items]
        
        print(f"[OK] {total_laminas} laminas encontradas")
        
        # Descargar cada lámina
        laminas_descargadas = 0
        for lamina in laminas_a_procesar:
            exito = self.descargar_piramide_lamina(
                lamina['id'],
                lamina['url_base']
            )
            if exito > 0:
                laminas_descargadas += 1
        
        print(f"\n[OK] {laminas_descargadas}/{total_laminas} laminas descargadas correctamente")
        
        # Actualizar JSON con URLs locales
        print("\n[*] Actualizando metadatos...")
        
        # Recargar datos originales para preservar formato
        json_path = Path(__file__).parent / 'laminas_ufrj_dados.json'
        with open(json_path, 'r', encoding='utf-8') as f:
            datos_originales = json.load(f)
        
        # Actualizar con URLs locales
        datos_actualizados = self.actualizar_laminas_metadata(datos_originales)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(datos_actualizados, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Guardado en {json_path}")
        
        print("\n" + "=" * 60)
        print("[DONE] Descarga completada!")
        print("=" * 60)
        print("\nProximos pasos:")
        print("1. Las imagenes estan en: imagens_laminas/lamina_{id}/")
        print("2. El HTML usara URLs locales (mas rapido)")
        print("3. Fallback a UFRJ si la local no existe")
        print("\nInicia el servidor: python -m http.server 8000")

if __name__ == '__main__':
    descargador = DescargarLaminasUFRJ()
    descargador.ejecutar()
