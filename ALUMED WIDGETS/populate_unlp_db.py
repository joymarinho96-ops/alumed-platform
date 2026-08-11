import os
import json
import re
from pypdf import PdfReader

apuntes_dir = r"c:\Users\joyce\OneDrive\Desktop\ALUMED WIDGETS\PDFS_APUNTES"
data_js_path = r"c:\Users\joyce\OneDrive\Desktop\ALUMED WIDGETS\data.js"

pdf_files = [f for f in os.listdir(apuntes_dir) if f.lower().endswith('.pdf')]

choices_list = []
pinches_list = []
orales_list = []

q_id = 1
p_id = 1
o_id = 1

def clasificar(filename):
    fn = filename.lower()
    if "biologia" in fn or "bio_" in fn:
        return "Biología Celular"
    elif "catedra a" in fn or "cat a" in fn:
        return "Anatomía Cátedra A"
    elif "catedra b" in fn or "cat b" in fn:
        return "Anatomía Cátedra B"
    elif "catedra c" in fn or "cat c" in fn or "union anato" in fn or "anatomia" in fn:
        return "Anatomía Cátedra C"
    else:
        return "Histología y Embriología"

for fname in pdf_files:
    fpath = os.path.join(apuntes_dir, fname)
    materia = clasificar(fname)
    print(f"[UNLP EXTRACTION] Leyendo {fname} -> {materia}")
    try:
        reader = PdfReader(fpath)
        raw_text = ""
        max_p = min(len(reader.pages), 60)
        for i in range(max_p):
            t = reader.pages[i].extract_text()
            if t:
                raw_text += t + "\n"

        blocks = re.split(r'\n(?=\d+[\.\-\)])|(?<=\n)(?=\d+[\.\-\)])', raw_text)
        for block in blocks:
            lines = [l.strip() for l in block.split('\n') if len(l.strip()) > 0]
            if len(lines) < 3:
                continue

            pergunta = lines[0]
            opcoes = []
            correta_idx = 0

            for l in lines[1:]:
                if re.match(r'^[a-dA-D][\.\)\-]', l) or re.match(r'^[1-4][\.\)\-]', l):
                    opcoes.append(l)
                    if "correcta" in l.lower() or "*" in l or "(x)" in l.lower():
                        correta_idx = len(opcoes) - 1

            if len(opcoes) >= 2:
                if correta_idx >= len(opcoes):
                    correta_idx = 0
                choices_list.append({
                    "id": q_id,
                    "materia": materia,
                    "pergunta": pergunta[:350],
                    "opcoes": opcoes[:4],
                    "correta": correta_idx,
                    "justificativa": f"Fuente de examen oficial UNLP: {fname}"
                })
                q_id += 1
    except Exception as e:
        print(f"Error procesando {fname}: {e}")

print(f"\n[UNLP COMPLETADO] Extraídas {len(choices_list)} preguntas de Multiple Choice!")

if len(choices_list) == 0:
    choices_list = [
        {
          "id": 1,
          "materia": "Biología Celular",
          "pergunta": "¿Cuál de las siguientes organelas participa activamente en la desintoxicación de fármacos en el hepatocito?",
          "opcoes": [
            "A) Retículo Endoplásmico Rugoso (RER)",
            "B) Retículo Endoplásmico Liso (REL)",
            "C) Complejo de Golgi",
            "D) Lisosoma secundario"
          ],
          "correta": 1,
          "justificativa": "El REL contiene enzimas de la familia citocromo P450 especializadas en la detoxificación celular."
        },
        {
          "id": 2,
          "materia": "Histología y Embriología",
          "pergunta": "¿Qué tipo de epitelio caracteriza la mucosa de la tráquea?",
          "opcoes": [
            "A) Epitelio cilíndrico simple con microvellosidades",
            "B) Epitelio plano estratificado no queratinizado",
            "C) Epitelio seudoestratificado cilíndrico ciliado con células caliciformes",
            "D) Epitelio polimorfo de transición"
          ],
          "correta": 2,
          "justificativa": "El epitelio respiratorio es seudoestratificado cilíndrico ciliado con células caliciformes."
        },
        {
          "id": 3,
          "materia": "Anatomía Cátedra C",
          "pergunta": "¿Qué vaso sanguíneo discurre por el surco interventricular anterior acompañado de la vena cardíaca magna?",
          "opcoes": [
            "A) Arteria coronaria derecha",
            "B) Rama interventricular anterior de la arteria coronaria izquierda",
            "C) Arteria circunfleja",
            "D) Arteria marginal derecha"
          ],
          "correta": 1,
          "justificativa": "La rama interventricular anterior proviene de la coronaria izquierda y transcurre junto a la vena cardíaca magna."
        }
    ]

pinches_list = [
    {
      "id": 1,
      "materia": "Anatomía Cátedra C",
      "imagem": "https://images.unsplash.com/photo-1559757175-5700dde675bc?auto=format&fit=crop&w=600&q=80",
      "pergunta": "Identifique la estructura vascular señalada en el preparado:",
      "respostasAceitas": ["arteria subclavia", "a. subclavia", "subclavia", "arteria subclavia izquierda"]
    },
    {
      "id": 2,
      "materia": "Histología y Embriología",
      "imagem": "https://images.unsplash.com/photo-1579154204601-01588f351e67?auto=format&fit=crop&w=600&q=80",
      "pergunta": "Identifique la estructura histológica renal señalada:",
      "respostasAceitas": ["glomerulo", "glomerulo renal", "glomérulo", "glomérulo renal"]
    }
]

orales_list = [
    {
      "id": 1,
      "materia": "Histología y Embriología",
      "bolilla": "Bolilla 5: Desarrollo Cardíaco y Circulación Fetal",
      "casoClinico": "Paciente recién nacido que presenta soplo cardíaco y leve cianosis en extremidades. Se evalúa falta de cierre del tabique interauricular.",
      "checklist": [
        "Formación y función del septum primum y septum secundum",
        "Mecanismo de cierre fisiológico del foramen oval al nacer",
        "Diferencias entre circulación fetal y postnatal (conducto arterioso y venoso)"
      ]
    },
    {
      "id": 2,
      "materia": "Biología Celular",
      "bolilla": "Bolilla 3: Tráfico de Endomembranas y Transporte Vesicular",
      "casoClinico": "Muestra celular con defecto genético en las proteínas de cubierta COP II, generando acumulación proteica en el RER.",
      "checklist": [
        "Direccionalidad del transporte vesicular: RER a Golgi (COP II) vs. retrógrado (COP I)",
        "Papel de las GTPasas Rab y complejo SNARE en el acoplamiento",
        "Modificaciones glucídicas en las cisternas del complejo de Golgi"
      ]
    }
]

full_db = {
    "choices": choices_list,
    "pinches": pinches_list,
    "orales": orales_list
}

js_output = f"""// Banco de Dados ALUMED - Medicina UNLP (Universidad Nacional de La Plata)
const bancoDados = {json.dumps(full_db, ensure_ascii=False, indent=2)};

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

print("[PROCESO UNLP COMPLETADO] data.js actualizado!")
