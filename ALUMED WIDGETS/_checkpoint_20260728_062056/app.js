/**
 * ALUMED OS — app.js
 * Toda la lógica de control de la SPA + Método Profe Joy.
 * Privacidad: nunca renderiza nombres de archivo, PDF, ruta ni página.
 */

// ─────────────────────────────────────────────────────────────
//  ESTADO GLOBAL
// ─────────────────────────────────────────────────────────────
let filteredChoices  = [];
let currentChoiceIndex = 0;
let selectedOption   = null;
let currentMateria   = "TODAS";
let currentPincheIndex = 0;
let yaValidado       = false;

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
//  NAVEGACIÓN DE TABS
// ─────────────────────────────────────────────────────────────
function switchTab(tabId) {
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
  const sec = document.getElementById(`tab-${tabId}`);
  const btn = document.getElementById(`btn-${tabId}`);
  if (sec) sec.classList.add('active');
  if (btn) btn.classList.add('active');
}

// ─────────────────────────────────────────────────────────────
//  FILTRO POR MATERIA
// ─────────────────────────────────────────────────────────────
function cambiarMateria(materia) {
  currentMateria = materia;
  filteredChoices = materia === "TODAS"
    ? [...bancoDados.choices]
    : bancoDados.choices.filter(q => q.materia === materia);
  currentChoiceIndex = 0;
  loadChoice();
  loadPinche();
}

// ─────────────────────────────────────────────────────────────
//  CARGA DE PREGUNTA (Multiple Choice)
// ─────────────────────────────────────────────────────────────
function loadChoice() {
  const fb = document.getElementById('mc-feedback');
  if (fb) { fb.innerHTML = ''; fb.className = 'feedback'; }
  selectedOption = null;
  yaValidado     = false;

  // Restaurar opciones a estado neutro
  document.querySelectorAll('.option-btn').forEach(b => {
    b.classList.remove('selected', 'correct-reveal', 'wrong-reveal');
    b.disabled = false;
  });

  if (!filteredChoices.length) {
    document.getElementById('mc-pergunta').innerText = 'No hay preguntas para esta cátedra.';
    document.getElementById('mc-opcoes').innerHTML   = '';
    document.getElementById('mc-counter').innerText  = 'Pregunta 0 de 0';
    return;
  }

  const q = filteredChoices[currentChoiceIndex];

  // Solo se muestra materia (nunca fuente/archivo)
  document.getElementById('mc-materia').innerText = q.materia;
  document.getElementById('mc-pergunta').innerText = q.pergunta;
  document.getElementById('mc-counter').innerText =
    `Pregunta ${currentChoiceIndex + 1} de ${filteredChoices.length}`;

  // Tema opcional, limpio
  const temaEl = document.getElementById('mc-tema');
  if (temaEl) temaEl.innerText = q.tema ? `Tema: ${q.tema}` : '';

  // Opciones
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
}

// ─────────────────────────────────────────────────────────────
//  VALIDACIÓN — MÉTODO PROFE JOY
// ─────────────────────────────────────────────────────────────
function validarChoice() {
  if (selectedOption === null || yaValidado) return;
  yaValidado = true;

  const q          = filteredChoices[currentChoiceIndex];
  const fb         = document.getElementById('mc-feedback');
  if (!fb) return;

  const esCorrecta  = selectedOption === q.correta;
  const letras      = ['A', 'B', 'C', 'D'];
  const letraEleg   = letras[selectedOption];
  const letraCorr   = letras[q.correta];

  // Colorear opciones y bloquearlas
  document.querySelectorAll('.option-btn').forEach((btn, idx) => {
    btn.disabled = true;
    btn.classList.remove('selected');
    if (idx === q.correta)    btn.classList.add('correct-reveal');
    else if (idx === selectedOption) btn.classList.add('wrong-reveal');
  });

  // Persistir
  guardarEnLocalStorage(q, selectedOption, esCorrecta);

  // Renderizar panel Joy
  fb.innerHTML  = generarPanelJoy(q, selectedOption, esCorrecta, letraEleg, letraCorr);
  fb.className  = 'feedback joy-active';

  // Scroll suave al feedback
  setTimeout(() => fb.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);
}

