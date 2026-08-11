import re

# ==========================================
# 1. PATCH INDEX.HTML
# ==========================================
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remove filter-section and replace nav-menu
filter_start = html.find('<div class="filter-section">')
nav_end = html.find('</nav>') + len('</nav>')

if filter_start != -1 and nav_end != -1:
    new_nav = """      <nav class="nav-menu" style="margin-top: 15px;">
        <div class="nav-group-title" style="color: var(--muted); font-size: 0.75rem; font-weight: 800; letter-spacing: 0.08em; padding: 0 16px 8px; text-transform: uppercase;">Entrenamiento Parcial</div>
        
        <button class="nav-btn active" id="nav-anatoa" onclick="prepararEntrenamiento('oral', 'Anatomía Cátedra A', this)">
          <i class="fa-solid fa-comments"></i>
          <span>Anatomía A</span>
        </button>
        
        <button class="nav-btn" id="nav-anatob" onclick="prepararEntrenamiento('pinches', 'Anatomía Cátedra B', this)">
          <i class="fa-solid fa-crosshairs"></i>
          <span>Anatomía B</span>
        </button>
        
        <button class="nav-btn" id="nav-anatoc" onclick="prepararEntrenamiento('oral', 'Anatomía Cátedra C', this)">
          <i class="fa-solid fa-comments"></i>
          <span>Anatomía C</span>
        </button>
        
        <button class="nav-btn" id="nav-bio" onclick="prepararEntrenamiento('choices', 'Biología', this)">
          <i class="fa-solid fa-list-check"></i>
          <span>Biología</span>
        </button>
        
        <button class="nav-btn" id="nav-hye" onclick="prepararEntrenamiento('choices', 'Histología y Embriología', this)">
          <i class="fa-solid fa-microscope"></i>
          <span>Histología y Embriología</span>
        </button>
        
        <div class="nav-divider" style="height: 1px; background: var(--border); margin: 15px 16px;"></div>
        
        <button class="nav-btn" id="nav-calendario" onclick="prepararEntrenamiento('calendario', null, this); initCalendario();">
          <i class="fa-solid fa-calendar-days"></i>
          <span>Calendario de Parciales</span>
        </button>
      </nav>"""
    html = html[:filter_start] + new_nav + html[nav_end:]

# Replace headings and titles
replacements = {
    "Módulo Multiple Choice": "Entrenamiento Parcial — Múltiple Choice",
    "Módulo Pinches — Anatomía Práctica": "Entrenamiento Parcial — Pinches",
    "Simulador de Examen Oral — Bolillas UNLP": "Entrenamiento Parcial — Práctica oral",
    "Sortear Bolilla / Caso Clínico": "Siguiente pregunta",
    "Examen Oral / Bolillas": "Práctica oral",
    "Bolillas UNLP": "UNLP",
    "Bolilla": "Pregunta"
}

for old, new in replacements.items():
    html = html.replace(old, new)

# Rename id="oral-bolilla" to "oral-titulo" for clarity, but if it breaks app.js we must patch app.js too
html = html.replace('id="oral-bolilla"', 'id="oral-titulo"')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("index.html patched.")

# ==========================================
# 2. PATCH APP.JS
# ==========================================
with open('app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

# Add prepararEntrenamiento function
prep_func = """
// ─────────────────────────────────────────────────────────────
//  NAVEGACIÓN DE ENTRENAMIENTO PARCIAL
// ─────────────────────────────────────────────────────────────
function prepararEntrenamiento(tabId, materia, btnEl) {
  // 1. Switch Tab UI
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
  const sec = document.getElementById(`tab-${tabId}`);
  if (sec) sec.classList.add('active');
  if (btnEl) btnEl.classList.add('active');

  // 2. Set Materia and Filter
  if (materia) {
    currentMateria = materia;
    filteredChoices = bancoDados.choices.filter(q => q.materia === materia);
    currentChoiceIndex = 0;
    
    // Si la tab es 'choices', cargamos choice
    if (tabId === 'choices') {
      loadChoice();
    }
    // Si la tab es 'pinches', cargamos pinche
    if (tabId === 'pinches') {
      loadPinche();
    }
    // Si la tab es 'oral', sorteamos la primera pregunta oral
    if (tabId === 'oral') {
      siguientePreguntaOral();
    }
  }
}
"""

if "function switchTab(" in app_js:
    # Replace the old switchTab / cambiarMateria section with the new logic
    nav_start = app_js.find("// ─────────────────────────────────────────────────────────────\n//  NAVEGACIÓN DE TABS")
    nav_end = app_js.find("// ─────────────────────────────────────────────────────────────\n//  CARGA DE PREGUNTA")
    if nav_start != -1 and nav_end != -1:
        app_js = app_js[:nav_start] + prep_func + app_js[nav_end:]

# Replace 'sortearOral' with 'siguientePreguntaOral'
app_js = app_js.replace("function sortearOral()", "function siguientePreguntaOral()")
app_js = app_js.replace("sortearOral()", "siguientePreguntaOral()")
app_js = app_js.replace("document.getElementById('oral-bolilla').innerText = o.bolilla;", "document.getElementById('oral-titulo').innerText = o.titulo || o.tema || o.bolilla || '';")

# Replace "No hay bolillas" alert with "No hay preguntas orales"
app_js = app_js.replace("No hay bolillas para la cátedra seleccionada", "No hay preguntas orales para la materia seleccionada")

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)
print("app.js patched.")

