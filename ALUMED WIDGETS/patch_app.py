import re

with open('app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

# 1. Inject Helper Functions at the top
helpers = """
// ─────────────────────────────────────────────────────────────
//  HELPER FUNCTIONS (PROFE JOY)
// ─────────────────────────────────────────────────────────────
const STORAGE_KEYS = {
  intentos: "alumed_intentos",
  errores: "alumed_errores",
  flashcards: "alumed_flashcards",
  repaso: "alumed_repaso"
};

function leerStorage(clave) {
  try {
    const valor = JSON.parse(localStorage.getItem(clave));
    return Array.isArray(valor) ? valor : [];
  } catch {
    return [];
  }
}

function escribirStorage(clave, valor) {
  localStorage.setItem(clave, JSON.stringify(valor));
}

function escaparHTML(valor = "") {
  const div = document.createElement("div");
  div.textContent = String(valor);
  return div.innerHTML;
}

function letraOpcion(indice) {
  return String.fromCharCode(65 + indice);
}

function etiquetasJoy(materia) {
  const mapas = {
    "Biología Celular": [
      ["queEs", "Qué es", "🔬"], ["dondeSe", "Dónde se encuentra", "📍"],
      ["estructura", "Estructura", "🧩"], ["funcion", "Función", "⚙️"],
      ["mecanismo", "Mecanismo básico", "↻"], ["siFalla", "Qué ocurre si falla", "⚠️"]
    ],
    "Biología": [
      ["queEs", "Qué es", "🔬"], ["dondeSe", "Dónde se encuentra", "📍"],
      ["estructura", "Estructura", "🧩"], ["funcion", "Función", "⚙️"],
      ["mecanismo", "Mecanismo básico", "↻"], ["siFalla", "Qué ocurre si falla", "⚠️"]
    ],
    "Histología": [
      ["tejido", "Tejido u órgano", "🔬"], ["celulas", "Células principales", "◉"],
      ["capasOrg", "Capas y organización", "🧩"], ["tincion", "Tinción", "🎨"],
      ["funcion", "Función", "⚙️"], ["reconocer", "Cómo reconocerlo", "👁️"]
    ],
    "Histología y Embriología": [
      ["tejido", "Tejido u órgano", "🔬"], ["celulas", "Células principales", "◉"],
      ["capasOrg", "Capas y organización", "🧩"], ["tincion", "Tinción", "🎨"],
      ["funcion", "Función", "⚙️"], ["reconocer", "Cómo reconocerlo", "👁️"]
    ],
    "Embriología": [
      ["estructura", "Qué estructura es", "🧬"], ["origenEmb", "Origen embrionario", "↗"],
      ["cuandoAparece", "Cuándo aparece", "🕐"], ["etapas", "Etapas", "➜"],
      ["derivados", "Derivados", "🌱"], ["reconocer", "Cómo reconocerla", "👁️"]
    ],
    "Anatomía": [
      ["queEs", "Qué es", "🦴"], ["ubicacion", "Ubicación", "📍"],
      ["partes", "Partes", "🧩"], ["relaciones", "Relaciones", "↔"],
      ["irrigInnerv", "Irrigación e inervación", "🫀"], ["reconocer", "Cómo reconocerlo", "👁️"]
    ],
    "Anatomía Cátedra A": [
      ["queEs", "Qué es", "🦴"], ["ubicacion", "Ubicación", "📍"],
      ["partes", "Partes", "🧩"], ["relaciones", "Relaciones", "↔"],
      ["irrigInnerv", "Irrigación e inervación", "🫀"], ["reconocer", "Cómo reconocerlo", "👁️"]
    ],
    "Anatomía Cátedra B": [
      ["queEs", "Qué es", "🦴"], ["ubicacion", "Ubicación", "📍"],
      ["partes", "Partes", "🧩"], ["relaciones", "Relaciones", "↔"],
      ["irrigInnerv", "Irrigación e inervación", "🫀"], ["reconocer", "Cómo reconocerlo", "👁️"]
    ],
    "Anatomía Cátedra C": [
      ["queEs", "Qué es", "🦴"], ["ubicacion", "Ubicación", "📍"],
      ["partes", "Partes", "🧩"], ["relaciones", "Relaciones", "↔"],
      ["irrigInnerv", "Irrigación e inervación", "🫀"], ["reconocer", "Cómo reconocerlo", "👁️"]
    ]
  };
  return mapas[materia] || mapas["Biología Celular"];
}
"""
app_js = app_js.replace("// ─────────────────────────────────────────────────────────────\n//  NAVEGACIÓN DE TABS", helpers + "\n// ─────────────────────────────────────────────────────────────\n//  NAVEGACIÓN DE TABS")

# 2. Update loadChoice() to disable btn-validar initially
loadChoice_orig = """  // Opciones
  const container = document.getElementById('mc-opcoes');
  container.innerHTML = '';
  q.opcoes.forEach((opt, idx) => {
    const btn = document.createElement('button');
    btn.className = 'option-btn';
    btn.id        = `opt-${idx}`;
    btn.innerText = opt;
    btn.onclick   = () => {
      if (yaValidado) return;
      document.querySelectorAll('.option-btn').forEach(b => b.classList.remove('selected'));
      btn.classList.add('selected');
      selectedOption = idx;
    };
    container.appendChild(btn);
  });
}"""

loadChoice_new = """  // Opciones
  const container = document.getElementById('mc-opcoes');
  container.innerHTML = '';
  const btnValidar = document.getElementById('btn-validar');
  if (btnValidar) btnValidar.disabled = true;
  q.opcoes.forEach((opt, idx) => {
    const btn = document.createElement('button');
    btn.className = 'option-btn';
    btn.id        = `opt-${idx}`;
    btn.setAttribute('role', 'radio');
    btn.setAttribute('aria-checked', 'false');
    btn.innerHTML = `<span class="option-letter">${letraOpcion(idx)}</span> <span>${escaparHTML(opt)}</span>`;
    btn.onclick   = () => {
      if (yaValidado) return;
      document.querySelectorAll('.option-btn').forEach(b => {
          b.classList.remove('selected');
          b.setAttribute('aria-checked', 'false');
      });
      btn.classList.add('selected');
      btn.setAttribute('aria-checked', 'true');
      selectedOption = idx;
      if (btnValidar) btnValidar.disabled = false;
    };
    container.appendChild(btn);
  });
}"""
app_js = app_js.replace(loadChoice_orig, loadChoice_new)


# 3. Replace validarChoice and generarPanelJoy
validar_start = app_js.find("function validarChoice()")
validar_end = app_js.find("// ─────────────────────────────────────────────────────────────\n//  MODAL FRAGMENTO")

if validar_start != -1 and validar_end != -1:
    old_validar = app_js[validar_start:validar_end]
    new_validar = """function validarChoice() {
  if (selectedOption === null || yaValidado) return;
  yaValidado = true;

  const q          = filteredChoices[currentChoiceIndex];
  const fb         = document.getElementById('mc-feedback');
  if (!fb) return;

  const esCorrecta  = selectedOption === q.correta;

  // Colorear opciones y bloquearlas
  document.querySelectorAll('.option-btn').forEach((btn, idx) => {
    btn.disabled = true;
    if (idx === q.correta)    btn.classList.add('correct-reveal');
    else if (idx === selectedOption) btn.classList.add('wrong-reveal');
  });

  // Persistir
  guardarEnLocalStorage(q, selectedOption);

  // Renderizar panel Joy
  fb.innerHTML  = generarPanelJoy(q, selectedOption);
  fb.className  = 'feedback joy-active';

  // Scroll suave al feedback
  setTimeout(() => fb.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);
}

// ─────────────────────────────────────────────────────────────
//  GENERADOR PANEL PROFE JOY
// ─────────────────────────────────────────────────────────────
function generarPanelJoy(q, seleccionado) {
  const correcta = seleccionado === q.correta;
  const joy = q.joy || {};
  const PLACEHOLDER = 'Este punto todavía no fue localizado en los apuntes ALUMED cargados.';
  const sinJoy = Object.keys(joy).length === 0;

  let seccionesHTML = '';
  if (!sinJoy) {
    seccionesHTML = etiquetasJoy(q.materia)
      .filter(([campo]) => joy[campo])
      .map(([campo, titulo, icono]) => `
        <div class="joy-section">
          <span class="joy-icon" aria-hidden="true">${icono}</span>
          <div><h4>${escaparHTML(titulo)}</h4><p>${escaparHTML(joy[campo])}</p></div>
        </div>`).join("");
  } else {
    seccionesHTML = `
        <div class="joy-section">
          <span class="joy-icon" aria-hidden="true">🧠</span>
          <div><h4>Explicación</h4><p>${q.justificativa ? escaparHTML(q.justificativa) : PLACEHOLDER}</p></div>
        </div>`;
  }

  const razones = q.opcoes.map((opcion, indice) => {
    if (indice === q.correta) return "";
    const texto = joy.porQueNoCorrectas?.[indice] || "Esta opción no corresponde al concepto evaluado.";
    return `<li><strong>${letraOpcion(indice)}. ${escaparHTML(opcion)}:</strong> ${escaparHTML(texto)}</li>`;
  }).join("");

  const tieneFragmento = !!(q.fragmentoApunte && q.fragmentoApunte.trim());

  return `
    <article class="joy-panel ${correcta ? "is-correct" : "is-wrong"}">
      <header class="joy-header">
        <div class="result-icon">${correcta ? "✓" : "×"}</div>
        <div>
          <span>${correcta ? "¡Correcto! — Profe Joy" : "Entendamos juntos — Método Profe Joy"}</span>
          <h3>${correcta
            ? `Marcaste ${letraOpcion(seleccionado)} y es la respuesta correcta.`
            : `Marcaste ${letraOpcion(seleccionado)}. La correcta es ${letraOpcion(q.correta)}.`}</h3>
        </div>
      </header>

      <div class="joy-title">
        <div class="joy-avatar"><i class="fa-solid fa-stethoscope"></i></div>
        <div><span>Entendamos juntos</span><h3>Método Profe Joy</h3></div>
      </div>

      <div class="joy-grid">${seccionesHTML}</div>

      ${joy.examen ? `<div class="joy-clave"><span class="joy-icon-span">🧠</span><div><h4>La clave para el examen</h4><p>${escaparHTML(joy.examen)}</p></div></div>` : ""}
      ${joy.trampa ? `<div class="joy-trampa"><span class="joy-icon-span">⚠️</span><div><h4>Ojo con la trampa</h4><p>${escaparHTML(joy.trampa)}</p></div></div>` : ""}

      ${!sinJoy ? `<div class="joy-no-correctas">
        <h4>¿Por qué las otras opciones no son correctas?</h4>
        <ul>${razones}</ul>
      </div>` : ''}

      <div class="joy-fuente">
        <div>
          <strong>Material de estudio</strong>
          <span>Explicación basada en materiales ALUMED.</span>
        </div>
        ${tieneFragmento ? `<button class="btn-link" type="button" onclick="abrirFragmento(${q.id})">Ver fragmento del apunte</button>` : ""}
      </div>

      <div class="joy-actions">
        <button class="btn btn-action-flashcard" type="button" onclick="crearFlashcard(${q.id})">＋ Crear flashcard</button>
        <button class="btn btn-action-repaso" type="button" onclick="agregarRepaso(${q.id})">↻ Agregar a repaso</button>
        <button class="btn btn-action-parecida" type="button" onclick="practicarParecida(${q.id})">⤴ Practicar parecida</button>
      </div>
    </article>`;
}

"""
    app_js = app_js.replace(old_validar, new_validar)
else:
    print("Failed to find validarChoice boundaries.")

# 4. Replace localstorage persistence
persist_start = app_js.find("function guardarEnLocalStorage(q, seleccionado, esCorrecta) {")
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
    // fuente: q.fuente || "",  <-- Removed per privacy instructions
    // pagina: q.pagina || "",
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

function crearFlashcard(qId) {
  const q = bancoDados.choices.find(x => x.id === qId);
  if (!q) return;
  const flashcards = leerStorage(STORAGE_KEYS.flashcards);
  if (!flashcards.some(item => item.preguntaId === q.id)) {
    flashcards.push({
      id: `fc-${q.id}-${Date.now()}`,
      preguntaId: q.id,
      frente: q.pergunta,
      reverso: `${q.opcoes[q.correta]}. ${q.justificativa || ""}`,
      materia: q.materia,
      tema: q.tema,
      // fuente: q.fuente || "", <-- Removed
      // pagina: q.pagina || "",
      nivel: 0,
      proximoRepaso: new Date().toISOString()
    });
    escribirStorage(STORAGE_KEYS.flashcards, flashcards);
    mostrarToast("✅ Flashcard creada en tu mazo");
  } else {
    mostrarToast("Esta flashcard ya existe");
  }
}

function agregarRepaso(qId) {
  const q = bancoDados.choices.find(x => x.id === qId);
  if (!q) return;
  const repaso = leerStorage(STORAGE_KEYS.repaso);
  if (!repaso.some(item => item.preguntaId === q.id)) {
    repaso.push({
      preguntaId: q.id, materia: q.materia, tema: q.tema,
      agregado: new Date().toISOString(), completado: false
    });
    escribirStorage(STORAGE_KEYS.repaso, repaso);
    mostrarToast("📌 Agregada al repaso de errores");
  } else {
    mostrarToast("Ya está en tu repaso");
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
else:
    print("Failed to find guardarEnLocalStorage boundaries.")

# Dark/Light mode theme init
theme_script = """
const temaGuardado = localStorage.getItem("alumed_tema") || "dark";
document.documentElement.dataset.theme = temaGuardado;

function toggleTheme() {
  const nuevo = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
  document.documentElement.dataset.theme = nuevo;
  localStorage.setItem("alumed_tema", nuevo);
}
"""
app_js += "\n" + theme_script + "\n"

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)
print("app.js updated.")

