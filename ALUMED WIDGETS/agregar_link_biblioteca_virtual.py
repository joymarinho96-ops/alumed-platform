import re

print("=== AGREGANDO LINK Y BOTÓN BIBLIOTECA VIRTUAL ===")

BIBLIO_URL = "https://www.conectafcm.com/biblioteca-virtual/965e8278-fa18-443d-8d0f-c00b1286f5b6"

# 1. UPDATE index.html navigation sidebar
with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

biblio_nav_btn = f"""
          <a class="nav-btn" id="nav-biblioteca" href="{BIBLIO_URL}" target="_blank" style="text-decoration: none; display: flex; align-items: center; gap: 10px;">
            <i class="fa-solid fa-book-open" style="color: var(--cyan-neon);"></i>
            <span>Biblioteca Virtual</span>
          </a>
"""

if 'id="nav-biblioteca"' not in html:
    html = html.replace(
        '</nav>',
        f'{biblio_nav_btn}\n        </nav>'
    )

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("1. Botón de Biblioteca Virtual agregado al menú de navegación en index.html.")

# 2. UPDATE app.js abrirFragmento and Profe Joy panel buttons
with open("app.js", "r", encoding="utf-8") as f:
    app_js = f.read()

# Make abrirFragmento redirect to the official Biblioteca Virtual URL
abrir_fragmento_updated = f"""function abrirFragmento(qId) {{
  window.open('{BIBLIO_URL}', '_blank');
}}"""

app_js = re.sub(r'function abrirFragmento\(qId\) \{[\s\S]*?\}', abrir_fragmento_updated, app_js)

# Update Profe Joy panel text for apunte/biblioteca
app_js = app_js.replace("Ver fragmento del apunte", "Ver en Biblioteca Virtual")
app_js = app_js.replace("Biblioteca Inteligente", "Biblioteca Virtual")

with open("app.js", "w", encoding="utf-8") as f:
    f.write(app_js)

print("2. Redirección y texto de Biblioteca Virtual actualizados en app.js.")
