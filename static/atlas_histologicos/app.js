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
        ${q.joy?.esquema ? `
        <div style="background: rgba(127, 0, 255, 0.1); border: 1px solid rgba(127, 0, 255, 0.3); border-radius: 10px; padding: 1rem;">
          <strong style="color: #c084fc; font-size: 0.88rem; display: block; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.05em;">
            🔥 ${q.joy?.esquemaTitulo || "CLAVE FUNDAMENTAL PARA EL EXAMEN"}
          </strong>
          <div style="color: #e9d5ff; font-size: 0.9rem; line-height: 1.6; font-family: monospace;">
            ${q.joy.esquema}
          </div>
        </div>
        ` : ''}
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


function abrirFragmento(qId) {
  window.open('https://www.conectafcm.com/biblioteca-virtual/965e8278-fa18-443d-8d0f-c00b1286f5b6', '_blank');
}

function cerrarFragmento() {
  const modal = document.getElementById('fragmento-modal');
  if (modal) modal.classList.remove('open');
}

// ─────────────────────────────────────────────────────────────
//  PERSISTENCIA — localStorage
// ─────────────────────────────────────────────────────────────
function guardarEnLocalStorage(q, seleccionado) {
  const intentos = leerStorage(STORAGE_KEYS.intentos);
  const anteriores = intentos.filter(item => item.preguntaId === q.id).length;
  const intento = {
    id: `${q.id}-${Date.now()}`,
    preguntaId: q.id,
    pregunta: (q.pregunta ?? q.pergunta),
    opcionElegida: seleccionado,
    letraElegida: letraOpcion(seleccionado),
    opcionCorrecta: q.correta,
    letraCorrecta: letraOpcion(q.correta),
    correcto: seleccionado === q.correta,
    explicacion: (q.explicacion ?? q.justificativa) || "",
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

// ─────────────────────────────────────────────────────────────
//  TOAST
// ─────────────────────────────────────────────────────────────
function mostrarToast(msg) {
  let toast = document.getElementById('alumed-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'alumed-toast';
    toast.className = 'alumed-toast';
    document.body.appendChild(toast);
  }
  toast.innerText = msg;
  toast.classList.add('visible');
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => toast.classList.remove('visible'), 3000);
}

// ─────────────────────────────────────────────────────────────
//  NAVEGACIÓN MC
// ─────────────────────────────────────────────────────────────
function nextChoice() {
  if (currentChoiceIndex < filteredChoices.length - 1) {
    currentChoiceIndex++;
    loadChoice();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
}

function prevChoice() {
  if (currentChoiceIndex > 0) {
    currentChoiceIndex--;
    loadChoice();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
}

// ─────────────────────────────────────────────────────────────
//  PINCHES
// ─────────────────────────────────────────────────────────────
function materiaActualPinches() {
  return currentMateria === "TODAS"
    ? bancoDados.pinches
    : bancoDados.pinches.filter(p => p.materia === currentMateria);
}

function loadPinche() {
  const fp = materiaActualPinches();
  if (!fp.length) {
    const el = document.getElementById('pinch-pergunta');
    if (el) el.innerText = 'No hay muestras para esta cátedra.';
    return;
  }
  const p = fp[currentPincheIndex % fp.length];
  const matEl  = document.getElementById('pinch-materia');
  const imgEl  = document.getElementById('pinch-img');
  const prgEl  = document.getElementById('pinch-pergunta');
  // Solo materia — sin nombre de archivo
  if (matEl)  matEl.innerText = p.materia;
  if (imgEl)  imgEl.src       = p.imagem;
  if (prgEl)  prgEl.innerText = p.pergunta;
}

function validarPinche() {
  const fp = materiaActualPinches();
  if (!fp.length) return;
  const p     = fp[currentPincheIndex % fp.length];
  const input = document.getElementById('pinch-input');
  if (!input) return;
  const val   = input.value.trim().toLowerCase();
  const fb    = document.getElementById('pinch-feedback');
  if (!fb) return;
  fb.style.display = 'block';
  if (p.respostasAceitas.map(r => r.toLowerCase()).includes(val)) {
    fb.className = 'feedback correct';
    fb.innerText = '🎯 ¡Excelente! Estructura anatómica correctamente identificada.';
  } else {
    fb.className = 'feedback incorrect';
    fb.innerText = `❌ Incorrecto. Respuestas válidas: ${p.respostasAceitas.join(' / ')}`;
  }
}

function nextPinche() {
  const input = document.getElementById('pinch-input');
  if (input) input.value = '';
  const fb = document.getElementById('pinch-feedback');
  if (fb) fb.style.display = 'none';
  const fp = materiaActualPinches();
  if (fp.length) {
    currentPincheIndex = (currentPincheIndex + 1) % fp.length;
    loadPinche();
  }
}

// ─────────────────────────────────────────────────────────────
//  ORAL / BOLILLAS
// ─────────────────────────────────────────────────────────────
function siguientePreguntaOral() {
  const rawOrales = currentMateria === "TODAS"
    ? bancoDados.orales
    : bancoDados.orales.filter(b => b.materia === currentMateria);
  if (!rawOrales.length) {
    alert('No hay preguntas orales para la materia seleccionada.');
    return;
  }
  const o    = rawOrales[Math.floor(Math.random() * rawOrales.length)];
  const card = document.getElementById('oral-card');
  if (card) card.style.display = 'block';
  const matEl = document.getElementById('oral-materia');
  if (matEl) matEl.innerText = o.materia; // solo materia
  document.getElementById('oral-titulo').innerText = o.titulo || o.tema || o.bolilla || '';
  document.getElementById('oral-caso').innerText    = o.casoClinico;
  const chk = document.getElementById('oral-checklist');
  if (chk) {
    chk.innerHTML = '';
    o.checklist.forEach(item => {
      chk.innerHTML += `<label><input type="checkbox"> ${item}</label>`;
    });
  }
}

// ─────────────────────────────────────────────────────────────
//  INIT
// ─────────────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
  filteredChoices = [...bancoDados.choices];
  loadChoice();
  loadPinche();

  // Cerrar modal al clicar fuera
  const modal = document.getElementById('fragmento-modal');
  if (modal) {
    modal.addEventListener('click', e => {
      if (e.target === modal) cerrarFragmento();
    });
  }

  // Esc cierra modal
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') cerrarFragmento();
  });

  // Verificar recordatorios al cargar
  checkReminders();
});

