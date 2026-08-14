#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para extraer inventario de láminas histológicas del sitio de la UFRJ
URL: http://www.histo.ufrj.br/LIB/banco.htm

Extrae enlaces de láminas/imágenes y los guarda en CSV
"""

import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin
import sys

# Configuraciones
URL_BASE = "http://www.histo.ufrj.br/LIB/banco.htm"
BASE_DOMAIN = "http://www.histo.ufrj.br/LIB/"
OUTPUT_CSV = "laminas_ufrj.csv"

def scraper_ufrj():
    """
    Realiza web scraping del banco de láminas de la UFRJ
    """
    print("="*70)
    print("🔬 Raspador de Láminas Histológicas - UFRJ")
    print("="*70)
    print(f"\n📥 Accediendo a: {URL_BASE}")
    
    try:
        # Realizar solicitud con tiempo de espera
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(URL_BASE, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"✅ Estado: {response.status_code}")
        
        # Analizar HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Lista para almacenar láminas
        laminas = []
        
        # Encontrar todos los enlaces
        print(f"\n🔍 Buscando láminas/imágenes...")
        links = soup.find_all('a')
        print(f"   Total de enlaces encontrados: {len(links)}")
        
        # Filtrar enlaces relevantes
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Verificar si contiene "Lámina" o "Imagen de"
            if any(keyword in text.lower() or keyword in href.lower() 
                   for keyword in ['lámina', 'imagen de', 'lamina', 'imagen']):
                
                # Convertir URL relativa en absoluta
                if href:
                    url_absoluta = urljoin(BASE_DOMAIN, href)
                    
                    # Remover parámetros innecesarios
                    if '?' in url_absoluta:
                        url_absoluta = url_absoluta.split('?')[0]
                    
                    laminas.append({
                        'nombre': text if text else href,
                        'url': url_absoluta
                    })
                    
                    print(f"   ✓ {text[:50]:50} | {url_absoluta[:40]}")
        
        # Remover duplicados (manteniendo la primera ocurrencia)
        laminas_unicas = []
        urls_vistas = set()
        
        for lamina in laminas:
            if lamina['url'] not in urls_vistas:
                laminas_unicas.append(lamina)
                urls_vistas.add(lamina['url'])
        
        print(f"\n📊 Resumen:")
        print(f"   Total encontrado: {len(laminas)}")
        print(f"   Únicas: {len(laminas_unicas)}")
        
        # Guardar en CSV
        if laminas_unicas:
            with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Nombre', 'URL']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for lamina in laminas_unicas:
                    writer.writerow({
                        'Nombre': lamina['nombre'],
                        'URL': lamina['url']
                    })
            
            print(f"\n✅ CSV guardado: {OUTPUT_CSV}")
            print(f"   📁 Ubicación: {OUTPUT_CSV}")
            
            # Mostrar contenido del CSV
            print(f"\n📋 Contenido del CSV:")
            print("-"*70)
            with open(OUTPUT_CSV, 'r', encoding='utf-8') as f:
                print(f.read())
            
            return True
        else:
            print("\n⚠️  ¡No se encontraron láminas!")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error de conexión: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error al procesar: {e}")
        import traceback
        traceback.print_exc()
        return False

def explorar_estructura_html():
    """
    Función auxiliar para explorar la estructura del HTML
    """
    print("\n" + "="*70)
    print("🔍 Explorando estructura HTML...")
    print("="*70)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(URL_BASE, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Mostrar secciones principales
        print("\n📌 Estructura de la página:")
        print(f"   Título: {soup.title.string if soup.title else 'N/A'}")
        
        # Encontrar elementos con "lamina" en cualquier atributo
        print(f"\n🔗 Primeros 10 enlaces de la página:")
        for i, link in enumerate(soup.find_all('a')[:10], 1):
            href = link.get('href', 'N/A')
            text = link.get_text(strip=True)[:60]
            print(f"   {i}. {text:60} → {href}")
        
        # Encontrar divs, tables, etc
        tables = soup.find_all('table')
        divs = soup.find_all('div')
        print(f"\n📊 Elementos encontrados:")
        print(f"   Tablas: {len(tables)}")
        print(f"   Divs: {len(divs)}")
        print(f"   Enlaces: {len(soup.find_all('a'))}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Explorar estructura primero (opcional)
    if len(sys.argv) > 1 and sys.argv[1] == "--explorar":
        explorar_estructura_html()
    
    # Ejecutar raspador
    exito = scraper_ufrj()
    
    if not exito:
        print("\n💡 Sugerencia: Ejecuta con --explorar para ver la estructura de la página")
        print("   python raspador_ufrj_laminas.py --explorar")
