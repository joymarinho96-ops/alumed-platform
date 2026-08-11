import re
import os

print("=== APLICANDO NORMALIZACIÓN DE TEXTO Y LOGS DE CONSOLA REQUERIDOS ===")

with open("app.js", "r", encoding="utf-8") as f:
    app_code = f.read()

# Replace or insert normalizarTexto helper
normalizar_helper = """
function normalizarTexto(valor = "") {
  return String(valor)
    .normalize("NFD")
    .replace(/[\\u0300-\\u036f]/g, "")
    .trim()
    .toLowerCase();
}
"""

if "function normalizarTexto" in app_code:
    app_code = re.sub(r'function normalizarTexto[\s\S]*?\}\s*\}', normalizar_helper, app_code)
    if "function normalizarTexto" not in app_code:
        app_code = re.sub(r'function normalizarTexto[\s\S]*?\}', normalizar_helper, app_code)
else:
    app_code = normalizar_helper + "\n" + app_code

# Update prepararEntrenamiento function
prep_norm = """function prepararEntrenamiento(tabId, materiaSolicitada, btnEl) {
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
}"""

app_code = re.sub(r'function prepararEntrenamiento\(tabId, materiaKeyOrName, btnEl\) \{[\s\S]*?loadPinche\(\);\s*\}\s*\}', prep_norm, app_code)
if "function prepararEntrenamiento" not in app_code or "reqNorm" not in app_code:
    app_code = re.sub(r'function prepararEntrenamiento\(tabId, materia, btnEl\) \{[\s\S]*?loadPinche\(\);\s*\}\s*\}', prep_norm, app_code)

# Replace DOMContentLoaded listener with exact required console.logs and try/catch wrapper
dom_unified_clean = """
// ==========================================
// INICIALIZACIÓN UNIFICADA CON TRY/CATCH Y LOGS EXPLICITOS
// ==========================================
document.addEventListener("DOMContentLoaded", () => {
  try {
    if (typeof bancoDados === "undefined") {
      throw new Error("bancoDados no está disponible en el entorno global");
    }

    console.log("Primera materia:", bancoDados.choices?.[0]?.materia);
    console.log(
      "Materias disponibles:",
      [...new Set(bancoDados.choices.map(q => q.materia))]
    );
    console.log(
      "Coincidencias biologia:",
      bancoDados.choices.filter(q =>
        normalizarTexto(q.materia).includes("biologia")
      ).length
    );

    console.log("Banco cargado exitosamente", {
      choices: bancoDados.choices?.length || 0,
      orales: bancoDados.orales?.length || 0,
      pinches: bancoDados.pinches?.length || 0
    });

    const bioBtn = document.getElementById("nav-bio");
    prepararEntrenamiento("choices", "Biología", bioBtn);
  } catch (error) {
    console.error("Error al inicializar el simulador:", error);

    const pregunta = document.getElementById("mc-pergunta");
    if (pregunta) {
      pregunta.textContent =
        "No se pudo cargar el banco de preguntas. Revisá la consola.";
    }
  }
});
"""

app_code = re.sub(r'// ==========================================\s*// INICIALIZACIÓN[\s\S]*$', dom_unified_clean, app_code)
if "INICIALIZACIÓN UNIFICADA CON TRY/CATCH" not in app_code:
    app_code += "\n" + dom_unified_clean

with open("app.js", "w", encoding="utf-8") as f:
    f.write(app_code)

print("app.js actualizado con normalizarTexto e inicializador try/catch unificado.")