// ─────────────────────────────────────────────────────────────
//  GENERADOR PANEL PROFE JOY
// ─────────────────────────────────────────────────────────────
function generarPanelJoy(q, seleccionado, esCorrecta, letraEleg, letraCorr) {
  const j      = q.joy || {};
  const sinJoy = Object.keys(j).length === 0;
  const PLACEHOLDER = 'Este punto todavía no fue localizado en los apuntes ALUMED cargados.';

  // ── Encabezado de resultado ──
  const headerHTML = esCorrecta
    ? `<div class="joy-verdict correct-text">
         <i class="fa-solid fa-circle-check"></i>
         <span>¡Correcto! Elegiste <strong>${letraEleg}</strong>. ¡Exacta!</span>
       </div>`
    : `<div class="joy-verdict incorrect-text">
         <i class="fa-solid fa-circle-xmark"></i>
         <span>Incorrecto. Marcaste <strong>${letraEleg}</strong>.
         &nbsp;·&nbsp; Correcta: <strong class="correct-letter">${letraCorr}</strong>.</span>
       </div>`;

  const temaTag = q.tema
    ? `<div class="joy-tema-tag"><i class="fa-solid fa-tag"></i> ${q.tema}</div>`
    : '';

  // ── Sin bloque Joy: mensaje simple ──
  if (sinJoy) {
    return `
      <div class="joy-panel ${esCorrecta ? 'joy-correct' : 'joy-incorrect'}">
        <div class="joy-header">${headerHTML}${temaTag}</div>
        <div class="joy-block">
          <div class="joy-block-body">${q.justificativa || PLACEHOLDER}</div>
        </div>
        <div class="joy-fuente"><i class="fa-solid fa-book-open"></i> ${etiquetaFuentePublica(q)}</div>
        ${renderJoyActions(q)}
      </div>`;
  }

  // ── Secciones adaptadas por materia ──
  let seccionesHTML = '';
  const m = q.materia || '';

  if (m.includes('Biología')) {
    seccionesHTML = `
      ${joyBlock('🔬', '¿Qué es?',            j.queEs      || PLACEHOLDER)}
      ${joyBlock('📍', '¿Dónde se encuentra?', j.dondeSe    || PLACEHOLDER)}
      ${joyBlock('🏗️', 'Estructura',           j.estructura || PLACEHOLDER)}
      ${joyBlock('⚙️', 'Función',              j.funcion    || PLACEHOLDER)}
      ${joyBlock('🔄', 'Mecanismo básico',     j.mecanismo  || PLACEHOLDER)}
      ${joyBlock('💥', '¿Qué ocurre si falla?',j.siFalla    || PLACEHOLDER)}`;

  } else if (m.includes('Histología') && !(j.origenEmb || j.cuandoAparece)) {
    // Histología general (no embriología)
    seccionesHTML = `
      ${joyBlock('🧫', 'Tejido / Órgano',              j.tejido    || PLACEHOLDER)}
      ${joyBlock('🔬', 'Células principales',           j.celulas   || PLACEHOLDER)}
      ${joyBlock('📋', 'Capas y organización',          j.capasOrg  || PLACEHOLDER)}
      ${joyBlock('🎨', 'Tinción y características',     j.tincion   || PLACEHOLDER)}
      ${joyBlock('⚙️', 'Función',                      j.funcion   || PLACEHOLDER)}
      ${joyBlock('👁️', 'Cómo reconocerlo en la lámina',j.reconocer || PLACEHOLDER)}`;

  } else if (m.includes('Embriología') || m.includes('Histología')) {
    // Histología y Embriología — detectar si es pregunta embriológica
    const esEmbrio = !!(j.origenEmb || j.cuandoAparece || j.etapas || j.derivados);
    if (esEmbrio) {
      seccionesHTML = `
        ${joyBlock('🥚', '¿Qué estructura es?',          j.estructura   || j.queEs || PLACEHOLDER)}
        ${joyBlock('🌱', 'Origen embrionario',            j.origenEmb    || PLACEHOLDER)}
        ${joyBlock('📅', '¿Cuándo aparece?',              j.cuandoAparece|| PLACEHOLDER)}
        ${joyBlock('🔄', 'Etapas y transformaciones',     j.etapas       || PLACEHOLDER)}
        ${joyBlock('🌿', 'Derivados',                     j.derivados    || PLACEHOLDER)}
        ${joyBlock('👁️', 'Cómo reconocerla en un esquema',j.reconocer   || PLACEHOLDER)}`;
    } else {
      seccionesHTML = `
        ${joyBlock('🧫', 'Tejido / Órgano',              j.tejido    || PLACEHOLDER)}
        ${joyBlock('🔬', 'Células principales',           j.celulas   || PLACEHOLDER)}
        ${joyBlock('📋', 'Capas y organización',          j.capasOrg  || PLACEHOLDER)}
        ${joyBlock('🎨', 'Tinción y características',     j.tincion   || PLACEHOLDER)}
        ${joyBlock('⚙️', 'Función',                      j.funcion   || PLACEHOLDER)}
        ${joyBlock('👁️', 'Cómo reconocerlo',             j.reconocer || PLACEHOLDER)}`;
    }

  } else if (m.includes('Anatomía')) {
    seccionesHTML = `
      ${joyBlock('🦴', '¿Qué es?',                     j.queEs       || PLACEHOLDER)}
      ${joyBlock('📍', 'Ubicación',                     j.ubicacion   || PLACEHOLDER)}
      ${joyBlock('🔧', 'Partes',                        j.partes      || PLACEHOLDER)}
      ${joyBlock('🔗', 'Relaciones',                    j.relaciones  || PLACEHOLDER)}
      ${joyBlock('🩸', 'Irrigación e inervación',       j.irrigInnerv || PLACEHOLDER)}
      ${joyBlock('👁️', 'Cómo reconocerlo en un pinche', j.reconocer  || PLACEHOLDER)}`;
  }

  // ── Por qué incorrectas ──
  let incorrectasHTML = '';
  if (Array.isArray(j.porQueNoCorrectas) && j.porQueNoCorrectas.length) {
    const letras = ['A', 'B', 'C', 'D'];
    const items  = j.porQueNoCorrectas.map((txt, i) => {
      if (i === q.correta) {
        return `<li class="incorrecta-item correcta-item"><strong>${letras[i]})</strong> ✅ Esta es la correcta.</li>`;
      }
      return `<li class="incorrecta-item"><strong>${letras[i]})</strong> ${txt || PLACEHOLDER}</li>`;
    }).join('');
    incorrectasHTML = `
      <div class="joy-no-correctas">
        <div class="joy-section-title">
          <i class="fa-solid fa-magnifying-glass"></i> ¿Por qué tu opción no es correcta?
        </div>
        <ul>${items}</ul>
      </div>`;
  }

  // ── Clave + Trampa ──
  const claveHTML = `
    <div class="joy-exam-row">
      <div class="joy-clave">
        <div class="joy-block-title"><i class="fa-solid fa-key"></i> La clave para el examen</div>
        <p>${j.examen || PLACEHOLDER}</p>
      </div>
      <div class="joy-trampa">
        <div class="joy-block-title"><i class="fa-solid fa-triangle-exclamation"></i> Ojo con la trampa</div>
        <p>${j.trampa || PLACEHOLDER}</p>
      </div>
    </div>`;

  // ── Fuente pública (nunca el nombre real del archivo) ──
  const fuentePublica = etiquetaFuentePublica(q);
  const tieneFragmento = !!(q.fragmentoApunte && q.fragmentoApunte.trim());
  const fuenteHTML = `
    <div class="joy-fuente">
      <i class="fa-solid fa-book-open"></i> ${fuentePublica}
      ${tieneFragmento
        ? `<button class="btn-fragmento" onclick="abrirFragmento(${q.id})">
             <i class="fa-solid fa-file-lines"></i> Ver fragmento del apunte
           </button>`
        : ''}
    </div>`;

  return `
    <div class="joy-panel ${esCorrecta ? 'joy-correct' : 'joy-incorrect'}">
      <div class="joy-header">${headerHTML}${temaTag}</div>
      <div class="joy-metodo-header">
        <i class="fa-solid fa-brain"></i> Entendamos juntos — <strong>Método Profe Joy</strong>
      </div>
      <div class="joy-sections">${seccionesHTML}</div>
      ${incorrectasHTML}
      ${claveHTML}
      ${fuenteHTML}
      ${renderJoyActions(q)}
    </div>`;
}

