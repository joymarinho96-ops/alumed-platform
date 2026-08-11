import re
import os

print("=== SINCRONIZANDO NAVEGACIÓN E INICIALIZACIÓN DE ALUMED OS ===")

# 1. UPDATE index.html
with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Add versioning query params to script tags
html = re.sub(r'<script src="data\.js[^"]*"[^>]*></script>', '<script src="data.js?v=20260728-1" charset="utf-8"></script>', html)
html = re.sub(r'<script src="app\.js[^"]*"[^>]*></script>', '<script src="app.js?v=20260728-1" charset="utf-8"></script>', html)

# Fix nav-btn active inconsistency: Make nav-bio active by default on tab-choices
html = html.replace('class="nav-btn active" id="nav-anatoa"', 'class="nav-btn" id="nav-anatoa"')
html = html.replace('class="nav-btn" id="nav-bio"', 'class="nav-btn active" id="nav-bio"')

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("1. index.html actualizado con script versioning (?v=20260728-1) y nav-bio activo por defecto.")

# 2. UPDATE app.js
with open("app.js", "r", encoding="utf-8") as f:
    app_js = f.read()

# Add try-catch & error reporting inside loadChoice
load_choice_safe = """function loadChoice() {
  try {
    if (typeof bancoDados === 'undefined' || !bancoDados.choices) {
      document.getElementById('mc-pergunta').innerText = "⚠️ Error: No se pudo cargar el banco de preguntas (data.js no cargado).";
      return;
    }

    if (!filteredChoices || filteredChoices.length === 0) {
      document.getElementById('mc-materia-tag').innerText = currentMateria || "Biología";
      document.getElementById('mc-counter').innerText     = "0 de 0";
      document.getElementById('mc-pergunta').innerText    = "No hay preguntas disponibles para la materia seleccionada.";
      document.getElementById('mc-opcoes').innerHTML      = "<div style='padding:20px; color:var(--muted); text-align:center;'>Selecciona otra materia o modo para practicar.</div>";
      const joyPanel = document.getElementById('mc-joy-panel');
      if (joyPanel) joyPanel.style.display = 'none';
      return;
    }

    if (currentChoiceIndex < 0) currentChoiceIndex = 0;
    if (currentChoiceIndex >= filteredChoices.length) currentChoiceIndex = filteredChoices.length - 1;

    const q = filteredChoices[currentChoiceIndex];
    if (!q) {
      document.getElementById('mc-pergunta').innerText = "⚠️ Error al obtener el registro de la pregunta.";
      return;
    }

    yaValidado = false;
    selectedOption = null;

    // Header y pregunta
    document.getElementById('mc-materia-tag').innerText = `${q.materia || currentMateria} • ${q.tpPrincipal || 'TP1'}: ${q.tema || 'Tema General'}`;
    document.getElementById('mc-counter').innerText     = `Pregunta ${currentChoiceIndex + 1} de ${filteredChoices.length}`;
    document.getElementById('mc-pergunta').innerText    = q.pregunta || q.pergunta || "Pregunta sin enunciado";

    // Limpiar feedback
    const fb = document.getElementById('mc-feedback');
    if (fb) {
      fb.className = 'feedback hidden';
      fb.innerHTML = '';
    }

    // Opciones
    const container = document.getElementById('mc-opcoes');
    container.innerHTML = '';
    const btnValidar = document.getElementById('btn-validar');
    if (btnValidar) btnValidar.disabled = true;

    const opciones = q.opciones || (q.opcoes ? q.opcoes.map(o => typeof o === 'string' ? {texto: o} : o) : []);

    if (opciones.length === 0) {
      container.innerHTML = "<div style='padding:15px; color:var(--muted);'>Esta pregunta es de desarrollo oral o respuesta corta.</div>";
    } else {
      opciones.forEach((opt, idx) => {
        const btn = document.createElement('button');
        btn.className = 'option-btn';
        const textVal = typeof opt === 'string' ? opt : (opt.texto || opt.opcion || '');
        btn.innerHTML = `<span class="option-label">${String.fromCharCode(65 + idx)}</span> <span>${textVal}</span>`;
        btn.onclick = () => validarChoice(btn, idx);
        container.appendChild(btn);
      });
    }

    const joyPanel = document.getElementById('mc-joy-panel');
    if (joyPanel) joyPanel.style.display = 'none';
  } catch (err) {
    console.error("❌ Error en loadChoice:", err);
    document.getElementById('mc-pergunta').innerText = `⚠️ Error al renderizar pregunta: ${err.message}`;
  }
}"""

app_js = re.sub(r'function loadChoice\(\) \{[\s\S]*?joyPanel\.style\.display = \'none\';\s*\}', load_choice_safe, app_js)

# Add explicit DOMContentLoaded block with console logs
dom_init = """
// ==========================================
// INICIALIZACIÓN AUTOMÁTICA Y CONSOLA DE DIAGNÓSTICO
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
  console.log('🚀 Inicializando ALUMED OS...');
  
  if (typeof bancoDados === 'undefined') {
    console.error('❌ ERROR CRÍTICO: bancoDados no se encuentra definido. data.js no cargó correctamente.');
    const elP = document.getElementById('mc-pergunta');
    if (elP) elP.innerText = "⚠️ Error: No se pudo cargar el banco de preguntas. Verifique data.js.";
    return;
  }

  console.log('✅ data.js cargado correctamente.');
  console.log('📦 Variable global encontrada: bancoDados');
  console.log(`📊 Conteo real de registros: Choices=${bancoDados.choices?.length || 0}, Orales=${bancoDados.orales?.length || 0}, Pinches=${bancoDados.pinches?.length || 0}`);

  const bioBtn = document.getElementById('nav-bio');
  console.log('🎯 Materia y modalidad iniciales: Biología (Multiple Choice)');
  prepararEntrenamiento('choices', 'biologia', bioBtn);
});
"""

# Remove previous init if exists and append clean one
if "INICIALIZACIÓN AUTOMÁTICA Y CONSOLA DE DIAGNÓSTICO" in app_js:
    app_js = app_js.split("// INICIALIZACIÓN AUTOMÁTICA Y CONSOLA DE DIAGNÓSTICO")[0]
elif "document.addEventListener('DOMContentLoaded'" in app_js:
    app_js = app_js.split("document.addEventListener('DOMContentLoaded'")[0]

app_js += "\n" + dom_init

with open("app.js", "w", encoding="utf-8") as f:
    f.write(app_js)

print("2. app.js actualizado con manejo de errores visible y logs de consola de diagnóstico.")
