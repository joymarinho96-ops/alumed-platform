import json
import re

print("=== APLICANDO SOLUCIÓN DEFINITIVA DE ENCODING Y MATCHING ===")

# 1. FIX index.html SCRIPT TAGS
with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace('<script src="data.js"></script>', '<script src="data.js" charset="utf-8"></script>')
html = html.replace('<script src="app.js"></script>', '<script src="app.js" charset="utf-8"></script>')

# Replace nav-btn onclick calls to pass ascii keys
html = html.replace("prepararEntrenamiento('choices', 'Biología', this)", "prepararEntrenamiento('choices', 'biologia', this)")
html = html.replace("prepararEntrenamiento('choices', 'Histología y Embriología', this)", "prepararEntrenamiento('choices', 'histo_embrio', this)")
html = html.replace("prepararEntrenamiento('oral', 'Anatomía Cátedra A', this)", "prepararEntrenamiento('oral', 'anato_a', this)")
html = html.replace("prepararEntrenamiento('pinches', 'Anatomía Cátedra B', this)", "prepararEntrenamiento('pinches', 'anato_b', this)")
html = html.replace("prepararEntrenamiento('oral', 'Anatomía Cátedra C', this)", "prepararEntrenamiento('oral', 'anato_c', this)")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("1. index.html actualizado con charset=utf-8 y claves ASCII en nav.")

# 2. FIX data.js MATERIA KEYS
with open("data.js", "r", encoding="utf-8") as f:
    raw = f.read()

first_b = raw.find('{')
last_b = raw.rfind('}')
banco = json.loads(raw[first_b:last_b+1])

choices = banco.get("choices", [])
orales = banco.get("orales", [])
pinches = banco.get("pinches", [])

for q in choices:
    mat = q.get("materia", "").lower()
    fuente = (q.get("fuenteInterna", "") or q.get("fuente", "")).lower()
    
    key = "biologia"
    materia_nombre = "Biología"
    
    if "histo" in mat or "embrio" in mat or "histo" in fuente or "embrio" in fuente:
        key = "histo_embrio"
        materia_nombre = "Histología y Embriología"
    elif "cátedra a" in mat or "catedra a" in mat or "anatomia-a" in fuente or "anato a" in fuente:
        key = "anato_a"
        materia_nombre = "Anatomía Cátedra A"
    elif "cátedra b" in mat or "catedra b" in mat or "anatomia-b" in fuente or "anato b" in fuente:
        key = "anato_b"
        materia_nombre = "Anatomía Cátedra B"
    elif "cátedra c" in mat or "catedra c" in mat or "anatomia-c" in fuente or "union anato c" in fuente or "anato c" in mat:
        key = "anato_c"
        materia_nombre = "Anatomía Cátedra C"
    elif "bio" in mat or "bio" in fuente:
        key = "biologia"
        materia_nombre = "Biología"
        
    q["materiaKey"] = key
    q["materia"] = materia_nombre

banco["choices"] = choices

out_content = "const bancoDados = " + json.dumps(banco, ensure_ascii=False, indent=2) + ";"
with open("data.js", "w", encoding="utf-8") as f:
    f.write(out_content)
print(f"2. data.js actualizado. {len(choices)} preguntas etiquetadas con materiaKey.")

# 3. FIX app.js FILTERING AND RENDER LOGIC
with open("app.js", "r", encoding="utf-8") as f:
    app_js = f.read()

prep_robust = """function prepararEntrenamiento(tabId, materiaKeyOrName, btnEl) {
  // 1. Switch Tab UI
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
  const sec = document.getElementById(`tab-${tabId}`);
  if (sec) sec.classList.add('active');
  if (btnEl) btnEl.classList.add('active');

  // 2. Set Materia and Filter robustly
  if (materiaKeyOrName) {
    currentMateria = materiaKeyOrName;
    const targetKey = materiaKeyOrName.toLowerCase();
    
    filteredChoices = (bancoDados.choices || []).filter(q => {
      if (q.materiaKey && q.materiaKey === targetKey) return true;
      if (q.materia && q.materia.toLowerCase().includes(targetKey)) return true;
      if (targetKey.includes('bio') && (q.materiaKey === 'biologia' || (q.materia && q.materia.toLowerCase().includes('bio')))) return true;
      if (targetKey.includes('histo') && (q.materiaKey === 'histo_embrio' || (q.materia && q.materia.toLowerCase().includes('histo')))) return true;
      if (targetKey.includes('anato_a') && (q.materiaKey === 'anato_a' || (q.materia && q.materia.toLowerCase().includes('a')))) return true;
      if (targetKey.includes('anato_b') && (q.materiaKey === 'anato_b' || (q.materia && q.materia.toLowerCase().includes('b')))) return true;
      if (targetKey.includes('anato_c') && (q.materiaKey === 'anato_c' || (q.materia && q.materia.toLowerCase().includes('c')))) return true;
      return false;
    });

    // Ultimate Fallback if zero items matched
    if (filteredChoices.length === 0) {
      filteredChoices = bancoDados.choices || [];
    }

    currentChoiceIndex = 0;

    if (tabId === 'choices' || tabId === 'oral') {
      loadChoice();
    }
    if (tabId === 'pinches') {
      loadPinche();
    }
  }
}"""

app_js = re.sub(r'function prepararEntrenamiento\(tabId, materiaKeyOrName, btnEl\) \{[\s\S]*?loadPinche\(\);\s*\}\s*\}', prep_robust, app_js)
if "function prepararEntrenamiento" not in app_js:
    app_js = re.sub(r'function prepararEntrenamiento\(tabId, materia, btnEl\) \{[\s\S]*?loadPinche\(\);\s*\}\s*\}', prep_robust, app_js)

with open("app.js", "w", encoding="utf-8") as f:
    f.write(app_js)

print("3. app.js actualizado con filtrado por materiaKey robusto.")