// Helper: bloque individual
function joyBlock(emoji, titulo, contenido) {
  if (!contenido) return '';
  return `
    <div class="joy-block">
      <div class="joy-block-title">${emoji} ${titulo}</div>
      <div class="joy-block-body">${contenido}</div>
    </div>`;
}

// Helper: botones de acción (sin datos internos en el HTML)
function renderJoyActions(q) {
  return `
    <div class="joy-actions">
      <button class="btn-action btn-flashcard" onclick="crearFlashcard(${q.id})">
        <i class="fa-solid fa-layer-group"></i> Crear flashcard
      </button>
      <button class="btn-action btn-repaso" onclick="agregarRepaso(${q.id})">
        <i class="fa-solid fa-rotate"></i> Agregar a repaso de errores
      </button>
      <button class="btn-action btn-parecida" onclick="practicarParecida(${q.id})">
        <i class="fa-solid fa-shuffle"></i> Practicar otra parecida
      </button>
    </div>`;
}

// ─────────────────────────────────────────────────────────────
//  MODAL FRAGMENTO — Solo muestra contenido, nunca nombre de archivo
// ─────────────────────────────────────────────────────────────
function abrirFragmento(qId) {
  const q = bancoDados.choices.find(x => x.id === qId);
  if (!q) return;
  const modal  = document.getElementById('fragmento-modal');
  const titulo = document.getElementById('fragmento-titulo');
  const cuerpo = document.getElementById('fragmento-cuerpo');
  const fuente = document.getElementById('fragmento-fuente');

  // Título: solo tema académico, nunca nombre de archivo
  if (titulo) titulo.innerText = q.tema || 'Fragmento ALUMED';
  // Cuerpo: el texto del apunte
  if (cuerpo) cuerpo.innerText = q.fragmentoApunte && q.fragmentoApunte.trim()
    ? q.fragmentoApunte
    : 'Este punto todavía no fue localizado en los apuntes ALUMED cargados.';
  // Pie: etiqueta genérica, nunca nombre real de archivo
  if (fuente) fuente.innerText = etiquetaFuentePublica(q);

  modal.classList.add('open');
}

