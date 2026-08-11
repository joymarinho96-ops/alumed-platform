// ==========================================
// ALUMED OS - FUNCIONES HELPER PRINCIPALES
// ==========================================
function normalizarTexto(valor = "") {
  return String(valor)
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .trim()
    .toLowerCase();
}

function obtenerIndiceCorrecto(q) {
  if (!q) return null;
  const valor = q.correcta ?? q.correta;
  return (Number.isInteger(valor) && valor >= 0) ? valor : null;
}

function normalizarOpcion(opcion) {
  if (typeof opcion === "string") {
    return { texto: opcion, explicacion: "" };
  }

  return {
    texto:
      opcion?.texto ??
      opcion?.text ??
      opcion?.opcion ??
      opcion?.contenido ??
      opcion?.label ??
      "",
    explicacion:
      opcion?.explicacion ??
      opcion?.explanation ??
      ""
  };
}

const REGLAS_PARCIALES_UNLP = {
  biologia: {
    nombre: "Biología Celular (1er Parcial)",
    tiempoMinutos: 45,
    totalPreguntas: 10,
    minAprobado: 4,      // 4 o más aprueba
    minPromocion: 7,     // 7 o más promociona
    modalidad: "CHOICE"
  },
  histo_embrio: {
    nombre: "Histología y Embriología (1er Parcial)",
    tiempoMinutos: 40,
    totalPreguntas: 20, // 10 Histo + 10 Embrio
    minAprobado: 8,     // 8 globales aprueban
    minPromocionHisto: 7, // Requisito extra: 7 Histo y 7 Embrio la 1ra vez
    minPromocionEmbrio: 7,
    modalidad: "CHOICE"
  },
  anato_a: {
    nombre: "Anatomía Cátedra A (1er Parcial)",
    tiempoMinutos: 30,
    modalidad: "ORAL",
    partes: ["Contenidos Mínimos Obligatorios (CMO)", "Módulo Osteología"]
  },
  anato_b: {
    nombre: "Anatomía Cátedra B (1er Parcial - Pinches)",
    estaciones: 20,
    tiempoPorEstacionSegundos: 60, // 1 minuto por estación (20 min total)
    modalidad: "PINCHE_STATION",
    tablaNotas: [
      { min: 0, max: 9, nota: "Desaprobado" },
      { min: 10, max: 11, nota: "4 (Aprobado)" },
      { min: 12, max: 13, nota: "5" },
      { min: 14, max: 15, nota: "6" },
      { min: 16, max: 20, nota: "7+ (Promoción)" }
    ]
  },
  anato_c: {
    nombre: "Anatomía Cátedra C (1er Parcial)",
    modalidad: "CHOICE",
    temas: ["Aparato Locomotor", "Cabeza y Cuello", "Tórax"],
    minPromocion: 7,
    tiempoMinutos: 30,
    totalPreguntas: 10
  }
};

let estadoExamen = {
  modo: null,
  tiempoTotalSegundos: 0,
  tiempoRestante: 0,
  timerInterval: null,
  respuestasUsuario: {},
  materiaKey: null
};

function calcularNotaFinalUNLP(materiaKey, respuestasCorrectas, totalPreguntas) {
  const regla = REGLAS_PARCIALES_UNLP[materiaKey];
  
  if (materiaKey === 'biologia') {
    if (respuestasCorrectas >= regla.minPromocion) {
      return { estado: "PROMOCIONADO 🏆", color: "#10b981", mensaje: "¡Excelente! Lograste 7 o más aciertos." };
    } else if (respuestasCorrectas >= regla.minAprobado) {
      return { estado: "APROBADO 🟢", color: "#06b6d4", mensaje: "Aprobaste el parcial (4 o más aciertos)." };
    } else {
      return { estado: "DESAPROBADO 🔴", color: "#ef4444", mensaje: "Necesitas repasar para el recuperatorio." };
    }
  }

  if (materiaKey === 'anato_b') {
    const notaTabla = regla.tablaNotas.find(n => respuestasCorrectas >= n.min && respuestasCorrectas <= n.max);
    return {
      estado: `NOTA: ${notaTabla.nota}`,
      color: respuestasCorrectas >= 10 ? "#10b981" : "#ef4444",
      mensaje: `Respondiste correctamente ${respuestasCorrectas} de 20 pinches.`
    };
  }

  if (materiaKey === 'anato_c') {
    if (respuestasCorrectas >= regla.minPromocion) {
      return { estado: "PROMOCIONADO 🏆", color: "#10b981", mensaje: `Lograste ${respuestasCorrectas} aciertos.` };
    } else if (respuestasCorrectas >= 4) {
      return { estado: "APROBADO 🟢", color: "#06b6d4", mensaje: "Aprobaste el parcial." };
    } else {
      return { estado: "DESAPROBADO 🔴", color: "#ef4444", mensaje: "A seguir repasando." };
    }
  }

  if (materiaKey === 'histo_embrio') {
    // Simplificación para Histo hasta tener etiquetado detallado
    if (respuestasCorrectas >= 14) {
      return { estado: "PROMOCIONADO 🏆", color: "#10b981", mensaje: `Lograste ${respuestasCorrectas}/20 aciertos.` };
    } else if (respuestasCorrectas >= regla.minAprobado) {
      return { estado: "APROBADO 🟢", color: "#06b6d4", mensaje: `Aprobaste con ${respuestasCorrectas}/20.` };
    } else {
      return { estado: "DESAPROBADO 🔴", color: "#ef4444", mensaje: "Necesitas 8 aciertos globales." };
    }
  }
  
  return { estado: "FINALIZADO", color: "#6b7280", mensaje: `Aciertos: ${respuestasCorrectas}/${totalPreguntas}` };
}

function iniciarEntrenamientoPorTema(materiaKey, tpId) {
  estadoExamen.modo = "PRACTICA_TP";
  estadoExamen.materiaKey = materiaKey;
  clearInterval(estadoExamen.timerInterval);
  document.getElementById('examen-header').style.display = 'none';
  
  // Ocultar modal si estaba
  document.getElementById('resultados-modal').style.display = 'none';

  let filterStr = "";
  if(materiaKey === 'biologia') filterStr = 'Biología';
  if(materiaKey === 'histo_embrio') filterStr = 'Histología y Embriología';
  if(materiaKey === 'anato_a') filterStr = 'Anatomía Cátedra A';
  if(materiaKey === 'anato_b') filterStr = 'Anatomía Cátedra B';
  if(materiaKey === 'anato_c') filterStr = 'Anatomía Cátedra C';
  
  const navBtn = document.getElementById(`nav-${materiaKey.replace('_','')}`);
  
  let tabId = 'choices';
  if(materiaKey === 'anato_b') tabId = 'pinches';
  if(materiaKey === 'anato_a') tabId = 'oral';
  
  prepararEntrenamiento(tabId, filterStr, navBtn);
}

function iniciarSimulacroParcialReal(materiaKey) {
  const regla = REGLAS_PARCIALES_UNLP[materiaKey];
  estadoExamen.modo = "PARCIAL_REAL";
  estadoExamen.materiaKey = materiaKey;
  estadoExamen.respuestasUsuario = {};
  
  // UI setup
  document.getElementById('examen-header').style.display = 'flex';
  document.getElementById('examen-titulo').innerText = `⏱️ PARCIAL REAL: ${regla.nombre}`;
  document.getElementById('resultados-modal').style.display = 'none';
  
  // Timer setup
  if (regla.tiempoMinutos) {
    estadoExamen.tiempoTotalSegundos = regla.tiempoMinutos * 60;
  } else if (regla.estaciones) {
    estadoExamen.tiempoTotalSegundos = regla.estaciones * regla.tiempoPorEstacionSegundos;
  }
  estadoExamen.tiempoRestante = estadoExamen.tiempoTotalSegundos;
  
  clearInterval(estadoExamen.timerInterval);
  actualizarTimerUI();
  estadoExamen.timerInterval = setInterval(() => {
    estadoExamen.tiempoRestante--;
    actualizarTimerUI();
    if (estadoExamen.tiempoRestante <= 0) {
      clearInterval(estadoExamen.timerInterval);
      entregarParcialManualmente();
    }
  }, 1000);

  // Filter and randomize
  let filterStr = "";
  if(materiaKey === 'biologia') filterStr = 'Biología';
  if(materiaKey === 'histo_embrio') filterStr = 'Histología y Embriología';
  if(materiaKey === 'anato_a') filterStr = 'Anatomía Cátedra A';
  if(materiaKey === 'anato_b') filterStr = 'Anatomía Cátedra B';
  if(materiaKey === 'anato_c') filterStr = 'Anatomía Cátedra C';
  
  let tabId = (regla.modalidad === 'CHOICE' || regla.modalidad === 'ORAL') ? 'choices' : 'pinches';
  if(materiaKey === 'anato_a') tabId = 'oral';
  
  // Switch to the correct tab and filter
  const navBtn = document.getElementById(`nav-${materiaKey.replace('_','')}`);
  prepararEntrenamiento(tabId, filterStr, navBtn);
  
  // Limit questions to max amount
  
  // Excluir preguntas sin gabarito válido de los simulacros autocorregibles (Regla 5)
  filteredChoices = filteredChoices.filter(q => obtenerIndiceCorrecto(q) !== null);

  if (regla.totalPreguntas && filteredChoices.length > regla.totalPreguntas) {
      // Shuffle array
      filteredChoices = filteredChoices.sort(() => 0.5 - Math.random()).slice(0, regla.totalPreguntas);
      currentChoiceIndex = 0;
      if(tabId === 'choices') loadChoice();
  }
}

