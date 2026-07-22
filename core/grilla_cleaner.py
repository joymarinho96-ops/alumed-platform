# -*- coding: utf-8 -*-
import re
import csv
import json
import os

def extraer_texto_archivo(ruta_archivo):
    """Extrae texto de archivos .txt o .pdf (usando fitz si está disponible)."""
    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_archivo}")

    ext = os.path.splitext(ruta_archivo)[1].lower()

    if ext == '.pdf':
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(ruta_archivo)
            texto = ""
            for page in doc:
                texto += page.get_text() + "\n"
            return texto
        except ImportError:
            # Fallback simple
            with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
    else:
        with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

def limpiar_grilla_estudiantes(texto_o_lineas):
    """
    Limpiador inteligente de grillas de notas para ALUMED / Conecta FCM.
    Elimina códigos de ruido (ej. 'FK884282 GAR', 'Bc417823', 'GK570118'),
    reordena Legajo, DNI, Apellido y Nombre, y clasifica el Estado (Aprobado / Promoción / Desaprobado).
    No requiere dependencias externas (funciona 100% nativo).
    """
    if isinstance(texto_o_lineas, str):
        lineas = texto_o_lineas.strip().split('\n')
    else:
        lineas = texto_o_lineas

    registros = []

    # Expresiones regulares para detección limpia
    re_estado = re.compile(r'\b(aprobado|promocion|promoción|desaprobado|ausente|reprobado)\b', re.IGNORECASE)
    re_codigo_basura = re.compile(r'\b([A-Za-z]{1,4}\d{4,8}[A-Za-z0-9]*|GAR|CEPA)\b', re.IGNORECASE)

    for linea in lineas:
        linea_str = linea.strip()
        if not linea_str or "comision" in linea_str.lower():
            continue

        # 1. Detectar Estado
        match_estado = re_estado.search(linea_str)
        estado = match_estado.group(1).capitalize() if match_estado else 'Sin Especificar'
        if estado.lower() == 'promocion':
            estado = 'Promoción'

        # Remover el estado de la línea para procesar el resto
        if match_estado:
            linea_sin_estado = linea_str[:match_estado.start()] + ' ' + linea_str[match_estado.end():]
        else:
            linea_sin_estado = linea_str

        # 2. Detectar Materia / Comisión (ej. "anatomia 8")
        comision = "Anatomía 8"
        match_comision = re.match(r'^(anatomia\s*\d*|histo\s*\d*|bio\s*\d*|embrio\s*\d*)\s*', linea_sin_estado, re.IGNORECASE)
        if match_comision:
            comision = match_comision.group(1).strip().title()
            linea_sin_estado = linea_sin_estado[match_comision.end():]

        # 3. Eliminar basura conocida (ej. FK884282, GAR, GK570118, etc.)
        linea_limpia = re_codigo_basura.sub('', linea_sin_estado).strip()

        # 4. Extraer números de Legajo y DNI
        numeros = re.findall(r'\b\d+\b', linea_limpia)
        
        legajo = "N/D"
        dni = "N/D"

        if len(numeros) >= 2:
            legajo = numeros[0]
            dni = numeros[1]
            if len(dni) > 8:
                dni = dni[:8]
        elif len(numeros) == 1:
            num = numeros[0]
            if num == "0":
                legajo = "0"
            elif len(num) >= 7 and num.startswith(('4', '9', '2', '3', '1', '5', '6')):
                dni = num
            else:
                legajo = num

        # 5. Extraer Apellido y Nombre (remover números procesados)
        nombre_raw = re.sub(r'\b\d+\b', '', linea_limpia).strip()
        nombre_clean = re.sub(r'\s+', ' ', nombre_raw).strip(',- ')
        
        if not nombre_clean or len(nombre_clean) < 2:
            nombre_clean = "S/N"

        registros.append({
            'Comision': comision,
            'Legajo': legajo,
            'DNI': dni,
            'Apellido_Nombre': nombre_clean.title(),
            'Estado': estado
        })

    return registros

def procesar_y_limpiar_notas(archivo_entrada, archivo_salida="grilla_limpia_alumed.csv"):
    """
    Procesa un archivo PDF o TXT de grilla de notas de ALUMED / Conecta FCM,
    limpia el ruido alfanumérico y exporta un archivo CSV estructurado.
    """
    print("🧹 Iniciando la limpieza y normalización de la grilla de notas...")

    try:
        texto = extraer_texto_archivo(archivo_entrada)
        registros = limpiar_grilla_estudiantes(texto)

        # Exportar a CSV de forma nativa
        with open(archivo_salida, 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = ['Comision', 'Legajo', 'DNI', 'Apellido_Nombre', 'Estado']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(registros)

        print(f"✅ ¡Proceso completado con éxito! {len(registros)} registros limpios guardados en: {archivo_salida}")
        return registros

    except FileNotFoundError as e:
        print(f"⚠️ {e}")
        return []

def a_dataframe_html(registros):
    """Genera una tabla HTML limpia y estilizada estilo AluMed OS."""
    html = """
    <table class="table table-dark table-hover table-striped align-middle" style="border-radius:12px; overflow:hidden;">
        <thead style="background:linear-gradient(135deg, #7c3aed, #6d28d9); color:white;">
            <tr>
                <th>Comisión</th>
                <th>Legajo</th>
                <th>DNI</th>
                <th>Apellido y Nombre</th>
                <th>Estado</th>
            </tr>
        </thead>
        <tbody>
    """
    for r in registros:
        badge_cls = "bg-success" if r['Estado'] == 'Aprobado' else ("bg-warning text-dark" if r['Estado'] == 'Promoción' else "bg-danger")
        html += f"""
            <tr>
                <td><span class="badge bg-secondary">{r['Comision']}</span></td>
                <td><code>{r['Legajo']}</code></td>
                <td><code>{r['DNI']}</code></td>
                <td><strong>{r['Apellido_Nombre']}</strong></td>
                <td><span class="badge {badge_cls}">{r['Estado']}</span></td>
            </tr>
        """
    html += "</tbody></table>"
    return html

if __name__ == '__main__':
    muestra_test = """
    anatomia 8  1061194 47312118 Ferreyra  aprobado
    anatomia 8  1119069 FK884282 GAR  Promocion
    anatomia 8  1109166 Bc417823 Iquinas Parra  Promocion
    anatomia 8  1098577 48303248 Lapitzondo Algañaras  aprobado
    anatomia 8  969759 95682565 Larrauri Acuña  aprobado
    anatomia 8  1117460 96282519 LIBERATO DE SOUZA  Promocion
    anatomia 8  1071063 GK570118 MESSIAS DE SOUZA FONS  Promocion
    anatomia 8  1088710 225928469 Mael Neves Cardim  aprobado
    anatomia 8  1100953 48430299 Nahon  Promocion
    anatomia 8 1027608 46829842 Navarro  aprobado
    0 larouca  Promocion
    868044 ojeda, martina  aprobado
    864347  Promocion
    888532 alves de andrade  Promocion
    938321 santos casteda, maria  aprobado
    837162 ayala,valentina  aprobado
    0 aguirre, rosa  Promocion
    0 hernandez, lautaro  Promocion
    0 kuster, liandra  Promocion
    0 fernandez pastore, noren  aprobado
    """
    res = limpiar_grilla_estudiantes(muestra_test)
    print(json.dumps(res, indent=2, ensure_ascii=False))
