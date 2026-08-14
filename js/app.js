/* ═════════════════════════════════════════════════════════════════
   CONECTA FCM — EDICIÓN DOURADO
   Main Interactive Application Controller
   ═════════════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  initSearch();
  renderNoticiasWidget();
  renderNoticiasSection('todos');
  renderBiblioteca('todos');
  renderExamenes();
  initCalculadora();
  initInteractiveMap();
  initAiAssistant();
  initModalListeners();
});

/* ── 1. Navigation & Tab Switching ── */
function initNavigation() {
  const tabs = document.querySelectorAll('.nav-tab');
  const sections = document.querySelectorAll('.section-block');
  const mobileToggle = document.getElementById('mobileNavToggle');
  const navMenu = document.getElementById('navMenu');

  tabs.forEach(tab => {
    tab.addEventListener('click', (e) => {
      const targetId = tab.getAttribute('data-target');
      if (!targetId) return;
      e.preventDefault();

      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');

      if (targetId === 'hero') {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        return;
      }

      const targetSection = document.getElementById(targetId);
      if (targetSection) {
        targetSection.scrollIntoView({ behavior: 'smooth' });
      }

      if (navMenu && navMenu.classList.contains('show')) {
        navMenu.classList.remove('show');
      }
    });
  });

  if (mobileToggle && navMenu) {
    mobileToggle.addEventListener('click', () => {
      navMenu.classList.toggle('show');
    });
  }
}

/* ── 2. Live Search across Cartelera and Biblioteca ── */
function initSearch() {
  const searchInput = document.getElementById('globalSearchInput');
  if (!searchInput) return;

  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase().trim();
    filterNoticiasByQuery(query);
    filterBibliotecaByQuery(query);
  });
}

function filterNoticiasByQuery(query) {
  const filtered = CONECTA_DATA.noticias.filter(n => 
    n.titulo.toLowerCase().includes(query) ||
    n.catedra.toLowerCase().includes(query) ||
    n.resumen.toLowerCase().includes(query)
  );
  renderNoticiasGrid(filtered);
}

function filterBibliotecaByQuery(query) {
  const filtered = CONECTA_DATA.biblioteca.filter(b =>
    b.titulo.toLowerCase().includes(query) ||
    b.categoria.toLowerCase().includes(query) ||
    b.descripcion.toLowerCase().includes(query)
  );
  renderBibliotecaGrid(filtered);
}

/* ── 3. Render Cartelera Live Widget ── */
function renderNoticiasWidget() {
  const widgetContainer = document.getElementById('widgetNoticiasList');
  if (!widgetContainer) return;

  const topNoticias = CONECTA_DATA.noticias.slice(0, 4);
  widgetContainer.innerHTML = topNoticias.map(n => `
    <div class="widget-notice-item" onclick="openNoticeModal(${n.id})">
      <span class="notice-tag ${n.urgente ? 'tag-urgente' : 'tag-parcial'}">${n.catedra}</span>
      <h4 class="notice-title-text">${n.titulo}</h4>
      <div class="notice-meta-text">
        <span><i class="far fa-calendar-alt"></i> ${n.fecha}</span>
        <span><i class="fas fa-graduation-cap"></i> ${n.anio}</span>
      </div>
    </div>
  `).join('');
}

/* ── 4. Render Main Cartelera Section & Filtering ── */
function renderNoticiasSection(filtro = 'todos') {
  const container = document.getElementById('noticiasGrid');
  if (!container) return;

  let noticias = CONECTA_DATA.noticias;
  if (filtro !== 'todos') {
    noticias = noticias.filter(n => n.tipo === filtro || (filtro === '1er' && n.anio === '1er Año'));
  }

  renderNoticiasGrid(noticias);
  initNoticiasFilterButtons();
}

function renderNoticiasGrid(noticias) {
  const container = document.getElementById('noticiasGrid');
  if (!container) return;

  if (noticias.length === 0) {
    container.innerHTML = `<p style="color:var(--text-muted); grid-column:1/-1;">No se encontraron avisos que coincidan con la búsqueda.</p>`;
    return;
  }

  container.innerHTML = noticias.map(n => `
    <div class="book-card" onclick="openNoticeModal(${n.id})">
      <div>
        <div style="display:flex; justify-shadow:space-between; align-items:center; margin-bottom:8px;">
          <span class="notice-tag ${n.urgente ? 'tag-urgente' : 'tag-catedra'}">${n.catedra}</span>
          <span style="font-size:0.65rem; color:var(--text-muted);">${n.fecha}</span>
        </div>
        <h3 class="book-title" style="font-size:0.95rem;">${n.titulo}</h3>
        <p class="book-desc">${n.resumen}</p>
      </div>
      <div class="book-actions" style="margin-top:14px;">
        <button class="btn-card-action"><i class="fas fa-eye"></i> Leer Aviso</button>
      </div>
    </div>
  `).join('');
}

