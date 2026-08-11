const fs = require('fs');

const MAPAS_TP = {
  "Biología": {
    "TP1": { nombre: "Introducción a la Biología & Organización Celular", keywords: ["procariota", "eucariota", "célula", "organela", "virus", "viroide", "prion"] },
    "TP2": { nombre: "Componentes Químicos I (Agua y Pequeñas Moléculas)", keywords: ["agua", "puente de hidrógeno", "ph", "buffer", "tampón", "ion", "hidrofílico", "hidrofóbico"] },
    "TP3": { nombre: "Componentes Químicos II (Lípidos y Macromoléculas)", keywords: ["lípido", "proteína", "carbohidrato", "aminoácido", "enlace peptídico", "glúcido", "ácido graso", "triglicérido", "fosfolípido"] },
    "TP4": { nombre: "Bioenergética y Cinética Enzimática", keywords: ["enzima", "catálisis", "sitio activo", "km", "vmax", "inhibidor", "alostérico", "atp", "energía libre", "termodinámica"] },
    "TP5": { nombre: "Mecanismos Genéticos Básicos I", keywords: ["adn", "arn", "nucleótido", "replicación", "polimerasa", "horquilla", "codón", "genes"] },
    "TP6": { nombre: "Mecanismos Genéticos Básicos II (Expresión y Regulación)", keywords: ["transcripción", "traducción", "promotor", "operón", "splicing", "intrón", "exón", "ribosoma", "arnt", "arnm"] },
    "TP7": { nombre: "Membrana Plasmática y Transporte (Ósmosis/Osmolaridad)", keywords: ["membrana", "transporte", "difusión", "ósmosis", "osmolaridad", "bomba", "na+/k+", "canales", "acuaporina", "bicapa"] },
    "TP8": { nombre: "Metabolismo Intermedio y Mitocondrias", keywords: ["mitocondria", "glucólisis", "krebs", "cadena respiratoria", "fosforilación oxidativa", "piruvato", "atp sintasa"] },
    "TP9": { nombre: "Membranas Internas I (RE y Golgi)", keywords: ["retículo", "endoplásmico", "golgi", "glicosilación", "secreción", "vesícula", "somatico", "rugoso", "liso"] },
    "TP10": { nombre: "Membranas Internas II (Lisosomas y Peroxisomas)", keywords: ["lisosoma", "peroxisoma", "endosoma", "fagocitosis", "autofagia", "hidrolasa", "catalasa", "digestión celular"] },
    "TP11": { nombre: "El Núcleo Celular", keywords: ["núcleo", "envoltura nuclear", "poro nuclear", "nucleólo", "cromatina", "heterocromatina", "eucromatina", "histona"] },
    "TP12": { nombre: "Citoesqueleto, Adhesión y Matriz Extracelular", keywords: ["citoesqueleto", "microtúbulo", "microfilamento", "filamento intermedio", "actina", "tubulina", "cilio", "flagelo", "matriz extracelular", "colágeno"] },
    "TP13": { nombre: "Ciclo Celular y Apoptosis", keywords: ["ciclo celular", "g1", "g2", "s", "p53", "cdk", "ciclina", "checkpoint", "punto de control", "apoptosis", "caspasa"] },
    "TP14": { nombre: "Mecanismos de División Celular (Mitosis y Meiosis)", keywords: ["mitosis", "meiosis", "profase", "metafase", "anafase", "telofase", "huso", "crossing over", "recombinación", "gameto"] },
    "TP15": { nombre: "Transmisión del Material Genético", keywords: ["mendel", "herencia", "alelo", "genotipo", "fenotipo", "dominante", "recesivo", "ligado al sexo"] },
    "TP16": { nombre: "Las Células en su Contexto Social (Comunicación)", keywords: ["comunicación celular", "receptor", "ligando", "segundo mensajero", "ampc", "quinasa", "transducción", "señalización"] }
  },
  "Histología y Embriología": {
    "TP1": { nombre: "Técnica Histológica", keywords: ["técnica", "fijación", "hematoxilina", "eosina", "tinción", "microscopio", "corte", "parafina"] },
    "TP2": { nombre: "Tejido Epitelial", keywords: ["epitelio", "revestimiento", "glandular", "cilio", "microvellosidad", "lámina basal", "unión ocluyente", "desmosoma"] },
    "TP3": { nombre: "Tejido Conectivo y Adiposo", keywords: ["conectivo", "conjuntivo", "fibroblasto", "colágeno", "matriz", "adipocito", "grasa", "laxo", "denso"] },
    "TP4": { nombre: "Tejido Cartilaginoso y Óseo", keywords: ["hueso", "cartílago", "osteocito", "osteoblasto", "osteoclasto", "condrocito", "osteona", "havers", "trabécula"] },
    "TP5": { nombre: "Sangre y Hematopoyesis", keywords: ["sangre", "glóbulo", "eritrocito", "leucocito", "plaqueta", "médula ósea", "hematopoyesis", "neutrófilo", "linfocito"] },
    "TP6": { nombre: "Tejido Nervioso y Sistema Nervioso", keywords: ["neurona", "axón", "dendrita", "glía", "astroctio", "oligodendrocito", "mielina", "sinapsis", "sustancia gris", "sustancia blanca"] },
    "TP7": { nombre: "Tejido Muscular", keywords: ["músculo", "estriado", "liso", "cardíaco", "sarcómero", "miocito", "miofilamento", "disco intercalar"] },
    "TP8": { nombre: "Sistema Cardiovascular", keywords: ["vaso", "arteria", "vena", "capilar", "endotelio", "corazón", "miocardio", "endocardio"] },
    "TP9": { nombre: "Tejido Linfoide y Sistema Linfoide", keywords: ["linfático", "ganglio", "bazo", "timo", "amígdala", "folículo linfoide"] },
    "TP10": { nombre: "Embriología: Fecundación y Primeras Semanas", keywords: ["fecundación", "zocota", "mórula", "blastocisto", "implantación", "trofoblasto", "embrioblasto", "segregación"] },
    "TP11": { nombre: "Embriología: 3ª y 4ª Semana (Gastrulación/Neurulación)", keywords: ["gastrulación", "ectodermo", "mesodermo", "endodermo", "notocorda", "tubo neural", "somita", "neurulación"] },
    "TP12": { nombre: "Embriología: Placenta y Anexos Embrionarios", keywords: ["placenta", "corion", "amnios", "cordón umbilical", "vellosidad coriónica", "saco vitelino"] }
  },
  "Anatomía Cátedra A": {
    "TP1": { nombre: "Huesos del Miembro Superior", keywords: ["escápula", "clavícula", "húmero", "cúbito", "radio", "carpo", "metacarpo", "falange"] },
    "TP2": { nombre: "Huesos del Miembro Inferior", keywords: ["coxal", "fémur", "rótula", "tibia", "peroné", "tarso", "metatarso"] },
    "TP3": { nombre: "Columna Vertebral y Tórax", keywords: ["vértebra", "cervical", "torácica", "lumbar", "sacro", "costilla", "esternón"] },
    "TP4": { nombre: "Cráneo (Bóveda y Base)", keywords: ["frontal", "parietal", "occipital", "temporal", "esfenoides", "etmoides", "agujero", "fosa cranial"] },
    "TP5": { nombre: "Macizo Facial", keywords: ["maxilar", "cigomático", "nasal", "vómer", "mandíbula", "orbita"] },
    "TP6": { nombre: "Artrología", keywords: ["articulación", "sinovial", "ligamento", "cápsula", "menisco", "diartrosis"] },
    "TP7": { nombre: "Miología Miembro Superior", keywords: ["biceps", "triceps", "deltoides", "pectoral", "manguito rotador", "pronador", "supinador"] },
    "TP8": { nombre: "Miología Miembro Inferior", keywords: ["cuádriceps", "isquiotibial", "glúteo", "gastrocnemio", "sóleo", "aductor"] },
    "TP9": { nombre: "Miología del Tronco", keywords: ["recto abdominal", "oblicuo", "diafragma", "dorsal ancho", "trapecio"] },
    "TP10": { nombre: "Miología Cabeza y Cuello", keywords: ["estrenocleidomastoideo", "masetero", "temporal", "mimica", "suprahioideo"] }
  }
};

