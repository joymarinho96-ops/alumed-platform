import re

with open("app.js", "r", encoding="utf-8") as f:
    app_code = f.read()

# Filter out questions without valid correct index for PARCIAL_REAL mode
parcial_filter_rule = """
  // Excluir preguntas sin gabarito válido de los simulacros autocorregibles (Regla 5)
  filteredChoices = filteredChoices.filter(q => obtenerIndiceCorrecto(q) !== null);
"""

if "obtenerIndiceCorrecto(q) !== null" not in app_code:
    app_code = app_code.replace(
        "if (regla.totalPreguntas && filteredChoices.length > regla.totalPreguntas) {",
        parcial_filter_rule + "\n  if (regla.totalPreguntas && filteredChoices.length > regla.totalPreguntas) {"
    )

with open("app.js", "w", encoding="utf-8") as f:
    f.write(app_code)

print("Regla 5 (Filtro de gabaritos en simulacros reales) aplicada a app.js.")
