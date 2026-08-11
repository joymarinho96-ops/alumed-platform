import re

with open("app.js", "r", encoding="utf-8") as f:
    app_js = f.read()

# Update loadChoice to handle empty filteredChoices gracefully
load_choice_robust = """function loadChoice() {
  if (!filteredChoices || filteredChoices.length === 0) {
    document.getElementById('mc-materia-tag').innerText = currentMateria || "Biología";
    document.getElementById('mc-counter').innerText     = "0 de 0";
    document.getElementById('mc-pergunta').innerText    = "No hay preguntas disponibles para la materia seleccionada.";
    document.getElementById('mc-opcoes').innerHTML      = "<div style='padding:20px; color:var(--muted); text-align:center;'>Selecciona otra materia o modo para practicar.</div>";
    const joyPanel = document.getElementById('mc-joy-panel');
    if (joyPanel) joyPanel.style.display = 'none';
    return;
  }

  // Ensure currentChoiceIndex is in range
  if (currentChoiceIndex < 0) currentChoiceIndex = 0;
  if (currentChoiceIndex >= filteredChoices.length) currentChoiceIndex = filteredChoices.length - 1;

  const q = filteredChoices[currentChoiceIndex];
  if (!q) return;

  yaValidado = false;
  selectedOption = null;

  // Header y pregunta
  document.getElementById('mc-materia-tag').innerText = q.materia || currentMateria;
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
}"""

# Replace loadChoice in app.js
app_js = re.sub(r'function loadChoice\(\) \{[\s\S]*?const joyPanel = document\.getElementById\(\'mc-joy-panel\'\);[\s\S]*?joyPanel\.style\.display = \'none\';\s*\}', load_choice_robust, app_js)

# Also update prepararEntrenamiento fallback logic
prep_old = r'function prepararEntrenamiento\(tabId, materia, btnEl\) \{[\s\S]*?if \(tabId === \'choices\'\) \{\s*loadChoice\(\);\s*\}'

prep_new = """function prepararEntrenamiento(tabId, materia, btnEl) {
  // 1. Switch Tab UI
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
  const sec = document.getElementById(`tab-${tabId}`);
  if (sec) sec.classList.add('active');
  if (btnEl) btnEl.classList.add('active');

  // 2. Set Materia and Filter with Fallbacks
  if (materia) {
    currentMateria = materia;
    
    // Strict match
    filteredChoices = (bancoDados.choices || []).filter(q => q.materia === materia);
    
    // Fallback if no questions for specific catedra
    if (filteredChoices.length === 0) {
       if (materia.includes("Anatomía")) {
           filteredChoices = (bancoDados.choices || []).filter(q => q.materia && q.materia.includes("Anatomía"));
       } else {
           filteredChoices = bancoDados.choices || [];
       }
    }
    
    currentChoiceIndex = 0;
    
    if (tabId === 'choices' || tabId === 'oral') {
      loadChoice();
    }
    if (tabId === 'pinches') {
      loadPinche();
    }
  }
}"""

app_js = re.sub(prep_old, prep_new, app_js)

with open("app.js", "w", encoding="utf-8") as f:
    f.write(app_js)

print("Robustness patch applied to app.js.")
