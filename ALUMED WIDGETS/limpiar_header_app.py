with open("app.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

clean_head = """// ==========================================
// ALUMED OS - FUNCIONES HELPER PRINCIPALES
// ==========================================
function normalizarTexto(valor = "") {
  return String(valor)
    .normalize("NFD")
    .replace(/[\\u0300-\\u036f]/g, "")
    .trim()
    .toLowerCase();
}

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
}
"""

# Find where `function generarInformeDiagnosticoUNLP` or similar begins
rest_code_idx = 0
for i, l in enumerate(lines):
    if "function generarInformeDiagnosticoUNLP" in l or "const REGLAS_PARCIALES_UNLP" in l:
        rest_code_idx = i
        break

new_app = clean_head + "\n" + "".join(lines[rest_code_idx:])

with open("app.js", "w", encoding="utf-8") as f:
    f.write(new_app)

print("Header de app.js reconstruido sin tokens huérfanos.")
