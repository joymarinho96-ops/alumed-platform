#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para extrair inventário de lâminas histológicas do site da UFRJ
URL: http://www.histo.ufrj.br/LIB/banco.htm

Extrai links de lâminas/imagens e salva em CSV
"""

import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin
import sys

# Configurações
URL_BASE = "http://www.histo.ufrj.br/LIB/banco.htm"
BASE_DOMAIN = "http://www.histo.ufrj.br/LIB/"
OUTPUT_CSV = "laminas_ufrj.csv"

def scraper_ufrj():
    """
    Faz scraping do banco de lâminas da UFRJ
    """
    print("="*70)
    print("🔬 Scraper de Lâminas Histológicas - UFRJ")
    print("="*70)
    print(f"\n📥 Acessando: {URL_BASE}")
    
    try:
        # Fazer request com timeout
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(URL_BASE, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"✅ Status: {response.status_code}")
        
        # Parsear HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Lista para armazenar lâminas
        laminas = []
        
        # Encontrar todos os links
        print(f"\n🔍 Procurando por lâminas/imagens...")
        links = soup.find_all('a')
        print(f"   Total de links encontrados: {len(links)}")
        
        # Filtrar links relevantes
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Verificar se contém "Lâmina" ou "Imagem de"
            if any(keyword in text.lower() or keyword in href.lower() 
                   for keyword in ['lâmina', 'imagem de', 'lamina', 'imagem']):
                
                # Converter URL relativa em absoluta
                if href:
                    url_absoluta = urljoin(BASE_DOMAIN, href)
                    
                    # Remover parâmetros desnecessários
                    if '?' in url_absoluta:
                        url_absoluta = url_absoluta.split('?')[0]
                    
                    laminas.append({
                        'nome': text if text else href,
                        'url': url_absoluta
                    })
                    
                    print(f"   ✓ {text[:50]:50} | {url_absoluta[:40]}")
        
        # Remover duplicatas (mantendo primeira ocorrência)
        laminas_unicas = []
        urls_vistas = set()
        
        for lamina in laminas:
            if lamina['url'] not in urls_vistas:
                laminas_unicas.append(lamina)
                urls_vistas.add(lamina['url'])
        
        print(f"\n📊 Resumo:")
        print(f"   Total encontrado: {len(laminas)}")
        print(f"   Únicas: {len(laminas_unicas)}")
        
        # Salvar em CSV
        if laminas_unicas:
            with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Nome', 'URL']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for lamina in laminas_unicas:
                    writer.writerow({
                        'Nome': lamina['nome'],
                        'URL': lamina['url']
                    })
            
            print(f"\n✅ CSV salvo: {OUTPUT_CSV}")
            print(f"   📁 Localização: {OUTPUT_CSV}")
            
            # Exibir conteúdo do CSV
            print(f"\n📋 Conteúdo do CSV:")
            print("-"*70)
            with open(OUTPUT_CSV, 'r', encoding='utf-8') as f:
                print(f.read())
            
            return True
        else:
            print("\n⚠️  Nenhuma lâmina encontrada!")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Erro de conexão: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Erro ao processar: {e}")
        import traceback
        traceback.print_exc()
        return False

def explorar_estrutura_html():
    """
    Função auxiliar para explorar a estrutura do HTML
    """
    print("\n" + "="*70)
    print("🔍 Explorando estrutura HTML...")
    print("="*70)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(URL_BASE, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Mostrar seções principais
        print("\n📌 Estrutura da página:")
        print(f"   Título: {soup.title.string if soup.title else 'N/A'}")
        
        # Encontrar elementos com "lamina" em qualquer atributo
        print(f"\n🔗 Primeiros 10 links da página:")
        for i, link in enumerate(soup.find_all('a')[:10], 1):
            href = link.get('href', 'N/A')
            text = link.get_text(strip=True)[:60]
            print(f"   {i}. {text:60} → {href}")
        
        # Encontrar divs, tables, etc
        tables = soup.find_all('table')
        divs = soup.find_all('div')
        print(f"\n📊 Elementos encontrados:")
        print(f"   Tables: {len(tables)}")
        print(f"   Divs: {len(divs)}")
        print(f"   Links: {len(soup.find_all('a'))}")
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    # Explorar estrutura primeiro (opcional)
    if len(sys.argv) > 1 and sys.argv[1] == "--explore":
        explorar_estrutura_html()
    
    # Executar scraper
    sucesso = scraper_ufrj()
    
    if not sucesso:
        print("\n💡 Dica: Execute com --explore para ver a estrutura da página")
        print("   python scraper_ufrj_laminas.py --explore")