// ═════════════════════════════════════════════════════════════
//  CALENDARIO DE PARCIALES — ALUMED OS
// ═════════════════════════════════════════════════════════════

const MESES_CAL    = ['Enero','Febrero','Marzo','Abril','Mayo','Junio',
                      'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];
const DIAS_LARGO   = ['Domingo','Lunes','Martes','Miércoles','Jueves','Viernes','Sábado'];
const MAT_ICONS    = {
  'Biología':                 '🔬',
  'Anatomía A':               '🦴',
  'Anatomía B':               '🫀',
  'Anatomía C':               '🧠',
  'Histología y Embriología': '🧫'
};

let calMesActual = 4; // Mayo = índice 4 (enero=0)
let calAnio      = 2026;
let calIniciado  = false;

// ── Navegación de vistas ───────────────────────────────────────
function initCalendario() {
  if (!calIniciado) {
    renderVistaCronologica();
    renderMes(calAnio, calMesActual);
    calIniciado = true;
  }
}

function switchVistaCalendario(vista) {
  ['cronologica', 'calendario'].forEach(v => {
    const el  = document.getElementById(`cal-vista-${v}`);
    const btn = document.getElementById(`cal-vista-btn-${v}`);
    if (el)  el.style.display  = v === vista ? 'block' : 'none';
    if (btn) btn.classList.toggle('active', v === vista);
  });
  if (vista === 'calendario') renderMes(calAnio, calMesActual);
}

function navCalendario(dir) {
  calMesActual += dir;
  if (calMesActual < 0)  { calMesActual = 11; calAnio--; }
  if (calMesActual > 11) { calMesActual = 0;  calAnio++; }
  renderMes(calAnio, calMesActual);
}

// ── Utilidades de fecha ────────────────────────────────────────
function getTodayStr() {
  const t = new Date();
  return `${t.getFullYear()}-${String(t.getMonth()+1).padStart(2,'0')}-${String(t.getDate()).padStart(2,'0')}`;
}

function formatFechaLarga(dateStr) {
  if (!dateStr) return null;
  const [y, m, d] = dateStr.split('-').map(Number);
  const dt = new Date(y, m - 1, d);
  return `${DIAS_LARGO[dt.getDay()]} ${d} de ${MESES_CAL[m - 1]} de ${y}`;
}

function getDaysUntil(dateStr) {
  if (!dateStr) return null;
  const today = new Date(); today.setHours(0, 0, 0, 0);
  const [y, m, d] = dateStr.split('-').map(Number);
  return Math.ceil((new Date(y, m - 1, d) - today) / 86400000);
}

function isParcialPast(p) {
  const end = p.fechaFin || p.fechaInicio;
  return end < getTodayStr();
}

function isDateInParcial(dateStr, p) {
  if (!p.esPeriodo) return dateStr === p.fechaInicio;
  return dateStr >= p.fechaInicio && dateStr <= (p.fechaFin || p.fechaInicio);
}

// ── Recuperar datos personales HyE (localStorage) ─────────────
function getHyEPersonal(id) {
  return JSON.parse(localStorage.getItem('alumed_hye_personal') || '{}')[id] || null;
}

// ── Renderizado de cuenta regresiva ────────────────────────────
function renderCountdown(p) {
  const today = getTodayStr();

  if (p.esPeriodo && p.fechaFin) {
    const daysStart = getDaysUntil(p.fechaInicio);
    const daysEnd   = getDaysUntil(p.fechaFin);
    if (daysEnd < 0)  return `<div class="countdown-box past"><span class="cnt-num">—</span><small>Finalizado</small></div>`;
    if (daysStart <= 0) return `<div class="countdown-box active-period"><span class="cnt-num">${Math.abs(daysEnd)}</span><small>días para cerrar</small></div>`;
    return `<div class="countdown-box upcoming"><span class="cnt-num">${daysStart}</span><small>días para el inicio</small></div>`;
  }

  const days = getDaysUntil(p.fechaInicio);
  if (days === null) return `<div class="countdown-box grey"><span class="cnt-num">—</span><small>Sin fecha</small></div>`;
  if (days < 0)      return `<div class="countdown-box past"><span class="cnt-num">—</span><small>Ya pasó</small></div>`;
  if (days === 0)    return `<div class="countdown-box today"><span class="cnt-num">HOY</span><small>¡Es hoy!</small></div>`;
  return `<div class="countdown-box upcoming"><span class="cnt-num">${days}</span><small>días</small></div>`;
}

// ── Badge de estado ────────────────────────────────────────────
function getEstadoBadge(estado) {
  const map = {
    'confirmada':        `<span class="estado-badge confirmada">✅ Confirmada</span>`,
    'estimada':          `<span class="estado-badge estimada">⚠️ Fecha estimada — sujeta a confirmación</span>`,
    'pendiente':         `<span class="estado-badge pendiente">🔘 Confirmación pendiente</span>`,
    'periodo-informado': `<span class="estado-badge periodo">📋 Período informado — asignación individual pendiente</span>`
  };
  return map[estado] || `<span class="estado-badge">—</span>`;
}

// ── Formulario editable HyE ────────────────────────────────────
function mostrarFormHyE(id) {
  const f = document.getElementById(`form-hye-${id}`);
  if (f) { f.style.display = 'block'; f.scrollIntoView({ behavior: 'smooth', block: 'nearest' }); }
}
function ocultarFormHyE(id) {
  const f = document.getElementById(`form-hye-${id}`);
  if (f) f.style.display = 'none';
}
function editarFechaHyE(id) { mostrarFormHyE(id); }

function guardarFechaHyE(id) {
  const diaEl  = document.getElementById(`hye-dia-${id}`);
  const horaEl = document.getElementById(`hye-hora-${id}`);
  const aulaEl = document.getElementById(`hye-aula-${id}`);
  const modEl  = document.getElementById(`hye-mod-${id}`);

  const dia = diaEl?.value;
  if (!dia) { mostrarToast('Seleccioná un día antes de guardar'); return; }

  const p = parciales.find(x => x.id === id);
  if (!p) return;

  const diasNum = { 'Lunes':1, 'Martes':2, 'Miércoles':3, 'Jueves':4, 'Viernes':5 };
  const [y, m, d] = p.fechaInicio.split('-').map(Number);
  let dt = new Date(y, m - 1, d);
  while (dt.getDay() !== diasNum[dia]) dt.setDate(dt.getDate() + 1);

  const fechaHuman = `${dia} ${dt.getDate()} de ${MESES_CAL[dt.getMonth()]} de ${dt.getFullYear()}`;
  const stored = JSON.parse(localStorage.getItem('alumed_hye_personal') || '{}');
  stored[id] = {
    diaEspecifico: fechaHuman,
    fecha:    `${dt.getFullYear()}-${String(dt.getMonth()+1).padStart(2,'0')}-${String(dt.getDate()).padStart(2,'0')}`,
    hora:     horaEl?.value   || null,
    aula:     aulaEl?.value   || null,
    modalidad:modEl?.value    || null
  };
  localStorage.setItem('alumed_hye_personal', JSON.stringify(stored));
  mostrarToast(`✅ Fecha guardada: ${fechaHuman}`);
  // Re-renderizar
  calIniciado = false;
  initCalendario();
  calIniciado = true;
}

function renderFormHyE(p) {
  const dias    = ['Lunes','Martes','Miércoles','Jueves','Viernes'];
  const opciones = dias.map(d => `<option value="${d}">${d}</option>`).join('');
  return `
    <div class="hye-form-inner">
      <h4><i class="fa-solid fa-pen-to-square"></i> Cargar mi fecha asignada — ${p.instancia}</h4>
      <div class="hye-form-grid">
        <div class="hye-form-field">
          <label>Día de la semana</label>
          <select id="hye-dia-${p.id}" class="input-field">
            <option value="">Seleccionar…</option>${opciones}
          </select>
        </div>
        <div class="hye-form-field">
          <label>Horario</label>
          <input type="time" id="hye-hora-${p.id}" class="input-field" placeholder="08:00">
        </div>
        <div class="hye-form-field">
          <label>Aula <span class="optional">(opcional)</span></label>
          <input type="text" id="hye-aula-${p.id}" class="input-field" placeholder="Ej: Aula 5">
        </div>
        <div class="hye-form-field">
          <label>Modalidad <span class="optional">(opcional)</span></label>
          <input type="text" id="hye-mod-${p.id}" class="input-field" placeholder="Ej: Presencial">
        </div>
      </div>
      <div class="hye-form-actions">
        <button class="btn-primary" style="padding:.6rem 1.2rem;font-size:.85rem" onclick="guardarFechaHyE('${p.id}')">
          <i class="fa-solid fa-floppy-disk"></i> Guardar fecha
        </button>
        <button class="btn-secondary" style="padding:.6rem 1.2rem;font-size:.85rem" onclick="ocultarFormHyE('${p.id}')">
          Cancelar
        </button>
      </div>
    </div>`;
}

// ── Tarjeta de parcial ─────────────────────────────────────────
function renderTarjetaParcial(p, highlight) {
  const icon   = MAT_ICONS[p.materia] || '📅';
  const hye    = p.editable ? getHyEPersonal(p.id) : null;
  const hora   = hye?.hora      || p.hora;
  const aula   = hye?.aula      || p.aula;
  const mod    = hye?.modalidad || p.modalidad;
  const isPast = isParcialPast(p);

  // ── Sección de fecha ──
  let fechaHTML = '';
  if (hye?.diaEspecifico) {
    fechaHTML = `
      <div class="parcial-info-row highlight-row">
        <i class="fa-solid fa-calendar-check"></i>
        <span>Tu fecha: <strong>${hye.diaEspecifico}</strong></span>
      </div>
      <div class="parcial-info-row muted-row">
        <i class="fa-solid fa-calendar-days"></i>
        <span>Período: ${formatFechaLarga(p.fechaInicio)} al ${formatFechaLarga(p.fechaFin)}</span>
      </div>`;
  } else if (p.esPeriodo) {
    fechaHTML = `
      <div class="parcial-info-row period-row">
        <i class="fa-solid fa-calendar-week"></i>
        <span>${p.textoPublico || `${formatFechaLarga(p.fechaInicio)} al ${formatFechaLarga(p.fechaFin)}`}</span>
      </div>`;
  } else if (p.esEstimado) {
    fechaHTML = `
      <div class="parcial-info-row estimated-row">
        <i class="fa-solid fa-calendar-xmark"></i>
        <span>${p.textoPublico || formatFechaLarga(p.fechaInicio)}</span>
      </div>`;
  } else {
    fechaHTML = `
      <div class="parcial-info-row">
        <i class="fa-solid fa-calendar"></i>
        <span>${formatFechaLarga(p.fechaInicio)}</span>
      </div>`;
  }

  // ── Bloque editable HyE ──
  let editHTML = '';
  if (p.editable) {
    const yaGuardado = !!(hye?.diaEspecifico);
    editHTML = `
      <div class="hye-edit-zone">
        ${yaGuardado
          ? `<div class="hye-saved-hint"><i class="fa-solid fa-circle-check"></i> Fecha personal guardada.
               <button class="btn-link" onclick="editarFechaHyE('${p.id}')"><i class="fa-solid fa-pen"></i> Editar</button>
             </div>`
          : `<div class="hye-pending-hint"><i class="fa-solid fa-pen-to-square"></i>
               ¿Ya te asignaron tu día?
               <button class="btn-link" onclick="mostrarFormHyE('${p.id}')">Cargarlo acá</button>
             </div>`
        }
        <div id="form-hye-${p.id}" class="hye-form" style="display:none">
          ${renderFormHyE(p)}
        </div>
      </div>`;
  }

  // ── Recordatorio ──
  const rems    = JSON.parse(localStorage.getItem('alumed_recordatorios') || '{}');
  const hasRem  = !!(rems[p.id]);

  return `
    <div class="parcial-card border-${p.colorKey}${highlight ? ' card-highlight' : ''}${isPast ? ' card-past' : ''}">
      <div class="parcial-card-top">
        <div class="parcial-icon-wrap bg-${p.colorKey}">${icon}</div>
        <div class="parcial-head-info">
          <div class="parcial-materia-name">${p.materia}</div>
          <div class="parcial-instancia-name">${p.instancia}</div>
        </div>
        ${renderCountdown(p)}
      </div>

      <div class="parcial-estado-strip">${getEstadoBadge(p.estado)}</div>

      <div class="parcial-body">
        ${fechaHTML}
        <div class="parcial-info-row${!hora ? ' muted-row' : ''}">
          <i class="fa-solid fa-clock"></i>
          <span>${hora || 'Horario por confirmar'}</span>
        </div>
        <div class="parcial-info-row${!mod ? ' muted-row' : ''}">
          <i class="fa-solid fa-chalkboard"></i>
          <span>${mod || 'Modalidad por confirmar'}</span>
        </div>
        ${aula ? `<div class="parcial-info-row"><i class="fa-solid fa-door-open"></i><span>Aula: ${aula}</span></div>` : ''}
        ${p.observacion ? `<div class="parcial-obs"><i class="fa-solid fa-circle-info"></i> ${p.observacion}</div>` : ''}
      </div>

      ${editHTML}

      <div class="parcial-card-footer">
        <button class="btn-cal-action ${hasRem ? 'btn-rem-on' : 'btn-rem-off'}" onclick="toggleRecordatorio('${p.id}')">
          <i class="fa-solid fa-bell${hasRem ? '' : '-slash'}"></i>
          ${hasRem ? 'Recordatorio activo' : 'Activar recordatorio'}
        </button>
      </div>
    </div>`;
}

// ── Vista cronológica ──────────────────────────────────────────
function renderVistaCronologica() {
  const container = document.getElementById('cal-cronologica-container');
  if (!container) return;

  const today = getTodayStr();
  const sortFn = (a, b) => (a.fechaInicio || '').localeCompare(b.fechaInicio || '');

  // Clasificación
  const proximos = parciales.filter(p => !isParcialPast(p) && getDaysUntil(p.fechaInicio) <= 30);
  const futuros  = parciales.filter(p => !isParcialPast(p) && getDaysUntil(p.fechaInicio) > 30);
  const pasados  = parciales.filter(p => isParcialPast(p));

  proximos.sort(sortFn);
  futuros.sort(sortFn);
  pasados.sort(sortFn);

  let html = '';

  if (proximos.length) {
    html += `
      <div class="cal-group">
        <div class="cal-group-title fire">
          <i class="fa-solid fa-fire-flame-curved"></i> Próximos Parciales
          <span class="cal-group-count">${proximos.length}</span>
        </div>
        <div class="parciales-grid">${proximos.map(p => renderTarjetaParcial(p, true)).join('')}</div>
      </div>`;
  }

  if (futuros.length) {
    html += `
      <div class="cal-group">
        <div class="cal-group-title">
          <i class="fa-solid fa-calendar-days"></i> Fechas Confirmadas y Estimadas
          <span class="cal-group-count">${futuros.length}</span>
        </div>
        <div class="parciales-grid">${futuros.map(p => renderTarjetaParcial(p, false)).join('')}</div>
      </div>`;
  }

  if (pasados.length) {
    html += `
      <div class="cal-group">
        <div class="cal-group-title muted-title">
          <i class="fa-solid fa-clock-rotate-left"></i> Parciales Anteriores
          <span class="cal-group-count">${pasados.length}</span>
        </div>
        <div class="parciales-grid">${pasados.map(p => renderTarjetaParcial(p, false)).join('')}</div>
      </div>`;
  }

  if (!html) html = '<p class="cal-empty">No hay parciales cargados aún.</p>';
  container.innerHTML = html;
}

// ── Vista mensual ──────────────────────────────────────────────
function renderMes(year, month) {
  const titleEl = document.getElementById('cal-mes-titulo');
  if (titleEl) titleEl.textContent = `${MESES_CAL[month]} ${year}`;

  const gridEl = document.getElementById('cal-mes-grid');
  if (!gridEl) return;

  const firstDay   = new Date(year, month, 1).getDay();
  const offset     = (firstDay + 6) % 7; // Lunes=0
  const daysInMonth= new Date(year, month + 1, 0).getDate();
  const today      = getTodayStr();

  // Encabezado de días
  let html = '<div class="cal-header-row">';
  ['Lun','Mar','Mié','Jue','Vie','Sáb','Dom'].forEach(d => {
    html += `<div class="cal-header-day">${d}</div>`;
  });
  html += '</div><div class="cal-days-wrap">';

  // Celdas vacías iniciales
  for (let i = 0; i < offset; i++) {
    html += '<div class="cal-day-cell empty"></div>';
  }

  // Celdas de días
  for (let d = 1; d <= daysInMonth; d++) {
    const dateStr = `${year}-${String(month+1).padStart(2,'0')}-${String(d).padStart(2,'0')}`;
    const isToday  = dateStr === today;
    const isPastD  = dateStr < today;

    const dayEvents = parciales.filter(p => isDateInParcial(dateStr, p));

    const pills = dayEvents.map(e => {
      const abbr    = e.materia === 'Histología y Embriología' ? 'HyE' :
                      e.materia.startsWith('Anatomía')        ? e.materia.replace('Anatomía ','Anat ') :
                      e.materia;
      const isStart = dateStr === e.fechaInicio;
      const isEnd   = dateStr === (e.fechaFin || e.fechaInicio);
      return `<div class="cal-pill cal-color-${e.colorKey}${e.esEstimado ? ' pill-estimada' : ''}${isStart ? ' pill-start' : ''}${isEnd ? ' pill-end' : ''}"
               title="${e.materia} — ${e.instancia}">${isStart ? abbr : ''}</div>`;
    }).join('');

    html += `<div class="cal-day-cell${isToday ? ' cal-today' : ''}${isPastD ? ' cal-past-day' : ''}${dayEvents.length ? ' has-event' : ''}">
      <span class="cal-day-num">${d}</span>
      <div class="cal-pills">${pills}</div>
    </div>`;
  }

  html += '</div>';
  gridEl.innerHTML = html;
}

// ── Recordatorios ──────────────────────────────────────────────
function toggleRecordatorio(id) {
  const rems = JSON.parse(localStorage.getItem('alumed_recordatorios') || '{}');
  if (rems[id]) {
    delete rems[id];
    mostrarToast('🔕 Recordatorio desactivado');
  } else {
    rems[id] = { activado: new Date().toISOString(), diasAntes: [30, 15, 7, 3, 1, 0] };
    mostrarToast('🔔 Recordatorio activo — te alertaremos en ALUMED OS');
  }
  localStorage.setItem('alumed_recordatorios', JSON.stringify(rems));
  // Re-renderizar tarjetas
  renderVistaCronologica();
}

function checkReminders() {
  const rems  = JSON.parse(localStorage.getItem('alumed_recordatorios') || '{}');
  const today = getTodayStr();

  Object.keys(rems).forEach(id => {
    const p = parciales.find(x => x.id === id);
    if (!p) return;
    const days    = getDaysUntil(p.fechaInicio);
    const diasAntes = rems[id].diasAntes || [30, 15, 7, 3, 1, 0];

    if (days !== null && diasAntes.includes(days)) {
      const shownKey = `alumed_rem_shown_${id}_${today}`;
      if (!localStorage.getItem(shownKey)) {
        localStorage.setItem(shownKey, '1');
        const msg = days === 0
          ? `🚨 ¡HOY tiene lugar el parcial de ${p.materia} (${p.instancia})!`
          : `⏰ Faltan ${days} días para el parcial de ${p.materia} — ${p.instancia}`;
        setTimeout(() => mostrarToast(msg), 2000);
      }
    }
  });
}



const temaGuardado = localStorage.getItem("alumed_tema") || "dark";
document.documentElement.dataset.theme = temaGuardado;

function toggleTheme() {
  const nuevo = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
  document.documentElement.dataset.theme = nuevo;
  localStorage.setItem("alumed_tema", nuevo);
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
  const targetMateria = eje === 'histo' ? 'histología' : 'embriología';
  estadoSplit.choicesFiltrados = (bancoDados?.choices || []).filter(q => {
    const mat = normalizarTexto(q.materia || '');
    return mat.includes(targetMateria);
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
  if (pregEl) pregEl.textContent = q.pregunta || q.pergunta || '';

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
  const fb = document.getElementById('split-mc-feedback');
  if (fb) {
    fb.innerHTML = generarPanelJoy(q, estadoSplit.selectedOption);
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

