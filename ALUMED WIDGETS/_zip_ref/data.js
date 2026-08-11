/* Banco demostrativo. Al procesar tus PDFs, conserva fuente, pagina y fragmentoApunte. */
const bancoDados = {
  choices: [
    {
      id: 1,
      materia: "Biología Celular",
      tema: "Retículo Endoplásmico Liso",
      fuente: "Apunte Profe Joy — Biología Celular",
      pagina: "p. 42",
      fragmentoApunte: "El retículo endoplásmico liso carece de ribosomas adheridos. Participa en la síntesis de lípidos, detoxificación y almacenamiento de calcio.",
      pergunta: "¿Cuál es una función característica del retículo endoplásmico liso?",
      opcoes: [
        "Síntesis de proteínas de exportación",
        "Síntesis de lípidos y detoxificación",
        "Producción de ATP por fosforilación oxidativa",
        "Modificación y clasificación de proteínas"
      ],
      correta: 1,
      justificativa: "El REL sintetiza lípidos, participa en detoxificación y almacena calcio.",
      joy: {
        queEs: "Es una red de túbulos membranosos que no tiene ribosomas adheridos.",
        dondeSe: "Está en el citoplasma y es especialmente abundante en hepatocitos, células esteroidogénicas y músculo.",
        estructura: "Forma una red tubular continua con el retículo endoplásmico rugoso.",
        funcion: "Sintetiza lípidos, participa en detoxificación y almacena calcio.",
        mecanismo: "Sus enzimas de membrana producen lípidos y modifican sustancias liposolubles; en músculo libera y recupera Ca²⁺.",
        siFalla: "Se altera el metabolismo lipídico, la detoxificación o el control del calcio, según la célula.",
        examen: "REL = lípidos, detoxificación y calcio. RER = proteínas.",
        trampa: "No confundas ausencia de ribosomas con falta de actividad: el REL es muy activo metabólicamente.",
        porQueNoCorrectas: [
          "La síntesis de proteínas de exportación ocurre principalmente en ribosomas asociados al RER.",
          "",
          "La fosforilación oxidativa ocurre en la membrana interna mitocondrial.",
          "La modificación y clasificación final de proteínas corresponde principalmente al aparato de Golgi."
        ]
      }
    },
    {
      id: 2,
      materia: "Embriología",
      tema: "Gastrulación y neurulación",
      fuente: "Apunte ALUMED — Embriología",
      pagina: "p. 18",
      fragmentoApunte: "La notocorda actúa como centro inductor del neuroectodermo suprayacente y establece el eje longitudinal del embrión.",
      pergunta: "¿Qué estructura induce principalmente la formación de la placa neural?",
      opcoes: [
        "Saco vitelino secundario",
        "Notocorda",
        "Alantoides",
        "Mesodermo lateral"
      ],
      correta: 1,
      justificativa: "La notocorda induce al ectodermo suprayacente para formar la placa neural.",
      joy: {
        estructura: "La notocorda es una estructura axial transitoria ubicada en la línea media.",
        origenEmb: "Se origina a partir de células del epiblasto que ingresan por el nodo primitivo.",
        cuandoAparece: "Se organiza durante la tercera semana, en el contexto de la gastrulación.",
        etapas: "Proceso notocordal → placa notocordal → notocorda definitiva.",
        derivados: "Persiste principalmente como núcleo pulposo de los discos intervertebrales.",
        reconocer: "En un corte, buscala en la línea media, ventral al tubo neural y dorsal al intestino primitivo.",
        examen: "Notocorda abajo → induce placa neural arriba.",
        trampa: "El mesodermo paraxial acompaña el eje y forma somitas, pero el inductor axial clave es la notocorda.",
        porQueNoCorrectas: [
          "El saco vitelino participa en nutrición inicial y hematopoyesis temprana, pero no induce la placa neural.",
          "",
          "El alantoides se relaciona con el desarrollo vascular y estructuras urinarias tempranas, no con la inducción neural.",
          "El mesodermo lateral origina, entre otros, serosas y componentes cardiovasculares; no es el inductor principal."
        ]
      }
    },
    {
      id: 3,
      materia: "Embriología",
      tema: "Gastrulación y neurulación",
      fuente: "Apunte ALUMED — Embriología",
      pagina: "p. 19",
      fragmentoApunte: "Los pliegues neurales se elevan y fusionan, transformando la placa neural en el tubo neural.",
      pergunta: "¿Qué proceso transforma la placa neural en el tubo neural?",
      opcoes: ["Segmentación", "Neurulación", "Implantación", "Delaminación del hipoblasto"],
      correta: 1,
      justificativa: "Durante la neurulación los pliegues neurales se fusionan y forman el tubo neural.",
      joy: {
        estructura: "La placa neural es un engrosamiento de neuroectodermo que se pliega para formar el tubo neural.",
        origenEmb: "Proviene del ectodermo inducido por señales de la notocorda.",
        cuandoAparece: "Comienza hacia el final de la tercera semana.",
        etapas: "Placa neural → surco y pliegues neurales → fusión → cierre de neuroporos.",
        derivados: "El tubo neural origina el sistema nervioso central.",
        reconocer: "Identificá un surco central con pliegues elevados que luego se unen dorsalmente.",
        examen: "Neurulación = formación y cierre del tubo neural.",
        trampa: "No confundas neurulación con gastrulación: la gastrulación forma las tres capas germinales.",
        porQueNoCorrectas: [
          "La segmentación divide el cigoto en blastómeros antes de la implantación.",
          "",
          "La implantación fija el blastocisto al endometrio.",
          "La delaminación del hipoblasto no produce el tubo neural."
        ]
      }
    }
  ]
};

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
    "Histología": [
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
    ]
  };
  return mapas[materia] || mapas["Biología Celular"];
}

