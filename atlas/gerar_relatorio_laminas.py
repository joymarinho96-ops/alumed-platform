#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Relatório de Lâminas Histológicas da UFRJ
Converte CSV para HTML para visualização melhor
"""

import csv
import json

def gerar_relatorio_html():
    """Gera relatório HTML a partir do CSV"""
    
    try:
        # Ler CSV
        laminas = []
        with open('laminas_ufrj.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            laminas = list(reader)
        
        # Categorizar por órgão/tecido
        categorias = {}
        for lamina in laminas:
            nome = lamina['Nome'].lower()
            
            # Detectar categoria
            if 'língua' in nome or 'lingua' in nome:
                cat = '👅 Língua'
            elif 'rim' in nome:
                cat = '🫘 Rim'
            elif 'fígado' in nome:
                cat = '🫗 Fígado'
            elif 'baço' in nome:
                cat = '🫀 Baço'
            elif 'coração' in nome or 'aurícula' in nome or 'vasos' in nome:
                cat = '❤️ Sistema Cardiovascular'
            elif 'estômago' in nome or 'esôfago' in nome or 'intestino' in nome or 'jejuno' in nome or 'duodeno' in nome or 'esofago' in nome:
                cat = '🫔 Trato Digestivo'
            elif 'traquéia' in nome or 'pulmão' in nome or 'traqueia' in nome:
                cat = '🫁 Sistema Respiratório'
            elif 'osso' in nome or 'coluna' in nome or 'articulação' in nome:
                cat = '🦴 Sistema Esquelético'
            elif 'pele' in nome:
                cat = '🧴 Pele'
            elif 'testículo' in nome or 'epidídimo' in nome or 'genital' in nome or 'testiculo' in nome:
                cat = '🔬 Sistema Genital'
            elif 'hipófise' in nome or 'tireóide' in nome or 'adrenal' in nome or 'paratireóide' in nome or 'hipofise' in nome or 'tireoide' in nome or 'paratireoide' in nome:
                cat = '🧬 Sistema Endócrino'
            elif 'medula' in nome or 'nervosa' in nome:
                cat = '🧠 Sistema Nervoso'
            elif 'linfonodo' in nome:
                cat = '⚪ Linfonodo'
            elif 'embrião' in nome or 'embrio' in nome or 'cordão' in nome or 'cordon' in nome:
                cat = '🚼 Embriologia'
            elif 'mastocitoma' in nome or 'bexiga' in nome:
                cat = '🏥 Patologia'
            else:
                cat = '📝 Outros'
            
            if cat not in categorias:
                categorias[cat] = []
            categorias[cat].append(lamina)
        
        # Gerar HTML
        html = f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Banco de Lâminas Histológicas - UFRJ</title>
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
        .lamina-nome {{
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
            <h1>🔬 Banco de Lâminas Histológicas</h1>
            <p>Universidade Federal do Rio de Janeiro (UFRJ)</p>
        </div>
        
        <div class="stats">
            <div class="stat">
                <div class="stat-number">{len(laminas)}</div>
                <div class="stat-label">Lâminas Totais</div>
            </div>
            <div class="stat">
                <div class="stat-number">{len(categorias)}</div>
                <div class="stat-label">Categorias</div>
            </div>
            <div class="stat">
                <div class="stat-number">100%</div>
                <div class="stat-label">Disponíveis Online</div>
            </div>
        </div>
        
        <div class="content">
"""
        
        # Adicionar categorias
        for cat in sorted(categorias.keys()):
            html += f'            <div class="categoria">\n'
            html += f'                <div class="categoria-title">{cat}</div>\n'
            for lamina in categorias[cat]:
                nome = lamina['Nome']
                url = lamina['URL']
                html += f'                <div class="lamina">\n'
                html += f'                    <div class="lamina-nome">{nome}</div>\n'
                html += f'                    <div class="lamina-url"><a href="{url}" target="_blank">🔗 Abrir Lâmina</a></div>\n'
                html += f'                </div>\n'
            html += f'            </div>\n'
        
        html += """        </div>
        
        <div class="footer">
            <p>📊 Relatório gerado automaticamente | Fonte: <strong>http://www.histo.ufrj.br/LIB/banco.htm</strong></p>
            <p style="margin-top: 10px; opacity: 0.7;">Todas as lâminas estão disponíveis publicamente para uso educacional e de pesquisa</p>
        </div>
    </div>
</body>
</html>"""
        
        # Salvar HTML
        with open('laminas_ufrj_relatorio.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ Relatório HTML gerado: laminas_ufrj_relatorio.html")
        print(f"📊 Total de lâminas: {len(laminas)}")
        print(f"📂 Total de categorias: {len(categorias)}")
        print(f"\nCategorias encontradas:")
        for cat in sorted(categorias.keys()):
            print(f"   {cat}: {len(categorias[cat])} lâminas")
        
        # Gerar JSON também
        with open('laminas_ufrj_banco.json', 'w', encoding='utf-8') as f:
            json.dump({
                'total': len(laminas),
                'categorias': {cat: len(laminas_cat) for cat, laminas_cat in categorias.items()},
                'laminas': laminas
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ JSON salvo: laminas_ufrj_banco.json")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("="*70)
    print("📊 Gerador de Relatório - Lâminas Histológicas UFRJ")
    print("="*70)
    gerar_relatorio_html()