function initNoticiasFilterButtons() {
  const filterBtns = document.querySelectorAll('.filter-btn-cartelera');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const filter = btn.getAttribute('data-filter');
      renderNoticiasSection(filter);
    });
  });
}

/* ── 5. Render Biblioteca Digital Dourada ── */
function renderBiblioteca(filtro = 'todos') {
  let libros = CONECTA_DATA.biblioteca;
  if (filtro !== 'todos') {
    libros = libros.filter(b => b.anio.toLowerCase().includes(filtro.toLowerCase()) || b.categoria.toLowerCase().includes(filtro.toLowerCase()));
  }
  renderBibliotecaGrid(libros);
  initBibliotecaFilterButtons();
}

function renderBibliotecaGrid(libros) {
  const container = document.getElementById('bibliotecaGrid');
  if (!container) return;

  if (libros.length === 0) {
    container.innerHTML = `<p style="color:var(--text-muted); grid-column:1/-1;">No hay libros en esta categoría.</p>`;
    return;
  }

  container.innerHTML = libros.map(b => `
    <div class="book-card">
      <div>
        <span class="book-year-badge">${b.anio} — ${b.categoria}</span>
        <h3 class="book-title">${b.titulo}</h3>
        <p class="book-desc">${b.descripcion}</p>
        <div style="font-size:0.72rem; color:var(--gold-primary); margin-bottom:12px;">
          <i class="fas fa-file-pdf"></i> ${b.paginas} páginas • ${b.formato}
        </div>
      </div>
      <div class="book-actions">
        <button class="btn-card-action" onclick="openBookReaderModal('${b.id}')"><i class="fas fa-book-open"></i> Leer PDF</button>
        <button class="btn-card-action" onclick="generateAiBookSummary('${b.id}')" style="background:rgba(192, 132, 252, 0.1); border-color:rgba(192, 132, 252, 0.3); color:var(--amethyst);"><i class="fas fa-wand-magic-sparkles"></i> Resumen IA</button>
      </div>
    </div>
  `).join('');
}

function initBibliotecaFilterButtons() {
  const filterBtns = document.querySelectorAll('.filter-btn-biblio');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const filter = btn.getAttribute('data-filter');
      renderBiblioteca(filter);
    });
  });
}

/* ── 6. Render Cronograma de Exámenes con Countdowns ── */
function renderExamenes() {
  const container = document.getElementById('examenesGrid');
  if (!container) return;

  const now = new Date();

  container.innerHTML = CONECTA_DATA.examenes.map(e => {
    const examDate = new Date(e.fecha + 'T00:00:00');
    const diffTime = examDate - now;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    const isSoon = diffDays <= 15 && diffDays >= 0;

    return `
      <div class="book-card" style="border-left: 4px solid ${isSoon ? 'var(--gold-primary)' : 'var(--sapphire)'};">
        <div>
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
            <span class="gold-badge">${e.estado}</span>
            <span style="font-size:0.75rem; font-weight:800; color:${isSoon ? 'var(--gold-primary)' : 'var(--emerald)'};">
              ${diffDays > 0 ? `Faltan ${diffDays} días` : '¡Hoy!'}
            </span>
          </div>
          <h3 class="book-title">${e.materia}</h3>
          <div style="font-size:0.82rem; color:var(--text-secondary); margin-bottom:6px;">
            <i class="fas fa-file-signature"></i> <strong>${e.tipo}</strong>
          </div>
          <div style="font-size:0.78rem; color:var(--text-muted);">
            <i class="far fa-clock"></i> ${e.fecha} — ${e.hora}
          </div>
          <div style="font-size:0.78rem; color:var(--text-muted); margin-top:4px;">
            <i class="fas fa-location-dot"></i> ${e.aula}
          </div>
        </div>
      </div>
    `;
  }).join('');
}

/* ── 7. Calculadora de Promedio FCM ── */
function initCalculadora() {
  const listContainer = document.getElementById('calcSubjectList');
  if (!listContainer) return;

  listContainer.innerHTML = CONECTA_DATA.materiasCalculadora.map(m => `
    <div class="calc-row">
      <div>
        <div class="calc-name">${m.nombre}</div>
        <div style="font-size:0.68rem; color:var(--text-muted);">${m.anio} • ${m.horas} hs</div>
      </div>
      <select class="calc-select mark-selector" data-id="${m.id}" onchange="recalculateAverage()">
        <option value="0">Sin cursar</option>
        <option value="4">4 (Cuatro)</option>
        <option value="5">5 (Cinco)</option>
        <option value="6">6 (Seis)</option>
        <option value="7">7 (Siete)</option>
        <option value="8">8 (Ocho)</option>
        <option value="9">9 (Nueve)</option>
        <option value="10">10 (Diez)</option>
      </select>
    </div>
  `).join('');

  recalculateAverage();
}