function cerrarFragmento() {
  const modal = document.getElementById('fragmento-modal');
  if (modal) modal.classList.remove('open');
}

// ─────────────────────────────────────────────────────────────
//  PERSISTENCIA — localStorage
// ─────────────────────────────────────────────────────────────
function guardarEnLocalStorage(q, seleccionado, esCorrecta) {
  const letras = ['A', 'B', 'C', 'D'];
  const registro = {
    id:                 q.id,
    pregunta:           q.pergunta,
    materia:            q.materia,
    tema:               q.tema   || '',
    subtema:            q.subtema || '',
    alternativaElegida: letras[seleccionado],
    alternativaCorrecta:letras[q.correta],
    explicacion:        q.justificativa || '',
    esCorrecta:         esCorrecta,
    fecha:              new Date().toISOString(),
    intentos:           1
    // ⚠️ No se almacena: archivo, pagina, fuente real, ruta
  };

  // Historial general
  let historial  = JSON.parse(localStorage.getItem('alumed_historial') || '[]');
  const idx      = historial.findIndex(r => r.id === q.id);
  if (idx >= 0) {
    historial[idx].intentos++;
    historial[idx].esCorrecta = esCorrecta;
    historial[idx].fecha      = registro.fecha;
  } else {
    historial.push(registro);
  }
  localStorage.setItem('alumed_historial', JSON.stringify(historial));

  // Auto-repaso si incorrecta
  if (!esCorrecta) agregarRepaso(q.id, registro);
}

function crearFlashcard(qId) {
  const q = bancoDados.choices.find(x => x.id === qId);
  if (!q) return;
  let fc = JSON.parse(localStorage.getItem('alumed_flashcards') || '[]');
  if (fc.find(f => f.id === q.id)) {
    mostrarToast('Ya existe esta flashcard en tu mazo 🃏');
    return;
  }
  fc.push({
    id:      q.id,
    frente:  q.pergunta,
    dorso:   q.opcoes[q.correta] + '\n\n' + (q.justificativa || ''),
    materia: q.materia,
    tema:    q.tema || ''
    // sin archivo, sin fuente real
  });
  localStorage.setItem('alumed_flashcards', JSON.stringify(fc));
  mostrarToast('✅ Flashcard guardada en tu mazo');
}

function agregarRepaso(qId, registroExtra) {
  const q = bancoDados.choices.find(x => x.id === qId);
  if (!q) return;
  let repaso = JSON.parse(localStorage.getItem('alumed_errores') || '[]');
  if (!repaso.find(r => r.id === q.id)) {
    repaso.push(registroExtra || {
      id:      q.id,
      pregunta:q.pergunta,
      materia: q.materia,
      tema:    q.tema || ''
    });
    localStorage.setItem('alumed_errores', JSON.stringify(repaso));
    mostrarToast('📌 Agregada a tu sesión de repaso de errores');
  } else {
    mostrarToast('Ya estaba en tu lista de repaso');
  }
}

function practicarParecida(qId) {
  const q = bancoDados.choices.find(x => x.id === qId);
  if (!q) return;
  let candidatos = filteredChoices.filter(c =>
    c.id !== qId && (c.materia === q.materia || c.tema === q.tema)
  );
  if (!candidatos.length) candidatos = filteredChoices.filter(c => c.id !== qId && c.materia === q.materia);
  if (!candidatos.length) candidatos = filteredChoices.filter(c => c.id !== qId);
  if (!candidatos.length) { mostrarToast('No hay más preguntas disponibles'); return; }
  const aleatorio = candidatos[Math.floor(Math.random() * candidatos.length)];
  currentChoiceIndex = filteredChoices.findIndex(c => c.id === aleatorio.id);
  loadChoice();
  window.scrollTo({ top: 0, behavior: 'smooth' });
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
function sortearOral() {
  const rawOrales = currentMateria === "TODAS"
    ? bancoDados.orales
    : bancoDados.orales.filter(b => b.materia === currentMateria);
  if (!rawOrales.length) {
    alert('No hay bolillas para la cátedra seleccionada.');
    return;
  }
  const o    = rawOrales[Math.floor(Math.random() * rawOrales.length)];
  const card = document.getElementById('oral-card');
  if (card) card.style.display = 'block';
  const matEl = document.getElementById('oral-materia');
  if (matEl) matEl.innerText = o.materia; // solo materia
  document.getElementById('oral-bolilla').innerText = o.bolilla;
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