function actualizarTimerUI() {
  const m = Math.floor(estadoExamen.tiempoRestante / 60).toString().padStart(2, '0');
  const s = (estadoExamen.tiempoRestante % 60).toString().padStart(2, '0');
  document.getElementById('examen-timer').innerText = `${m}:${s}`;
}

function entregarParcialManualmente() {
  clearInterval(estadoExamen.timerInterval);
  document.getElementById('examen-header').style.display = 'none';
  
  let respuestasCorrectas = 0;
  let historialExamen = [];

  Object.keys(estadoExamen.respuestasUsuario).forEach(qId => {
    const resp = estadoExamen.respuestasUsuario[qId];
    const qObj = filteredChoices.find(q => q.id === qId);
    
    if (resp.esCorrecta) {
      respuestasCorrectas++;
    }
    
    if (qObj) {
      historialExamen.push({
        tpId: qObj.tpId || "TP1",
        esCorrecto: resp.esCorrecta,
        justificativa: qObj.joy?.examen || qObj.explicacion || qObj.justificativa || "",
        preguntaObj: qObj,
        respuestaSeleccionada: resp.elegida
      });
    }
  });
  
  const regla = REGLAS_PARCIALES_UNLP[estadoExamen.materiaKey] || {};
  const nota = calcularNotaFinalUNLP(estadoExamen.materiaKey, respuestasCorrectas, regla.totalPreguntas || regla.estaciones || filteredChoices.length);
  const diagnosticoHtml = generarInformeDiagnosticoUNLP(historialExamen, estadoExamen.materiaKey);
  
  document.getElementById('resultado-estado').innerText = nota.estado;
  document.getElementById('resultado-estado').style.color = nota.color;
  document.getElementById('resultado-mensaje').innerHTML = `
    <p style="font-size: 1.1rem; margin-bottom: 15px;">${nota.mensaje}</p>
    ${diagnosticoHtml}
  `;
  document.getElementById('resultados-modal').style.display = 'flex';
}

function cerrarResultados() {
  document.getElementById('resultados-modal').style.display = 'none';
}

// Toggle logic for the sidebar sub-menus
function toggleSubMenu(submenuId, btn) {
    document.querySelectorAll('.sub-menu').forEach(el => {
        if(el.id !== submenuId) el.style.display = 'none';
    });
    const sm = document.getElementById(submenuId);
    if(sm.style.display === 'none') {
        sm.style.display = 'flex';
    } else {
        sm.style.display = 'none';
    }
}


// ─────────────────────────────────────────────────────────────
//  UTILIDADES DE PRIVACIDAD
//  Nunca exponen archivo, página, ruta ni nombre real de fuente.
// ─────────────────────────────────────────────────────────────
function etiquetaFuentePublica(q) {
  const tipo = (q.tipoFuente || '').toLowerCase();
  if (tipo.includes('examen') || tipo.includes('parcial') ||
      tipo.includes('simulacro') || tipo.includes('recuperatorio')) {
    return 'Basada en examen anterior.';
  }
  return 'Explicación basada en materiales ALUMED.';
}



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

// ─────────────────────────────────────────────────────────────
//  NAVEGACIÓN DE ENTRENAMIENTO PARCIAL
// ─────────────────────────────────────────────────────────────
function prepararEntrenamiento(tabId, materiaSolicitada, btnEl) {
  try {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
    
    const sec = document.getElementById(`tab-${tabId}`);
    if (sec) sec.classList.add('active');
    if (btnEl) btnEl.classList.add('active');

    if (materiaSolicitada) {
      currentMateria = materiaSolicitada;
      
      const reqNorm = normalizarTexto(materiaSolicitada);
      
      filteredChoices = (bancoDados.choices || []).filter(q => {
        const matNorm = normalizarTexto(q.materia);
        const keyNorm = normalizarTexto(q.materiaKey);
        
        if (matNorm === reqNorm || keyNorm === reqNorm) return true;
        if (reqNorm.includes("biologia") && (matNorm.includes("biologia") || keyNorm.includes("biologia"))) return true;
        if (reqNorm.includes("histo") && (matNorm.includes("histo") || keyNorm.includes("histo"))) return true;
        if (reqNorm.includes("embrio") && (matNorm.includes("embrio") || keyNorm.includes("embrio"))) return true;
        if (reqNorm.includes("anato_a") || reqNorm.includes("catedra a")) return matNorm.includes("catedra a") || keyNorm === "anato_a";
        if (reqNorm.includes("anato_b") || reqNorm.includes("catedra b")) return matNorm.includes("catedra b") || keyNorm === "anato_b";
        if (reqNorm.includes("anato_c") || reqNorm.includes("catedra c")) return matNorm.includes("catedra c") || keyNorm === "anato_c";
        return false;
      });

      currentChoiceIndex = 0;

      if (filteredChoices.length === 0) {
        const elP = document.getElementById('mc-pergunta');
        if (elP) elP.textContent = "No se encontraron preguntas para esta materia";
        const elOp = document.getElementById('mc-opcoes');
        if (elOp) elOp.innerHTML = "";
        return;
      }

      if (tabId === 'choices' || tabId === 'oral') {
        loadChoice();
      }
      if (tabId === 'pinches') {
        loadPinche();
      }
    }
  } catch (err) {
    console.error("Error en prepararEntrenamiento:", err);
    const elP = document.getElementById('mc-pergunta');
    if (elP) elP.textContent = "No se pudieron filtrar las preguntas. Revisá la consola.";
  }
}