function recalculateAverage() {
  const selectors = document.querySelectorAll('.mark-selector');
  let totalMarks = 0;
  let count = 0;

  selectors.forEach(select => {
    const val = parseFloat(select.value);
    if (val > 0) {
      totalMarks += val;
      count++;
    }
  });

  const avgDisplay = document.getElementById('calcAverageResult');
  const countDisplay = document.getElementById('calcCountResult');

  if (avgDisplay) {
    avgDisplay.innerText = count > 0 ? (totalMarks / count).toFixed(2) : '0.00';
  }

  if (countDisplay) {
    countDisplay.innerText = `${count} de ${CONECTA_DATA.materiasCalculadora.length} materias aprobadas`;
  }
}

/* ── 8. Mapa Interactivo FCM ── */
function initInteractiveMap() {
  const canvas = document.getElementById('mapVisualCanvas');
  const detailBox = document.getElementById('mapDetailBox');
  if (!canvas || !detailBox) return;

  canvas.innerHTML = CONECTA_DATA.ubicaciones.map((u, index) => `
    <div class="map-building-block ${index === 0 ? 'active' : ''}" onclick="selectBuilding('${u.id}')">
      <i class="fas ${u.icono} building-icon"></i>
      <div class="building-title">${u.nombre}</div>
    </div>
  `).join('');

  selectBuilding(CONECTA_DATA.ubicaciones[0].id);
}

function selectBuilding(id) {
  const location = CONECTA_DATA.ubicaciones.find(u => u.id === id);
  if (!location) return;

  const blocks = document.querySelectorAll('.map-building-block');
  blocks.forEach(b => b.classList.remove('active'));

  const detailBox = document.getElementById('mapDetailBox');
  if (detailBox) {
    detailBox.innerHTML = `
      <h3 style="font-family:'Cinzel',serif; color:var(--gold-primary); margin-bottom:6px;">${location.nombre}</h3>
      <span class="gold-badge" style="margin-bottom:12px;">${location.categoria}</span>
      <p style="font-size:0.85rem; color:var(--text-secondary); line-height:1.5; margin-bottom:12px;">${location.descripcion}</p>
      <div style="font-size:0.78rem; color:var(--text-muted);">
        <i class="fas fa-compass"></i> <strong>Ubicación:</strong> ${location.piso}
      </div>
    `;
  }
}

/* ── 9. Asistente IA Dourado Chatbot Logic ── */
function initAiAssistant() {
  const input = document.getElementById('chatInput');
  const sendBtn = document.getElementById('chatSendBtn');

  if (sendBtn && input) {
    sendBtn.addEventListener('click', () => sendUserMessage());
    input.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') sendUserMessage();
    });
  }
}

function sendUserMessage(customText = null) {
  const input = document.getElementById('chatInput');
  const history = document.getElementById('chatHistory');
  const text = customText || (input ? input.value.trim() : '');

  if (!text || !history) return;

  // Append user bubble
  const userBubble = document.createElement('div');
  userBubble.className = 'chat-bubble user';
  userBubble.innerText = text;
  history.appendChild(userBubble);

  if (input) input.value = '';
  history.scrollTop = history.scrollHeight;

  // Simulate AI Response
  setTimeout(() => {
    const botBubble = document.createElement('div');
    botBubble.className = 'chat-bubble bot';
    botBubble.innerHTML = generateAiResponseText(text);
    history.appendChild(botBubble);
    history.scrollTop = history.scrollHeight;
  }, 700);
}

function generateAiResponseText(query) {
  const q = query.toLowerCase();

  if (q.includes('henle') || q.includes('asa')) {
    return `<strong>Asistente IA Dourado:</strong> El <em>Asa de Henle</em> es la porción de la nefrona que conecta el túbulo contorneado proximal con el distal.<br>1. <strong>Rama Descendente:</strong> Muy permeable al agua e impermeable a solutos.<br>2. <strong>Rama Ascendente Gruesa:</strong> Transporta activamente Na+/K+/2Cl- hacia el intersticio medular creando el gradiente osmótico multiplicador por contracorriente.`;
  }

  if (q.includes('histología') || q.includes('epitelio')) {
    return `<strong>Asistente IA Dourado:</strong> Para el final de Histología, recordá los 4 tejidos fundamentales: Epitelial, Conectivo, Muscular y Nervioso. Poné especial foco en la clasificación morfológica de los epitelios de revestimiento y las especializaciones de la membrana apical (cilias, microvellosidades, estereocilias).`;
  }

  if (q.includes(' shock') || q.includes('anafiláctico')) {
    return `<strong>Asistente IA Dourado:</strong> El shock anafiláctico es una reacción de hipersensibilidad Tipo I mediada por IgE. Causa degranulación masiva de mastocitos y basófilos liberando histamina. Tratamiento de primera línea: <strong>Adrenalina intramuscular</strong> (0.3 - 0.5 mg).`;
  }

  return `<strong>Asistente IA Dourado:</strong> He analizado tu consulta sobre "<em>${query}</em>" en la base de datos clínica de la FCM. ¿Querés que busque resúmenes de biblioteca, guías prácticas o preguntas frecuentes de exámenes finales relacionadas?`;
}

