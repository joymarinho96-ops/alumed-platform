import re

with open("app.js", "r", encoding="utf-8") as f:
    app_js = f.read()

init_code = """
// ==========================================
// INICIALIZACIÓN AUTOMÁTICA AL CARGAR LA PÁGINA
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
  const bioBtn = document.getElementById('nav-bio');
  prepararEntrenamiento('choices', 'Biología', bioBtn);
});
"""

if "document.addEventListener('DOMContentLoaded'" not in app_js:
    app_js += "\n" + init_code

with open("app.js", "w", encoding="utf-8") as f:
    f.write(app_js)

print("DOMContentLoaded initialization added to app.js.")
