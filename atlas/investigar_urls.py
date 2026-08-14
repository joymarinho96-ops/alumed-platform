#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para investigar a estrutura de URLs da UFRJ
"""

import requests
import sys

# Configurar encoding
if sys.platform == 'win32':
    import os
    os.system('chcp 65001 > nul')

def testar_url(url):
    """Tenta acessar uma URL e retorna o status"""
    try:
        response = requests.head(url, timeout=5)
        return response.status_code
    except:
        return 'TIMEOUT'

print("=" * 60)
print("INVESTIGADOR DE URLs UFRJ")
print("=" * 60)

# URL base de uma lâmina
url_base = "http://www.histo.ufrj.br/LIB/Lamina%2002_files/"

print(f"\nTestando URL base: {url_base}")
print("\nVariacoes a testar:")

# Variações de URLs
variacoes = [
    ("Nivel 5", f"{url_base}5/0_0.jpg"),
    ("Nivel 4", f"{url_base}4/0_0.jpg"),
    ("Nivel 3", f"{url_base}3/0_0.jpg"),
    ("Nivel 2", f"{url_base}2/0_0.jpg"),
    ("Nivel 1", f"{url_base}1/0_0.jpg"),
    ("Nivel 0", f"{url_base}0/0_0.jpg"),
    ("DZI Info", f"{url_base}DZI"),
    ("XML", f"{url_base}dzi.xml"),
    ("Metadata", f"{url_base}metadata.xml"),
]

for nombre, url in variacoes:
    status = testar_url(url)
    print(f"  [{status:>7}] {nombre:20} {url}")

# Intentar sin la barra final
print("\nSin barra final:")
url_base_sin_barra = "http://www.histo.ufrj.br/LIB/Lamina%2002_files"
status = testar_url(f"{url_base_sin_barra}/0/0_0.jpg")
print(f"  [{status:>7}] Con %20   {url_base_sin_barra}/0/0_0.jpg")

# Intentar con encoding diferente
print("\nCon encoding diferente:")
url_alt = "http://www.histo.ufrj.br/LIB/Lamina 02_files/0/0_0.jpg"
status = testar_url(url_alt)
print(f"  [{status:>7}] Espacio  {url_alt}")

# Probar si la estructura es diferente
print("\nAlternativas de estructura:")
urls_alt = [
    "http://www.histo.ufrj.br/LIB/02/0/0_0.jpg",
    "http://www.histo.ufrj.br/laminas/02/0/0_0.jpg",
    "http://www.histo.ufrj.br/images/02/0/0_0.jpg",
    "http://www.histo.ufrj.br/Lamina02_files/0/0_0.jpg",
]

for url in urls_alt:
    status = testar_url(url)
    print(f"  [{status:>7}] {url}")

print("\n" + "=" * 60)
print("FIN DE INVESTIGACION")
print("=" * 60)
