import re

with open("app.js", "r", encoding="utf-8") as f:
    app_js = f.read()

new_modules = """
// ==========================================
// 1. MAPEADOR DE CRONOGRAMA UNLP 2026 (BASE DE TEMAS)
// ==========================================
const CRONOGRAMA_UNLP_2026 = {
  biologia: {
    "TP1": "Introducción a la Biología & Organización Celular",
    "TP2": "Componentes Químicos I (Agua y Pequeñas Moléculas)",
    "TP3": "Componentes Químicos II (Lípidos y Macromoléculas)",
    "TP4": "Bioenergética y Cinética Enzimática",
    "TP5": "Mecanismos Genéticos Básicos I",
    "TP6": "Mecanismos Genéticos Básicos II (Expresión y Regulación)",
    "TP7": "Membrana Plasmática y Transporte (Ósmosis/Osmolaridad)",
    "TP8": "Metabolismo Intermedio y Mitocondrias",
    "TP9": "Membranas Internas I (RE y Golgi)",
    "TP10": "Membranas Internas II (Lisosomas y Peroxisomas)",
    "TP11": "El Núcleo Celular",
    "TP12": "Citoesqueleto, Adhesión y Matriz Extracelular",
    "TP13": "Ciclo Celular y Apoptosis",
    "TP14": "Mecanismos de División Celular (Mitosis y Meiosis)",
    "TP15": "Transmisión del Material Genético",
    "TP16": "Las Células en su Contexto Social (Comunicación)"
  },
  histo_embrio: {
    "TP1": "Técnica Histológica",
    "TP2": "Tejido Epitelial",
    "TP3": "Tejido Conectivo y Adiposo",
    "TP4": "Tejido Cartilaginoso y Óseo",
    "TP5": "Sangre y Hematopoyesis",
    "TP6": "Tejido Nervioso y Sistema Nervioso",
    "TP7": "Tejido Muscular",
    "TP8": "Sistema Cardiovascular",
    "TP9": "Tejido Linfoide y Sistema Linfoide",
    "TP10": "Embriología: Fecundación y Primeras Semanas",
    "TP11": "Embriología: 3ª y 4ª Semana (Gastrulación/Neurulación)",
    "TP12": "Embriología: Placenta y Anexos Embrionarios"
  },
  histologia: {
    "TP1": "Técnica Histológica",
    "TP2": "Tejido Epitelial",
    "TP3": "Tejido Conectivo y Adiposo",
    "TP4": "Tejido Cartilaginoso y Óseo",
    "TP5": "Sangre y Hematopoyesis",
    "TP6": "Tejido Nervioso y Sistema Nervioso",
    "TP7": "Tejido Muscular",
    "TP8": "Sistema Cardiovascular",
    "TP9": "Tejido Linfoide y Sistema Linfoide",
    "TP10": "Embriología: Fecundación y Primeras Semanas",
    "TP11": "Embriología: 3ª y 4ª Semana (Gastrulación/Neurulación)",
    "TP12": "Embriología: Placenta y Anexos Embrionarios"
  },
  anatomia_a: {
    "TP1": "Huesos del Miembro Superior",
    "TP2": "Huesos del Miembro Inferior",
    "TP3": "Columna Vertebral y Tórax",
    "TP4": "Cráneo (Bóveda y Base)",
    "TP5": "Macizo Facial",
    "TP6": "Artrología",
    "TP7": "Miología Miembro Superior",
    "TP8": "Miología Miembro Inferior",
    "TP9": "Miología del Tronco",
    "TP10": "Miología Cabeza y Cuello"
  },
  anato_a: {
    "TP1": "Huesos del Miembro Superior",
    "TP2": "Huesos del Miembro Inferior",
    "TP3": "Columna Vertebral y Tórax",
    "TP4": "Cráneo (Bóveda y Base)",
    "TP5": "Macizo Facial",
    "TP6": "Artrología",
    "TP7": "Miología Miembro Superior",
    "TP8": "Miología Miembro Inferior",
    "TP9": "Miología del Tronco",
    "TP10": "Miología Cabeza y Cuello"
  }
};

// ==========================================
// 2. MÓDULO FLASHCARD DE ERRORES (MÉTODO JOY)
// ==========================================
function renderizarFlashcardError(pregunta, intentoAlumno) {
  const tpId = pregunta.tpId || "TP1";
  const tpNombre = CRONOGRAMA_UNLP_2026[pregunta.materiaKey]?.[tpId] || tpId;
  const opciones = pregunta.opciones || (pregunta.opcoes ? pregunta.opcoes.map(o => o.texto) : []);
  const opcionElegida = opciones[intentoAlumno.respuestaSeleccionada] || "No respondida";
  const opcionCorrecta = opciones[pregunta.correcta] || "Opción correcta";
  const justificativa = pregunta.joy?.examen || pregunta.explicacion || pregunta.justificativa || "Revisar bibliografía oficial de la cátedra.";

  return `
    <div class="flashcard-error-card bg-slate-900 border-2 border-red-500/50 rounded-xl p-5 text-white shadow-xl my-4">
      <div class="flex justify-between items-center mb-3">
        <span class="text-xs font-bold uppercase tracking-wider text-amber-400 bg-amber-400/10 px-3 py-1 rounded-full border border-amber-400/30">
          📌 ${tpId}: ${tpNombre}
        </span>
        <span class="text-xs text-red-400 font-semibold flex items-center gap-1">
          ⚠️ Modo Análisis de Error
        </span>
      </div>

      <h4 class="text-base font-semibold mb-4 text-slate-100">${pregunta.pregunta || pregunta.pergunta}</h4>

      <div class="space-y-2 mb-4">
        <div class="p-3 rounded-lg bg-red-950/40 border border-red-500/40 text-sm">
          <span class="text-red-400 font-bold block text-xs uppercase">❌ Tu Elección (Error):</span>
          <span class="text-red-200">${opcionElegida}</span>
        </div>
        <div class="p-3 rounded-lg bg-emerald-950/40 border border-emerald-500/40 text-sm">
          <span class="text-emerald-400 font-bold block text-xs uppercase">✅ Opción Correcta:</span>
          <span class="text-emerald-200">${opcionCorrecta}</span>
        </div>
      </div>

      <div class="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-xs leading-relaxed space-y-2">
        <p class="font-bold text-amber-300 text-sm flex items-center gap-2">
          💡 Método Profe Joy — ¿Dónde estuvo la trampa?
        </p>
        <p class="text-amber-100/90">${justificativa}</p>
        <div class="pt-2 border-t border-amber-500/20 text-amber-200/80 font-mono text-[11px]">
          🎯 <strong>Tip de Examen:</strong> Revisa la bibliografía oficial, polaridad o inserciones según corresponda.
        </div>
      </div>
    </div>
  `;
}

// ==========================================
// 3. GENERADOR DE INFORME DIAGNÓSTICO FINAL
// ==========================================
function generarInformeDiagnosticoUNLP(historialExamen, materiaKey) {
  const cronogramaMateria = CRONOGRAMA_UNLP_2026[materiaKey] || {};
  let resumenPorTP = {};

  historialExamen.forEach(item => {
    const tpKey = item.tpId || "General";
    if (!resumenPorTP[tpKey]) {
      resumenPorTP[tpKey] = {
        nombre: cronogramaMateria[tpKey] || tpKey,
        totales: 0,
        correctas: 0,
        errores: 0,
        tiposError: { concepto: 0, trampaCat: 0, atencion: 0 }
      };
    }
    
    resumenPorTP[tpKey].totales++;
    if (item.esCorrecto) {
      resumenPorTP[tpKey].correctas++;
    } else {
      resumenPorTP[tpKey].errores++;
      const expl = item.justificativa || item.explicacion || "";
      if (expl.toLowerCase().includes('trampa') || expl.toLowerCase().includes('distractor')) {
        resumenPorTP[tpKey].tiposError.trampaCat++;
      } else {
        resumenPorTP[tpKey].tiposError.concepto++;
      }
    }
  });

  let totalPreguntas = historialExamen.length || 1;
  let totalCorrectas = historialExamen.filter(x => x.esCorrecto).length;
  let porcentajeGlobal = Math.round((totalCorrectas / totalPreguntas) * 100);
  let nivelRiesgo = porcentajeGlobal >= 70 ? "BAJO (Rumbo a Promoción 🏆)" : porcentajeGlobal >= 40 ? "MEDIO (En Zona de Aprobación 🟢)" : "ALTO (Requiere Repaso Urgente 🔴)";

  let htmlReporte = `
    <div class="reporte-container bg-slate-950 p-6 rounded-2 border border-amber-500/30 text-white max-w-4xl mx-auto space-y-6 text-left">
      
      <div class="text-center border-b border-amber-500/20 pb-4">
        <span class="text-xs uppercase tracking-widest text-amber-400 font-bold">Facultad de Ciencias Médicas UNLP</span>
        <h2 class="text-2xl font-black text-amber-400 mt-1">📊 Informe Diagnóstico de Rendimiento</h2>
        <p class="text-xs text-slate-400 mt-1">Basado en el Cronograma Oficial 2026 — Método Profe Joy</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4" style="display: flex; gap: 10px; justify-content: space-around;">
        <div class="bg-slate-900 p-4 rounded-xl border border-slate-800 text-center flex-1">
          <span class="text-xs text-slate-400 font-semibold block">Acierto Global</span>
          <span class="text-3xl font-black ${porcentajeGlobal >= 70 ? 'text-emerald-400' : 'text-amber-400'}" style="font-size: 1.8rem; font-weight: bold; color: #10b981;">${porcentajeGlobal}%</span>
        </div>
        <div class="bg-slate-900 p-4 rounded-xl border border-slate-800 text-center flex-1">
          <span class="text-xs text-slate-400 font-semibold block">Aprobadas / Total</span>
          <span class="text-3xl font-black text-cyan-400" style="font-size: 1.8rem; font-weight: bold; color: #06b6d4;">${totalCorrectas} / ${totalPreguntas}</span>
        </div>
        <div class="bg-slate-900 p-4 rounded-xl border border-slate-800 text-center flex-1">
          <span class="text-xs text-slate-400 font-semibold block">Nivel de Riesgo Parcial</span>
          <span class="text-sm font-bold block mt-2 ${porcentajeGlobal >= 70 ? 'text-emerald-400' : porcentajeGlobal >= 40 ? 'text-amber-400' : 'text-red-400'}">${nivelRiesgo}</span>
        </div>
      </div>

      <div class="space-y-4 pt-2">
        <h3 class="text-lg font-bold text-slate-200 flex items-center gap-2">
          🎯 Probabilidad de Error & Estado por Trabajo Práctico (TP)
        </h3>
  `;

  Object.keys(resumenPorTP).forEach(tpKey => {
    let tp = resumenPorTP[tpKey];
    let pctEfectividad = Math.round((tp.correctas / tp.totales) * 100);
    let probError = 100 - pctEfectividad;
    let patronDominante = tp.tiposError.trampaCat > tp.tiposError.concepto ? "Caída en Trampas de Cátedra ⚠️" : "Vacío de Concepto Teórico 📚";

    htmlReporte += `
      <div class="bg-slate-900 p-4 rounded-xl border ${pctEfectividad < 60 ? 'border-red-500/40' : 'border-slate-800'} space-y-3 my-2" style="background: rgba(15, 23, 42, 0.6); padding: 12px; border-radius: 8px; border: 1px solid #334155;">
        <div class="flex flex-col md:flex-row justify-between md:items-center gap-2" style="display: flex; justify-content: space-between; align-items: center;">
          <div>
            <span class="text-xs font-bold text-amber-400 uppercase" style="color: #f59e0b; font-size: 0.75rem;">${tpKey}</span>
            <h4 class="text-sm font-bold text-slate-100" style="margin: 2px 0;">${tp.nombre}</h4>
          </div>
          <div class="flex items-center gap-3">
            <span class="text-xs font-bold px-3 py-1 rounded-full ${pctEfectividad >= 70 ? 'bg-emerald-500/20 text-emerald-300' : 'bg-red-500/20 text-red-300'}" style="padding: 4px 8px; border-radius: 12px; font-size: 0.75rem; background: rgba(239, 68, 68, 0.2); color: #fca5a5;">
              Prob. Error: ${probError}%
            </span>
            <button onclick="compartirAnalisisTema('${tpKey}', '${tp.nombre}', ${probError})" class="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-lg border border-slate-700 transition" style="cursor: pointer; padding: 4px 8px; border-radius: 6px; background: #334155; color: #fff; border: none;">
              📤 Compartir
            </button>
          </div>
        </div>

        <div class="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800" style="background: #020617; height: 8px; border-radius: 4px; overflow: hidden; margin: 8px 0;">
          <div class="h-full ${pctEfectividad >= 70 ? 'bg-emerald-400' : pctEfectividad >= 40 ? 'bg-amber-400' : 'bg-red-500'}" style="width: ${pctEfectividad}%; height: 100%; background: ${pctEfectividad >= 70 ? '#34d399' : pctEfectividad >= 40 ? '#fbbf24' : '#f87171'};"></div>
        </div>

        ${tp.errores > 0 ? `
          <div class="text-xs text-slate-400 bg-slate-950/60 p-2.5 rounded-lg flex items-center gap-2 border border-slate-800/60" style="font-size: 0.8rem; color: #94a3b8;">
            <span class="text-amber-400 font-bold" style="color: #f59e0b;">🔍 Diagnóstico:</span>
            <span>Patrón detectado: <strong class="text-slate-200" style="color: #e2e8f0;">${patronDominante}</strong> en ${tp.errores} pregunta(s).</span>
          </div>
        ` : `
          <div class="text-xs text-emerald-400/90 font-medium" style="font-size: 0.8rem; color: #34d399;">✨ ¡Dominio completo de este TP! Mantené el repaso activo.</div>
        `}
      </div>
    `;
  });

  htmlReporte += `
      </div>

      <div class="flex flex-wrap gap-3 pt-4 border-t border-slate-800 justify-end" style="margin-top: 15px; text-align: right;">
        <button onclick="iniciarEntrenamientoEnfocadoErrores('${materiaKey}')" class="bg-gradient-to-r from-red-600 to-amber-600 text-white text-xs font-bold px-5 py-3 rounded-xl hover:opacity-90 transition shadow-lg" style="cursor: pointer; background: linear-gradient(to right, #dc2626, #d97706); color: white; padding: 10px 16px; border-radius: 8px; border: none; font-weight: bold;">
          🔥 Entrenar Solo Mis Errores de este Examen
        </button>
      </div>

    </div>
  `;

  return htmlReporte;
}

// ==========================================
// 4. FUNCIÓN PARA COMPARTIR RESUMEN POR TEMA Y ENTRENAR ERRORES
// ==========================================
function compartirAnalisisTema(tpKey, tpNombre, probError) {
  const textoCompartir = `🩺 *ALUMED OS — FCM UNLP 2026*\\n\\n📌 *Análisis de Tema:* ${tpKey} - ${tpNombre}\\n⚠️ *Probabilidad de Error:* ${probError}%\\n💡 *Objetivo:* Reforzar según el Método Profe Joy antes del Parcial.\\n\\n¡Entrená gratis en la plataforma! ⚡`;
  
  if (navigator.share) {
    navigator.share({
      title: 'Diagnóstico ALUMED UNLP',
      text: textoCompartir
    }).catch(() => {});
  } else {
    navigator.clipboard.writeText(textoCompartir);
    alert('¡Resumen del tema copiado al portapapeles para compartir! 📋✨');
  }
}

function iniciarEntrenamientoEnfocadoErrores(materiaKey) {
  const qErrores = [];
  Object.keys(estadoExamen.respuestasUsuario).forEach(qId => {
    const r = estadoExamen.respuestasUsuario[qId];
    if (!r.esCorrecta) {
      const qObj = filteredChoices.find(q => q.id === qId);
      if (qObj) qErrores.push(qObj);
    }
  });

  if (qErrores.length === 0) {
    alert("¡No tuviste errores en este examen! 🎉");
    return;
  }

  document.getElementById('resultados-modal').style.display = 'none';
  estadoExamen.modo = "PRACTICA_TP";
  filteredChoices = qErrores;
  currentChoiceIndex = 0;
  loadChoice();
}
"""

# Insert before '// MODO DE ESTUDIO Y REGLAS UNLP' or after 'let yaValidado = false;'
if "// MODO DE ESTUDIO Y REGLAS UNLP" in app_js:
    app_js = app_js.replace("// MODO DE ESTUDIO Y REGLAS UNLP", new_modules + "\n// MODO DE ESTUDIO Y REGLAS UNLP")

# Update entregarParcialManualmente to include diagnostic report
entregar_old = r'function entregarParcialManualmente\(\) \{[\s\S]*?cerrarResultados\(\)'

entregar_new = """function entregarParcialManualmente() {
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

function cerrarResultados()"""

app_js = re.sub(entregar_old, entregar_new, app_js)

with open("app.js", "w", encoding="utf-8") as f:
    f.write(app_js)

print("Patch applied successfully.")
