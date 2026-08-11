import re

print("=== INTEGRANDO MÉTODO PROFE JOY EN APP.JS ===")

with open("app.js", "r", encoding="utf-8") as f:
    app_js = f.read()

profe_joy_full_code = """
// ==========================================
// MÉTODO PROFE JOY — SISTEMA PEDAGÓGICO CENTRAL
// "Primero comprender. Memorizar es la consecuencia."
// ==========================================

function determinarTipoError(q, seleccionada) {
  const expl = (q.joy?.porQueNoCorrectas?.[seleccionada] || q.joy?.trampa || q.justificativa || "").toLowerCase();
  
  if (expl.includes("trampa") || expl.includes("distractor") || expl.includes("palabra") || expl.includes("excepto") || expl.includes("incorrecta")) {
    return {
      tipo: "Error de Interpretación",
      icono: "🔍",
      subtitulo: "Conocías el tema, pero la cátedra puso una trampa de lectura en el enunciado.",
      consejo: "Enseña cómo piensa la cátedra de La Plata y qué palabras clave modifican el sentido."
    };
  } else if (expl.includes("asociación") || expl.includes("mezcl") || expl.includes("confun") || expl.includes("diferen")) {
    return {
      tipo: "Error de Asociación",
      icono: "🔀",
      subtitulo: "Conocés ambos temas, pero los cruzaste en la respuesta.",
      consejo: "Comparemos lado a lado hasta que la diferencia resulte evidente."
    };
  } else if (expl.includes("memoria") || expl.includes("dato") || expl.includes("número") || expl.includes("fecha")) {
    return {
      tipo: "Error de Memoria",
      icono: "💡",
      subtitulo: "El razonamiento era impecable, solo faltó fijar la asociación lógica del dato.",
      consejo: "Creemos una asociación lógica para que el dato quede fijado de forma definitiva."
    };
  } else {
    return {
      tipo: "Error Conceptual",
      icono: "🧠",
      subtitulo: "El concepto base necesita ser reconstruido desde el principio.",
      consejo: "Volvamos al mapa general: ¿Qué es? ¿Dónde ocurre? ¿Cuál es su función? ¿Por qué existe?"
    };
  }
}

function generarPanelJoy(preguntaObj, seleccionadaIdx = null, esCorrecta = null) {
  const q = preguntaObj;
  const materia = q.materia || currentMateria || "Medicina UNLP";
  const tp = q.tpPrincipal || "TP1";
  const tema = q.tema || "Tema General";
  
  const indiceCorrecto = obtenerIndiceCorrecto(q);
  const letraCorrecta = indiceCorrecto !== null ? String.fromCharCode(65 + indiceCorrecto) : "A";
  const optCorrectaObj = normalizarOpcion((q.opciones || q.opcoes || [])[indiceCorrecto] || "");
  
  const seleccionValida = seleccionadaIdx !== null && seleccionadaIdx !== undefined && seleccionadaIdx >= 0;
  const letraSeleccionada = seleccionValida ? String.fromCharCode(65 + seleccionadaIdx) : null;
  const optSeleccionadaObj = seleccionValida ? normalizarOpcion((q.opciones || q.opcoes || [])[seleccionadaIdx] || "") : null;
  
  const esExito = esCorrecta === true || (seleccionValida && seleccionadaIdx === indiceCorrecto);
  
  // Diagnóstico del Error
  const diagError = (!esExito && seleccionValida) ? determinarTipoError(q, seleccionadaIdx) : null;
  
  // Contenidos explicativos
  const conceptoClave = q.joy?.examen || q.justificativa || q.justificacionClasificacion || "Esta consigna evalúa el mecanismo estructural básico del tema según la bibliografía oficial de la Cátedra.";
  const trampaDocente = q.joy?.trampa || "Prestá atención a las palabras absolutas (siempre, nunca, sólo) y a las variaciones histopatológicas.";
  const porqueCorrecta = optCorrectaObj.explicacion || q.joy?.porQueNoCorrectas?.[indiceCorrecto] || "Es la única alternativa que satisface la correlación anatomoclínica y la bibliografía oficial.";
  const porqueSeleccionada = (!esExito && optSeleccionadaObj) ? (optSeleccionadaObj.explicacion || q.joy?.porQueNoCorrectas?.[seleccionadaIdx] || "Esta opción suele ser un distractor frecuente que cambia un término científico clave.") : "";

  return `
    <div class="joy-panel ${esExito ? 'joy-correct' : 'joy-incorrect'} animate-fade-in">
      
      <!-- Encabezado Profe Joy -->
      <div class="joy-header">
        <div class="joy-verdict ${esExito ? 'correct-text' : 'incorrect-text'}">
          <i class="fa-solid ${esExito ? 'fa-circle-check' : 'fa-triangle-exclamation'}"></i>
          <span>${esExito ? '¡Excelente Razonamiento!' : 'Diagnóstico de la Profe Joy'}</span>
        </div>
        <div class="joy-tema-tag">
          <i class="fa-solid fa-graduation-cap"></i>
          <span>${escaparHTML(materia)} • ${escaparHTML(tp)}</span>
        </div>
      </div>

      <!-- Lema del Método -->
      <div class="joy-metodo-header">
        <i class="fa-solid fa-brain" style="color: var(--cyan-neon);"></i>
        <span>"Primero comprender. Memorizar es la consecuencia." — Método Profe Joy</span>
      </div>

      <!-- Cuerpo del Análisis -->
      <div style="padding: 1.25rem 1.5rem; display: flex; flex-direction: column; gap: 1.25rem; background: #0b0f19;">
        
        ${!esExito && diagError ? `
        <!-- Cuadro Diagnóstico del Error -->
        <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 10px; padding: 1rem 1.25rem;">
          <div style="display: flex; align-items: center; gap: 0.6rem; color: #f87171; font-weight: bold; font-size: 1rem; margin-bottom: 0.4rem;">
            <span>${diagError.icono}</span>
            <span>${diagError.tipo}: ¿Dónde se rompió el razonamiento?</span>
          </div>
          <p style="color: #fca5a5; font-size: 0.9rem; margin-bottom: 0.4rem; line-height: 1.4;">
            ${diagError.subtitulo}
          </p>
          <div style="font-size: 0.85rem; color: #fda4af; font-style: italic; background: rgba(0,0,0,0.3); padding: 0.5rem 0.8rem; border-radius: 6px;">
            💡 <strong>Estrategia Profe Joy:</strong> ${diagError.consejo}
          </div>
        </div>
        ` : ''}

        <!-- 1. Construcción del Mapa Lógico (El Mecanismo) -->
        <div class="joy-clave" style="background: rgba(16, 185, 129, 0.06); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 10px; padding: 1rem 1.25rem;">
          <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom: 0.5rem;">
            <strong style="color: #34d399; font-size: 0.98rem;">
              <i class="fa-solid fa-map-location-dot" style="margin-right:0.4rem;"></i>
              1. Construcción Lógica del Concepto (¿Por qué es así?)
            </strong>
            <span style="font-size:0.75rem; color:#6ee7b7; background:rgba(16,185,129,0.2); padding:2px 8px; border-radius:12px;">Cátedra FCM UNLP</span>
          </div>
          <p style="color: #d1fae5; font-size: 0.92rem; line-height: 1.55; margin: 0;">
            ${conceptoClave}
          </p>
        </div>

        <!-- 2. Desglose de Alternativas (Análisis Cátedra) -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem;">
          
          <!-- Opción Correcta -->
          <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 10px; padding: 1rem;">
            <div style="color: #34d399; font-weight: bold; font-size: 0.9rem; margin-bottom: 0.4rem; display: flex; align-items: center; gap: 0.4rem;">
              <span class="option-label" style="background:#10b981; color:#000; padding:2px 8px; border-radius:4px; font-weight:bold;">${letraCorrecta}</span>
              <span>Respuesta Correcta UNLP</span>
            </div>
            <p style="color: #a7f3d0; font-size: 0.88rem; line-height: 1.45; margin: 0;">
              <strong>"${escaparHTML(optCorrectaObj.texto)}":</strong> ${porqueCorrecta}
            </p>
          </div>

          ${!esExito && optSeleccionadaObj ? `
          <!-- Opción Elegida (Error) -->
          <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.4); border-radius: 10px; padding: 1rem;">
            <div style="color: #f87171; font-weight: bold; font-size: 0.9rem; margin-bottom: 0.4rem; display: flex; align-items: center; gap: 0.4rem;">
              <span class="option-label" style="background:#ef4444; color:#fff; padding:2px 8px; border-radius:4px; font-weight:bold;">${letraSeleccionada}</span>
              <span>Tu opción marcada</span>
            </div>
            <p style="color: #fca5a5; font-size: 0.88rem; line-height: 1.45; margin: 0;">
              <strong>"${escaparHTML(optSeleccionadaObj.texto)}":</strong> ${porqueSeleccionada}
            </p>
          </div>
          ` : ''}

        </div>

        <!-- 3. Ojo del Docente / La Trampa del Examen -->
        <div class="joy-trampa" style="background: rgba(251, 191, 36, 0.06); border: 1px solid rgba(251, 191, 36, 0.3); border-radius: 10px; padding: 1rem 1.25rem;">
          <strong style="color: #fbbf24; font-size: 0.95rem; display: block; margin-bottom: 0.4rem;">
            <i class="fa-solid fa-eye" style="margin-right:0.4rem;"></i>
            ¿Qué quiso evaluar el profesor con esta pregunta? (La Trampa)
          </strong>
          <p style="color: #fde68a; font-size: 0.9rem; line-height: 1.5; margin: 0;">
            ${trampaDocente}
          </p>
        </div>

      </div>

      <!-- Pie de página con acciones del estudiante -->
      <div class="joy-actions" style="padding: 1rem 1.5rem; background: #111827; border-top: 1px solid var(--border); display: flex; gap: 0.75rem; flex-wrap: wrap;">
        <button class="btn-action-flashcard" onclick="crearFlashcard('${q.id}')">
          <i class="fa-solid fa-bolt"></i> Crear Flashcard
        </button>
        <button class="btn-action-repaso" onclick="agregarRepaso('${q.id}')">
          <i class="fa-solid fa-bookmark"></i> Agregar a Repaso
        </button>
        <button class="btn-action-parecida" onclick="practicarParecida('${q.id}')">
          <i class="fa-solid fa-rotate-right"></i> Practicar Parecida
        </button>
      </div>

    </div>
  `;
}
"""

