import re

with open("app.js", "r", encoding="utf-8") as f:
    app_js = f.read()

# Enhance tag rendering in loadChoice
old_tag_line = r"document\.getElementById\('mc-materia-tag'\)\.innerText\s*=\s*.*;"
new_tag_line = "document.getElementById('mc-materia-tag').innerText = `${q.materia || currentMateria} • ${q.tpPrincipal || 'TP1'}: ${q.tema || 'Tema General'}`;"

app_js = re.sub(old_tag_line, new_tag_line, app_js)

with open("app.js", "w", encoding="utf-8") as f:
    f.write(app_js)

print("Tag display enhanced with Materia + TP + Tema in app.js.")
