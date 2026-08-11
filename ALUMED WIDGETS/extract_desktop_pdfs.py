import os
import json
import re
from pypdf import PdfReader

desktop_path = r"C:\Users\joyce\OneDrive\Desktop"

pdf_files = [
    ("CUESTIONES BIOLOGIA ANUAL (7) (2).pdf", "Biología Celular"),
    ("CUESTIONES HISTO 1º CUADRIMESTRE - @ALUMEDINSTITUTO_211006_194327[1].pdf", "Histología y Embriología"),
    ("SIMULACRO HyE PARCIAL 1 (2).pdf", "Histología y Embriología"),
    ("HISTO TODOS.pdf", "Histología y Embriología"),
    ("BIOLOGIA - JOYCE MARINHO.pdf", "Biología Celular")
]

choices_list = []
q_id = 1

for filename, materia in pdf_files:
    full_path = os.path.join(desktop_path, filename)
    if not os.path.exists(full_path):
        print(f"[AVISO] No encontrado: {filename}")
        continue
    
    print(f"[INFO] Leyendo: {filename} -> {materia}")
    try:
        reader = PdfReader(full_path)
        raw_text = ""
        # Leer hasta 50 páginas máximo por rapidez
        max_pages = min(len(reader.pages), 50)
        for i in range(max_pages):
            t = reader.pages[i].extract_text()
            if t:
                raw_text += t + "\n"

        blocks = re.split(r'\n(?=\d+[\.\-\)])', raw_text)
        for b in blocks:
            lines = [l.strip() for l in b.split('\n') if l.strip()]
            if len(lines) < 3:
                continue

            pergunta = lines[0]
            opcoes = []
            correta_idx = 0

            for l in lines[1:]:
                if re.match(r'^[a-dA-D][\.\)\-]', l):
                    opcoes.append(l)
                    if "correcta" in l.lower() or "*" in l or "(x)" in l.lower():
                        correta_idx = len(opcoes) - 1

            if len(opcoes) >= 2:
                choices_list.append({
                    "id": q_id,
                    "materia": materia,
                    "pergunta": pergunta[:300],
                    "opcoes": opcoes[:4],
                    "correta": correta_idx,
                    "justificativa": f"Pregunta extraída del apunte oficial: {filename}"
                })
                q_id += 1
    except Exception as e:
        print(f"[ERRO] al procesar {filename}: {e}")

print(f"[TOTAL] Extraídas {len(choices_list)} preguntas reales de los PDFs!")

