import re

print("=== ACTUALIZANDO RESOLUCIÓN PASO A PASO PROFE JOY ===")

with open("app.js", "r", encoding="utf-8") as f:
    app_js = f.read()

nueva_resolucion_joy = """
// ==========================================
// MÉTODO PROFE JOY — RESOLUCIÓN PASO A PASO COMPLETA
// Explica cada alternativa: La correcta y por qué, las equivocadas y por qué.
// ==========================================

function generarPanelJoy(preguntaObj, seleccionadaIdx = null, esCorrecta = null) {
  const q = preguntaObj;
  const materia = q.materia || currentMateria || "Medicina UNLP";
  const tp = q.tpPrincipal || "TP1";
  const tema = q.tema || "Tema General";
  
  const indiceCorrecto = obtenerIndiceCorrecto(q);
  const rawOpts = q.opciones || q.opcoes || [];
  
  const seleccionValida = seleccionadaIdx !== null && seleccionadaIdx !== undefined && seleccionadaIdx >= 0;
  const esExito = esCorrecta === true || (seleccionValida && seleccionadaIdx === indiceCorrecto);
  
  // Diagnóstico del Error si falló
  const diagError = (!esExito && seleccionValida) ? determinarTipoError(q, seleccionadaIdx) : null;
  
  // Construcción del desglose paso a paso de TODAS las alternativas
  let desgloseOpcionesHTML = "";
  
  rawOpts.forEach((optRaw, idx) => {
    const optNorm = normalizarOpcion(optRaw);
    const letra = String.fromCharCode(65 + idx);
    const esEstaCorrecta = (indiceCorrecto !== null && idx === indiceCorrecto);
    const esEstaSeleccionada = (seleccionValida && idx === seleccionadaIdx);
    
    // Obtener la justificación específica del banco o generar la explicación Profe Joy
    let explicacionDetallada = optNorm.explicacion || q.joy?.porQueNoCorrectas?.[idx] || "";
    
    if (esEstaCorrecta) {
      if (!explicacionDetallada) {
        explicacionDetallada = q.joy?.examen || q.justificativa || "Esta afirmación responde directamente al mecanismo biológico/anatómico evaluado en la bibliografía oficial de la Cátedra.";
      }
    } else {
      if (!explicacionDetallada) {
        explicacionDetallada = q.joy?.trampa || "Esta opción contiene un término o localización errónea que altera el significado conceptual.";
      }
    }

    desgloseOpcionesHTML += `
      <div style="background: ${esEstaCorrecta ? 'rgba(16, 185, 129, 0.08)' : (esEstaSeleccionada ? 'rgba(239, 68, 68, 0.08)' : 'rgba(255, 255, 255, 0.02)')}; border: 1px solid ${esEstaCorrecta ? 'rgba(16, 185, 129, 0.4)' : (esEstaSeleccionada ? 'rgba(239, 68, 68, 0.4)' : 'rgba(255, 255, 255, 0.08)')}; border-radius: 8px; padding: 0.9rem 1.1rem; margin-bottom: 0.75rem;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.4rem; flex-wrap: wrap; gap: 0.5rem;">
          <div style="display: flex; align-items: center; gap: 0.5rem; font-weight: bold; font-size: 0.95rem;">
            <span style="background: ${esEstaCorrecta ? '#10b981' : (esEstaSeleccionada ? '#ef4444' : '#334155')}; color: #fff; padding: 2px 8px; border-radius: 4px;">${letra}</span>
            <span style="color: ${esEstaCorrecta ? '#34d399' : (esEstaSeleccionada ? '#f87171' : 'var(--fg-default)')};">"${escaparHTML(optNorm.texto)}"</span>
          </div>
          <span style="font-size: 0.8rem; font-weight: bold; padding: 3px 10px; border-radius: 20px; ${esEstaCorrecta ? 'background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #10b981;' : 'background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3);'}">
            ${esEstaCorrecta ? '✓ OPCIÓN CORRECTA' : '❌ EQUIVOCADA'}
          </span>
        </div>
        
        <div style="font-size: 0.88rem; line-height: 1.45; color: ${esEstaCorrecta ? '#a7f3d0' : '#cbd5e1'}; margin-top: 0.4rem; padding-left: 0.4rem; border-left: 3px solid ${esEstaCorrecta ? '#10b981' : (esEstaSeleccionada ? '#ef4444' : '#475569')};">
          <strong>${esEstaCorrecta ? '¿Por qué está CORRECTA?' : '¿Por qué está EQUIVOCADA?'}</strong><br/>
          ${escaparHTML(explicacionDetallada)}
        </div>
      </div>
    `;
  });

  return `
    <div class="joy-panel ${esExito ? 'joy-correct' : 'joy-incorrect'} animate-fade-in" style="margin-top: 1.5rem; border-radius: 12px; overflow: hidden; border: 1px solid ${esExito ? '#10b981' : '#ef4444'};">
      
      <!-- Header Profe Joy -->
      <div class="joy-header" style="background: #0f172a; padding: 1.25rem 1.5rem; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.75rem;">
        <div class="joy-verdict ${esExito ? 'correct-text' : 'incorrect-text'}" style="font-size: 1.1rem; font-weight: bold; display: flex; align-items: center; gap: 0.6rem; color: ${esExito ? '#34d399' : '#f87171'};">
          <i class="fa-solid ${esExito ? 'fa-circle-check' : 'fa-graduation-cap'}"></i>
          <span>${esExito ? '¡Excelente! Respuesta Correcta' : 'Resolución Paso a Paso — Método Profe Joy'}</span>
        </div>
        <div class="joy-tema-tag" style="font-size: 0.8rem; padding: 4px 12px; border-radius: 20px; background: rgba(0, 229, 255, 0.1); color: var(--cyan-neon); border: 1px solid rgba(0, 229, 255, 0.3);">
          <span>${escaparHTML(materia)} • ${escaparHTML(tp)}</span>
        </div>
      </div>

      <!-- Lema del Método Profe Joy -->
      <div class="joy-metodo-header" style="background: linear-gradient(135deg, rgba(127, 0, 255, 0.2), rgba(0, 229, 255, 0.1)); padding: 0.85rem 1.5rem; font-size: 0.95rem; font-weight: 600; color: var(--cyan-neon); border-bottom: 1px solid rgba(0, 229, 255, 0.15); display: flex; align-items: center; gap: 0.6rem;">
        <i class="fa-solid fa-brain"></i>
        <span>"Primero comprender. Memorizar es la consecuencia." — Profe Joy</span>
      </div>

      <!-- Contenido Paso a Paso -->
      <div style="padding: 1.25rem 1.5rem; background: #0b0f19; display: flex; flex-direction: column; gap: 1.25rem;">
        
        ${!esExito && diagError ? `
        <!-- Diagnóstico del Error -->
        <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 10px; padding: 1rem 1.25rem;">
          <div style="display: flex; align-items: center; gap: 0.5rem; color: #f87171; font-weight: bold; font-size: 1rem; margin-bottom: 0.4rem;">
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

        <!-- Paso 1: Entender el Enunciado y la Lógica del Concepto -->
        <div style="background: rgba(59, 130, 246, 0.08); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 10px; padding: 1rem 1.25rem;">
          <strong style="color: #60a5fa; font-size: 0.95rem; display: block; margin-bottom: 0.4rem;">
            <i class="fa-solid fa-layer-group" style="margin-right: 0.4rem;"></i>
            PASO 1: Reconstrucción Lógica del Concepto
          </strong>
          <p style="color: #bfdbfe; font-size: 0.9rem; line-height: 1.5; margin: 0;">
            ${escaparHTML(q.joy?.examen || q.justificativa || "Analizamos el mecanismo central antes de evaluar las opciones. Recordá: En la Cátedra de La Plata la estructura y la función están estrictamente ligadas.")}
          </p>
        </div>

        <!-- Paso 2: Análisis Paso a Paso de Cada Opción (Correcta vs Equivocadas) -->
        <div>
          <strong style="color: #f1f5f9; font-size: 1rem; display: block; margin-bottom: 0.75rem;">
            <i class="fa-solid fa-list-check" style="margin-right: 0.4rem; color: var(--cyan-neon);"></i>
            PASO 2: Análisis Detallado de Alternativas (Profe Joy)
          </strong>
          ${desgloseOpcionesHTML}
        </div>

        <!-- Paso 3: Conclusión y Trampa del Docente -->
        <div style="background: rgba(251, 191, 36, 0.08); border: 1px solid rgba(251, 191, 36, 0.3); border-radius: 10px; padding: 1rem 1.25rem;">
          <strong style="color: #fbbf24; font-size: 0.95rem; display: block; margin-bottom: 0.4rem;">
            <i class="fa-solid fa-lightbulb" style="margin-right: 0.4rem;"></i>
            PASO 3: Conclusión y La Trampa del Docente
          </strong>
          <p style="color: #fde68a; font-size: 0.9rem; line-height: 1.5; margin: 0;">
            ${escaparHTML(q.joy?.trampa || "Por lo tanto, la única opción que satisface el 100% de los criterios académicos es la alternativa " + (indiceCorrecto !== null ? String.fromCharCode(65 + indiceCorrecto) : "correcta") + ". Cuidate de los distractores que alteran una sola palabra.")}
          </p>
        </div>

      </div>

      <!-- Footer con acciones didácticas -->
      <div class="joy-actions" style="padding: 1rem 1.5rem; background: #0f172a; border-top: 1px solid var(--border); display: flex; gap: 0.75rem; flex-wrap: wrap;">
        <button class="btn-action-flashcard" onclick="crearFlashcard('${q.id}')" style="background: rgba(127, 0, 255, 0.2); color: #c084fc; border: 1px solid rgba(127, 0, 255, 0.4); padding: 8px 16px; border-radius: 6px; font-weight: 600; cursor: pointer;">
          <i class="fa-solid fa-bolt"></i> Crear Flashcard
        </button>
        <button class="btn-action-repaso" onclick="agregarRepaso('${q.id}')" style="background: rgba(0, 229, 255, 0.15); color: var(--cyan-neon); border: 1px solid rgba(0, 229, 255, 0.3); padding: 8px 16px; border-radius: 6px; font-weight: 600; cursor: pointer;">
          <i class="fa-solid fa-bookmark"></i> Agregar a Repaso
        </button>
        <a class="btn-action-biblio" href="https://www.conectafcm.com/biblioteca-virtual/965e8278-fa18-443d-8d0f-c00b1286f5b6" target="_blank" style="background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); padding: 8px 16px; border-radius: 6px; font-weight: 600; text-decoration: none; display: inline-flex; align-items: center; gap: 6px;">
          <i class="fa-solid fa-book-open"></i> Ver en Biblioteca Virtual
        </a>
      </div>

    </div>
  `;
}
"""

# Replace generarPanelJoy in app.js
app_js = re.sub(r'function generarPanelJoy\(preguntaObj[\s\S]*?\}\n\n// ==========================================', nueva_resolucion_joy + "\n\n// ==========================================", app_js)
if "PASO 2: Análisis Detallado de Alternativas" not in app_js:
    app_js = re.sub(r'function generarPanelJoy\(preguntaObj[\s\S]*?\}\n\n', nueva_resolucion_joy + "\n\n", app_js)

with open("app.js", "w", encoding="utf-8") as f:
    f.write(app_js)

print("Resolución paso a paso del Método Profe Joy integrada exitosamente en app.js.")
