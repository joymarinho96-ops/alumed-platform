import json
import re
import os

print("=== REFACTORIZACIÓN Y NORMALIZACIÓN COMPLETA ===")

# ==========================================
# 1. LIMPIEZA Y NORMALIZACIÓN DE DATA.JS
# ==========================================
with open("data.js", "r", encoding="utf-8", errors="replace") as f:
    raw = f.read()

# Fix Mojibake in raw string before parsing
mojibake_map = {
    "BiologÃa": "Biología",
    "HistologÃa": "Histología",
    "EmbriologÃa": "Embriología",
    "AnatomÃa": "Anatomía",
    "CÃ¡tedra": "Cátedra",
    "ExplicaciÃ³n": "Explicación",
    "OrganizaciÃ³n": "Organización",
    "IntroducciÃ³n": "Introducción",
    "OpciÃ³n": "Opción",
    "Ã³": "ó",
    "Ã¡": "á",
    "Ã©": "é",
    "Ã­": "í",
    "Ãº": "ú",
    "Ã±": "ñ",
    "Ã": "Á"
}

for k, v in mojibake_map.items():
    raw = raw.replace(k, v)

first_b = raw.find('{')
last_b = raw.rfind('}')
banco = json.loads(raw[first_b:last_b+1])

choices = banco.get("choices", [])
clean_choices = []

garbage_patterns = [
    r"(?i)^\s*¡*muchos\s+éxitos!*\s*$",
    r"(?i)^\s*buena\s+suerte!*\s*$",
    r"(?i)^\s*página\s+\d+\s*$",
    r"(?i)^\s*cátedra\s+[a-c]\s*$",
    r"(?i)^\s*fcm\s*-\s*unlp\s*$",
    r"^\s*aannaattoom\s*$"
]

sin_gabarito_count = 0
basura_filtrada = 0

for q in choices:
    pregunta_txt = q.get("pregunta") or q.get("pergunta") or ""
    
    # Check if garbage text
    is_garbage = False
    for p in garbage_patterns:
        if re.search(p, pregunta_txt.strip()):
            is_garbage = True
            break
            
    if is_garbage or len(pregunta_txt.strip()) < 5:
        basura_filtrada += 1
        continue

    # Fix materia names to exact string match
    mat = q.get("materia", "")
    key = q.get("materiaKey", "")
    
    if "histo" in mat.lower() or "embrio" in mat.lower() or key == "histo_embrio":
        q["materia"] = "Histología y Embriología"
        q["materiaKey"] = "histo_embrio"
    elif "cátedra a" in mat.lower() or "catedra a" in mat.lower() or key == "anato_a":
        q["materia"] = "Anatomía Cátedra A"
        q["materiaKey"] = "anato_a"
    elif "cátedra b" in mat.lower() or "catedra b" in mat.lower() or key == "anato_b":
        q["materia"] = "Anatomía Cátedra B"
        q["materiaKey"] = "anato_b"
    elif "cátedra c" in mat.lower() or "catedra c" in mat.lower() or key == "anato_c":
        q["materia"] = "Anatomía Cátedra C"
        q["materiaKey"] = "anato_c"
    else:
        q["materia"] = "Biología"
        q["materiaKey"] = "biologia"

    # Normalize options format
    raw_opts = q.get("opciones") or q.get("opcoes") or []
    norm_opts = []
    for opt in raw_opts:
        if isinstance(opt, str):
            norm_opts.append({"texto": opt.strip(), "explicacion": ""})
        elif isinstance(opt, dict):
            txt = opt.get("texto") or opt.get("text") or opt.get("opcion") or ""
            exp = opt.get("explicacion") or ""
            norm_opts.append({"texto": str(txt).strip(), "explicacion": str(exp).strip()})
    q["opciones"] = norm_opts

    # Normalize correct answer index
    correcta_val = q.get("correcta") if q.get("correcta") is not None else q.get("correta")
    if isinstance(correcta_val, int) and 0 <= correcta_val < len(norm_opts):
        q["correcta"] = correcta_val
        q["requiereRevision"] = False
    else:
        q["correcta"] = None
        q["requiereRevision"] = True
        sin_gabarito_count += 1

    clean_choices.append(q)

