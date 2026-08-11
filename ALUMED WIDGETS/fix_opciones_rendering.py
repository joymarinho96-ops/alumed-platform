import re

print("=== CORRIGIENDO RENDERIZADO DE OPCIONES (NORMALIZACIÓN EXACTA) ===")

with open("app.js", "r", encoding="utf-8") as f:
    app_js = f.read()

# 1. Exact normalizarOpcion definition requested by user
norm_opcion_def = """function normalizarOpcion(opcion) {
  if (typeof opcion === "string") {
    return {
      texto: opcion,
      explicacion: ""
    };
  }

  return {
    texto: opcion?.texto || opcion?.text || opcion?.opcion || "",
    explicacion: opcion?.explicacion || opcion?.explanation || ""
  };
}"""

app_js = re.sub(r'function normalizarOpcion\(opcion\) \{[\s\S]*?\}\s*\}', norm_opcion_def, app_js)
if "function normalizarOpcion" not in app_js:
    app_js = norm_opcion_def + "\n" + app_js

# 2. Update loadChoice option rendering loop to use textContent safely
load_choice_rendering = """    if (container) {
      container.innerHTML = '';
      const btnValidar = document.getElementById('btn-validar');
      if (btnValidar) btnValidar.disabled = true;

      const rawOpts = q.opciones || q.opcoes || [];
      if (rawOpts.length === 0) {
        container.innerHTML = "<div style='padding:15px; color:var(--muted);'>Esta pregunta es de desarrollo oral o respuesta corta.</div>";
      } else {
        rawOpts.forEach((optRaw, idx) => {
          const opcionNormalizada = normalizarOpcion(optRaw);
          
          const btn = document.createElement('button');
          btn.className = 'option-btn';
          
          const labelSpan = document.createElement('span');
          labelSpan.className = 'option-label';
          labelSpan.textContent = String.fromCharCode(65 + idx);
          
          const textSpan = document.createElement('span');
          textSpan.textContent = opcionNormalizada.texto;
          
          btn.appendChild(labelSpan);
          btn.appendChild(document.createTextNode(' '));
          btn.appendChild(textSpan);
          
          btn.onclick = () => validarChoice(btn, idx);
          container.appendChild(btn);
        });
      }
    }"""

app_js = re.sub(r'if \(container\) \{[\s\S]*?container\.appendChild\(btn\);\s*\}\s*\}', load_choice_rendering, app_js)

# 3. Update validarChoice option feedback rendering
validar_choice_rendering = """function validarChoice(btn, index) {
  if (yaValidado) return;
  yaValidado = true;
  
  const q = filteredChoices[currentChoiceIndex];
  const indiceCorrecto = obtenerIndiceCorrecto(q);
  const isCorrect = (indiceCorrecto !== null && index === indiceCorrecto);
  
  if (estadoExamen.modo === 'PARCIAL_REAL') {
      estadoExamen.respuestasUsuario[q.id] = {
          esCorrecta: isCorrect,
          elegida: index
      };
      btn.style.borderColor = 'var(--accent)';
      setTimeout(() => {
          siguienteChoice();
      }, 500);
      return;
  }
  
  const container = document.getElementById('mc-opcoes');
  const allBtns = container ? container.querySelectorAll('button') : [];
  const rawOpts = q.opciones || q.opcoes || [];
  
  allBtns.forEach((b, i) => {
    const isThisCorrect = (indiceCorrecto !== null && i === indiceCorrecto);
    const optNorm = normalizarOpcion(rawOpts[i]);
    const expl = optNorm.explicacion;
    
    if (isThisCorrect) {
      b.style.borderColor = 'var(--success)';
      b.style.backgroundColor = 'rgba(16, 185, 129, 0.05)';
      if (expl) {
        const explDiv = document.createElement('div');
        explDiv.style.cssText = "margin-top:8px; font-size:0.85rem; color: var(--fg-default);";
        explDiv.textContent = expl;
        b.appendChild(explDiv);
      }
    } else if (i === index && !isCorrect) {
      b.style.borderColor = 'var(--danger)';
      b.style.backgroundColor = 'rgba(239, 68, 68, 0.05)';
      if (expl) {
        const explDiv = document.createElement('div');
        explDiv.style.cssText = "margin-top:8px; font-size:0.85rem; color: var(--fg-default);";
        explDiv.textContent = expl;
        b.appendChild(explDiv);
      }
    } else {
      b.style.opacity = '0.7';
    }
  });

  const joyPanel = document.getElementById('mc-joy-panel');
  if (joyPanel) {
    joyPanel.innerHTML = generarPanelJoy(q);
    joyPanel.style.display = 'block';
  }

  if (!isCorrect) {
    if (!errores.includes(q.id)) errores.push(q.id);
    localStorage.setItem(STORAGE_KEYS.errores, JSON.stringify(errores));
  }
}"""

app_js = re.sub(r'function validarChoice\(btn, index\) \{[\s\S]*?localStorage\.setItem\(STORAGE_KEYS\.errores, JSON\.stringify\(errores\)\);\s*\}', validar_choice_rendering, app_js)

with open("app.js", "w", encoding="utf-8") as f:
    f.write(app_js)

print("Renderización de opciones corregida utilizando textContent y normalizarOpcion.")