function triggerPrompt(promptText) {
  sendUserMessage(promptText);
}

/* ── 10. Reusable Modal Dialog System ── */
function initModalListeners() {
  const modalOverlay = document.getElementById('modalOverlay');
  const closeBtn = document.getElementById('modalCloseBtn');

  if (closeBtn && modalOverlay) {
    closeBtn.addEventListener('click', () => closeModal());
    modalOverlay.addEventListener('click', (e) => {
      if (e.target === modalOverlay) closeModal();
    });
  }
}

function openNoticeModal(noticeId) {
  const notice = CONECTA_DATA.noticias.find(n => n.id === noticeId);
  if (!notice) return;

  const modalTitle = document.getElementById('modalTitle');
  const modalBody = document.getElementById('modalBody');

  if (modalTitle && modalBody) {
    modalTitle.innerHTML = `<span class="gold-gradient-text">${notice.titulo}</span>`;
    modalBody.innerHTML = `
      <div style="margin-bottom:14px;"><span class="gold-badge">${notice.catedra} — ${notice.anio}</span></div>
      <p style="font-size:0.92rem; color:var(--text-primary); line-height:1.6; margin-bottom:16px;">${notice.detalleCompleto}</p>
      <div style="font-size:0.78rem; color:var(--text-muted); background:rgba(0,0,0,0.3); padding:12px; border-radius:10px; border:1px solid var(--bg-card-border);">
        <i class="far fa-calendar-alt"></i> Fecha de emisión: ${notice.fecha}
      </div>
    `;
    openModal();
  }
}

function openBookReaderModal(bookId) {
  const book = CONECTA_DATA.biblioteca.find(b => b.id === bookId);
  if (!book) return;

  const modalTitle = document.getElementById('modalTitle');
  const modalBody = document.getElementById('modalBody');

  if (modalTitle && modalBody) {
    modalTitle.innerHTML = `<i class="fas fa-book-open" style="color:var(--gold-primary);"></i> ${book.titulo}`;
    modalBody.innerHTML = `
      <p style="color:var(--text-secondary); margin-bottom:14px;">Visor de lectura digital interactiva activado.</p>
      <div style="height:250px; background:rgba(0,0,0,0.6); border-radius:12px; border:1px solid var(--bg-card-border); display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; padding:20px;">
        <i class="fas fa-file-pdf" style="font-size:3rem; color:var(--gold-primary); margin-bottom:12px;"></i>
        <div style="font-weight:700; font-size:1.1rem; color:var(--text-primary);">${book.titulo}</div>
        <div style="font-size:0.8rem; color:var(--text-muted); margin-top:4px;">${book.paginas} Páginas • Formato ${book.formato}</div>
      </div>
      <button class="nav-cta" style="width:100%; margin-top:16px; justify-content:center;" onclick="alert('Descarga de documento oficial iniciada.')">
        <i class="fas fa-download"></i> Descargar Ejemplar Completo
      </button>
    `;
    openModal();
  }
}

function generateAiBookSummary(bookId) {
  const book = CONECTA_DATA.biblioteca.find(b => b.id === bookId);
  if (!book) return;

  const modalTitle = document.getElementById('modalTitle');
  const modalBody = document.getElementById('modalBody');

  if (modalTitle && modalBody) {
    modalTitle.innerHTML = `<i class="fas fa-wand-magic-sparkles" style="color:var(--amethyst);"></i> Resumen Sintético IA: ${book.titulo}`;
    modalBody.innerHTML = `
      <div style="padding:16px; border-radius:14px; background:rgba(192, 132, 252, 0.08); border:1px solid rgba(192, 132, 252, 0.3); color:var(--text-primary); font-size:0.9rem; line-height:1.6;">
        ${book.resumenIa}
      </div>
      <div style="margin-top:16px; font-size:0.8rem; color:var(--text-muted);">
        <i class="fas fa-check-circle" style="color:var(--emerald);"></i> Verificado por el equipo docente de la FCM.
      </div>
    `;
    openModal();
  }
}

function openModal() {
  const modalOverlay = document.getElementById('modalOverlay');
  if (modalOverlay) modalOverlay.classList.add('active');
}

function closeModal() {
  const modalOverlay = document.getElementById('modalOverlay');
  if (modalOverlay) modalOverlay.classList.remove('active');
}
