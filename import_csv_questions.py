#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALUMED OS — Script de Importación de Preguntas CSV / JSON
Importa preguntas desde un archivo CSV a la base de datos de ALUMED OS (data.js y Django).
Uso: python import_csv_questions.py preguntas_tendon.csv
"""

import os
import sys
import json
import pandas as pd
import django

# 1. Configuración del Entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumed.settings')
try:
    django.setup()
    print("Entorno Django configurado exitosamente.")
except Exception as e:
    print(f"Aviso al inicializar Django: {e}")

DATA_JS_PATH = r"C:\Users\joyce\Downloads\alumesitemdesenvolvimento-main\alumed-platform\ALUMED WIDGETS\data.js"
STATIC_DATA_JS_PATH = r"C:\Users\joyce\Downloads\alumesitemdesenvolvimento-main\alumed-platform\static\atlas_histologico\data.js"

def importar_preguntas_csv(caminho_csv):
    if not os.path.exists(caminho_csv):
        print(f"Error: El archivo '{caminho_csv}' no existe.")
        return

    print(f"Leyendo CSV: {caminho_csv}...")
    df = pd.read_csv(caminho_csv)
    print(f"Filas encontradas en CSV: {len(df)}")

    # Cargar bancoDados existente
    with open(DATA_JS_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    start_idx = content.find("const bancoDados = ")
    if start_idx != -1:
        json_str = content[start_idx + len("const bancoDados = "):].strip().rstrip(";")
        banco = json.loads(json_str)
    else:
        banco = {"choices": [], "pinches": [], "orales": []}

    choices = banco.get("choices", [])
    max_id = max([q.get('id', 0) for q in choices], default=1000)

    count_importadas = 0
    for _, row in df.iterrows():
        max_id += 1
        enunciado = str(row.get('pregunta', row.get('enunciado', '')))
        opcion_a = str(row.get('opcion_a', row.get('A', '')))
        opcion_b = str(row.get('opcion_b', row.get('B', '')))
        opcion_c = str(row.get('opcion_c', row.get('C', '')))
        opcion_d = str(row.get('opcion_d', row.get('D', '')))

        respuesta_correcta = row.get('respuesta_correcta', row.get('correta', 0))
        try:
            respuesta_correcta = int(respuesta_correcta)
        except (ValueError, TypeError):
            respuesta_correcta = 0

        materia = str(row.get('materia', 'Histología y Embriología'))
        tp = str(row.get('tp', row.get('modulo', 'TP 2: Tejido Conectivo (Denso, Laxo) y Adiposo')))
        justificativa = str(row.get('justificativa', row.get('explicacion', 'Devolución oficial del Método Profe Joy.')))

        nueva_q = {
            "id": max_id,
            "materia": materia,
            "tp": tp,
            "pergunta": enunciado,
            "opcoes": [
                f"A) {opcion_a}" if not opcion_a.startswith("A)") else opcion_a,
                f"B) {opcion_b}" if not opcion_b.startswith("B)") else opcion_b,
                f"C) {opcion_c}" if not opcion_c.startswith("C)") else opcion_c,
                f"D) {opcion_d}" if not opcion_d.startswith("D)") else opcion_d,
            ],
            "correta": respuesta_correcta,
            "justificativa": justificativa
        }

        choices.append(nueva_q)
        count_importadas += 1

    banco['choices'] = choices

    # Guardar en data.js
    js_out = f"// ALUMED OS — Banco de Preguntas REAL UNLP\n"
    js_out += f"const bancoDados = {json.dumps(banco, indent=2, ensure_ascii=False)};\n"

    with open(DATA_JS_PATH, 'w', encoding='utf-8') as f:
        f.write(js_out)
    with open(STATIC_DATA_JS_PATH, 'w', encoding='utf-8') as f:
        f.write(js_out)

    print(f" Importación concluida con éxito! Se añadieron {count_importadas} preguntas.")
    print(f"Total actual en el banco: {len(choices)} preguntas.")

if __name__ == '__main__':
    caminho = sys.argv[1] if len(sys.argv) > 1 else 'preguntas_tendon_histologia.csv'
    importar_preguntas_csv(caminho)