function loadChoice() {
  const q = filteredChoices[currentChoiceIndex];
  if (!q) return;

  yaValidado = false;
  selectedOption = null;

  // Header y pregunta
  document.getElementById('mc-materia-tag').innerText = `${q.materia || currentMateria} • ${q.tpPrincipal || 'TP1'}: ${q.tema || 'Tema General'}`;
  document.getElementById('mc-counter').innerText     = `Pregunta ${currentChoiceIndex + 1} de ${filteredChoices.length}`;
  document.getElementById('mc-pergunta').innerText = (q.pregunta ?? q.pergunta);

  // Limpiar feedback
  const fb = document.getElementById('mc-feedback');
  fb.className = 'feedback hidden';
  fb.innerHTML = '';

  // Opciones
  const container = document.getElementById('mc-opcoes');
  container.innerHTML = '';
  const btnValidar = document.getElementById('btn-validar');
  if (btnValidar) btnValidar.disabled = true; // Deshabilitado inicialmente

  ((q.opciones ?? q.opcoes) || []).forEach((opt, idx) => {
      const opcionNormalizada = normalizarOpcion(opt);
      console.log("OPCIÓN REAL:", opt);
      console.log("OPCIÓN NORMALIZADA:", opcionNormalizada);

      const btn = document.createElement('button');
      btn.className = 'option-btn';
      btn.id        = `opt-${idx}`;
      btn.setAttribute('role', 'radio');
      btn.setAttribute('aria-checked', 'false');
      
      const letra = typeof letraOpcion === 'function' ? letraOpcion(idx) : String.fromCharCode(65 + idx);

      btn.innerHTML = `
        <div class="option-content">
          <span class="option-letter">${letra}</span>
          <span class="option-text">${escaparHTML(opcionNormalizada.texto)}</span>
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
        if (btnValidar) btnValidar.disabled = false;
      };
      container.appendChild(btn);
    });
}

function validarChoice() {
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
  fb.innerHTML = generarPanelJoy(q, selectedOption, yaValidado ? (selectedOption === obtenerIndiceCorrecto(q)) : null);
  fb.className = 'feedback joy-active';

  // Scroll suave al feedback
  setTimeout(() => fb.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);
}

// ─────────────────────────────────────────────────────────────
//  GENERADOR PANEL PROFE JOY
// ─────────────────────────────────────────────────────────────

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


// ==========================================
// MÉTODO PROFE JOY — CORRECCIÓN RECONSTRUIDA
// "Primero comprender. Memorizar es la consecuencia."
// ==========================================

function generarPanelJoy(preguntaObj, seleccionadaIdx = null, esCorrecta = null) {
  const q = preguntaObj;
  const materia = q.materia || currentMateria || "Medicina UNLP";
  const tp = q.tpPrincipal || q.tp || "TP1";
  const tema = q.tema || "Tema General";
  
  const indiceCorrecto = obtenerIndiceCorrecto(q);
  const rawOpts = q.opciones || q.opcoes || [];
  const letraCorrecta = indiceCorrecto !== null ? String.fromCharCode(65 + indiceCorrecto) : "A";
  
  const seleccionValida = seleccionadaIdx !== null && seleccionadaIdx !== undefined && seleccionadaIdx >= 0;
  const esExito = esCorrecta === true || (seleccionValida && seleccionadaIdx === indiceCorrecto);

  // Error Diagnosis
  let diagnosticoErrorHTML = "";
  if (seleccionValida && !esExito) {
    const errorDiag = determinarTipoError(q, seleccionadaIdx);
    diagnosticoErrorHTML = `
      <div style="background: rgba(239, 68, 68, 0.15); border-left: 4px solid #ef4444; border-radius: 8px; padding: 1rem; margin-bottom: 1.5rem;">
        <h4 style="color: #f87171; font-size: 1rem; margin: 0 0 0.5rem 0; display: flex; align-items: center; gap: 0.5rem;">
          <span>${errorDiag.icono}</span> DIAGNÓSTICO DO SEU ERRO: ${errorDiag.tipo}
        </h4>
        <p style="color: #fecaca; font-size: 0.9rem; margin: 0 0 0.4rem 0;">${errorDiag.subtitulo}</p>
        <div style="color: #fca5a5; font-size: 0.85rem; font-style: italic;">👉 ${errorDiag.consejo}</div>
      </div>
    `;
  }

  // 1. O que a questão está realmente perguntando?
  const oQuePergunta = q.joy?.preguntaSimplificada || q.joy?.oquePergunta || `Qual característica ou conceito define "${escaparHTML(tema)}" neste cenário?`;

  // 2. Qual é a pista-chave?
  const pistaChave = q.joy?.pistaChave || "Identificar a relação entre a estrutura citada e a sua função primária no tecido.";

  // 3. Raciocínio
  const raciocinio = q.joy?.mecanismo || q.joy?.raciocinio || q.justificativa || "Analisando a pista, deduzimos que a estrutura se adapta para realizar esta função, descartando as outras opções.";

  // 4. Análise dos distratores
  let analisisOpcionesHTML = "";
  rawOpts.forEach((optRaw, idx) => {
    const optNorm = normalizarOpcion(optRaw);
    const letra = String.fromCharCode(65 + idx);
    const esEstaCorrecta = (indiceCorrecto !== null && idx === indiceCorrecto);
    const esEstaSeleccionada = (seleccionValida && idx === seleccionadaIdx);
    
    let explicacionEspecifica = optNorm.explicacion || q.joy?.porQueNoCorrectas?.[idx] || "";
    if (esEstaCorrecta) {
      explicacionEspecifica = explicacionEspecifica || "É a correta porque reúne as características exigidas pelo enunciado.";
    } else {
      explicacionEspecifica = explicacionEspecifica || "Pertence a outro conceito ou descreve uma estrutura diferente.";
    }

    analisisOpcionesHTML += `
      <div style="background: ${esEstaCorrecta ? 'rgba(16, 185, 129, 0.08)' : 'rgba(30, 41, 59, 0.4)'}; border: 1px solid ${esEstaCorrecta ? '#10b981' : 'rgba(255, 255, 255, 0.08)'}; border-radius: 8px; padding: 0.75rem 1rem; margin-bottom: 0.6rem;">
        <div style="display: flex; gap: 0.5rem; align-items: flex-start;">
          <strong style="color: ${esEstaCorrecta ? '#34d399' : '#f87171'}; min-width: 25px;">${esEstaCorrecta ? '✅' : '❌'} ${letra}</strong>
          <span style="color: #cbd5e1; font-size: 0.9rem;">${escaparHTML(explicacionEspecifica)}</span>
        </div>
      </div>
    `;
  });

  // 5. Regra Profe Joy
  const regra = q.joy?.regra || q.joy?.perla || `Sempre que pensar em ${escaparHTML(tema)}, associe diretamente à sua função principal.`;

  // 6. E se a prova mudasse isso?
  const eSe = q.joy?.eSe || `Se o enunciado mencionasse uma localização diferente, qual seria a resposta correta?`;

  return `
    <div class="joy-panel ${esExito ? 'joy-correct' : 'joy-incorrect'} animate-fade-in" style="margin-top: 1.5rem; border-radius: 14px; overflow: hidden; border: 1px solid ${esExito ? '#10b981' : '#ef4444'}; box-shadow: 0 10px 30px rgba(0,0,0,0.5); text-align: left;">
      
      <!-- Cabecera -->
      <div style="background: #0f172a; padding: 1.25rem 1.5rem; border-bottom: 1px solid var(--border);">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem;">
          <span style="background: rgba(127, 0, 255, 0.2); color: #c084fc; font-weight: 800; font-size: 0.85rem; padding: 4px 14px; border-radius: 20px; border: 1px solid rgba(127, 0, 255, 0.4);">
            ✨ CORREÇÃO PROFE JOY
          </span>
          <span style="font-size: 0.8rem; color: var(--cyan-neon); background: rgba(0, 229, 255, 0.1); padding: 4px 12px; border-radius: 20px; border: 1px solid rgba(0, 229, 255, 0.3);">
            ${escaparHTML(materia)}
          </span>
        </div>
        
        ${diagnosticoErrorHTML}
        
        <!-- 1. O que a questão está realmente perguntando? -->
        <h4 style="color: #f8fafc; font-size: 1rem; font-weight: bold; margin: 0 0 0.5rem 0;">🎯 1. O que a questão está realmente perguntando?</h4>
        <div style="background: rgba(0, 229, 255, 0.06); border: 1px solid rgba(0, 229, 255, 0.2); border-radius: 8px; padding: 0.75rem 1rem; color: #67e8f9; font-weight: 600; font-size: 0.92rem; margin-bottom: 1.25rem;">
          "${escaparHTML(oQuePergunta)}"
        </div>

        <!-- 2. Qual é a pista-chave? -->
        <h4 style="color: #f1f5f9; font-size: 1rem; font-weight: bold; margin: 0 0 0.5rem 0;">🔎 2. Qual é a pista-chave?</h4>
        <p style="color: #94a3b8; font-size: 0.95rem; margin: 0 0 1.25rem 0;">
          <strong>Pista:</strong> ${escaparHTML(pistaChave)}
        </p>

        <!-- 3. Raciocínio -->
        <h4 style="color: #38bdf8; font-size: 1rem; font-weight: bold; margin: 0 0 0.5rem 0;">🧩 3. Raciocínio</h4>
        <p style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.55; margin: 0 0 1.25rem 0;">
          ${escaparHTML(raciocinio)}
        </p>
      </div>

      <!-- 4. Análise dos distratores -->
      <div style="background: #0b0f19; padding: 1.25rem 1.5rem; border-bottom: 1px solid var(--border);">
        <h4 style="color: #f1f5f9; font-size: 1rem; font-weight: bold; margin: 0 0 1rem 0;">❌ 4. Por que as outras estão erradas?</h4>
        ${analisisOpcionesHTML}
      </div>

      <!-- 5. Regra Profe Joy & 6. E se... -->
      <div style="background: #0f172a; padding: 1.25rem 1.5rem; display: flex; flex-direction: column; gap: 1.25rem;">
        
        <!-- 5. Regra Profe Joy -->
        <div style="background: linear-gradient(135deg, rgba(251, 191, 36, 0.1), rgba(245, 158, 11, 0.05)); border: 1px solid rgba(251, 191, 36, 0.4); border-radius: 10px; padding: 1rem 1.25rem;">
          <h4 style="color: #fbbf24; font-size: 1rem; font-weight: bold; margin: 0 0 0.4rem 0;">🧠 5. Regra Profe Joy</h4>
          <p style="color: #fde68a; font-size: 0.95rem; line-height: 1.5; margin: 0; font-weight: 600;">
            ${escaparHTML(regra)}
          </p>
        </div>

        <!-- 6. E se a prova mudasse isso? -->
        <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 10px; padding: 1rem 1.25rem;">
          <h4 style="color: #f87171; font-size: 1rem; font-weight: bold; margin: 0 0 0.4rem 0;">🔥 6. E se a prova mudasse isso?</h4>
          <p style="color: #fecaca; font-size: 0.95rem; line-height: 1.5; margin: 0;">
            ${escaparHTML(eSe)}
          </p>
        </div>

      </div>
    </div>
  `;
}

// ==========================================================================
// MÓDULO ATLAS HISTOLÓGICO Y EMBRIOLÓGICO — ALUMED OS
// ==========================================================================
let estadoAtlas = {
  modulo: 'histo', // 'histo' | 'embrio'
  categoria: 'all',
  busqueda: '',
  preparadoActual: null,
  visorModo: 'static', // 'static' | 'live'
  pinEdicionTemp: { x: 50, y: 50 }
};

function initAtlas() {
  renderAtlasGrid();
}

function switchModuloAtlas(eje) {
  estadoAtlas.modulo = eje;
  document.getElementById('atlas-tab-histo').classList.toggle('active', eje === 'histo');
  document.getElementById('atlas-tab-embrio').classList.toggle('active', eje === 'embrio');
  renderAtlasGrid();
}

function filtrarAtlasCategoria(cat, btnEl) {
  estadoAtlas.categoria = cat;
  document.querySelectorAll('.atlas-cat-nav .nav-btn').forEach(btn => btn.classList.remove('active'));
  if (btnEl) btnEl.classList.add('active');
  renderAtlasGrid();
}

function buscarAtlas(query) {
  estadoAtlas.busqueda = normalizarTexto(query);
  renderAtlasGrid();
}

function renderAtlasGrid() {
  const container = document.getElementById('atlasGrid');
  if (!container) return;

  const dataset = window.ATLAS_HISTOLOGICO_DATA || bancoDados?.atlas || [];
  
  const filtrados = dataset.filter(item => {
    // Filtrar por módulo (histo/embrio)
    const matchModulo = (item.eje || 'histo') === estadoAtlas.modulo;
    
    // Filtrar por categoría
    const matchCat = estadoAtlas.categoria === 'all' || item.categoria === estadoAtlas.categoria;
    
    // Filtrar por búsqueda
    const textTarget = normalizarTexto(`${item.titulo} ${item.muestra} ${item.tp} ${item.clavesDiagnosticas?.join(' ')}`);
    const matchSearch = !estadoAtlas.busqueda || textTarget.includes(estadoAtlas.busqueda);
    
    return matchModulo && matchCat && matchSearch;
  });

  const badgeEl = document.getElementById('atlas-total-badge');
  if (badgeEl) badgeEl.textContent = `${filtrados.length} Microfotografías Virtuales`;

  if (filtrados.length === 0) {
    container.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--text-muted);">
        <i class="fa-solid fa-microscope" style="font-size: 3rem; opacity: 0.3; margin-bottom: 15px;"></i>
        <p>No se encontraron preparados que coincidan con los criterios de búsqueda.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = filtrados.map(item => `
    <div class="atlas-card" onclick="abrirAtlasModal('${item.id}')">
      <div class="atlas-card-img-wrap">
        <img src="${item.urlImagem || 'https://histologyguide.com/slideimages/MH-016x-small-intestine/04-slide-1.jpg'}" alt="${item.titulo}" loading="lazy" onerror="this.src='https://histologyguide.com/slideimages/MHS-281-pavement-epithelium/02-slide-1.jpg'">
        <span class="atlas-card-badge">${item.tp || 'TP UNLP'}</span>
        <span class="atlas-card-pins-badge"><i class="fa-solid fa-thumbtack"></i> ${item.pinches?.length || 0} Pins</span>
      </div>
      <div class="atlas-card-body">
        <h3 class="atlas-card-title">${item.titulo}</h3>
        <p class="atlas-card-specimen"><i class="fa-solid fa-vial"></i> ${item.muestra}</p>
        <div class="atlas-card-footer">
          <span style="font-size: 0.78rem; color: var(--cyan-neon); font-weight: 700;">
            <i class="fa-solid fa-eye"></i> Explorar Muestra
          </span>
          <i class="fa-solid fa-chevron-right" style="font-size: 0.8rem; color: var(--text-muted);"></i>
        </div>
      </div>
    </div>
  `).join('');
}

function abrirAtlasModal(id) {
  const dataset = window.ATLAS_HISTOLOGICO_DATA || bancoDados?.atlas || [];
  const item = dataset.find(s => s.id === id);
  if (!item) return;

  estadoAtlas.preparadoActual = item;

  document.getElementById('atlasModalCategory').textContent = item.tp;
  document.getElementById('atlasModalSlideTitle').textContent = item.titulo;
  
  const subHtml = `
    <div style="margin-top: 4px; font-size: 0.85rem; color: #cbd5e1;">
      <div><strong>Muestra:</strong> ${item.muestra}</div>
      ${item.nomenclaturaOficial ? `<div style="color: var(--cyan-neon); font-style: italic; margin-top:2px;"><strong>Nomenclatura Oficial:</strong> ${item.nomenclaturaOficial}</div>` : ''}
      ${item.tecnicaTincion ? `<div style="color: #ec4899; font-size: 0.8rem; margin-top:2px;"><strong>Técnica:</strong> ${item.tecnicaTincion}</div>` : ''}
    </div>
  `;
  document.getElementById('atlasModalSpecimen').innerHTML = subHtml;
  document.getElementById('atlasModalImg').src = item.urlImagem || '';
  document.getElementById('atlasExternalLink').href = item.enlaceVirtual || '#';

  // Render Claves Diagnósticas
  const clavesUl = document.getElementById('atlasClavesList');
  clavesUl.innerHTML = (item.clavesDiagnosticas || []).map(c => `<li>${c}</li>`).join('');

  // Render Pins / SelectView
  const pinsContainer = document.getElementById('atlasPinsContainer');
  const pinsList = document.getElementById('atlasPinsList');
  
  pinsContainer.innerHTML = (item.pinches || []).map(p => `
    <div class="pin-hotspot" style="left: ${p.x}%; top: ${p.y}%;" onclick="highlightPinAtlas(${p.pinId}, event)" title="${p.titulo}">
      ${p.pinId}
    </div>
  `).join('');

  pinsList.innerHTML = (item.pinches || []).map(p => `
    <div class="pin-item-card" id="pin-card-${p.pinId}" onclick="focusPinAtlas(${p.x}, ${p.y})">
      <div><strong>Pin ${p.pinId}: ${p.titulo || 'Estructura'}</strong></div>
      <div style="font-size: 0.85rem; margin-top: 4px; color: #cbd5e1;">${p.pergunta}</div>
      ${p.conceptoClave ? `<div style="font-size: 0.8rem; color: #34d399; margin-top: 4px;"><i class="fa-solid fa-lightbulb"></i> ${p.conceptoClave}</div>` : ''}
      ${p.trampaCatedra ? `<div style="font-size: 0.8rem; color: #fbbf24; margin-top: 4px;"><i class="fa-solid fa-triangle-exclamation"></i> ${p.trampaCatedra}</div>` : ''}
    </div>
  `).join('');

  // Render Accordion Preguntas Parcial
  const examContainer = document.getElementById('atlasExamQuestions');
  examContainer.innerHTML = (item.preguntasParcial || []).map((qObj, idx) => `
    <div class="exam-q-item">
      <div class="exam-q-header" onclick="toggleExamQAtlas(${idx})">
        <span><i class="fa-solid fa-circle-question" style="color: var(--cyan-neon); margin-right: 6px;"></i> ${qObj.q}</span>
        <i class="fa-solid fa-chevron-down" id="exam-arrow-${idx}"></i>
      </div>
      <div class="exam-q-body" id="exam-body-${idx}" style="display: none;">
        ${qObj.a}
      </div>
    </div>
  `).join('');

  setVisorAtlas('static');
  document.getElementById('atlasModal').style.display = 'flex';

  // Configurar capturador de coordenadas en la imagen para el Editor
  const canvas = document.getElementById('atlasCanvas');
  if (canvas) {
    canvas.onclick = (e) => {
      const rect = canvas.getBoundingClientRect();
      const x = Math.round(((e.clientX - rect.left) / rect.width) * 100);
      const y = Math.round(((e.clientY - rect.top) / rect.height) * 100);
      estadoAtlas.pinEdicionTemp = { x, y };
      const elX = document.getElementById('editorAtlasX');
      const elY = document.getElementById('editorAtlasY');
      if (elX) elX.textContent = `${x}.0%`;
      if (elY) elY.textContent = `${y}.0%`;
    };
  }
}

function setVisorAtlas(modo) {
  estadoAtlas.visorModo = modo;
  const staticBtn = document.getElementById('atlasTabStaticView');
  const liveBtn = document.getElementById('atlasTabLiveEmbed');
  const iframe = document.getElementById('atlasIframe');
  const bg = document.getElementById('atlasCanvasBg');
  const pins = document.getElementById('atlasPinsContainer');

  if (modo === 'live') {
    if (staticBtn) staticBtn.classList.remove('active');
    if (liveBtn) liveBtn.classList.add('active');
    if (iframe) {
      iframe.src = estadoAtlas.preparadoActual?.enlaceVirtual || 'about:blank';
      iframe.classList.remove('hidden');
    }
    if (bg) bg.style.display = 'none';
    if (pins) pins.style.display = 'none';
  } else {
    if (liveBtn) liveBtn.classList.remove('active');
    if (staticBtn) staticBtn.classList.add('active');
    if (iframe) iframe.classList.add('hidden');
    if (bg) bg.style.display = 'block';
    if (pins) pins.style.display = 'block';
  }
}

function cerrarAtlasModal() {
  const modal = document.getElementById('atlasModal');
  if (modal) modal.style.display = 'none';
  const iframe = document.getElementById('atlasIframe');
  if (iframe) iframe.src = 'about:blank';
}

function toggleExamQAtlas(idx) {
  const body = document.getElementById(`exam-body-${idx}`);
  const arrow = document.getElementById(`exam-arrow-${idx}`);
  if (body) {
    if (body.style.display === 'none') {
      body.style.display = 'block';
      if (arrow) arrow.className = 'fa-solid fa-chevron-up';
    } else {
      body.style.display = 'none';
      if (arrow) arrow.className = 'fa-solid fa-chevron-down';
    }
  }
}

function highlightPinAtlas(pinId, event) {
  if (event) event.stopPropagation();
  document.querySelectorAll('.pin-item-card').forEach(el => el.style.borderColor = 'var(--border)');
  const target = document.getElementById(`pin-card-${pinId}`);
  if (target) {
    target.style.borderColor = '#ec4899';
    target.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
}

function focusPinAtlas(x, y) {
  console.log(`Pin coords: X=${x}%, Y=${y}%`);
}

function abrirEditorPinsAtlas() {
  const drawer = document.getElementById('atlasEditorDrawer');
  if (drawer) drawer.style.display = 'block';
}

function cerrarEditorAtlas() {
  const drawer = document.getElementById('atlasEditorDrawer');
  if (drawer) drawer.style.display = 'none';
}

function guardarPinAtlas() {
  const item = estadoAtlas.preparadoActual;
  if (!item) return;

  const tituloEl = document.getElementById('editorAtlasTitulo');
  const pregEl = document.getElementById('editorAtlasPregunta');
  const claveEl = document.getElementById('editorAtlasClave');

  const titulo = tituloEl ? tituloEl.value.trim() : '';
  const pregunta = pregEl ? pregEl.value.trim() : '';
  const clave = claveEl ? claveEl.value.trim() : '';

  if (!titulo || !pregunta) {
    alert('Por favor completa el nombre y la pregunta para el nuevo pin.');
    return;
  }

  const nuevoPin = {
    pinId: (item.pinches?.length || 0) + 1,
    x: estadoAtlas.pinEdicionTemp.x,
    y: estadoAtlas.pinEdicionTemp.y,
    titulo: titulo,
    pergunta: pregunta,
    conceptoClave: clave
  };

  item.pinches = item.pinches || [];
  item.pinches.push(nuevoPin);

  cerrarEditorAtlas();
  abrirAtlasModal(item.id);

  const toast = document.getElementById('alumed-toast');
  if (toast) {
    toast.textContent = '¡Pin guardado exitosamente!';
    toast.style.display = 'block';
    setTimeout(() => { toast.style.display = 'none'; }, 3000);
  }
}

// ==========================================================================
// MÓDULO VISTA DIVIDIDA (ATLAS + SIMULADOR LADO A LADO) — ALUMED OS
// ==========================================================================
let estadoSplit = {
  modulo: 'histo', // 'histo' | 'embrio'
  categoria: 'all',
  busqueda: '',
  preparadoActualId: null,
  choiceIndex: 0,
  choicesFiltrados: [],
  selectedOption: null,
  yaValidado: false
};

function initVistaDividida() {
  switchModuloSplit(estadoSplit.modulo || 'histo');
}

function switchModuloSplit(eje) {
  estadoSplit.modulo = eje;
  estadoSplit.choiceIndex = 0;
  estadoSplit.selectedOption = null;
  estadoSplit.yaValidado = false;

  // Tab buttons active states
  const histoTab = document.getElementById('split-tab-histo');
  const embrioTab = document.getElementById('split-tab-embrio');
  if (histoTab) histoTab.classList.toggle('active', eje === 'histo');
  if (embrioTab) embrioTab.classList.toggle('active', eje === 'embrio');

  // Update status badge
  const statusBadge = document.getElementById('split-status-badge');
  if (statusBadge) {
    statusBadge.textContent = `Módulo: ${eje === 'histo' ? 'Histología' : 'Embriología'}`;
    statusBadge.style.color = eje === 'histo' ? '#67e8f9' : '#f472b6';
  }

  // Filter choices for the selected subject
  const targetMateria = eje === 'histo' ? 'histo' : 'embrio';
  estadoSplit.choicesFiltrados = (bancoDados?.choices || []).filter(q => {
    const mat = normalizarTexto(q.materia || '');
    const tp = normalizarTexto(q.tp || '');
    return mat.includes(targetMateria) || tp.includes(targetMateria);
  });

  // Filter Atlas slides
  renderSplitAtlasGrid();

  // Render Simulator choice question
  renderSplitChoice();
}

function filtrarSplitCategoria(cat, btnEl) {
  estadoSplit.categoria = cat;
  document.querySelectorAll('[data-split-cat]').forEach(btn => btn.classList.remove('active'));
  if (btnEl) btnEl.classList.add('active');
  renderSplitAtlasGrid();
}

function buscarSplitAtlas(query) {
  estadoSplit.busqueda = normalizarTexto(query);
  renderSplitAtlasGrid();
}

function renderSplitAtlasGrid() {
  const container = document.getElementById('splitAtlasGrid');
  if (!container) return;

  const dataset = window.ATLAS_HISTOLOGICO_DATA || bancoDados?.atlas || [];
  
  const filtrados = dataset.filter(item => {
    const matchModulo = (item.eje || 'histo') === estadoSplit.modulo;
    const matchCat = estadoSplit.categoria === 'all' || item.categoria === estadoSplit.categoria;
    const textTarget = normalizarTexto(`${item.titulo} ${item.muestra} ${item.tp} ${item.clavesDiagnosticas?.join(' ')}`);
    const matchSearch = !estadoSplit.busqueda || textTarget.includes(estadoSplit.busqueda);
    return matchModulo && matchCat && matchSearch;
  });

  const countBadge = document.getElementById('split-atlas-count');
  if (countBadge) countBadge.textContent = `${filtrados.length} Preparados`;

  if (filtrados.length === 0) {
    container.innerHTML = `<p style="grid-column:1/-1; text-align:center; padding:15px; color:var(--text-muted); font-size:0.85rem;">No hay preparados disponibles.</p>`;
    return;
  }

  if (!estadoSplit.preparadoActualId || !filtrados.some(x => x.id === estadoSplit.preparadoActualId)) {
    if (filtrados.length > 0) {
      seleccionarSplitSlide(filtrados[0].id);
    }
  }

  container.innerHTML = filtrados.map(item => `
    <div class="atlas-card ${item.id === estadoSplit.preparadoActualId ? 'active-slide-card' : ''}" 
         onclick="seleccionarSplitSlide('${item.id}')" 
         style="padding: 8px; font-size: 0.8rem; background: ${item.id === estadoSplit.preparadoActualId ? 'rgba(0, 229, 255, 0.15)' : 'rgba(30,41,59,0.5)'}; border: 1px solid ${item.id === estadoSplit.preparadoActualId ? 'var(--cyan-neon)' : 'rgba(255,255,255,0.1)'}; border-radius: 8px;">
      <div style="font-weight:700; color:#fff; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${item.titulo}</div>
      <div style="font-size:0.72rem; color:var(--text-muted);">${item.tp || 'TP UNLP'}</div>
    </div>
  `).join('');
}

function seleccionarSplitSlide(id) {
  const dataset = window.ATLAS_HISTOLOGICO_DATA || bancoDados?.atlas || [];
  const item = dataset.find(s => s.id === id);
  if (!item) return;

  estadoSplit.preparadoActualId = id;

  document.getElementById('splitSlideTp').textContent = item.tp || 'TP UNLP';
  document.getElementById('splitSlideTitle').textContent = item.titulo;
  document.getElementById('splitSlideSpecimen').textContent = `Muestra: ${item.muestra}`;
  document.getElementById('splitSlideImg').src = item.urlImagem || 'https://histologyguide.com/slideimages/MHS-281-pavement-epithelium/02-slide-1.jpg';
  document.getElementById('splitExternalLink').href = item.enlaceVirtual || '#';

  const clavesUl = document.getElementById('splitClavesList');
  if (clavesUl) {
    clavesUl.innerHTML = (item.clavesDiagnosticas || []).map(c => `<li>${c}</li>`).join('');
  }

  const pinsContainer = document.getElementById('splitPinsContainer');
  if (pinsContainer) {
    pinsContainer.innerHTML = (item.pinches || []).map(p => `
      <div class="pin-hotspot" style="left: ${p.x}%; top: ${p.y}%; font-size:0.75rem; width:20px; height:20px; line-height:20px;" title="${p.titulo}">
        ${p.pinId}
      </div>
    `).join('');
  }

  renderSplitAtlasGrid();
}

function renderSplitChoice() {
  const list = estadoSplit.choicesFiltrados;
  const counterEl = document.getElementById('split-choice-counter');
  const materiaTag = document.getElementById('split-mc-materia-tag');
  const temaTag = document.getElementById('split-mc-tema');
  const pregEl = document.getElementById('split-mc-pregunta');
  const container = document.getElementById('split-mc-opcoes');
  const fb = document.getElementById('split-mc-feedback');
  const btnValidar = document.getElementById('split-btn-validar');

  if (!list || list.length === 0) {
    if (counterEl) counterEl.textContent = '0 Preguntas';
    if (pregEl) pregEl.textContent = 'No hay preguntas disponibles para este módulo.';
    if (container) container.innerHTML = '';
    if (fb) fb.innerHTML = '';
    return;
  }

  const q = list[estadoSplit.choiceIndex];
  if (!q) return;

  estadoSplit.yaValidado = false;
  estadoSplit.selectedOption = null;

  if (counterEl) counterEl.textContent = `Pregunta ${estadoSplit.choiceIndex + 1} de ${list.length}`;
  if (materiaTag) materiaTag.textContent = q.materia || (estadoSplit.modulo === 'histo' ? 'Histología' : 'Embriología');
  if (temaTag) temaTag.textContent = `${q.tpPrincipal || 'TP'}: ${q.tema || 'Tema General'}`;
  if (pregEl) {
    pregEl.textContent = q.pregunta || q.pergunta || '';
    if (q.imagem) {
      const imgHtml = `<img src="${q.imagem}" alt="Imagen adjunta a la pregunta" style="max-width: 100%; border-radius: 8px; margin-top: 15px; border: 1px solid var(--border);">`;
      pregEl.innerHTML += imgHtml;
    }
  }

  if (fb) {
    fb.className = 'feedback hidden';
    fb.innerHTML = '';
  }

  if (btnValidar) btnValidar.disabled = true;

  if (container) {
    container.innerHTML = '';
    const rawOpts = q.opciones || q.opcoes || [];
    rawOpts.forEach((opt, idx) => {
      const optNorm = normalizarOpcion(opt);
      const btn = document.createElement('button');
      btn.className = 'option-btn';
      btn.style.cssText = 'padding: 10px 14px; font-size: 0.9rem; margin-bottom: 6px; border-radius: 8px;';
      btn.innerHTML = `
        <span class="option-letter" style="background: rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 4px; font-weight:700; margin-right: 8px;">${letraOpcion(idx)}</span>
        <span class="option-text">${escaparHTML(optNorm.texto)}</span>
      `;

      btn.onclick = () => {
        if (estadoSplit.yaValidado) return;
        document.querySelectorAll('#split-mc-opcoes .option-btn').forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');
        estadoSplit.selectedOption = idx;
        if (btnValidar) btnValidar.disabled = false;
      };

      container.appendChild(btn);
    });
  }
}

function validarChoiceSplit() {
  const list = estadoSplit.choicesFiltrados;
  const q = list[estadoSplit.choiceIndex];
  if (!q || estadoSplit.selectedOption === null || estadoSplit.yaValidado) return;

  estadoSplit.yaValidado = true;
  
  // Dynamic Diagnostic Logging
  
  if (!estadoSplit.stats) estadoSplit.stats = { totalRespuestas: 0, correctas: 0, racha: 0, maxRacha: 0, temasErrados: {} };
  estadoSplit.stats.totalRespuestas++;
  const esCorrecta = (obtenerIndiceCorrecto(q) === estadoSplit.selectedOption);
  if (esCorrecta) {
    estadoSplit.stats.correctas++;
    estadoSplit.stats.racha++;
    if (estadoSplit.stats.racha > estadoSplit.stats.maxRacha) estadoSplit.stats.maxRacha = estadoSplit.stats.racha;
  } else {
    estadoSplit.stats.racha = 0;
    const t = q.tema || q.tp || "General";
    estadoSplit.stats.temasErrados[t] = (estadoSplit.stats.temasErrados[t] || 0) + 1;
  }

  if (!esCorrecta) {
    const errorDiag = determinarTipoError(q, estadoSplit.selectedOption);
    const tipoCod = errorDiag.tipo.toLowerCase().includes("conceptual") ? "conceptual" 
                  : errorDiag.tipo.toLowerCase().includes("interpretación") ? "interpretacion" 
                  : errorDiag.tipo.toLowerCase().includes("asociación") ? "asociacion" : "memoria";
                  
    if (estadoSplit.diagnostico) {
      estadoSplit.diagnostico.historialErrores[tipoCod] = (estadoSplit.diagnostico.historialErrores[tipoCod] || 0) + 1;
      estadoSplit.diagnostico.temaFoco = q.tema || q.tp || null;
      estadoSplit.diagnostico.ultimoError = errorDiag.tipo;
      estadoSplit.diagnostico.mostrarAlertaReencuadre = true;
    }
  } else {
    if (estadoSplit.diagnostico && estadoSplit.diagnostico.temaFoco === (q.tema || q.tp)) {
        estadoSplit.diagnostico.temaFoco = null; // Mastered the focal point
    }
    if(estadoSplit.diagnostico) estadoSplit.diagnostico.mostrarAlertaReencuadre = false;
  }

  const fb = document.getElementById('split-mc-feedback');
  if (fb) {
    fb.innerHTML = generarPanelJoy(q, estadoSplit.selectedOption, esCorrecta);
    fb.className = 'feedback joy-active';
  }
}

function prevChoiceSplit() {
  if (estadoSplit.choiceIndex > 0) {
    estadoSplit.choiceIndex--;
    renderSplitChoice();
  }
}

function nextChoiceSplit() {
  if (estadoSplit.choiceIndex < estadoSplit.choicesFiltrados.length - 1) {
    
    // ALUMED OS - Motor de Reencuadre Dinámico
    if (estadoSplit.diagnostico && estadoSplit.diagnostico.temaFoco && estadoSplit.diagnostico.mostrarAlertaReencuadre) {
        // Buscar la próxima pregunta del mismo tema
        const currentIndex = estadoSplit.choiceIndex;
        let foundIndex = -1;
        for (let i = currentIndex + 1; i < estadoSplit.choicesFiltrados.length; i++) {
            const tempQ = estadoSplit.choicesFiltrados[i];
            if ((tempQ.tema && tempQ.tema === estadoSplit.diagnostico.temaFoco) || (tempQ.tp && tempQ.tp === estadoSplit.diagnostico.temaFoco)) {
                foundIndex = i;
                break;
            }
        }
        
        if (foundIndex !== -1 && foundIndex !== currentIndex + 1) {
            // Mover la pregunta encontrada al slot siguiente
            const qToMove = estadoSplit.choicesFiltrados.splice(foundIndex, 1)[0];
            estadoSplit.choicesFiltrados.splice(currentIndex + 1, 0, qToMove);
        }
        
        estadoSplit.diagnostico.mostrarAlertaReencuadre = false; // Solo mostramos una vez tras el error
        
        // Inyectamos una alerta temporal visual en el UI
        setTimeout(() => {
            const container = document.getElementById('split-mc-pergunta');
            if(container) {
                const banner = document.createElement('div');
                banner.style.cssText = "background: rgba(127, 0, 255, 0.15); border: 1px solid rgba(127, 0, 255, 0.4); border-radius: 8px; padding: 1rem; margin-bottom: 1rem; animation: fadeIn 0.5s;";
                banner.innerHTML = `
                    <div style="color: #c084fc; font-weight: bold; font-size: 0.95rem; margin-bottom: 4px;">
                        <i class="fa-solid fa-microchip"></i> ALUMED OS | DIAGNÓSTICO ACTIVO
                    </div>
                    <div style="color: #e9d5ff; font-size: 0.9rem;">
                        Detectamos un <strong>${estadoSplit.diagnostico.ultimoError}</strong> en "${estadoSplit.diagnostico.temaFoco}". 
                        Hemos modificado tu examen en tiempo real y seleccionado esta pregunta específica para ayudarte a consolidar el concepto antes de avanzar.
                    </div>
                `;
                container.parentNode.insertBefore(banner, container);
            }
        }, 100);
    }

    estadoSplit.choiceIndex++;
    renderSplitChoice();
  }
}

// ==========================================
// INICIALIZACIÓN UNIFICADA CON TRY/CATCH Y LOGS EXPLICITOS
// ==========================================
document.addEventListener("DOMContentLoaded", () => {
  try {
    if (typeof bancoDados === "undefined") {
      throw new Error("bancoDados no está disponible en el entorno global");
    }

    console.log("Banco cargado exitosamente", {
      choices: bancoDados.choices?.length || 0,
      orales: bancoDados.orales?.length || 0,
      pinches: bancoDados.pinches?.length || 0
    });

    // Default Homepage view: Dual Split View (Simulador + Atlas Lado a Lado)
    const simBtn = document.getElementById("nav-simulador") || document.getElementById("nav-split");
    prepararEntrenamiento("split", null, simBtn);
    initVistaDividida();
  } catch (error) {
    console.error("Error al inicializar el simulador:", error);

    const pregunta = document.getElementById("mc-pergunta");
    if (pregunta) {
      pregunta.textContent =
        "No se pudo cargar el banco de preguntas. Revisá la consola.";
    }
  }
});



// ==========================================
// MÓDULO DASHBOARD / DIAGNÓSTICO
// ==========================================

// Inicializar estadísticas si no existen
if (!estadoSplit.stats) {
  estadoSplit.stats = { totalRespuestas: 0, correctas: 0, racha: 0, maxRacha: 0, temasErrados: {} };
}

function abrirDashboard(btn) {
  // Manejo de tabs
  document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  
  document.getElementById('tab-dashboard').classList.add('active');
  if(btn) btn.classList.add('active');
  
  renderDashboard();
}






// --- ALUMED DIAGNOSTIC DASHBOARD LOGIC ---

function carregarDiagnostico() {
  try {
    const saved = localStorage.getItem('alumed_diagnostico');
    if (saved) {
      const parsed = JSON.parse(saved);
      if (parsed.stats && parsed.diagnostico) {
        estadoSplit.stats = parsed.stats;
        estadoSplit.diagnostico = parsed.diagnostico;
      }
    }
  } catch (e) {
    console.error("Erro ao carregar diagnostico", e);
  }
}

function salvarDiagnostico() {
  try {
    const dataToSave = {
      stats: estadoSplit.stats,
      diagnostico: estadoSplit.diagnostico
    };
    localStorage.setItem('alumed_diagnostico', JSON.stringify(dataToSave));
  } catch (e) {
    console.error("Erro ao salvar diagnostico", e);
  }
}

function resetarDiagnostico() {
  if(confirm("¿Estás seguro de que quieres borrar todo tu historial cognitivo? Esto no se puede deshacer.")) {
    localStorage.removeItem('alumed_diagnostico');
    estadoSplit.stats = { correctas: 0, incorrectas: 0, totalRespuestas: 0, racha: 0, temasErrados: {}, tiempos: [] };
    estadoSplit.diagnostico = { historialErrores: { conceptual: 0, interpretacion: 0, asociacion: 0, memoria: 0 } };
    renderDashboard();
    alert("Historial reiniciado correctamente.");
  }
}

function renderDashboard() {
  const stats = estadoSplit.stats;
  const diag = estadoSplit.diagnostico?.historialErrores || { conceptual: 0, interpretacion: 0, asociacion: 0, memoria: 0 };
  
  const totalResp = stats.totalRespuestas || 0;
  
  // Empty State Logic
  const emptyState = document.getElementById('dash-empty-state');
  const contentState = document.getElementById('dash-content-state');
  
  if (totalResp === 0) {
    if (emptyState) emptyState.style.display = 'flex';
    if (contentState) contentState.style.display = 'none';
    return;
  } else {
    if (emptyState) emptyState.style.display = 'none';
    if (contentState) contentState.style.display = 'block';
  }
  
  // Calcular KPI Globales
  const precision = totalResp > 0 ? Math.round((stats.correctas / totalResp) * 100) : 0;
  
  // Tiempo Medio
  let avgTime = 0;
  if (stats.tiempos && stats.tiempos.length > 0) {
    const sum = stats.tiempos.reduce((a, b) => a + b, 0);
    avgTime = Math.round(sum / stats.tiempos.length);
  }
  
  // Mejor Materia / Tema
  let bestSubject = "-";
  // (Lógica simplificada: aquí se podría trackear temas correctos, por ahora mostramos un placeholder)
  bestSubject = "Histología"; 
  
  const elAccuracy = document.getElementById('dash-accuracy');
  if(elAccuracy) elAccuracy.innerText = precision + '%';
  const elTotalQ = document.getElementById('dash-total-q');
  if(elTotalQ) elTotalQ.innerText = totalResp;
  const elStreak = document.getElementById('dash-streak');
  if(elStreak) elStreak.innerText = stats.racha || 0;
  const elAvgTime = document.getElementById('dash-avg-time');
  if(elAvgTime) elAvgTime.innerText = avgTime + 's';
  const elBestSubject = document.getElementById('dash-best-subject');
  if(elBestSubject) elBestSubject.innerText = bestSubject;

  // Calcular Perfil Cognitivo
  const totalErrores = diag.conceptual + diag.interpretacion + diag.asociacion + diag.memoria;
  const pConcept = totalErrores > 0 ? Math.round((diag.conceptual / totalErrores) * 100) : 0;
  const pAsoc = totalErrores > 0 ? Math.round((diag.asociacion / totalErrores) * 100) : 0;
  const pInterp = totalErrores > 0 ? Math.round((diag.interpretacion / totalErrores) * 100) : 0;
  const pMem = totalErrores > 0 ? Math.round((diag.memoria / totalErrores) * 100) : 0;

  const barConcept = document.getElementById('bar-conceptual');
  if(barConcept) barConcept.style.width = pConcept + '%';
  const lblConcept = document.getElementById('lbl-conceptual');
  if(lblConcept) lblConcept.innerText = pConcept + '%';
  
  const barAsoc = document.getElementById('bar-asociacion');
  if(barAsoc) barAsoc.style.width = pAsoc + '%';
  const lblAsoc = document.getElementById('lbl-asociacion');
  if(lblAsoc) lblAsoc.innerText = pAsoc + '%';
  
  const barInterp = document.getElementById('bar-interpretacion');
  if(barInterp) barInterp.style.width = pInterp + '%';
  const lblInterp = document.getElementById('lbl-interpretacion');
  if(lblInterp) lblInterp.innerText = pInterp + '%';
  
  const barMem = document.getElementById('bar-memoria');
  if(barMem) barMem.style.width = pMem + '%';
  const lblMem = document.getElementById('lbl-memoria');
  if(lblMem) lblMem.innerText = pMem + '%';

  // Temas Críticos
  const temas = stats.temasErrados || {};
  const temasList = document.getElementById('dash-temas-criticos');
  if (temasList) {
    if (Object.keys(temas).length > 0) {
      const sorted = Object.entries(temas).sort((a, b) => b[1] - a[1]).slice(0, 3);
      temasList.innerHTML = sorted.map(t => `<li><span>${t[0]}</span> <span style="color: #ef4444; font-weight: bold;">${t[1]} fallos</span></li>`).join('');
    } else {
      temasList.innerHTML = '<li><i class="fa-solid fa-check" style="color: #34d399; margin-right:6px;"></i> ¡Todo excelente! No hay temas críticos.</li>';
    }
  }
}

function iniciarReentrenamiento(tipoFiltro = 'auto') {
  const temas = estadoSplit.stats?.temasErrados || {};
  if (Object.keys(temas).length === 0 && tipoFiltro === 'auto') {
    alert("Todavía no tienes errores registrados para armar un re-entrenamiento automático.");
    return;
  }
  
  let pool = bancoDados.choices || [];
  let filtradas = [];
  
  if (tipoFiltro === 'auto') {
    const peoresTemas = Object.entries(temas).sort((a, b) => b[1] - a[1]).map(t => t[0]);
    filtradas = pool.filter(q => peoresTemas.includes(q.tema));
  } else {
    // Filtrar por tag de error específico (si existiese) o devolver un random
    // Por simplicidad, tomamos 10 aleatorias para simular el refuerzo de ese tipo
    filtradas = pool.sort(() => 0.5 - Math.random()); 
  }
  
  // Limitar a 10
  filtradas = filtradas.sort(() => 0.5 - Math.random()).slice(0, 10);
  
  if (filtradas.length === 0) {
    alert("No se encontraron suficientes preguntas para ese filtro.");
    return;
  }
  
  estadoSplit.choicesFiltrados = filtradas;
  estadoSplit.indexAtual = 0;
  
  document.getElementById('nav-simulador').click();
  prepararEntrenamiento();
}

// Inicializar carga de persistencia al abrir
document.addEventListener('DOMContentLoaded', () => {
  carregarDiagnostico();
});

// --- FIN ALUMED DIAGNOSTIC DASHBOARD LOGIC ---


// --- ALUMED ESTATUTO SEARCH ENGINE LOGIC ---

const ESTATUTO_DATA = [
  {
    id: "regla_1",
    titulo: "¿Cómo apruebo la ERA 1?",
    tags: ["#Regulamento", "#Exámenes"],
    tipo: "regla",
    contenido: "Para aprobar la Evaluación de Rendimiento Académico (ERA) 1, necesitas alcanzar el 60% del puntaje total en el examen Choice. Asegúrate de practicar con los simulacros de ALUMED."
  },
  {
    id: "prob_1",
    titulo: "Reprobé la ERA 1, ¿qué hago ahora?",
    tags: ["#Soluciones", "#Exámenes", "#Recuperatorio"],
    tipo: "solucion",
    contenido: "No te preocupes. Tienes derecho a un recuperatorio al final del cuatrimestre. Te recomendamos revisar el 'Diagnóstico Cognitivo' en tu panel de ALUMED para ver en qué temas fallaste más y lanzar un simulacro enfocado."
  },
  {
    id: "regla_2",
    titulo: "¿Cómo funciona la puntuación del Atlas?",
    tags: ["#Atlas", "#DudasFrecuentes"],
    tipo: "alerta",
    contenido: "El Atlas Histológico no suma nota directa para la ERA, pero los preparados que identificas incorrectamente se restan de tu racha de precisión. Es vital para entrenar tu reconocimiento visual."
  },
  {
    id: "prob_2",
    titulo: "Siento que olvido rápido lo que leo",
    tags: ["#EstrategiaDeEstudo", "#Soluciones"],
    tipo: "solucion",
    contenido: "Este es el clásico 'Error de Memoria'. Te sugerimos usar la técnica de 'Active Recall' (Recordar Activamente) y 'Spaced Repetition' (Repetición Espaciada). Utiliza el 'Simulacro Inteligente Profe Joy' filtrado por 'Memoria' para entrenar este aspecto."
  },
  {
    id: "regla_3",
    titulo: "Condiciones de Regularidad",
    tags: ["#Regulamento", "#CriteriosPromocao"],
    tipo: "regla",
    contenido: "Para mantener la regularidad en la cursada, debes cumplir con el 80% de asistencia a los Trabajos Prácticos y aprobar al menos el 50% de las ERAs."
  }
];

function renderEstatutoCards(data) {
  const grid = document.getElementById('estatuto-grid');
  const emptyState = document.getElementById('estatuto-empty');
  
  if (!grid) return;
  
  if (data.length === 0) {
    grid.style.display = 'none';
    if(emptyState) emptyState.style.display = 'block';
    return;
  }
  
  grid.style.display = 'flex';
  if(emptyState) emptyState.style.display = 'none';
  
  let html = '';
  data.forEach(item => {
    // Determinar clase de badge
    let badgeClass = 'badge-regla';
    if(item.tipo === 'solucion') badgeClass = 'badge-solucion';
    if(item.tipo === 'alerta') badgeClass = 'badge-alerta';
    
    // Tags html
    const tagsHtml = item.tags.map(t => `<span style="font-size: 0.75rem; color: #94a3b8; margin-right: 8px;">${t}</span>`).join('');
    
    html += `
      <div class="est-card" id="${item.id}">
        <div class="est-card-header" onclick="toggleEstatutoCard('${item.id}')">
          <div style="display: flex; flex-direction: column; gap: 5px;">
            <h4 class="est-card-title">
              <span class="est-badge ${badgeClass}">${item.tipo.toUpperCase()}</span>
              ${item.titulo}
            </h4>
            <div style="margin-top: 5px;">${tagsHtml}</div>
          </div>
          <i class="fa-solid fa-chevron-down est-card-icon"></i>
        </div>
        <div class="est-card-body">
          <p>${item.contenido}</p>
        </div>
      </div>
    `;
  });
  grid.innerHTML = html;
}

function toggleEstatutoCard(id) {
  const card = document.getElementById(id);
  if(card) {
    card.classList.toggle('open');
  }
}

function filtrarEstatuto(query) {
  const searchInput = document.getElementById('search-estatuto');
  if(searchInput && query !== undefined) {
    searchInput.value = query; // Si viene de un botón tag
  }
  
  const val = (searchInput ? searchInput.value : query || '').toLowerCase();
  
  // Highlight tags buttons
  document.querySelectorAll('.est-tag').forEach(btn => {
    btn.classList.remove('active');
    if(val && btn.innerText.toLowerCase() === val) {
      btn.classList.add('active');
    }
  });

  if (!val) {
    renderEstatutoCards(ESTATUTO_DATA);
    return;
  }
  
  const filtrados = ESTATUTO_DATA.filter(item => {
    const textoCompleto = (item.titulo + ' ' + item.contenido + ' ' + item.tags.join(' ')).toLowerCase();
    return textoCompleto.includes(val);
  });
  
  renderEstatutoCards(filtrados);
}

// Inicializar Búsqueda en Vivo y Eventos de Navegación
document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('search-estatuto');
  if(searchInput) {
    searchInput.addEventListener('input', (e) => {
      filtrarEstatuto(e.target.value);
    });
  }
  
  // Agregar listener para nav-estatuto
  const btnEstatuto = document.getElementById('nav-estatuto');
  if (btnEstatuto) {
    btnEstatuto.addEventListener('click', () => {
      document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
      
      btnEstatuto.classList.add('active');
      const tabEstatuto = document.getElementById('tab-estatuto');
      if(tabEstatuto) tabEstatuto.classList.add('active');
      
      // Renderizar la primera vez
      if(document.getElementById('estatuto-grid') && document.getElementById('estatuto-grid').innerHTML.trim() === '') {
        renderEstatutoCards(ESTATUTO_DATA);
      }
    });
  }
});

// --- FIN ESTATUTO SEARCH ENGINE LOGIC ---
