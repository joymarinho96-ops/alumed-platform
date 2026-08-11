/**
 * ALUMED - Lógica Principal del Simulador Médico (Vanilla JS)
 * Módulos: Multiple Choice, Pinches, Examen Oral y Lector de PDF
 */

document.addEventListener('DOMContentLoaded', () => {

  // ==========================================
  // ESTADO GLOBAL DE LA APLICACIÓN
  // ==========================================
  const state = {
    materiaFiltro: 'TODAS',
    busquedaChoice: '',
    
    // Estadísticas
    totalRespondidas: 0,
    correctasCount: 0,
    rachaActual: 0,

    // Módulo Choices
    choiceIndex: 0,
    filteredChoices: [],

    // Módulo Pinches
    pincheIndex: 0,
    filteredPinches: [],

    // Módulo Oral
    bolillaActual: null,
    checklistState: {},

    // Módulo PDF Extraído
    pdfQuestions: []
  };

  // ==========================================
  // REFERENCIAS AL DOM
  // ==========================================
  const sidebar = document.getElementById('sidebar');
  const toggleSidebarBtn = document.getElementById('toggleSidebarBtn');
  const mobileToggle = document.getElementById('mobileToggle');
  const materiaSelect = document.getElementById('materiaSelect');
  const navItems = document.querySelectorAll('.nav-item');
  const moduleViews = document.querySelectorAll('.module-view');
  const currentModuleTitle = document.getElementById('currentModuleTitle');

  // Stats
  const statTotal = document.getElementById('statTotal');
  const statAccuracy = document.getElementById('statAccuracy');
  const statStreak = document.getElementById('statStreak');

  // Choice DOM
  const choiceSearch = document.getElementById('choiceSearch');
  const choiceActiveMateriaTag = document.getElementById('choiceActiveMateriaTag');
  const qMateriaBadge = document.getElementById('qMateriaBadge');
  const qCounterText = document.getElementById('qCounterText');
  const qQuestionText = document.getElementById('qQuestionText');
  const qOptionsList = document.getElementById('qOptionsList');
  const qJustificationBox = document.getElementById('qJustificationBox');
  const qJustificationText = document.getElementById('qJustificationText');
  const btnPrevQ = document.getElementById('btnPrevQ');
  const btnNextQ = document.getElementById('btnNextQ');

  // Pinche DOM
  const pMateriaBadge = document.getElementById('pMateriaBadge');
  const pTituloText = document.getElementById('pTituloText');
  const pincheSvgContainer = document.getElementById('pincheSvgContainer');
  const pHintBox = document.getElementById('pHintBox');
  const pHintText = document.getElementById('pHintText');
  const pincheInput = document.getElementById('pincheInput');
  const btnShowHint = document.getElementById('btnShowHint');
  const btnValidatePinche = document.getElementById('btnValidatePinche');
  const pincheFeedback = document.getElementById('pincheFeedback');
  const btnPrevPinche = document.getElementById('btnPrevPinche');
  const btnNextPinche = document.getElementById('btnNextPinche');

  // Oral DOM
  const btnDrawBolilla = document.getElementById('btnDrawBolilla');
  const bolillaActiveCard = document.getElementById('bolillaActiveCard');
  const oralBolillaNumber = document.getElementById('oralBolillaNumber');
  const oralMateriaBadge = document.getElementById('oralMateriaBadge');
  const oralTitleText = document.getElementById('oralTitleText');
  const oralClinicalCaseText = document.getElementById('oralClinicalCaseText');
  const oralTopicsChecklist = document.getElementById('oralTopicsChecklist');
  const oralGradeText = document.getElementById('oralGradeText');
  const oralStatusBadge = document.getElementById('oralStatusBadge');

  // PDF DOM
  const pdfDropzone = document.getElementById('pdfDropzone');
  const pdfFileInput = document.getElementById('pdfFileInput');
  const pdfMateriaSelect = document.getElementById('pdfMateriaSelect');
  const pdfProgressContainer = document.getElementById('pdfProgressContainer');
  const pdfProgressBar = document.getElementById('pdfProgressBar');
  const pdfProgressText = document.getElementById('pdfProgressText');
  const pdfResultsCard = document.getElementById('pdfResultsCard');
  const pdfExtractedCount = document.getElementById('pdfExtractedCount');
  const pdfPreviewList = document.getElementById('pdfPreviewList');
  const btnAddToDatabase = document.getElementById('btnAddToDatabase');
  const btnDownloadDataJs = document.getElementById('btnDownloadDataJs');

  // ==========================================
  // INICIALIZACIÓN
  // ==========================================
  function init() {
    setupEventListeners();
    updateFilteredData();
    renderChoiceQuestion();
    renderPincheQuestion();
  }

  // ==========================================
  // MANEJADORES DE EVENTOS
  // ==========================================
  function setupEventListeners() {
    // Sidebar collapse
    if (toggleSidebarBtn) {
      toggleSidebarBtn.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
      });
    }

    if (mobileToggle) {
      mobileToggle.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
      });
    }

    // Módulos Navigation
    navItems.forEach(item => {
      item.addEventListener('click', () => {
        const targetModule = item.getAttribute('data-target');
        
        navItems.forEach(n => n.classList.remove('active'));
        item.classList.add('active');

        moduleViews.forEach(view => {
          if (view.id === targetModule) {
            view.classList.add('active');
          } else {
            view.classList.remove('active');
          }
        });

        // Actualizar título del header
        const moduleNames = {
          'module-choice': 'Multiple Choice',
          'module-pinche': 'Pinches / Anatomía Práctica',
          'module-oral': 'Examen Oral / Bolillas',
          'module-pdf': 'Cargar Parcial PDF'
        };
        currentModuleTitle.textContent = moduleNames[targetModule] || 'Simulador UBA';
      });
    });

    // Selector de Materia
    materiaSelect.addEventListener('change', (e) => {
      state.materiaFiltro = e.target.value;
      state.choiceIndex = 0;
      state.pincheIndex = 0;
      choiceActiveMateriaTag.textContent = state.materiaFiltro;
      updateFilteredData();
      renderChoiceQuestion();
      renderPincheQuestion();
    });

    // Búsqueda en choices
    choiceSearch.addEventListener('input', (e) => {
      state.busquedaChoice = e.target.value.toLowerCase().trim();
      state.choiceIndex = 0;
      updateFilteredData();
      renderChoiceQuestion();
    });

    // Botones de navegación Choices
    btnPrevQ.addEventListener('click', () => {
      if (state.choiceIndex > 0) {
        state.choiceIndex--;
        renderChoiceQuestion();
      }
    });

    btnNextQ.addEventListener('click', () => {
      if (state.choiceIndex < state.filteredChoices.length - 1) {
        state.choiceIndex++;
        renderChoiceQuestion();
      }
    });

    // Botones Pinches
    btnShowHint.addEventListener('click', () => {
      pHintBox.classList.toggle('hidden');
    });

    btnValidatePinche.addEventListener('click', validatePincheAnswer);
    pincheInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') validatePincheAnswer();
    });

    btnPrevPinche.addEventListener('click', () => {
      if (state.pincheIndex > 0) {
        state.pincheIndex--;
        renderPincheQuestion();
      }
    });

    btnNextPinche.addEventListener('click', () => {
      if (state.pincheIndex < state.filteredPinches.length - 1) {
        state.pincheIndex++;
        renderPincheQuestion();
      }
    });

    // Módulo Oral
    btnDrawBolilla.addEventListener('click', drawRandomBolilla);

    // Módulo PDF Upload
    pdfDropzone.addEventListener('click', () => pdfFileInput.click());
    pdfFileInput.addEventListener('change', handlePdfFileSelect);

    pdfDropzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      pdfDropzone.classList.add('dragover');
    });

    pdfDropzone.addEventListener('dragleave', () => {
      pdfDropzone.classList.remove('dragover');
    });

    pdfDropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      pdfDropzone.classList.remove('dragover');
      if (e.dataTransfer.files.length > 0) {
        processPdfFile(e.dataTransfer.files[0]);
      }
    });

    btnAddToDatabase.addEventListener('click', addPdfQuestionsToDatabase);
    btnDownloadDataJs.addEventListener('click', downloadDataJsFile);
  }

  // ==========================================
  // ACTUALIZAR DATOS FILTRADOS
  // ==========================================
  function updateFilteredData() {
    const rawChoices = window.bancoDados ? window.bancoDados.choices : [];
    const rawPinches = window.bancoDados ? window.bancoDados.pinches : [];

    state.filteredChoices = rawChoices.filter(item => {
      const matchMateria = state.materiaFiltro === 'TODAS' || item.materia === state.materiaFiltro;
      const matchSearch = !state.busquedaChoice || 
        item.pergunta.toLowerCase().includes(state.busquedaChoice) ||
        item.justificativa.toLowerCase().includes(state.busquedaChoice);
      return matchMateria && matchSearch;
    });

    state.filteredPinches = rawPinches.filter(item => {
      return state.materiaFiltro === 'TODAS' || item.materia.startsWith(state.materiaFiltro) || item.materia === state.materiaFiltro;
    });
  }

  // ==========================================
  // RENDEREAR MULTIPLE CHOICE
  // ==========================================
  function renderChoiceQuestion() {
    qJustificationBox.classList.add('hidden');
    qOptionsList.innerHTML = '';

    if (state.filteredChoices.length === 0) {
      qMateriaBadge.textContent = state.materiaFiltro;
      qCounterText.textContent = '0 de 0';
      qQuestionText.textContent = 'No se encontraron preguntas de la materia seleccionada o con ese filtro de búsqueda.';
      btnPrevQ.disabled = true;
      btnNextQ.disabled = true;
      return;
    }

    const current = state.filteredChoices[state.choiceIndex];
    qMateriaBadge.textContent = current.materia;
    qCounterText.textContent = `Pregunta ${state.choiceIndex + 1} de ${state.filteredChoices.length}`;
    qQuestionText.textContent = current.pergunta;
    qJustificationText.textContent = current.justificativa || "Sin justificación adicional.";

    current.opcoes.forEach((opcText, idx) => {
      const optDiv = document.createElement('div');
      optDiv.className = 'option-item';
      optDiv.innerHTML = `<span>${opcText}</span><i class="fa-regular fa-circle opt-icon"></i>`;
      
      optDiv.addEventListener('click', () => handleOptionSelect(optDiv, idx, current.correta));
      qOptionsList.appendChild(optDiv);
    });

    btnPrevQ.disabled = state.choiceIndex === 0;
    btnNextQ.disabled = state.choiceIndex === state.filteredChoices.length - 1;
  }

  function handleOptionSelect(selectedDiv, selectedIdx, correctIdx) {
    const allOptions = qOptionsList.querySelectorAll('.option-item');
    allOptions.forEach(opt => opt.classList.add('disabled')); // Deshabilitar clics posteriores

    state.totalRespondidas++;

    if (selectedIdx === correctIdx) {
      selectedDiv.classList.add('selected-correct');
      selectedDiv.querySelector('.opt-icon').className = 'fa-solid fa-circle-check text-success';
      state.correctasCount++;
      state.rachaActual++;
    } else {
      selectedDiv.classList.add('selected-wrong');
      selectedDiv.querySelector('.opt-icon').className = 'fa-solid fa-circle-xmark text-danger';
      state.rachaActual = 0;

      // Resaltar la respuesta correcta
      if (allOptions[correctIdx]) {
        allOptions[correctIdx].classList.add('show-correct');
        allOptions[correctIdx].querySelector('.opt-icon').className = 'fa-solid fa-circle-check text-success';
      }
    }

    qJustificationBox.classList.remove('hidden');
    updateStatsDisplay();
  }

  function updateStatsDisplay() {
    statTotal.textContent = state.totalRespondidas;
    const accuracy = state.totalRespondidas > 0 
      ? Math.round((state.correctasCount / state.totalRespondidas) * 100) 
      : 0;
    statAccuracy.textContent = `${accuracy}%`;
    statStreak.textContent = state.rachaActual;
  }

  // ==========================================
  // RENDEREAR PINCHES / PRÁCTICO
  // ==========================================
  function renderPincheQuestion() {
    pHintBox.classList.add('hidden');
    pincheFeedback.className = 'pinche-feedback hidden';
    pincheInput.value = '';

    if (state.filteredPinches.length === 0) {
      pMateriaBadge.textContent = state.materiaFiltro;
      pTituloText.textContent = 'Sin Pinches Disponibles';
      pincheSvgContainer.innerHTML = '<p style="color:#94a3b8;">No hay muestras anatómicas para el filtro seleccionado.</p>';
      btnPrevPinche.disabled = true;
      btnNextPinche.disabled = true;
      return;
    }

    const current = state.filteredPinches[state.pincheIndex];
    pMateriaBadge.textContent = current.materia;
    pTituloText.textContent = `${current.titulo} (${state.pincheIndex + 1}/${state.filteredPinches.length})`;
    pincheSvgContainer.innerHTML = current.imagenSvg;
    pHintText.textContent = current.pista;

    btnPrevPinche.disabled = state.pincheIndex === 0;
    btnNextPinche.disabled = state.pincheIndex === state.filteredPinches.length - 1;
  }

  function normalizeText(text) {
    return text.toLowerCase()
      .normalize("NFD").replace(/[\u0300-\u036f]/g, "") // quita acentos
      .replace(/[^a-z0-9\s]/g, "")
      .trim();
  }

  function validatePincheAnswer() {
    const current = state.filteredPinches[state.pincheIndex];
    if (!current) return;

    const userVal = normalizeText(pincheInput.value);
    if (!userVal) return;

    const isCorrect = current.respostasValidas.some(val => normalizeText(val) === userVal);

    pincheFeedback.classList.remove('hidden');
    if (isCorrect) {
      pincheFeedback.className = 'pinche-feedback correct';
      pincheFeedback.innerHTML = `<i class="fa-solid fa-circle-check"></i> ¡Excelente! Identificaste correctamente la estructura anatómica.`;
      state.totalRespondidas++;
      state.correctasCount++;
      state.rachaActual++;
    } else {
      pincheFeedback.className = 'pinche-feedback incorrect';
      const aceptadosStr = current.respostasValidas.slice(0, 3).join(', ');
      pincheFeedback.innerHTML = `<i class="fa-solid fa-circle-xmark"></i> Incorrecto. Términos anatómicos válidos: <strong>${aceptadosStr}</strong>`;
      state.totalRespondidas++;
      state.rachaActual = 0;
    }
    updateStatsDisplay();
  }

  // ==========================================
  // RENDEREAR EXAMEN ORAL / BOLILLAS
  // ==========================================
  function drawRandomBolilla() {
    const rawOrales = window.bancoDados ? window.bancoDados.orales : [];
    const filtrados = rawOrales.filter(b => state.materiaFiltro === 'TODAS' || b.materia === state.materiaFiltro);

    if (filtrados.length === 0) {
      alert('No se encontraron bolillas disponibles para la materia seleccionada.');
      return;
    }

    const randomIndex = Math.floor(Math.random() * filtrados.length);
    state.bolillaActual = filtrados[randomIndex];
    state.checklistState = {};

    oralBolillaNumber.textContent = `Bolilla #${state.bolillaActual.bolillaNumero}`;
    oralMateriaBadge.textContent = state.bolillaActual.materia;
    oralTitleText.textContent = state.bolillaActual.titulo;
    oralClinicalCaseText.textContent = state.bolillaActual.casoClinico;

    // Render Checklist
    oralTopicsChecklist.innerHTML = '';
    state.bolillaActual.topicos.forEach(topic => {
      const checkDiv = document.createElement('div');
      checkDiv.className = 'check-item';
      checkDiv.innerHTML = `
        <input type="checkbox" id="check_${topic.id}">
        <label for="check_${topic.id}">${topic.texto}</label>
      `;

      const inputCheck = checkDiv.querySelector('input');
      inputCheck.addEventListener('change', () => {
        state.checklistState[topic.id] = inputCheck.checked;
        calculateOralGrade();
      });

      oralTopicsChecklist.appendChild(checkDiv);
    });

    bolillaActiveCard.classList.remove('hidden');
    calculateOralGrade();
  }

  function calculateOralGrade() {
    if (!state.bolillaActual) return;
    const totalTopicos = state.bolillaActual.topicos.length;
    let marcados = 0;

    state.bolillaActual.topicos.forEach(t => {
      if (state.checklistState[t.id]) marcados++;
    });

    const nota = Math.round((marcados / totalTopicos) * 10 * 10) / 10;
    oralGradeText.textContent = `${nota} / 10`;

    if (nota >= 7) {
      oralStatusBadge.className = 'score-status text-success';
      oralStatusBadge.style.background = '#d1fae5';
      oralStatusBadge.style.color = '#065f46';
      oralStatusBadge.textContent = '¡Aprobado / Promocionado!';
    } else if (nota >= 4) {
      oralStatusBadge.className = 'score-status text-warning';
      oralStatusBadge.style.background = '#fef3c7';
      oralStatusBadge.style.color = '#92400e';
      oralStatusBadge.textContent = 'Regularizado (Aprobado Justo)';
    } else {
      oralStatusBadge.className = 'score-status text-danger';
      oralStatusBadge.style.background = '#fee2e2';
      oralStatusBadge.style.color = '#991b1b';
      oralStatusBadge.textContent = 'Insuficiente / A Repasar';
    }
  }

  // ==========================================
  // LECTOR DE PDF DINÁMICO (PDF.js)
  // ==========================================
  function handlePdfFileSelect(e) {
    if (e.target.files.length > 0) {
      processPdfFile(e.target.files[0]);
    }
  }

  async function processPdfFile(file) {
    if (!window.pdfjsLib) {
      alert('Error: La librería PDF.js no está cargada.');
      return;
    }

    pdfProgressContainer.classList.remove('hidden');
    pdfProgressBar.style.width = '10%';
    pdfProgressText.textContent = 'Leyendo archivo PDF...';

    try {
      const arrayBuffer = await file.arrayBuffer();
      const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
      let fullText = '';

      for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
        const textContent = await page.getTextContent();
        const pageText = textContent.items.map(item => item.str).join(' ');
        fullText += pageText + '\n';

        const percent = Math.round((i / pdf.numPages) * 80);
        pdfProgressBar.style.width = `${percent}%`;
        pdfProgressText.textContent = `Extrayendo texto de página ${i} de ${pdf.numPages}...`;
      }

      pdfProgressBar.style.width = '90%';
      pdfProgressText.textContent = 'Analizando preguntas y alternativas...';

      parsePdfTextToQuestions(fullText, pdfMateriaSelect.value);

      pdfProgressBar.style.width = '100%';
      pdfProgressText.textContent = '¡Proceso completado!';
      setTimeout(() => pdfProgressContainer.classList.add('hidden'), 1200);

    } catch (err) {
      console.error(err);
      alert('Hubo un error al procesar el archivo PDF: ' + err.message);
      pdfProgressContainer.classList.add('hidden');
    }
  }

  function parsePdfTextToQuestions(rawText, materia) {
    // Regex de división por números de pregunta (1., 2-, 3), etc)
    const blocks = rawText.split(/\n(?=\d+[\.\-\)])|(?<=\n)(?=\d+[\.\-\)])/);
    const parsedList = [];
    let startId = window.bancoDados.choices.length + 1;

    blocks.forEach((block) => {
      const lines = block.split('\n').map(l => l.trim()).filter(l => l.length > 0);
      if (lines.length < 3) return;

      const pergunta = lines[0];
      const opcoes = [];
      let corretaIdx = 0;

      lines.slice(1).forEach(line => {
        if (/^[a-dA-D][\.\)\-]/.test(line)) {
          opcoes.append ? null : null;
          opcoes.push(line);

          if (line.toLowerCase().includes('correcta') || line.includes('*') || line.toLowerCase().includes('(x)')) {
            corretaIdx = opcoes.length - 1;
          }
        }
      });

      if (opcoes.length >= 2) {
        parsedList.push({
          id: startId++,
          materia: materia,
          pergunta: pergunta,
          opcoes: opcoes,
          correta: corretaIdx,
          justificativa: `Extraída automáticamente del PDF cargado: ${materia}`
        });
      }
    });

    state.pdfQuestions = parsedList;
    renderPdfResultsPreview();
  }

  function renderPdfResultsPreview() {
    pdfResultsCard.classList.remove('hidden');
    pdfExtractedCount.textContent = state.pdfQuestions.length;
    pdfPreviewList.innerHTML = '';

    if (state.pdfQuestions.length === 0) {
      pdfPreviewList.innerHTML = '<p style="color:#64748b;">No se detectaron preguntas estructuradas en el formato (1. Pregunta \n a) Opción A \n b) Opción B...).</p>';
      return;
    }

    state.pdfQuestions.forEach((q, idx) => {
      const item = document.createElement('div');
      item.className = 'preview-item';
      item.innerHTML = `
        <strong>#${idx + 1} (${q.materia}):</strong> ${q.pergunta}
        <div style="font-size:12px; color:#64748b; margin-top:4px;">
          Alternativas (${q.opcoes.length}): ${q.opcoes.slice(0, 2).join(' | ')}...
        </div>
      `;
      pdfPreviewList.appendChild(item);
    });
  }

  function addPdfQuestionsToDatabase() {
    if (state.pdfQuestions.length === 0) return;

    window.bancoDados.choices.push(...state.pdfQuestions);
    alert(`¡Éxito! Se han incorporado ${state.pdfQuestions.length} preguntas al banco activo de datos.`);
    
    updateFilteredData();
    renderChoiceQuestion();
    pdfResultsCard.classList.add('hidden');
    state.pdfQuestions = [];
  }

  function downloadDataJsFile() {
    const dataJsContent = `/**
 * Banco de Datos Generado Dinámicamente - ALUMED Medicina UBA
 */
const bancoDados = ${JSON.stringify(window.bancoDados, null, 2)};
`;

    const blob = new Blob([dataJsContent], { type: 'text/javascript' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'data.js';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  // Arrancar la app
  init();
});
