import re

with open("app.js", "r", encoding="utf-8") as f:
    app_js = f.read()

# Add the REGLAS and Mode Logic at the top (after let yaValidado = false;)
injection_logic = """
// ==========================================
// MODO DE ESTUDIO Y REGLAS UNLP
// ==========================================
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
  // Solo sumamos los aciertos
  Object.keys(estadoExamen.respuestasUsuario).forEach(qId => {
    if(estadoExamen.respuestasUsuario[qId].esCorrecta) {
       respuestasCorrectas++;
    }
  });
  
  const regla = REGLAS_PARCIALES_UNLP[estadoExamen.materiaKey];
  const nota = calcularNotaFinalUNLP(estadoExamen.materiaKey, respuestasCorrectas, regla.totalPreguntas || regla.estaciones);
  
  document.getElementById('resultado-estado').innerText = nota.estado;
  document.getElementById('resultado-estado').style.color = nota.color;
  document.getElementById('resultado-mensaje').innerText = nota.mensaje;
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
"""

if "let yaValidado       = false;" in app_js:
    app_js = app_js.replace("let yaValidado       = false;", "let yaValidado       = false;\n\n" + injection_logic)
else:
    print("Could not find anchor 'let yaValidado = false;'")

# Modify validarChoice to respect PARCIAL_REAL mode (no immediate feedback)
validar_pattern = r'function validarChoice\(btn, index\) \{[\s\S]*?\}'

validar_choice_replacement = """function validarChoice(btn, index) {
  if (yaValidado) return;
  yaValidado = true;
  
  const q = filteredChoices[currentChoiceIndex];
  const isCorrect = (index === q.correcta);
  
  // Register answer
  if (estadoExamen.modo === 'PARCIAL_REAL') {
      estadoExamen.respuestasUsuario[q.id] = {
          esCorrecta: isCorrect,
          elegida: index
      };
      // No feedback in partial mode, just advance
      btn.style.borderColor = 'var(--accent)';
      setTimeout(() => {
          siguienteChoice();
      }, 500);
      return;
  }
  
  // PRACTICA_TP Mode (Immediate Feedback)
  const allBtns = document.getElementById('mc-opcoes').querySelectorAll('button');
  
  allBtns.forEach((b, i) => {
    const isThisCorrect = (i === q.correcta);
    const expl = (q.opciones ?? q.opcoes ?? [])[i].explicacion;
    const explHtml = expl ? `<div style="margin-top:8px; font-size:0.85rem; color: var(--fg-default);">${expl}</div>` : '';
    
    if (isThisCorrect) {
      b.style.borderColor = 'var(--success)';
      b.style.backgroundColor = 'rgba(16, 185, 129, 0.05)';
      b.innerHTML += ` <i class="fa-solid fa-circle-check" style="color:var(--success); margin-left:8px;"></i>`;
      if (explHtml) b.innerHTML += explHtml;
    } else if (i === index && !isCorrect) {
      b.style.borderColor = 'var(--danger)';
      b.style.backgroundColor = 'rgba(239, 68, 68, 0.05)';
      b.innerHTML += ` <i class="fa-solid fa-circle-xmark" style="color:var(--danger); margin-left:8px;"></i>`;
      if (explHtml) b.innerHTML += explHtml;
    } else {
      b.style.opacity = '0.7';
    }
  });

  document.getElementById('mc-joy-panel').innerHTML = generarPanelJoy(q);
  document.getElementById('mc-joy-panel').style.display = 'block';

  // Guardar error si aplica
  if (!isCorrect) {
    if (!errores.includes(q.id)) errores.push(q.id);
    localStorage.setItem(STORAGE_KEYS.errores, JSON.stringify(errores));
  }
}"""

app_js = re.sub(validar_pattern, validar_choice_replacement, app_js)


with open("app.js", "w", encoding="utf-8") as f:
    f.write(app_js)