banco["choices"] = clean_choices
# Populate orales and pinches arrays for backward compatibility
banco["orales"] = [q for q in clean_choices if q.get("modalidad") == "ORAL"]
banco["pinches"] = [q for q in clean_choices if q.get("modalidad") == "PINCHE_STATION"]

out_data = "const bancoDados = " + json.dumps(banco, ensure_ascii=False, indent=2) + ";"
with open("data.js", "w", encoding="utf-8") as f:
    f.write(out_data)

print(f"data.js limpio y normalizado:")
print(f" - Choices válidas: {len(clean_choices)}")
print(f" - Basura excluida: {basura_filtrada}")
print(f" - Sin gabarito (requiere revisión): {sin_gabarito_count}")
print(f" - Orales: {len(banco['orales'])}")
print(f" - Pinches: {len(banco['pinches'])}")

# ==========================================
# 2. REFACTORIZACIÓN DE APP.JS
# ==========================================
with open("app.js", "r", encoding="utf-8", errors="replace") as f:
    app_code = f.read()

# Fix Mojibake in app.js
for k, v in mojibake_map.items():
    app_code = app_code.replace(k, v)

# Inject helpers: obtenerIndiceCorrecto & normalizarOpcion
helpers_code = """
// ==========================================
// FUNCIONES DE NORMALIZACIÓN (ALUMED OS)
// ==========================================
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
"""

if "function obtenerIndiceCorrecto" not in app_code:
    app_code = helpers_code + "\n" + app_code

# Replace loadChoice with clean implementation using helper functions
load_choice_clean = """function loadChoice() {
  try {
    const elPergunta = document.getElementById('mc-pergunta');
    const elTag = document.getElementById('mc-materia-tag');
    const elCounter = document.getElementById('mc-counter');
    const elOpcoes = document.getElementById('mc-opcoes');

    if (!elPergunta || !elOpcoes) return;

    if (typeof bancoDados === 'undefined' || !bancoDados.choices) {
      elPergunta.textContent = "No se pudo cargar el banco de preguntas. Revisá la consola.";
      return;
    }

    if (!filteredChoices || filteredChoices.length === 0) {
      if (elTag) elTag.innerText = currentMateria || "Biología";
      if (elCounter) elCounter.innerText = "0 de 0";
      elPergunta.textContent = "No hay preguntas disponibles para la materia seleccionada.";
      elOpcoes.innerHTML = "<div style='padding:20px; color:var(--muted); text-align:center;'>Selecciona otra materia o modo para practicar.</div>";
      const joyPanel = document.getElementById('mc-joy-panel');
      if (joyPanel) joyPanel.style.display = 'none';
      return;
    }

    if (currentChoiceIndex < 0) currentChoiceIndex = 0;
    if (currentChoiceIndex >= filteredChoices.length) currentChoiceIndex = filteredChoices.length - 1;

    const q = filteredChoices[currentChoiceIndex];
    if (!q) {
      elPergunta.textContent = "No se pudo obtener la pregunta actual.";
      return;
    }

    yaValidado = false;
    selectedOption = null;

    if (elTag) elTag.innerText = `${q.materia || currentMateria} • ${q.tpPrincipal || 'TP1'}: ${q.tema || 'Tema General'}`;
    if (elCounter) elCounter.innerText = `Pregunta ${currentChoiceIndex + 1} de ${filteredChoices.length}`;
    elPergunta.textContent = q.pregunta || q.pergunta || "Pregunta sin enunciado";

    const fb = document.getElementById('mc-feedback');
    if (fb) {
      fb.className = 'feedback hidden';
      fb.innerHTML = '';
    }

    elOpcoes.innerHTML = '';
    const btnValidar = document.getElementById('btn-validar');
    if (btnValidar) btnValidar.disabled = true;

    const rawOpts = q.opciones || q.opcoes || [];
    if (rawOpts.length === 0) {
      elOpcoes.innerHTML = "<div style='padding:15px; color:var(--muted);'>Esta pregunta es de desarrollo oral o respuesta corta.</div>";
    } else {
      rawOpts.forEach((optRaw, idx) => {
        const opt = normalizarOpcion(optRaw);
        const btn = document.createElement('button');
        btn.className = 'option-btn';
        btn.innerHTML = `<span class="option-label">${String.fromCharCode(65 + idx)}</span> <span>${escaparHTML(opt.texto)}</span>`;
        btn.onclick = () => validarChoice(btn, idx);
        elOpcoes.appendChild(btn);
      });
    }

    const joyPanel = document.getElementById('mc-joy-panel');
    if (joyPanel) joyPanel.style.display = 'none';
  } catch (err) {
    console.error("Error al cargar la pregunta:", err);
    const elP = document.getElementById('mc-pergunta');
    if (elP) elP.textContent = "No se pudo cargar la pregunta actual. Revisá la consola.";
  }
}"""

