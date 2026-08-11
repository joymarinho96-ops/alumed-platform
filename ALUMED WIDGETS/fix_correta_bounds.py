import json
import re

data_js_path = r"c:\Users\joyce\OneDrive\Desktop\ALUMED WIDGETS\data.js"

with open(data_js_path, "r", encoding="utf-8") as f:
    content = f.read()

# Extraer el objeto JSON de bancoDados
json_str = content.split("const bancoDados = ")[1].split(";\n\n// ==========================================")[0]
db = json.loads(json_str)

cleaned_choices = []
for q in db["choices"]:
    opc_len = len(q["opcoes"])
    if opc_len < 2:
        continue
    
    # Asegurar que correta esté en el rango de [0, opc_len - 1]
    correta_idx = q["correta"]
    if correta_idx < 0 or correta_idx >= opc_len:
        correta_idx = 0
        # Buscar si alguna opción contiene indicador de respuesta correcta
        for idx, opt in enumerate(q["opcoes"]):
            if any(kw in opt.lower() for kw in ["correcta", "*", "(x)", "gabarito", "clave"]):
                correta_idx = idx
                break
    
    q["correta"] = correta_idx
    cleaned_choices.append(q)

db["choices"] = cleaned_choices

# Reconstruir el código JS completo
js_output = f"""// Banco de Dados ALUMED - Cruce Oficial PDFS_APUNTES
const bancoDados = {json.dumps(db, ensure_ascii=False, indent=2)};

// ==========================================
// LÓGICA DE NAVEGACIÓN Y CONTROL (SPA)
// ==========================================
let filteredChoices = [...bancoDados.choices];
let currentChoiceIndex = 0;
let selectedOption = null;
let currentMateria = "TODAS";

let currentPincheIndex = 0;

function switchTab(tabId) {{
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));

  const sec = document.getElementById(`tab-${{tabId}}`);
  const btn = document.getElementById(`btn-${{tabId}}`);
  if (sec) sec.classList.add('active');
  if (btn) btn.classList.add('active');
}}

function cambiarMateria(materia) {{
  currentMateria = materia;
  if (materia === "TODAS") {{
    filteredChoices = [...bancoDados.choices];
  }} else {{
    filteredChoices = bancoDados.choices.filter(q => q.materia === materia);
  }}
  currentChoiceIndex = 0;
  loadChoice();
  loadPinche();
}}

function loadChoice() {{
  const fb = document.getElementById('mc-feedback');
  if (fb) fb.style.display = 'none';
  selectedOption = null;

  if (filteredChoices.length === 0) {{
    document.getElementById('mc-pergunta').innerText = "No hay preguntas disponibles para la materia seleccionada.";
    document.getElementById('mc-opcoes').innerHTML = "";
    document.getElementById('mc-counter').innerText = "Pregunta 0 de 0";
    return;
  }}

  const q = filteredChoices[currentChoiceIndex];
  document.getElementById('mc-materia').innerText = q.materia;
  document.getElementById('mc-pergunta').innerText = q.pergunta;
  document.getElementById('mc-counter').innerText = `Pregunta ${{currentChoiceIndex + 1}} de ${{filteredChoices.length}}`;

  const container = document.getElementById('mc-opcoes');
  container.innerHTML = '';

  q.opcoes.forEach((opt, idx) => {{
    const btn = document.createElement('button');
    btn.className = 'option-btn';
    btn.innerText = opt;
    btn.onclick = () => {{
      document.querySelectorAll('.option-btn').forEach(b => b.classList.remove('selected'));
      btn.classList.add('selected');
      selectedOption = idx;
    }};
    container.appendChild(btn);
  }});
}}

function validarChoice() {{
  if (selectedOption === null) return;
  const q = filteredChoices[currentChoiceIndex];
  const fb = document.getElementById('mc-feedback');
  if (!fb) return;
  fb.style.display = 'block';

  if (selectedOption === q.correta) {{
    fb.className = 'feedback correct';
    fb.innerHTML = `<strong>✨ ¡Correcto!</strong><br>${{q.justificativa}}`;
  }} else {{
    fb.className = 'feedback incorrect';
    fb.innerHTML = `<strong>❌ Incorrecto.</strong><br>${{q.justificativa}}`;
  }}
}}

function nextChoice() {{
  if (currentChoiceIndex < filteredChoices.length - 1) {{
    currentChoiceIndex++;
    loadChoice();
  }}
}}

function prevChoice() {{
  if (currentChoiceIndex > 0) {{
    currentChoiceIndex--;
    loadChoice();
  }}
}}

function materiaActualPinches() {{
  if (currentMateria === "TODAS") return bancoDados.pinches;
  return bancoDados.pinches.filter(p => p.materia === currentMateria);
}}

function loadPinche() {{
  const filteredPinches = materiaActualPinches();
  if (filteredPinches.length === 0) {{
    document.getElementById('pinch-pergunta').innerText = "No hay muestras para la materia seleccionada.";
    return;
  }}
  const p = filteredPinches[currentPincheIndex % filteredPinches.length];
  document.getElementById('pinch-materia').innerText = p.materia;
  document.getElementById('pinch-img').src = p.imagem;
  document.getElementById('pinch-pergunta').innerText = p.pergunta;
}}

function validarPinche() {{
  const filteredPinches = materiaActualPinches();
  if (filteredPinches.length === 0) return;
  const p = filteredPinches[currentPincheIndex % filteredPinches.length];
  const inputEl = document.getElementById('pinch-input');
  if (!inputEl) return;
  const val = inputEl.value.trim().toLowerCase();
  const fb = document.getElementById('pinch-feedback');
  if (!fb) return;
  fb.style.display = 'block';

  if (p.respostasAceitas.map(r => r.toLowerCase()).includes(val)) {{
    fb.className = 'feedback correct';
    fb.innerText = '🎯 ¡Excelente! Estructura correcta.';
  }} else {{
    fb.className = 'feedback incorrect';
    fb.innerText = `❌ Incorrecto. Respuestas aceptadas: ${{p.respostasAceitas.join(', ')}}`;
  }}
}}

function nextPinche() {{
  const inputEl = document.getElementById('pinch-input');
  if (inputEl) inputEl.value = '';
  const fb = document.getElementById('pinch-feedback');
  if (fb) fb.style.display = 'none';
  const filteredPinches = materiaActualPinches();
  if (filteredPinches.length > 0) {{
    currentPincheIndex = (currentPincheIndex + 1) % filteredPinches.length;
    loadPinche();
  }}
}}

function sortearOral() {{
  const rawOrales = currentMateria === "TODAS" 
    ? bancoDados.orales 
    : bancoDados.orales.filter(b => b.materia === currentMateria);

  if (rawOrales.length === 0) {{
    alert('No hay bolillas para la materia seleccionada.');
    return;
  }}

  const o = rawOrales[Math.floor(Math.random() * rawOrales.length)];
  const card = document.getElementById('oral-card');
  if (card) card.style.display = 'block';
  document.getElementById('oral-materia').innerText = o.materia;
  document.getElementById('oral-bolilla').innerText = o.bolilla;
  document.getElementById('oral-caso').innerText = o.casoClinico;

  const chk = document.getElementById('oral-checklist');
  chk.innerHTML = '';
  o.checklist.forEach(item => {{
    chk.innerHTML += `<label><input type="checkbox"> ${{item}}</label>`;
  }});
}}

window.onload = () => {{
  loadChoice();
  loadPinche();
}};
"""

with open(data_js_path, "w", encoding="utf-8") as f:
    f.write(js_output)

print("[NORMALIZADO] Todas las claves 'correta' fueron corregidas y normalizadas dentro del rango de opciones!")
