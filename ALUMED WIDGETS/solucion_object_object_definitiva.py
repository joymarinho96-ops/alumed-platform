import re

print("=== REPARANDO ESCAPARHTML Y RENDERIZADO DE OPCIONES EN APP.JS ===")

with open("app.js", "r", encoding="utf-8") as f:
    app_js = f.read()

# 1. Update escaparHTML to handle objects safely
escapar_html_safe = """function escaparHTML(str) {
  if (str === null || str === undefined) return '';
  if (typeof str === 'object') {
    str = str.texto || str.text || str.opcion || str.label || '';
  }
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}"""

app_js = re.sub(r'function escaparHTML\(str\) \{[\s\S]*?\}', escapar_html_safe, app_js)

# 2. Fix normalizarOpcion
norm_opcion_clean = """function normalizarOpcion(opcion) {
  if (typeof opcion === "string") {
    return {
      texto: opcion,
      explicacion: ""
    };
  }
  if (!opcion || typeof opcion !== "object") {
    return { texto: "", explicacion: "" };
  }
  return {
    texto: opcion.texto || opcion.text || opcion.opcion || "",
    explicacion: opcion.explicacion || opcion.explanation || ""
  };
}"""

app_js = re.sub(r'function normalizarOpcion\(opcion\) \{[\s\S]*?\}', norm_opcion_clean, app_js)

# 3. Replace loadChoice option loop to pass optNorm.texto to escaparHTML
load_choice_loop_old = r'\(\(q\.opciones \?\? q\.opcoes\) \|\| \[\]\)\.forEach\(\(opt, idx\) => \{[\s\S]*?<span>\$\{escaparHTML\(opt\)\}</span>'
load_choice_loop_new = """((q.opciones ?? q.opcoes) || []).forEach((optRaw, idx) => {
      const optNorm = normalizarOpcion(optRaw);
      const btn = document.createElement('button');
      btn.className = 'option-btn';
      btn.id        = `opt-${idx}`;
      btn.setAttribute('role', 'radio');
      btn.setAttribute('aria-checked', 'false');
      
      btn.innerHTML = `
        <div class="option-content">
          <span class="option-letter">${letraOpcion(idx)}</span> 
          <span>${escaparHTML(optNorm.texto)}</span>
        </div>
        <div class="option-explanation hidden"></div>
      `;"""

app_js = re.sub(load_choice_loop_old, load_choice_loop_new, app_js)

# Also check for any standalone <span>${escaparHTML(opt)}</span>
app_js = app_js.replace('<span>${escaparHTML(opt)}</span>', '<span>${escaparHTML(normalizarOpcion(opt).texto)}</span>')

with open("app.js", "w", encoding="utf-8") as f:
    f.write(app_js)

print("Parche de escaping y normalización de objetos aplicado a app.js.")