function generarPanelJoy(q, seleccionado) {
  const correcta = seleccionado === q.correta;
  const joy = q.joy || {};
  const secciones = etiquetasJoy(q.materia)
    .filter(([campo]) => joy[campo])
    .map(([campo, titulo, icono]) => `
      <div class="joy-section">
        <span class="joy-icon" aria-hidden="true">${icono}</span>
        <div><h4>${escaparHTML(titulo)}</h4><p>${escaparHTML(joy[campo])}</p></div>
      </div>`).join("");

  const razones = q.opcoes.map((opcion, indice) => {
    if (indice === q.correta) return "";
    const texto = joy.porQueNoCorrectas?.[indice] || "Esta opción no corresponde al concepto evaluado.";
    return `<li><strong>${letraOpcion(indice)}. ${escaparHTML(opcion)}:</strong> ${escaparHTML(texto)}</li>`;
  }).join("");

  return `
    <article class="joy-panel ${correcta ? "is-correct" : "is-wrong"}">
      <header class="joy-header">
        <div class="result-icon">${correcta ? "✓" : "×"}</div>
        <div>
          <span>${correcta ? "¡Correcto! — Profe Joy" : "Vamos a entenderlo — Profe Joy"}</span>
          <h3>${correcta
            ? `Marcaste ${letraOpcion(seleccionado)} y es la respuesta correcta.`
            : `Marcaste ${letraOpcion(seleccionado)}. La correcta es ${letraOpcion(q.correta)}.`}</h3>
        </div>
      </header>

      <div class="joy-title">
        <span class="joy-avatar">JOY</span>
        <div><span>Entendamos juntos</span><h3>Método Profe Joy</h3></div>
      </div>

      <div class="joy-grid">${secciones}</div>

      ${joy.examen ? `<div class="joy-clave"><span>🧠</span><div><h4>La clave para el examen</h4><p>${escaparHTML(joy.examen)}</p></div></div>` : ""}
      ${joy.trampa ? `<div class="joy-trampa"><span>⚠️</span><div><h4>Ojo con la trampa</h4><p>${escaparHTML(joy.trampa)}</p></div></div>` : ""}

      <div class="joy-no-correctas">
        <h4>¿Por qué las otras opciones no son correctas?</h4>
        <ul>${razones}</ul>
      </div>

      <div class="joy-fuente">
        <div>
          <strong>Material de estudio</strong>
          <span>Explicación basada en materiales ALUMED.</span>
        </div>
        ${q.fragmentoApunte ? `<button class="btn-link" type="button" data-action="fragmento">Ver fragmento del apunte</button>` : ""}
      </div>

      <div class="joy-actions">
        <button class="btn btn-action-flashcard" type="button" data-action="flashcard">＋ Crear flashcard</button>
        <button class="btn btn-action-repaso" type="button" data-action="repaso">↻ Agregar a repaso</button>
        <button class="btn btn-action-parecida" type="button" data-action="parecida">⤴ Practicar parecida</button>
      </div>
    </article>`;
}

function guardarEnLocalStorage(q, seleccionado) {
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
    fuente: q.fuente || "",
    pagina: q.pagina || "",
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

function crearFlashcard(q) {
  const flashcards = leerStorage(STORAGE_KEYS.flashcards);
  if (!flashcards.some(item => item.preguntaId === q.id)) {
    flashcards.push({
      id: `fc-${q.id}-${Date.now()}`,
      preguntaId: q.id,
      frente: q.pergunta,
      reverso: `${q.opcoes[q.correta]}. ${q.justificativa || ""}`,
      materia: q.materia,
      tema: q.tema,
      fuente: q.fuente || "",
      pagina: q.pagina || "",
      nivel: 0,
      proximoRepaso: new Date().toISOString()
    });
    escribirStorage(STORAGE_KEYS.flashcards, flashcards);
    return "Flashcard creada";
  }
  return "Esta flashcard ya existe";
}

function agregarRepaso(q) {
  const repaso = leerStorage(STORAGE_KEYS.repaso);
  if (!repaso.some(item => item.preguntaId === q.id)) {
    repaso.push({
      preguntaId: q.id, materia: q.materia, tema: q.tema,
      agregado: new Date().toISOString(), completado: false
    });
    escribirStorage(STORAGE_KEYS.repaso, repaso);
    return "Agregada al repaso";
  }
  return "Ya está en tu repaso";
}

function buscarParecida(q) {
  return bancoDados.choices.find(item =>
    item.id !== q.id && item.materia === q.materia && item.tema === q.tema
  ) || bancoDados.choices.find(item => item.id !== q.id && item.materia === q.materia);
}