# Cargar también preguntas de muestra ricas si son menos de 10
default_choices = [
    {
      "id": 1001,
      "materia": "Biología Celular",
      "pergunta": "¿Cuál de las siguientes organelas participa activamente en la desintoxicación de fármacos en el hepatocito?",
      "opcoes": [
        "A) Retículo Endoplásmico Rugoso (RER)",
        "B) Retículo Endoplásmico Liso (REL)",
        "C) Complejo de Golgi",
        "D) Lisosoma secundario"
      ],
      "correta": 1,
      "justificativa": "El REL contiene enzimas de la familia citocromo P450 especializadas en la detoxificación celular en tejidos hepáticos."
    },
    {
      "id": 1002,
      "materia": "Histología y Embriología",
      "pergunta": "¿Qué tipo de epitelio caracteriza la mucosa de la tráquea?",
      "opcoes": [
        "A) Epitelio cilíndrico simple con microvellosidades",
        "B) Epitelio plano estratificado no queratinizado",
        "C) Epitelio seudoestratificado cilíndrico ciliado con células caliciformes",
        "D) Epitelio polimorfo de transición"
      ],
      "correta": 2,
      "justificativa": "El epitelio respiratorio tráqueo-bronquial es seudoestratificado cilíndrico ciliado con células caliciformes secretoras de mucus."
    },
    {
      "id": 1003,
      "materia": "Anatomía Cátedra A",
      "pergunta": "¿Qué estructura discurre por el túnel carpiano junto a los tendones flexores de los dedos?",
      "opcoes": [
        "A) Nervio Cubital",
        "B) Nervio Mediano",
        "C) Arteria Radial",
        "D) Nervio Musculocutáneo"
      ],
      "correta": 1,
      "justificativa": "El nervio mediano transcurre por el túnel carpiano por debajo del retináculo flexor junto a los 9 tendones flexores."
    },
    {
      "id": 1004,
      "materia": "Anatomía Cátedra B",
      "pergunta": "¿En qué cavidad cardíaca desemboca el Seno Coronario?",
      "opcoes": [
        "A) Ventrículo Izquierdo",
        "B) Aurícula Derecha",
        "C) Aurícula Izquierda",
        "D) Ventrículo Derecho"
      ],
      "correta": 1,
      "justificativa": "El seno coronario recoge la mayor parte de las venas cardíacas y desemboca en la pared posterior de la Aurícula Derecha."
    },
    {
      "id": 1005,
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

# Fusionar
all_choices = choices_list + default_choices

pinches_data = [
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
      "pergunta": "Identifique el tejido/estructura señalada en el corte histológico:",
      "respostasAceitas": ["glomerulo", "glomerulo renal", "glomérulo", "glomérulo renal"]
    },
    {
      "id": 3,
      "materia": "Anatomía Cátedra B",
      "imagem": "https://images.unsplash.com/photo-1530210124550-912dc1381cb8?auto=format&fit=crop&w=600&q=80",
      "pergunta": "Identifique el vaso arterial emergente del ventrículo izquierdo:",
      "respostasAceitas": ["aorta", "arteria aorta", "aorta ascendente", "a. aorta"]
    }
]

orales_data = [
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
      "casoClinico": "Muestra celular con defecto genético en las proteínas de cubierta COP II, generando acumulación proteica en el retículo endoplásmico rugoso.",
      "checklist": [
        "Direccionalidad del transporte vesicular: RER a Golgi (COP II) vs. retrógrado (COP I)",
        "Papel de las GTPasas Rab y complejo SNARE en el acoplamiento",
        "Modificaciones glucídicas en las cisternas del complejo de Golgi"
      ]
    },
    {
      "id": 3,
      "materia": "Anatomía Cátedra C",
      "bolilla": "Bolilla 12: Irrigación Encefálica y Círculo Arterial de Willis",
      "casoClinico": "Paciente de 62 años consulta por pérdida súbita de fuerza en el brazo derecho y alteración del lenguaje comprensivo.",
      "checklist": [
        "Origen y anastomosis entre el sistema carotídeo interno y el sistema vertebrobasilar",
        "Componentes del Polígono Arterial de Willis (comunicantes anterior y posterior)",
        "Territorio de irrigación de la arteria cerebral media (Silviana)"
      ]
    }
]

full_db = {
    "choices": all_choices,
    "pinches": pinches_data,
    "orales": orales_data
}

# Código JS final con la lógica de control completa
js_code = f"""// Banco de Dados ALUMED - 1er Cuatrimestre UBA
const bancoDados = {json.dumps(full_db, ensure_ascii=False, indent=2)};

// ==========================================
// LÓGICA DE NAVEGACIÓN Y APLICACIÓN
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

// Pinches
function loadPinche() {{
  const filteredPinches = materiaActualPinches();
  if (filteredPinches.length === 0) return;
  const p = filteredPinches[currentPincheIndex % filteredPinches.length];
  document.getElementById('pinch-materia').innerText = p.materia;
  document.getElementById('pinch-img').src = p.imagem;
  document.getElementById('pinch-pergunta').innerText = p.pergunta;
}}

function materiaActualPinches() {{
  if (currentMateria === "TODAS") return bancoDados.pinches;
  return bancoDados.pinches.filter(p => p.materia === currentMateria);
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

// Oral
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

with open(r"c:\Users\joyce\OneDrive\Desktop\ALUMED WIDGETS\data.js", "w", encoding="utf-8") as f:
    f.write(js_code)

print("[COMPLETADO] data.js actualizado con exito con preguntas extraidas de los PDFs!")
