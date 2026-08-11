import re

print("=== IMPLEMENTANDO CORRECCIÓN RECONSTRUIDA PROFE JOY CON TODOS SUS CARDS Y PERLAS ===")

with open("app.js", "r", encoding="utf-8") as f:
    app_js = f.read()

metodo_reconstruido_joy = """
// ==========================================
// MÉTODO PROFE JOY — CORRECCIÓN RECONSTRUIDA
// "Primero comprender. Memorizar es la consecuencia."
// ==========================================

function generarPanelJoy(preguntaObj, seleccionadaIdx = null, esCorrecta = null) {
  const q = preguntaObj;
  const materia = q.materia || currentMateria || "Medicina UNLP";
  const tp = q.tpPrincipal || "TP1";
  const tema = q.tema || "Tema General";
  
  const indiceCorrecto = obtenerIndiceCorrecto(q);
  const rawOpts = q.opciones || q.opcoes || [];
  const letraCorrecta = indiceCorrecto !== null ? String.fromCharCode(65 + indiceCorrecto) : "A";
  const optCorrectaObj = normalizarOpcion(rawOpts[indiceCorrecto] || "");
  
  const seleccionValida = seleccionadaIdx !== null && seleccionadaIdx !== undefined && seleccionadaIdx >= 0;
  const letraSeleccionada = seleccionValida ? String.fromCharCode(65 + seleccionadaIdx) : null;
  const optSeleccionadaObj = seleccionValida ? normalizarOpcion(rawOpts[seleccionadaIdx] || "") : null;
  
  const esExito = esCorrecta === true || (seleccionValida && seleccionadaIdx === indiceCorrecto);

  // 1. Traducir el Enunciado (¿Qué está preguntando realmente?)
  const enunciadoTexto = q.pregunta || q.pergunta || "Enunciado de la consigna";
  const simplificacionEnunciado = q.joy?.preguntaSimplificada || `👉 ¿Cuál afirmación o mecanismo respecto a "${escaparHTML(tema)}" es la única correcta?`;

  // 2. Construcción Lógica del Mecanismo (Explicación conceptual profunda)
  const explicacionMecanismo = q.joy?.mecanismo || q.joy?.examen || q.justificativa || "En la Cátedra de La Plata, cada estructura biológica existe para cumplir una función específica. Comprender la secuencia permite deducir la respuesta sin memorizar números aislados.";

  // 3. Generación de las tarjetas de Opciones Analizadas una por una
  let analisisOpcionesHTML = "";
  
  rawOpts.forEach((optRaw, idx) => {
    const optNorm = normalizarOpcion(optRaw);
    const letra = String.fromCharCode(65 + idx);
    const esEstaCorrecta = (indiceCorrecto !== null && idx === indiceCorrecto);
    const esEstaSeleccionada = (seleccionValida && idx === seleccionadaIdx);
    
    let explicacionEspecifica = optNorm.explicacion || q.joy?.porQueNoCorrectas?.[idx] || "";
    
    if (esEstaCorrecta) {
      if (!explicacionEspecifica) {
        explicacionEspecifica = "En este estado/nivel el material genético o la estructura alcanza su condición exacta respondiendo 100% al enunciado.";
      }
    } else {
      if (!explicacionEspecifica) {
        explicacionEspecifica = "Esta opción contiene un término o localización errónea que altera el significado o invierte el orden del proceso.";
      }
    }

    analisisOpcionesHTML += `
      <div style="background: ${esEstaCorrecta ? 'rgba(16, 185, 129, 0.08)' : (esEstaSeleccionada ? 'rgba(239, 68, 68, 0.1)' : 'rgba(30, 41, 59, 0.4)')}; border: 1px solid ${esEstaCorrecta ? '#10b981' : (esEstaSeleccionada ? '#ef4444' : 'rgba(255, 255, 255, 0.08)')}; border-radius: 10px; padding: 1rem; margin-bottom: 0.85rem; transition: all 0.2s ease;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem; flex-wrap: wrap; gap: 0.5rem;">
          <div style="display: flex; align-items: center; gap: 0.6rem; font-weight: bold; font-size: 0.95rem;">
            <span style="background: ${esEstaCorrecta ? '#10b981' : (esEstaSeleccionada ? '#ef4444' : '#334155')}; color: #fff; width: 28px; height: 28px; display: inline-flex; align-items: center; justify-content: center; border-radius: 6px; font-size: 0.9rem;">${letra}</span>
            <span style="color: ${esEstaCorrecta ? '#34d399' : (esEstaSeleccionada ? '#f87171' : '#f1f5f9')}; font-size: 0.95rem;">${escaparHTML(optNorm.texto)}</span>
          </div>
          <span style="font-size: 0.8rem; font-weight: 800; padding: 4px 12px; border-radius: 20px; ${esEstaCorrecta ? 'background: rgba(16, 185, 129, 0.25); color: #34d399; border: 1px solid #10b981;' : (esEstaSeleccionada ? 'background: rgba(239, 68, 68, 0.25); color: #f87171; border: 1px solid #ef4444;' : 'background: rgba(255, 255, 255, 0.05); color: #94a3b8; border: 1px solid rgba(255, 255, 255, 0.1);')}">
            ${esEstaCorrecta ? '✔ Correcta' : (esEstaSeleccionada ? '❌ Tu elección (Incorrecta)' : '❌ Incorrecta')}
          </span>
        </div>
        
        <div style="font-size: 0.9rem; line-height: 1.5; color: ${esEstaCorrecta ? '#a7f3d0' : '#cbd5e1'}; margin-top: 0.5rem; padding-left: 0.6rem; border-left: 3px solid ${esEstaCorrecta ? '#10b981' : (esEstaSeleccionada ? '#ef4444' : '#475569')};">
          ${esEstaSeleccionada && !esEstaCorrecta ? `
            <div style="color: #fca5a5; font-weight: bold; margin-bottom: 0.3rem; font-size: 0.88rem;">
              💬 <strong>Profe Joy:</strong> Entiendo por qué elegiste esta opción. Tu razonamiento comenzó bien, pero aquí apareció la confusión:
            </div>
          ` : ''}
          ${escaparHTML(explicacionEspecifica)}
        </div>
      </div>
    `;
  });

  // 4. Pregunta Oral de la Cátedra UNLP
  const preguntaOralUNLP = q.joy?.preguntaOral || `Profe: Joyce, ¿cuál es el mecanismo fisiológico/estructural fundamental en ${escaparHTML(tema)}?`;
  const respuestaOralUNLP = q.joy?.respuestaOral || `Respuesta Método Profe Joy: La estructura y la función están acopladas. En la Cátedra de La Plata, se evalúa la capacidad de deducir la consecuencia a partir del principio biológico básico.`;

  return `
    <div class="joy-panel ${esExito ? 'joy-correct' : 'joy-incorrect'} animate-fade-in" style="margin-top: 1.5rem; border-radius: 14px; overflow: hidden; border: 1px solid ${esExito ? '#10b981' : '#ef4444'}; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
      
      <!-- 📌 CARD 1: ¿Qué está preguntando realmente el enunciado? -->
      <div style="background: #0f172a; padding: 1.25rem 1.5rem; border-bottom: 1px solid var(--border);">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.75rem; flex-wrap: wrap; gap: 0.5rem;">
          <span style="background: rgba(127, 0, 255, 0.2); color: #c084fc; font-weight: 800; font-size: 0.85rem; padding: 4px 14px; border-radius: 20px; border: 1px solid rgba(127, 0, 255, 0.4);">
            ✨ CORRECCIÓN RECONSTRUIDA PROFE JOY
          </span>
          <span style="font-size: 0.8rem; color: var(--cyan-neon); background: rgba(0, 229, 255, 0.1); padding: 4px 12px; border-radius: 20px; border: 1px solid rgba(0, 229, 255, 0.3);">
            ${escaparHTML(materia)} • ${escaparHTML(tp)}
          </span>
        </div>
        
        <h3 style="color: #f8fafc; font-size: 1.05rem; font-weight: bold; margin: 0 0 0.5rem 0; display: flex; align-items: center; gap: 0.5rem;">
          <span>📌</span> Primero... ¿qué está preguntando?
        </h3>
        <p style="color: #94a3b8; font-size: 0.92rem; margin: 0 0 0.75rem 0; font-style: italic; line-height: 1.4;">
          "${escaparHTML(enunciadoTexto)}"
        </p>
        <div style="background: rgba(0, 229, 255, 0.06); border: 1px solid rgba(0, 229, 255, 0.2); border-radius: 8px; padding: 0.75rem 1rem; color: #67e8f9; font-weight: 600; font-size: 0.92rem;">
          ${simplificacionEnunciado}
        </div>
      </div>

      <!-- 🧬 CARD 2: Construyamos la Lógica del Mecanismo -->
      <div style="background: #0b0f19; padding: 1.25rem 1.5rem; border-bottom: 1px solid var(--border);">
        <h4 style="color: #38bdf8; font-size: 1rem; font-weight: bold; margin: 0 0 0.6rem 0; display: flex; align-items: center; gap: 0.5rem;">
          <span>🧬</span> ¿Por qué funciona así? (El Mecanismo)
        </h4>
        <p style="color: #cbd5e1; font-size: 0.92rem; line-height: 1.55; margin: 0 0 1rem 0;">
          ${escaparHTML(explicacionMecanismo)}
        </p>
        
        <div style="background: rgba(127, 0, 255, 0.1); border: 1px solid rgba(127, 0, 255, 0.3); border-radius: 10px; padding: 1rem;">
          <strong style="color: #c084fc; font-size: 0.88rem; display: block; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.05em;">
            🔥 SECUENCIA FUNDAMENTAL PARA EL EXAMEN UNLP
          </strong>
          <div style="color: #e9d5ff; font-size: 0.9rem; line-height: 1.6; font-family: monospace;">
            ① ADN (Doble hélice)<br/>
            &nbsp;&nbsp;⬇<br/>
            ② Nucleosomas (Fibra de 11 nm) — <em>Primer Nivel</em><br/>
            &nbsp;&nbsp;⬇<br/>
            ③ Fibra de 30 nm — <em>Segundo Nivel</em><br/>
            &nbsp;&nbsp;⬇<br/>
            ④ Bucles / Loops<br/>
            &nbsp;&nbsp;⬇<br/>
            ⑤ Cromátidas<br/>
            &nbsp;&nbsp;⬇<br/>
            ⑥ Cromosoma Metafásico — <em>Máximo Nivel de Compactación</em>
          </div>
        </div>
      </div>

      <!-- 🔍 CARD 3: Ahora analicemos una por una -->
      <div style="background: #0f172a; padding: 1.25rem 1.5rem; border-bottom: 1px solid var(--border);">
        <h4 style="color: #f1f5f9; font-size: 1rem; font-weight: bold; margin: 0 0 1rem 0; display: flex; align-items: center; gap: 0.5rem;">
          <span>🔍</span> Ahora analicemos una por una:
        </h4>
        ${analisisOpcionesHTML}
      </div>

      <!-- 🎯 CARD 4: Respuesta Final, Perla Profe Joy y Pregunta Oral UNLP -->
      <div style="background: #0b0f19; padding: 1.25rem 1.5rem; display: flex; flex-direction: column; gap: 1.25rem;">
        
        <!-- Veredicto Final -->
        <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid #10b981; border-radius: 10px; padding: 1rem 1.25rem; text-align: center;">
          <div style="color: #34d399; font-size: 1.1rem; font-weight: 800; margin-bottom: 0.3rem;">
            🎯 Entonces la respuesta correcta es... ✅ ${letraCorrecta}
          </div>
          <div style="color: #a7f3d0; font-size: 0.95rem; font-weight: bold;">
            "${escaparHTML(optCorrectaObj.texto)}"
          </div>
        </div>

        <!-- 🧠 Perla Profe Joy -->
        <div style="background: linear-gradient(135deg, rgba(251, 191, 36, 0.1), rgba(245, 158, 11, 0.05)); border: 1px solid rgba(251, 191, 36, 0.4); border-radius: 10px; padding: 1rem 1.25rem;">
          <strong style="color: #fbbf24; font-size: 0.95rem; display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.4rem;">
            <span>🧠</span> Perla Profe Joy (para no olvidarte nunca)
          </strong>
          <p style="color: #fde68a; font-size: 0.9rem; line-height: 1.5; margin: 0;">
            Imaginá que vas guardando una cuerda muy larga: 🧵 ADN ⬇ 📿 Nucleosomas (11 nm) ⬇ 🧶 Fibra de 30 nm ⬇ ➰ Bucles ⬇ 📦 Cromátidas ⬇ 📚 Cromosoma metafásico.
          </p>
        </div>

        <!-- 🎓 Lo que preguntaría un profesor oral de la UNLP -->
        <div style="background: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 10px; padding: 1rem 1.25rem;">
          <strong style="color: #818cf8; font-size: 0.95rem; display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.4rem;">
            <span>🎓</span> Lo que preguntaría un profesor oral de la UNLP
          </strong>
          <p style="color: #c7d2fe; font-size: 0.9rem; font-weight: bold; margin: 0 0 0.4rem 0;">
            ${escaparHTML(preguntaOralUNLP)}
          </p>
          <p style="color: #e0e7ff; font-size: 0.88rem; line-height: 1.5; margin: 0; font-style: italic; background: rgba(0,0,0,0.3); padding: 0.6rem 0.8rem; border-radius: 6px;">
            ${escaparHTML(respuestaOralUNLP)}
          </p>
        </div>

        <!-- 💜 Mensaje Profe Joy -->
        <div style="color: #e0e7ff; font-size: 0.9rem; line-height: 1.5; text-align: center; border-top: 1px dashed rgba(255,255,255,0.1); padding-top: 0.85rem;">
          💜 <strong>No memorices datos aislados.</strong> Entendé la secuencia: cada nivel compacta más al ADN hasta llegar a la respuesta. Esa lógica te permite responder cualquier pregunta en el examen.
        </div>

      </div>

      <!-- Acciones de Navegación Didáctica -->
      <div class="joy-actions" style="padding: 1rem 1.5rem; background: #0f172a; border-top: 1px solid var(--border); display: flex; gap: 0.75rem; flex-wrap: wrap; justify-content: space-between;">
        <div style="display:flex; gap:0.5rem; flex-wrap:wrap;">
          <button class="btn-action-flashcard" onclick="crearFlashcard('${q.id}')" style="background: rgba(127, 0, 255, 0.2); color: #c084fc; border: 1px solid rgba(127, 0, 255, 0.4); padding: 8px 16px; border-radius: 6px; font-weight: 600; cursor: pointer;">
            ⚡ Crear Flashcard
          </button>
          <button class="btn-action-repaso" onclick="agregarRepaso('${q.id}')" style="background: rgba(0, 229, 255, 0.15); color: var(--cyan-neon); border: 1px solid rgba(0, 229, 255, 0.3); padding: 8px 16px; border-radius: 6px; font-weight: 600; cursor: pointer;">
            📌 Agregar a Repaso
          </button>
        </div>
        <a class="btn-action-biblio" href="https://www.conectafcm.com/biblioteca-virtual/965e8278-fa18-443d-8d0f-c00b1286f5b6" target="_blank" style="background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); padding: 8px 16px; border-radius: 6px; font-weight: 600; text-decoration: none; display: inline-flex; align-items: center; gap: 6px;">
          📖 Biblioteca Virtual
        </a>
      </div>

    </div>
  `;
}
"""

# Find start of generarPanelJoy and end of function in app.js
start_pos = app_js.find("function generarPanelJoy")
end_pos = app_js.find("function abrirFragmento")

app_js = app_js[:start_pos] + metodo_reconstruido_joy + "\n\n" + app_js[end_pos:]

with open("app.js", "w", encoding="utf-8") as f:
    f.write(app_js)

print("Corrección Reconstruida Profe Joy aplicada exitosamente a app.js.")
