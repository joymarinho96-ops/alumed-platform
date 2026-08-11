import re

with open('app.js', 'r', encoding='utf-8') as f:
    app = f.read()

# Replace q.pergunta -> (q.pregunta ?? q.pergunta)
# Replace q.opcoes -> (q.opciones ?? q.opcoes)
# Replace q.justificativa -> (q.explicacion ?? q.justificativa)
# Also apply to item.* when mapping

# First, in search logic or filters:
app = app.replace('item.pergunta.toLowerCase()', '(item.pregunta ?? item.pergunta).toLowerCase()')
app = app.replace('q.pergunta', '(q.pregunta ?? q.pergunta)')

app = app.replace('q.opcoes', '(q.opciones ?? q.opcoes)')
app = app.replace('q.justificativa', '(q.explicacion ?? q.justificativa)')

# In loadChoice():
# const opcionesArr = (q.opciones ?? q.opcoes);
# q.opcoes.forEach( -> (q.opciones ?? q.opcoes).forEach(
app = app.replace('(q.opciones ?? q.opcoes).forEach', '(q.opciones ?? q.opcoes || []).forEach')

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(app)

print("app.js keys patched.")
