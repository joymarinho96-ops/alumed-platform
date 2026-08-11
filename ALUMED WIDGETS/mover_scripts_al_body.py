import re

print("=== MOVIENDO SCRIPTS AL FINAL DEL BODY EN INDEX.HTML ===")

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Remove script tags from head
html = re.sub(r'\s*<!-- Scripts: primero los datos, luego la lï¿½gica -->\s*<script src="data\.js[^"]*"[^>]*></script>\s*<script src="app\.js[^"]*"[^>]*></script>', '', html)
html = re.sub(r'\s*<script src="data\.js[^"]*"[^>]*></script>\s*<script src="app\.js[^"]*"[^>]*></script>', '', html)

# Insert script tags right before </body>
scripts_bottom = """
  <!-- Scripts al final del body para garantizar que todo el DOM exista -->
  <script src="data.js?v=20260728-2" charset="utf-8"></script>
  <script src="app.js?v=20260728-2" charset="utf-8"></script>
</body>"""

html = html.replace('</body>', scripts_bottom)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("1. Scripts movidos al final de </body> en index.html.")

# 2. UPDATE app.js WITH WINDOW.ONLOAD & DEFENSIVE NULL CHECKS
with open("app.js", "r", encoding="utf-8") as f:
    app_js = f.read()

load_choice_ultra_safe = """function loadChoice() {
  try {
    const elPergunta = document.getElementById('mc-pergunta');
    const elTag = document.getElementById('mc-materia-tag');
    const elCounter = document.getElementById('mc-counter');
    const elOpcoes = document.getElementById('mc-opcoes');

    if (!elPergunta || !elOpcoes) {
      console.warn("⚠️ Elementos DOM de MC aún no disponibles.");
      return;
    }

    if (typeof bancoDados === 'undefined' || !bancoDados.choices) {
      elPergunta.innerText = "⚠️ Error: No se pudo cargar el banco de preguntas (data.js no cargado).";
      return;
    }

    if (!filteredChoices || filteredChoices.length === 0) {
      if (elTag) elTag.innerText = currentMateria || "Biología";
      if (elCounter) elCounter.innerText = "0 de 0";
      elPergunta.innerText = "No hay preguntas disponibles para la materia seleccionada.";
      elOpcoes.innerHTML = "<div style='padding:20px; color:var(--muted); text-align:center;'>Selecciona otra materia o modo para practicar.</div>";
      const joyPanel = document.getElementById('mc-joy-panel');
      if (joyPanel) joyPanel.style.display = 'none';
      return;
    }

    if (currentChoiceIndex < 0) currentChoiceIndex = 0;
    if (currentChoiceIndex >= filteredChoices.length) currentChoiceIndex = filteredChoices.length - 1;

    const q = filteredChoices[currentChoiceIndex];
    if (!q) {
      elPergunta.innerText = "⚠️ Error al obtener el registro de la pregunta.";
      return;
    }

    yaValidado = false;
    selectedOption = null;

    // Header y pregunta
    if (elTag) elTag.innerText = `${q.materia || currentMateria} • ${q.tpPrincipal || 'TP1'}: ${q.tema || 'Tema General'}`;
    if (elCounter) elCounter.innerText = `Pregunta ${currentChoiceIndex + 1} de ${filteredChoices.length}`;
    elPergunta.innerText = q.pregunta || q.pergunta || "Pregunta sin enunciado";

    // Limpiar feedback
    const fb = document.getElementById('mc-feedback');
    if (fb) {
      fb.className = 'feedback hidden';
      fb.innerHTML = '';
    }

    // Opciones
    elOpcoes.innerHTML = '';
    const btnValidar = document.getElementById('btn-validar');
    if (btnValidar) btnValidar.disabled = true;

    const opciones = q.opciones || (q.opcoes ? q.opcoes.map(o => typeof o === 'string' ? {texto: o} : o) : []);

    if (opciones.length === 0) {
      elOpcoes.innerHTML = "<div style='padding:15px; color:var(--muted);'>Esta pregunta es de desarrollo oral o respuesta corta.</div>";
    } else {
      opciones.forEach((opt, idx) => {
        const btn = document.createElement('button');
        btn.className = 'option-btn';
        const textVal = typeof opt === 'string' ? opt : (opt.texto || opt.opcion || '');
        btn.innerHTML = `<span class="option-label">${String.fromCharCode(65 + idx)}</span> <span>${textVal}</span>`;
        btn.onclick = () => validarChoice(btn, idx);
        elOpcoes.appendChild(btn);
      });
    }

    const joyPanel = document.getElementById('mc-joy-panel');
    if (joyPanel) joyPanel.style.display = 'none';
  } catch (err) {
    console.error("❌ Error en loadChoice:", err);
    const elP = document.getElementById('mc-pergunta');
    if (elP) elP.innerText = `⚠️ Error al renderizar pregunta: ${err.message}`;
  }
}"""

app_js = re.sub(r'function loadChoice\(\) \{[\s\S]*?joyPanel\.style\.display = \'none\';\s*\}\s*\} catch[\s\S]*?\}\s*\}', load_choice_ultra_safe, app_js)
if "function loadChoice" in app_js:
    app_js = re.sub(r'function loadChoice\(\) \{[\s\S]*?const joyPanel = document\.getElementById\(\'mc-joy-panel\'\);[\s\S]*?joyPanel\.style\.display = \'none\';\s*\}', load_choice_ultra_safe, app_js)

# Add window.onload + DOMContentLoaded double trigger
onload_trigger = """
// ==========================================
// INICIALIZACIÓN DOBLE SEGURA (DOMContentLoaded + window.onload)
// ==========================================
function inicializarApp() {
  console.log('🚀 Inicializando ALUMED OS...');
  if (typeof bancoDados === 'undefined') {
    console.error('❌ ERROR CRÍTICO: bancoDados no se encuentra definido.');
    const elP = document.getElementById('mc-pergunta');
    if (elP) elP.innerText = "⚠️ Error: No se pudo cargar el banco de preguntas. Verifique data.js.";
    return;
  }

  console.log('✅ data.js cargado correctamente.');
  console.log(`📊 Conteo real de registros: Choices=${bancoDados.choices?.length || 0}, Orales=${bancoDados.orales?.length || 0}, Pinches=${bancoDados.pinches?.length || 0}`);

  const bioBtn = document.getElementById('nav-bio');
  prepararEntrenamiento('choices', 'biologia', bioBtn);
}

if (document.readyState === 'complete' || document.readyState === 'interactive') {
  setTimeout(inicializarApp, 100);
} else {
  document.addEventListener('DOMContentLoaded', inicializarApp);
  window.addEventListener('load', inicializarApp);
}
"""

if "function inicializarApp" not in app_js:
    app_js += "\n" + onload_trigger

with open("app.js", "w", encoding="utf-8") as f:
    f.write(app_js)

print("2. app.js actualizado con loadChoice ultra-seguro e inicializador doble (onload + DOMContentLoaded).")
