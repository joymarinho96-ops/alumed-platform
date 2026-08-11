import re

print("=== REPLACING EXACT OPTION RENDERER IN APP.JS ===")

# 1. Update index.html script tag version to app.js?v=20260728-4
with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

html = re.sub(r'app\.js\?v=[^"]*', 'app.js?v=20260728-4', html)
html = re.sub(r'data\.js\?v=[^"]*', 'data.js?v=20260728-4', html)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("1. index.html updated with version ?v=20260728-4.")

# 2. Update app.js
with open("app.js", "r", encoding="utf-8") as f:
    app_js = f.read()

norm_fn = """function normalizarOpcion(opcion) {
  if (typeof opcion === "string") {
    return { texto: opcion, explicacion: "" };
  }

  return {
    texto:
      opcion?.texto ??
      opcion?.text ??
      opcion?.opcion ??
      opcion?.contenido ??
      opcion?.label ??
      "",
    explicacion:
      opcion?.explicacion ??
      opcion?.explanation ??
      ""
  };
}"""

# Insert or replace normalizarOpcion
if "function normalizarOpcion" in app_js:
    app_js = re.sub(r'function normalizarOpcion\(opcion\) \{[\s\S]*?\}\s*\}', norm_fn, app_js)
    if "function normalizarOpcion" not in app_js:
        app_js = re.sub(r'function normalizarOpcion\(opcion\) \{[\s\S]*?\}', norm_fn, app_js)
else:
    app_js = norm_fn + "\n" + app_js

# Update loop inside loadChoice
# We need to find the loop starting at `((q.opciones ?? q.opcoes) || []).forEach((opt, idx) => {`
target_loop_regex = r'\(\(q\.opciones \?\? q\.opcoes\) \|\| \[\]\)\.forEach\(\(opt, idx\) => \{[\s\S]*?container\.appendChild\(btn\);\s*\}\);'

replacement_loop = """((q.opciones ?? q.opcoes) || []).forEach((opt, idx) => {
      const opcionNormalizada = normalizarOpcion(opt);
      console.log("OPCIÓN REAL:", opt);
      console.log("OPCIÓN NORMALIZADA:", opcionNormalizada);

      const btn = document.createElement('button');
      btn.className = 'option-btn';
      btn.id        = `opt-${idx}`;
      btn.setAttribute('role', 'radio');
      btn.setAttribute('aria-checked', 'false');
      
      const letra = typeof letraOpcion === 'function' ? letraOpcion(idx) : String.fromCharCode(65 + idx);

      btn.innerHTML = `
        <div class="option-content">
          <span class="option-letter">${letra}</span>
          <span class="option-text">${escaparHTML(opcionNormalizada.texto)}</span>
        </div>
        <div class="option-explanation hidden"></div>
      `;
      
      btn.onclick   = () => {
        if (yaValidado) return;
        document.querySelectorAll('.option-btn').forEach(b => {
            b.classList.remove('selected');
            b.setAttribute('aria-checked', 'false');
        });
        btn.classList.add('selected');
        btn.setAttribute('aria-checked', 'true');
        selectedOption = idx;
        if (btnValidar) btnValidar.disabled = false;
      };
      container.appendChild(btn);
    });"""

app_js = re.sub(target_loop_regex, replacement_loop, app_js)

# Also ensure validación loop uses normalizarOpcion
if "normalizarOpcion(rawOpts[i])" not in app_js:
    app_js = app_js.replace(
        "const opt = q.opciones[i];",
        "const optNorm = normalizarOpcion((q.opciones || q.opcoes || [])[i]);"
    )

with open("app.js", "w", encoding="utf-8") as f:
    f.write(app_js)

print("2. app.js updated with exact normalizarOpcion function and option renderer.")