app_code = re.sub(r'function loadChoice\(\) \{[\s\S]*?joyPanel\.style\.display = \'none\';\s*\}\s*\} catch[\s\S]*?\}\s*\}', load_choice_clean, app_code)
if "function loadChoice" in app_code and "normalizarOpcion" not in app_code:
    app_code = re.sub(r'function loadChoice\(\) \{[\s\S]*?const joyPanel = document\.getElementById\(\'mc-joy-panel\'\);[\s\S]*?joyPanel\.style\.display = \'none\';\s*\}', load_choice_clean, app_code)

# Replace validarChoice to use obtenerIndiceCorrecto(q) & normalizarOpcion(opt)
validar_choice_clean = """function validarChoice(btn, index) {
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
  
  const allBtns = document.getElementById('mc-opcoes').querySelectorAll('button');
  const rawOpts = q.opciones || q.opcoes || [];
  
  allBtns.forEach((b, i) => {
    const isThisCorrect = (indiceCorrecto !== null && i === indiceCorrecto);
    const optNorm = normalizarOpcion(rawOpts[i]);
    const expl = optNorm.explicacion;
    const explHtml = expl ? `<div style="margin-top:8px; font-size:0.85rem; color: var(--fg-default);">${escaparHTML(expl)}</div>` : '';
    
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

  if (!isCorrect) {
    if (!errores.includes(q.id)) errores.push(q.id);
    localStorage.setItem(STORAGE_KEYS.errores, JSON.stringify(errores));
  }
}"""

app_code = re.sub(r'function validarChoice\(btn, index\) \{[\s\S]*?localStorage\.setItem\(STORAGE_KEYS\.errores, JSON\.stringify\(errores\)\);\s*\}', validar_choice_clean, app_code)

# Replace DOMContentLoaded listeners with UNIFIED SINGLE LISTENER
single_dom_listener = """
// ==========================================
// INICIALIZACIÓN UNIFICADA DE ALUMED OS
// ==========================================
document.addEventListener("DOMContentLoaded", () => {
  try {
    if (typeof bancoDados === "undefined") {
      throw new Error("bancoDados no está disponible");
    }

    console.log("Banco cargado", {
      choices: bancoDados.choices?.length || 0,
      orales: bancoDados.orales?.length || 0,
      pinches: bancoDados.pinches?.length || 0
    });

    const bioBtn = document.getElementById("nav-bio");
    prepararEntrenamiento("choices", "Biología", bioBtn);
  } catch (error) {
    console.error("Error al inicializar el simulador:", error);

    const pregunta = document.getElementById("mc-pregunta");
    if (pregunta) {
      pregunta.textContent =
        "No se pudo cargar el banco de preguntas. Revisá la consola.";
    }
  }
});
"""

# Remove old listener blocks
app_code = re.sub(r'// ==========================================\s*// INICIALIZACIÓN[\s\S]*$', single_dom_listener, app_code)
if "INICIALIZACIÓN UNIFICADA DE ALUMED OS" not in app_code:
    app_code += "\n" + single_dom_listener

with open("app.js", "w", encoding="utf-8") as f:
    f.write(app_code)

print("app.js refactorizado exitosamente con inicializador único y funciones helper.")
