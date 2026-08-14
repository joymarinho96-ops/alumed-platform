#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de Informe - Láminas Histológicas de la UFRJ
Convierte CSV a HTML para mejor visualización
"""

import csv
import json

def generar_informe_html():
    """Genera informe HTML a partir del CSV"""
    
    try:
        # Leer CSV
        laminas = []
        with open('laminas_ufrj.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            laminas = list(reader)
        
        # Categorizar por órgano/tejido
        categorias = {}
        for lamina in laminas:
            nombre = lamina['Nombre'].lower()
            
            # Detectar categoría
            if 'lengua' in nombre or 'lingua' in nombre:
                cat = '👅 Lengua'
            elif 'riñón' in nombre or 'rim' in nombre:
                cat = '🫘 Riñón'
            elif 'hígado' in nombre or 'fígado' in nombre:
                cat = '🫗 Hígado'
            elif 'bazo' in nombre:
                cat = '🫀 Bazo'
            elif 'corazón' in nombre or 'aurícula' in nombre or 'vasos' in nombre:
                cat = '❤️ Sistema Cardiovascular'
            elif 'estómago' in nombre or 'esófago' in nombre or 'intestino' in nombre or 'jejuno' in nombre or 'duodeno' in nombre or 'esofago' in nombre:
                cat = '🫔 Aparato Digestivo'
            elif 'tráquea' in nombre or 'pulmón' in nombre or 'traqueia' in nombre:
                cat = '🫁 Sistema Respiratorio'
            elif 'hueso' in nombre or 'columna' in nombre or 'articulación' in nombre:
                cat = '🦴 Sistema Esquelético'
            elif 'piel' in nombre:
                cat = '🧴 Piel'
            elif 'testículo' in nombre or 'epidídimo' in nombre or 'genital' in nombre or 'testiculo' in nombre:
                cat = '🔬 Sistema Genital'
            elif 'hipófisis' in nombre or 'tiroides' in nombre or 'adrenal' in nombre or 'paratiroides' in nombre or 'hipofise' in nombre or 'tireoide' in nombre or 'paratireoide' in nombre:
                cat = '🧬 Sistema Endocrino'
            elif 'médula' in nombre or 'nerviosa' in nombre:
                cat = '🧠 Sistema Nervioso'
            elif 'ganglio' in nombre:
                cat = '⚪ Ganglio Linfático'
            elif 'embrión' in nombre or 'embrio' in nombre or 'cordón' in nombre or 'cordon' in nombre:
                cat = '🚼 Embriología'
            elif 'mastocitoma' in nombre or 'vejiga' in nombre:
                cat = '🏥 Patología'
            else:
                cat = '📝 Otros'
            
            if cat not in categorias:
                categorias[cat] = []
            categorias[cat].append(lamina)
        
        # Generar HTML
        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Banco de Láminas Histológicas - UFRJ</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header p {{ font-size: 1.1em; opacity: 0.9; }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px 20px;
            background: #f8f9fa;
            border-bottom: 2px solid #eee;
        }}
        .stat {{
            text-align: center;
            padding: 20px;
            background: white;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        .stat-label {{ color: #666; margin-top: 5px; }}
        .content {{ padding: 30px 20px; }}
        .categoria {{
            margin-bottom: 40px;
        }}
        .categoria-title {{
            font-size: 1.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        .lamina {{
            background: #f8f9fa;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 6px;
            border-left: 4px solid #764ba2;
        }}
        .lamina-nombre {{
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
        }}
        .lamina-url {{
            font-size: 0.9em;
            color: #667eea;
            word-break: break-all;
            overflow-wrap: break-word;
        }}
        .lamina-url a {{
            color: #667eea;
            text-decoration: none;
            transition: color 0.3s;
        }}
        .lamina-url a:hover {{
            color: #764ba2;
            text-decoration: underline;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            border-top: 2px solid #eee;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔬 Banco de Láminas Histológicas</h1>
            <p>Universidad Federal de Rio de Janeiro (UFRJ)</p>
        </div>
        
        <div class="stats">
            <div class="stat">
                <div class="stat-number">{len(laminas)}</div>
                <div class="stat-label">Láminas Totales</div>
            </div>
            <div class="stat">
                <div class="stat-number">{len(categorias)}</div>
                <div class="stat-label">Categorías</div>
            </div>
            <div class="stat">
                <div class="stat-number">100%</div>
                <div class="stat-label">Disponibles En Línea</div>
            </div>
        </div>
        
        <div class="content">
"""
        
        # Agregar categorías
        for cat in sorted(categorias.keys()):
            html += f'            <div class="categoria">\n'
            html += f'                <div class="categoria-title">{cat}</div>\n'
            for lamina in categorias[cat]:
                nombre = lamina['Nombre']
                url = lamina['URL']
                html += f'                <div class="lamina">\n'
                html += f'                    <div class="lamina-nombre">{nombre}</div>\n'
                html += f'                    <div class="lamina-url"><a href="{url}" target="_blank">🔗 Abrir Lámina</a></div>\n'
                html += f'                </div>\n'
            html += f'            </div>\n'
        
        html += """        </div>
        
        <div class="footer">
            <p>📊 Informe generado automáticamente | Fuente: <strong>http://www.histo.ufrj.br/LIB/banco.htm</strong></p>
            <p style="margin-top: 10px; opacity: 0.7;">Todas las láminas están disponibles públicamente para uso educativo e investigación</p>
        </div>
    </div>
</body>
</html>"""
        
        # Guardar HTML
        with open('laminas_ufrj_informe.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ Informe HTML generado: laminas_ufrj_informe.html")
        print(f"📊 Total de láminas: {len(laminas)}")
        print(f"📂 Total de categorías: {len(categorias)}")
        print(f"\nCategorías encontradas:")
        for cat in sorted(categorias.keys()):
            print(f"   {cat}: {len(categorias[cat])} láminas")
        
        # Generar JSON también
        with open('laminas_ufrj_banco.json', 'w', encoding='utf-8') as f:
            json.dump({
                'total': len(laminas),
                'categorias': {cat: len(laminas_cat) for cat, laminas_cat in categorias.items()},
                'laminas': laminas
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ JSON guardado: laminas_ufrj_banco.json")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("="*70)
    print("📊 Generador de Informe - Láminas Histológicas UFRJ")
    print("="*70)
    generar_informe_html()
