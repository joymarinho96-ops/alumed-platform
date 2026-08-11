import re

with open("app.js", "r", encoding="utf-8") as f:
    code = f.read()

clean_prep_and_load = """function normalizarTexto(valor = "") {
  return String(valor)
    .normalize("NFD")
    .replace(/[\\u0300-\\u036f]/g, "")
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
    texto: opcion?.texto || opcion?.text || "",
    explicacion: opcion?.explicacion || ""
  };
}

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
  try {
    const materiaTag = document.getElementById('mc-materia-tag') || document.getElementById('mc-materia');
    const counter    = document.getElementById('mc-counter');
    const pregunta   = document.getElementById('mc-pergunta');
    const container  = document.getElementById('mc-opcoes');

    if (typeof bancoDados === 'undefined' || !bancoDados.choices) {
      if (pregunta) pregunta.textContent = "No se pudo cargar el banco de preguntas. Revisá la consola.";
      return;
    }

    if (!filteredChoices || filteredChoices.length === 0) {
      if (materiaTag) materiaTag.textContent = currentMateria || "Biología";
      if (counter)    counter.textContent    = "0 de 0";
      if (pregunta)   pregunta.textContent   = "No se encontraron preguntas para esta materia.";
      if (container)  container.innerHTML    = "<div style='padding:20px; color:var(--muted); text-align:center;'>Selecciona otra materia o modo para practicar.</div>";
      const joyPanel = document.getElementById('mc-joy-panel');
      if (joyPanel) joyPanel.style.display = 'none';
      return;
    }

    if (currentChoiceIndex < 0) currentChoiceIndex = 0;
    if (currentChoiceIndex >= filteredChoices.length) currentChoiceIndex = filteredChoices.length - 1;

    const q = filteredChoices[currentChoiceIndex];
    if (!q) {
      if (pregunta) pregunta.textContent = "No se pudo obtener la pregunta actual.";
      return;
    }

    yaValidado = false;
    selectedOption = null;

    if (materiaTag) {
      materiaTag.textContent = `${q.materia || currentMateria} • ${q.tpPrincipal || 'TP1'}: ${q.tema || 'Tema General'}`;
    }

    if (counter) {
      counter.textContent = `Pregunta ${currentChoiceIndex + 1} de ${filteredChoices.length}`;
    }

    if (pregunta) {
      pregunta.textContent = q.pregunta || q.pergunta || "Pregunta sin contenido";
    }

    const fb = document.getElementById('mc-feedback');
    if (fb) {
      fb.className = 'feedback hidden';
      fb.innerHTML = '';
    }

    if (container) {
      container.innerHTML = '';
      const btnValidar = document.getElementById('btn-validar');
      if (btnValidar) btnValidar.disabled = true;

      const rawOpts = q.opciones || q.opcoes || [];
      if (rawOpts.length === 0) {
        container.innerHTML = "<div style='padding:15px; color:var(--muted);'>Esta pregunta es de desarrollo oral o respuesta corta.</div>";
      } else {
        rawOpts.forEach((optRaw, idx) => {
          const opt = normalizarOpcion(optRaw);
          const btn = document.createElement('button');
          btn.className = 'option-btn';
          btn.innerHTML = `<span class="option-label">${String.fromCharCode(65 + idx)}</span> <span>${escaparHTML(opt.texto)}</span>`;
          btn.onclick = () => validarChoice(btn, idx);
          container.appendChild(btn);
        });
      }
    }

    const joyPanel = document.getElementById('mc-joy-panel');
    if (joyPanel) joyPanel.style.display = 'none';
  } catch (err) {
    console.error("Error al cargar la pregunta:", err);
    const pregunta = document.getElementById('mc-pergunta');
    if (pregunta) pregunta.textContent = `No se pudo cargar la pregunta actual. Error: ${err.message}`;
  }
}"""

# Use lambda in re.sub to avoid backslash escaping issues
code = re.sub(r'function normalizarTexto[\s\S]*?function loadChoice\(\) \{[\s\S]*?joyPanel\.style\.display = \'none\';\s*\}', lambda m: clean_prep_and_load, code)
if "function loadChoice" not in code:
    code = re.sub(r'function prepararEntrenamiento[\s\S]*?function loadChoice\(\) \{[\s\S]*?joyPanel\.style\.display = \'none\';\s*\}', lambda m: clean_prep_and_load, code)

with open("app.js", "w", encoding="utf-8") as f:
    f.write(code)

print("Replacement complete successfully.")
