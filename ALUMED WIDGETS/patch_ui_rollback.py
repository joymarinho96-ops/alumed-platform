import re

# ==========================================
# 1. PATCH APP.JS
# ==========================================
with open('app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

# Restore the user's requested functions
user_helpers = """
// ─────────────────────────────────────────────────────────────
//  HELPER FUNCTIONS (PROFE JOY)
// ─────────────────────────────────────────────────────────────
const STORAGE_KEYS = {
  intentos: "alumed_intentos",
  errores: "alumed_errores",
  flashcards: "alumed_flashcards",
  repaso: "alumed_repaso"
};

function leerStorage(key, defaultVal = []) {
  try {
    const d = localStorage.getItem(key);
    return d ? JSON.parse(d) : defaultVal;
  } catch (e) {
    return defaultVal;
  }
}

function escribirStorage(key, val) {
  try {
    localStorage.setItem(key, JSON.stringify(val));
  } catch (e) {
    console.error('Error guardando en localStorage:', e);
  }
}

function escaparHTML(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function letraOpcion(idx) {
  return ['A', 'B', 'C', 'D', 'E'][idx] || '';
}

function etiquetasJoy(materia) {
  const m = (materia || '').toLowerCase();
  if (m.includes('bio')) {
    return {
      clave: '💡 Concepto Celular Clave',
      trampa: '⚠️ Trampa de Osmolaridad / Coeficiente σ'
    };
  } else if (m.includes('histo')) {
    return {
      clave: '🔬 Característica Histológica',
      trampa: '⚠️ Confusión de Tinción / Origen Embrionario'
    };
  } else if (m.includes('anato')) {
    return {
      clave: '🦴 Relación Anatómica Clave',
      trampa: '⚠️ Error Frecuente en Nomenclatura UNLP'
    };
  }
  return {
    clave: '💡 Clave de Estudio',
    trampa: '⚠️ Distractor Frecuente'
  };
}
"""

# We need to replace the old helpers block that was injected previously
helpers_start = app_js.find("// ─────────────────────────────────────────────────────────────\n//  HELPER FUNCTIONS (PROFE JOY)")
helpers_end = app_js.find("// ─────────────────────────────────────────────────────────────\n//  NAVEGACIÓN DE ENTRENAMIENTO PARCIAL")

if helpers_start != -1 and helpers_end != -1:
    app_js = app_js[:helpers_start] + user_helpers + "\n" + app_js[helpers_end:]

# Update loadChoice
loadChoice_start = app_js.find("function loadChoice() {")
loadChoice_end = app_js.find("function validarChoice() {")

if loadChoice_start != -1 and loadChoice_end != -1:
    old_load = app_js[loadChoice_start:loadChoice_end]
    new_load = """function loadChoice() {
  const q = filteredChoices[currentChoiceIndex];
  if (!q) return;

  yaValidado = false;
  selectedOption = null;

  // Header y pregunta
  document.getElementById('mc-materia-tag').innerText = q.materia;
  document.getElementById('mc-counter').innerText     = `Pregunta ${currentChoiceIndex + 1} de ${filteredChoices.length}`;
  document.getElementById('mc-question-text').innerText = q.pergunta;

  // Limpiar feedback
  const fb = document.getElementById('mc-feedback');
  fb.className = 'feedback hidden';
  fb.innerHTML = '';

  // Opciones
  const container = document.getElementById('mc-opcoes');
  container.innerHTML = '';
  const btnValidar = document.getElementById('btn-validar');
  if (btnValidar) btnValidar.disabled = true; // Deshabilitado inicialmente

  q.opcoes.forEach((opt, idx) => {
    const btn = document.createElement('button');
    btn.className = 'option-btn';
    btn.id        = `opt-${idx}`;
    btn.setAttribute('role', 'radio');
    btn.setAttribute('aria-checked', 'false');
    
    // Add option letter and text container
    btn.innerHTML = `
      <div class="option-content">
        <span class="option-letter">${letraOpcion(idx)}</span> 
        <span>${escaparHTML(opt)}</span>
      </div>
      <div class="option-explanation hidden"></div>
    `;
    
    btn.onclick   = () => {
      if (yaValidado) return;
      document.querySelectorAll('.option-btn').forEach(b => {
          b.classList.remove('selected');
          b.setAttribute('aria-checked', 'false');
      });
      btn.classList.add('selected');
      btn.setAttribute('aria-checked', 'true');
      selectedOption = idx;
      if (btnValidar) btnValidar.disabled = false; // Habilitado al seleccionar
    };
    container.appendChild(btn);
  });
}

"""
    app_js = app_js.replace(old_load, new_load)

# Update validarChoice and generarPanelJoy
validar_start = app_js.find("function validarChoice() {")
validar_end = app_js.find("// ─────────────────────────────────────────────────────────────\n//  MODAL FRAGMENTO")

if validar_start != -1 and validar_end != -1:
    old_validar = app_js[validar_start:validar_end]
    new_validar = """function validarChoice() {
  if (selectedOption === null || yaValidado) return;
  yaValidado = true;

  const q = filteredChoices[currentChoiceIndex];
  const fb = document.getElementById('mc-feedback');
  if (!fb) return;

  const esCorrecta = selectedOption === q.correta;

  // Deshabilitar botón de confirmar
  const btnValidar = document.getElementById('btn-validar');
  if (btnValidar) btnValidar.disabled = true;

  // Colorear opciones y mostrar explicaciones dentro de ellas
  document.querySelectorAll('.option-btn').forEach((btn, idx) => {
    btn.disabled = true; // bloquear el cambio de respuesta
    const explanationDiv = btn.querySelector('.option-explanation');
    explanationDiv.classList.remove('hidden');

    if (idx === q.correta) {
      btn.classList.add('correct-reveal');
      explanationDiv.innerHTML = `<strong>✅ Esta es la correcta.</strong> ${escaparHTML(q.joy?.porQueNoCorrectas?.[idx] || '')}`;
    } else if (idx === selectedOption) {
      btn.classList.add('wrong-reveal');
      explanationDiv.innerHTML = `<strong>❌ Incorrecto.</strong> ${escaparHTML(q.joy?.porQueNoCorrectas?.[idx] || 'Esta opción no corresponde al concepto evaluado.')}`;
    } else {
      explanationDiv.innerHTML = escaparHTML(q.joy?.porQueNoCorrectas?.[idx] || 'Esta opción es incorrecta.');
    }
  });

  // Persistir
  guardarEnLocalStorage(q, selectedOption);

  // Renderizar panel Joy
  fb.innerHTML = generarPanelJoy(q);
  fb.className = 'feedback joy-active';

  // Scroll suave al feedback
  setTimeout(() => fb.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);
}

// ─────────────────────────────────────────────────────────────
//  GENERADOR PANEL PROFE JOY
// ─────────────────────────────────────────────────────────────
function generarPanelJoy(preguntaObj) {
  const et = etiquetasJoy(preguntaObj.materia);
  const explicacionClave = escaparHTML(preguntaObj.joy?.examen || preguntaObj.justificativa || 'Respuesta basada en la bibliografía de la cátedra.');
  const explicacionTrampa = escaparHTML(preguntaObj.joy?.trampa || 'Lee bien las opciones, algunas palabras cambian por completo el sentido.');
  
  return `
    <div class="joy-panel animate-fade-in">
      <div class="joy-header">
        <span class="joy-badge">💛 Método Profe Joy</span>
      </div>
      
      <div class="joy-cards-container">
        <div class="joy-section joy-clave">
          <strong>${et.clave}:</strong>
          <p>${explicacionClave}</p>
        </div>
        <div class="joy-section joy-trampa">
          <strong>${et.trampa}:</strong>
          <p>${explicacionTrampa}</p>
        </div>
      </div>

      <div class="joy-fuente">
        <span>📖 Basada en examen anterior.</span>
        <button class="btn-link" onclick="abrirFragmento('${preguntaObj.id}')">Ver fragmento del apunte</button>
      </div>

      <div class="joy-actions">
        <button class="btn-action-flashcard" onclick="crearFlashcard('${preguntaObj.id}')">🎴 Crear flashcard</button>
        <button class="btn-action-repaso" onclick="agregarRepaso('${preguntaObj.id}')">📌 Agregar a repaso</button>
        <button class="btn-action-parecida" onclick="practicarParecida('${preguntaObj.id}')">🔀 Practicar parecida</button>
      </div>
    </div>
  `;
}

"""
    app_js = app_js.replace(old_validar, new_validar)


# Update persistencia block to match new storage helpers exactly
persist_start = app_js.find("function guardarEnLocalStorage(q, seleccionado) {")
persist_end = app_js.find("// ─────────────────────────────────────────────────────────────\n//  TOAST")

if persist_start != -1 and persist_end != -1:
    old_persist = app_js[persist_start:persist_end]
    new_persist = """function guardarEnLocalStorage(q, seleccionado) {
  const intentos = leerStorage(STORAGE_KEYS.intentos);
  const anteriores = intentos.filter(item => item.preguntaId === q.id).length;
  const intento = {
    id: `${q.id}-${Date.now()}`,
    preguntaId: q.id,
    pregunta: q.pergunta,
    opcionElegida: seleccionado,
    letraElegida: letraOpcion(seleccionado),
    opcionCorrecta: q.correta,
    letraCorrecta: letraOpcion(q.correta),
    correcto: seleccionado === q.correta,
    explicacion: q.justificativa || "",
    materia: q.materia,
    tema: q.tema,
    numeroIntento: anteriores + 1,
    fecha: new Date().toISOString()
  };
  intentos.push(intento);
  escribirStorage(STORAGE_KEYS.intentos, intentos);

  if (!intento.correcto) {
    const errores = leerStorage(STORAGE_KEYS.errores);
    errores.push(intento);
    escribirStorage(STORAGE_KEYS.errores, errores);
  }
  return intento;
}

function crearFlashcard(preguntaId) {
  let flashcards = leerStorage(STORAGE_KEYS.flashcards);
  if (!flashcards.includes(preguntaId)) {
    flashcards.push(preguntaId);
    escribirStorage(STORAGE_KEYS.flashcards, flashcards);
    mostrarToast('¡Flashcard guardada con éxito en tu mazo! 🎴');
  } else {
    mostrarToast('Esta pregunta ya está en tus flashcards.');
  }
}

function agregarRepaso(preguntaId) {
  let repaso = leerStorage(STORAGE_KEYS.repaso);
  if (!repaso.includes(preguntaId)) {
    repaso.push(preguntaId);
    escribirStorage(STORAGE_KEYS.repaso, repaso);
    mostrarToast('Añadida a tu lista de repaso prioritario 📌');
  } else {
    mostrarToast('Esta pregunta ya está en tu lista de repaso.');
  }
}

function buscarParecida(q) {
  return filteredChoices.find(item =>
    item.id !== q.id && item.materia === q.materia && item.tema === q.tema
  ) || filteredChoices.find(item => item.id !== q.id && item.materia === q.materia);
}

function practicarParecida(qId) {
  const q = bancoDados.choices.find(x => x.id === qId);
  if (!q) return;
  const parecida = buscarParecida(q);
  if (!parecida) {
    mostrarToast("Todavía no hay otra pregunta parecida");
    return;
  }
  currentChoiceIndex = filteredChoices.findIndex(item => item.id === parecida.id);
  loadChoice();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

"""
    app_js = app_js.replace(old_persist, new_persist)

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)
print("app.js rollback done.")