# Replace old generarPanelJoy in app.js
app_js = re.sub(r'function generarPanelJoy\(preguntaObj\) \{[\s\S]*?\}\n\n// ==========================================', profe_joy_full_code + "\n\n// ==========================================", app_js)
if "function determinarTipoError" not in app_js:
    app_js = re.sub(r'function generarPanelJoy\(preguntaObj[\s\S]*?\}\n\n', profe_joy_full_code + "\n\n", app_js)

# Update validarChoice call to pasar (q, selectedOption, isCorrect)
validar_call_old = r'const joyPanel = document\.getElementById\(\'mc-joy-panel\'\);\s*if \(joyPanel\) \{\s*joyPanel\.innerHTML = generarPanelJoy\(q\);\s*joyPanel\.style\.display = \'block\';\s*\}'
validar_call_new = """const joyPanel = document.getElementById('mc-joy-panel');
  if (joyPanel) {
    joyPanel.innerHTML = generarPanelJoy(q, index, isCorrect);
    joyPanel.style.display = 'block';
  }"""

app_js = re.sub(validar_call_old, validar_call_new, app_js)

# Also check for any other generarPanelJoy(q) calls
app_js = app_js.replace("generarPanelJoy(q)", "generarPanelJoy(q, selectedOption, yaValidado ? (selectedOption === obtenerIndiceCorrecto(q)) : null)")

with open("app.js", "w", encoding="utf-8") as f:
    f.write(app_js)

print("Método Profe Joy integrado completamente en app.js.")
