const estado = {
  indice: 0,
  seleccionado: null,
  respondida: false
};

const $ = selector => document.querySelector(selector);
const elementos = {
  materia: $("#materia-badge"),
  tema: $("#tema-label"),
  numero: $("#question-number"),
  total: $("#question-total"),
  progreso: $("#progress-bar"),
  pregunta: $("#question-text"),
  opciones: $("#options"),
  validar: $("#btn-validar"),
  siguiente: $("#btn-siguiente"),
  feedback: $("#feedback"),
  modal: $("#fragmento-modal"),
  modalFragmento: $("#modal-fragment")
};

function preguntaActual() {
  return bancoDados.choices[estado.indice];
}

function renderPregunta() {
  const q = preguntaActual();
  estado.seleccionado = null;
  estado.respondida = false;
  elementos.materia.textContent = q.materia;
  elementos.tema.textContent = q.tema || "Tema general";
  elementos.numero.textContent = estado.indice + 1;
  elementos.total.textContent = bancoDados.choices.length;
  elementos.progreso.style.width = `${((estado.indice + 1) / bancoDados.choices.length) * 100}%`;
  elementos.pregunta.textContent = q.pergunta;
  elementos.opciones.innerHTML = q.opcoes.map((opcion, indice) => `
    <button class="option-btn" type="button" role="radio" aria-checked="false" data-index="${indice}">
      <span class="option-letter">${letraOpcion(indice)}</span>
      <span>${escaparHTML(opcion)}</span>
    </button>`).join("");
  elementos.feedback.innerHTML = "";
  elementos.validar.disabled = true;
  elementos.validar.hidden = false;
  elementos.siguiente.hidden = true;
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function seleccionarOpcion(boton) {
  if (estado.respondida) return;
  elementos.opciones.querySelectorAll(".option-btn").forEach(item => {
    item.classList.remove("selected");
    item.setAttribute("aria-checked", "false");
  });
  boton.classList.add("selected");
  boton.setAttribute("aria-checked", "true");
  estado.seleccionado = Number(boton.dataset.index);
  elementos.validar.disabled = false;
}

function validarChoice() {
  if (estado.seleccionado === null || estado.respondida) return;
  const q = preguntaActual();
  estado.respondida = true;

  elementos.opciones.querySelectorAll(".option-btn").forEach((boton, indice) => {
    boton.disabled = true;
    if (indice === q.correta) boton.classList.add("correct-reveal");
    if (indice === estado.seleccionado && indice !== q.correta) boton.classList.add("wrong-reveal");
  });

  guardarEnLocalStorage(q, estado.seleccionado);
  elementos.feedback.innerHTML = generarPanelJoy(q, estado.seleccionado);
  elementos.validar.hidden = true;
  elementos.siguiente.hidden = false;
  elementos.siguiente.textContent = estado.indice === bancoDados.choices.length - 1
    ? "Volver al inicio" : "Siguiente pregunta";
  elementos.feedback.scrollIntoView({ behavior: "smooth", block: "start" });
}

function mostrarToast(mensaje) {
  document.querySelector(".toast")?.remove();
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.textContent = mensaje;
  document.body.appendChild(toast);
  requestAnimationFrame(() => toast.classList.add("show"));
  setTimeout(() => toast.remove(), 2400);
}

function abrirFragmento(q) {
  elementos.modalFragmento.textContent = q.fragmentoApunte || "Fragmento no disponible.";
  elementos.modal.hidden = false;
  document.body.classList.add("modal-open");
  $(".modal-close").focus();
}

function cerrarModal() {
  elementos.modal.hidden = true;
  document.body.classList.remove("modal-open");
}

function practicarParecida(q) {
  const parecida = buscarParecida(q);
  if (!parecida) {
    mostrarToast("Todavía no hay otra pregunta de este tema");
    return;
  }
  estado.indice = bancoDados.choices.findIndex(item => item.id === parecida.id);
  renderPregunta();
}

elementos.opciones.addEventListener("click", evento => {
  const boton = evento.target.closest(".option-btn");
  if (boton) seleccionarOpcion(boton);
});
elementos.validar.addEventListener("click", validarChoice);
elementos.siguiente.addEventListener("click", () => {
  estado.indice = (estado.indice + 1) % bancoDados.choices.length;
  renderPregunta();
});
elementos.feedback.addEventListener("click", evento => {
  const boton = evento.target.closest("[data-action]");
  if (!boton) return;
  const q = preguntaActual();
  const acciones = {
    flashcard: () => mostrarToast(crearFlashcard(q)),
    repaso: () => mostrarToast(agregarRepaso(q)),
    parecida: () => practicarParecida(q),
    fragmento: () => abrirFragmento(q)
  };
  acciones[boton.dataset.action]?.();
});
elementos.modal.addEventListener("click", evento => {
  if (evento.target.closest("[data-close-modal]")) cerrarModal();
});
document.addEventListener("keydown", evento => {
  if (evento.key === "Escape" && !elementos.modal.hidden) cerrarModal();
});

const temaGuardado = localStorage.getItem("alumed_tema") || "light";
document.documentElement.dataset.theme = temaGuardado;
$("#theme-toggle").addEventListener("click", () => {
  const nuevo = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
  document.documentElement.dataset.theme = nuevo;
  localStorage.setItem("alumed_tema", nuevo);
});

renderPregunta();