# ==========================================
# 2. PATCH STYLE.CSS
# ==========================================
with open('style.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Add CSS for option explanation, side-by-side joy cards, and button states
custom_css = """
/* Profe Joy UI Rollback */
.option-btn {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  transition: all 0.2s ease;
}

.option-content {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.option-explanation {
  margin-top: 10px;
  font-size: 0.85rem;
  padding: 8px 12px;
  border-radius: 6px;
  background-color: rgba(255, 255, 255, 0.05);
  width: 100%;
  text-align: left;
}

.option-explanation.hidden {
  display: none;
}

.option-btn.correct-reveal {
  border: 1px solid #00E676 !important;
  background: rgba(0, 230, 118, 0.05) !important;
}

.option-btn.correct-reveal .option-explanation {
  background: rgba(0, 230, 118, 0.1);
  color: #00E676;
}

.option-btn.wrong-reveal {
  border: 1px solid #FF5252 !important;
  background: rgba(255, 82, 82, 0.05) !important;
}

.option-btn.wrong-reveal .option-explanation {
  background: rgba(255, 82, 82, 0.1);
  color: #FF5252;
}

.joy-cards-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin: 20px 0;
}

.joy-section {
  padding: 16px;
  border-radius: 8px;
  text-align: left;
}

.joy-clave {
  border: 1px solid #00E676;
  background: rgba(0, 230, 118, 0.05);
}
.joy-clave strong { color: #00E676; display: block; margin-bottom: 8px; }

.joy-trampa {
  border: 1px solid #FFD700;
  background: rgba(255, 215, 0, 0.05);
}
.joy-trampa strong { color: #FFD700; display: block; margin-bottom: 8px; }

.joy-badge {
  background: rgba(255, 215, 0, 0.1);
  color: #FFD700;
  padding: 4px 12px;
  border-radius: 12px;
  font-weight: bold;
  font-size: 0.9rem;
}

.joy-header {
  text-align: center;
  margin-bottom: 15px;
}

.joy-fuente {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--surface);
  padding: 10px 16px;
  border-radius: 6px;
  margin-bottom: 20px;
  font-size: 0.85rem;
  color: var(--muted);
}

.joy-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn-action-flashcard, .btn-action-repaso, .btn-action-parecida {
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  border: none;
  transition: opacity 0.2s;
}

.btn-action-flashcard { background: #673AB7; color: white; }
.btn-action-repaso { background: #FF9800; color: white; }
.btn-action-parecida { background: #009688; color: white; }

.btn-action-flashcard:hover, .btn-action-repaso:hover, .btn-action-parecida:hover {
  opacity: 0.9;
}

.btn-link {
  background: none;
  border: none;
  color: #2196F3;
  cursor: pointer;
  text-decoration: underline;
  font-size: 0.85rem;
}

#btn-validar:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .joy-cards-container {
    grid-template-columns: 1fr;
  }
  .joy-fuente {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
}
"""

if "/* Profe Joy UI Rollback */" not in css:
    with open('style.css', 'a', encoding='utf-8') as f:
        f.write("\n" + custom_css)
    print("style.css rollback done.")