function clasificarItem(item) {
  const materia = item.materia || "Biología";
  const texto = ((item.pregunta || item.pergunta || "") + " " + (item.explicacion || item.justificativa || "") + " " + JSON.stringify(item.opciones || [])).toLowerCase();
  
  const mapa = MAPAS_TP[materia] || MAPAS_TP["Biología"];
  let maxScore = 0;
  let bestTp = "TP1";
  let kwMatch = [];

  Object.keys(mapa).forEach(tpId => {
    let score = 0;
    let matches = [];
    mapa[tpId].keywords.forEach(kw => {
      if (texto.includes(kw)) {
        score++;
        matches.push(kw);
      }
    });
    if (score > maxScore) {
      maxScore = score;
      bestTp = tpId;
      kwMatch = matches;
    }
  });

  const confianza = maxScore >= 3 ? "alta" : (maxScore >= 1 ? "media" : "baja");
  const estado = (confianza === "alta" || confianza === "media") ? "clasificado" : "pendiente_revision";

  item.tpPrincipal = bestTp;
  item.tpId = bestTp;
  item.tema = mapa[bestTp] ? mapa[bestTp].nombre : "General";
  item.subtema = kwMatch.length > 0 ? kwMatch[0].charAt(0).toUpperCase() + kwMatch[0].slice(1) : "Conceptos Básicos";
  item.conceptosClave = kwMatch.length > 0 ? kwMatch : ["general"];
  item.tpRelacionados = Object.keys(mapa).filter(k => k !== bestTp).slice(0, 2);
  item.justificacionClasificacion = `Anclado a ${bestTp} por afinidad semántica con términos clave: ${kwMatch.slice(0,3).join(', ') || 'análisis temático unificado'}.`;
  item.confianzaClasificacion = confianza;
  item.estadoClasificacion = estado;

  return item;
}

// Read data.js as JS text
let dataRaw = fs.readFileSync('data.js', 'utf8');

// Match starting position of JSON
const firstBrace = dataRaw.indexOf('{');
const lastBrace = dataRaw.lastIndexOf('}');
const jsonStr = dataRaw.substring(firstBrace, lastBrace + 1);

let bancoDados;
try {
  bancoDados = JSON.parse(jsonStr);
} catch (e) {
  // If parsing fails, eval safely
  bancoDados = eval('(' + jsonStr + ')');
}

["choices", "pinches", "orales"].forEach(cat => {
  if (bancoDados[cat]) {
    bancoDados[cat].forEach(clasificarItem);
  }
});

const outStr = "const bancoDados = " + JSON.stringify(bancoDados, null, 2) + ";";
fs.writeFileSync('data.js', outStr, 'utf8');
console.log("Clasificación pedagógica por TP completada exitosamente.");
