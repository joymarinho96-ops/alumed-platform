import re

print("=== CORRIGIENDO IDS EN INDEX.HTML Y AGREGANDO DEFENSAS EN APP.JS ===")

# 1. FIX index.html
with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Add id="mc-materia-tag" to <span class="badge badge-materia" id="mc-materia">
html = html.replace('id="mc-materia"', 'id="mc-materia-tag"')

# Add toast element if missing
if 'id="alumed-toast"' not in html:
    toast_elem = '<div id="alumed-toast" class="toast" style="display:none; position:fixed; bottom:20px; right:20px; background:#1e293b; color:#fff; padding:12px 20px; border-radius:8px; border:1px solid #334155; z-index:9999;"></div>'
    html = html.replace('</body>', f'  {toast_elem}\n</body>')

# Add timer elements if missing
if 'id="examen-header"' not in html:
    header_elem = """
    <!-- Header Examen Contrarreloj -->
    <div id="examen-header" style="display:none; background: #0f172a; padding: 12px 20px; border-radius: 12px; margin-bottom: 20px; border: 1px solid #e11d48; display: flex; justify-content: space-between; align-items: center;">
      <span id="examen-titulo" style="font-weight: bold; color: #f43f5e; font-size: 1rem;">⏱️ PARCIAL REAL EN CURSO</span>
      <span id="examen-timer" style="font-family: monospace; font-size: 1.4rem; font-weight: bold; color: #ef4444; background: #000; padding: 4px 12px; border-radius: 6px; border: 1px solid #991b1b;">00:00</span>
    </div>
    """
    html = html.replace('<section id="tab-choices" class="tab-content active">', f'<section id="tab-choices" class="tab-content active">\n{header_elem}')

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("1. index.html actualizado con id='mc-materia-tag', alumed-toast, examen-header, examen-titulo y examen-timer.")

# 2. FIX app.js WITH DEFENSIVE NULL CHECKS FOR ALL DOM ELEMENTS
with open("app.js", "r", encoding="utf-8") as f:
    app_js = f.read()

# Update loadChoice with strict defensive checks for every element
load_choice_guaranteed = """function loadChoice() {
  try {
    const materiaTag = document.getElementById('mc-materia-tag') || document.getElementById('mc-materia');
    const counter    = document.getElementById('mc-counter');
    const pregunta   = document.getElementById('mc-pergunta');
    const container  = document.getElementById('mc-opcoes');

    if (typeof bancoDados === 'undefined' || !bancoDados.choices) {
      if (pregunta) pregunta.textContent = "No se pudo cargar el banco de preguntas. Revisá la consola.";
      return;
    }

    if (!filteredChoices || filteredChoices.length === 0) {
      if (materiaTag) materiaTag.textContent = currentMateria || "Biología";
      if (counter)    counter.textContent    = "0 de 0";
      if (pregunta)   pregunta.textContent   = "No se encontraron preguntas para esta materia.";
      if (container)  container.innerHTML    = "<div style='padding:20px; color:var(--muted); text-align:center;'>Selecciona otra materia o modo para practicar.</div>";
      const joyPanel = document.getElementById('mc-joy-panel');
      if (joyPanel) joyPanel.style.display = 'none';
      return;
    }

    if (currentChoiceIndex < 0) currentChoiceIndex = 0;
    if (currentChoiceIndex >= filteredChoices.length) currentChoiceIndex = filteredChoices.length - 1;

    const q = filteredChoices[currentChoiceIndex];
    if (!q) {
      if (pregunta) pregunta.textContent = "No se pudo obtener la pregunta actual.";
      return;
    }

    yaValidado = false;
    selectedOption = null;

    if (materiaTag) {
      materiaTag.textContent = `${q.materia || currentMateria} • ${q.tpPrincipal || 'TP1'}: ${q.tema || 'Tema General'}`;
    }

    if (counter) {
      counter.textContent = `Pregunta ${currentChoiceIndex + 1} de ${filteredChoices.length}`;
    }

    if (pregunta) {
      pregunta.textContent = q.pregunta || q.pergunta || "Pregunta sin contenido";
    }

    const fb = document.getElementById('mc-feedback');
    if (fb) {
      fb.className = 'feedback hidden';
      fb.innerHTML = '';
    }

    if (container) {
      container.innerHTML = '';
      const btnValidar = document.getElementById('btn-validar');
      if (btnValidar) btnValidar.disabled = true;

      const rawOpts = q.opciones || q.opcoes || [];
      if (rawOpts.length === 0) {
        container.innerHTML = "<div style='padding:15px; color:var(--muted);'>Esta pregunta es de desarrollo oral o respuesta corta.</div>";
      } else {
        rawOpts.forEach((optRaw, idx) => {
          const opt = normalizarOpcion(optRaw);
          const btn = document.createElement('button');
          btn.className = 'option-btn';
          btn.innerHTML = `<span class="option-label">${String.fromCharCode(65 + idx)}</span> <span>${escaparHTML(opt.texto)}</span>`;
          btn.onclick = () => validarChoice(btn, idx);
          container.appendChild(btn);
        });
      }
    }

    const joyPanel = document.getElementById('mc-joy-panel');
    if (joyPanel) joyPanel.style.display = 'none';
  } catch (err) {
    console.error("Error al cargar la pregunta:", err);
    const pregunta = document.getElementById('mc-pergunta');
    if (pregunta) pregunta.textContent = `No se pudo cargar la pregunta actual. Error: ${err.message}`;
  }
}"""

app_js = re.sub(r'function loadChoice\(\) \{[\s\S]*?joyPanel\.style\.display = \'none\';\s*\}\s*\} catch[\s\S]*?\}\s*\}', load_choice_guaranteed, app_js)

with open("app.js", "w", encoding="utf-8") as f:
    f.write(app_js)

print("2. app.js actualizado con loadChoice ultra-defensivo usando null checks en todos los IDs.")
