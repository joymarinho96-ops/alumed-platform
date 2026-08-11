import os

paths = [
    r"C:\Users\joyce\Downloads\alumesitemdesenvolvimento-main\alumed-platform\static\atlas_histologico\app.js",
    r"C:\Users\joyce\Downloads\alumesitemdesenvolvimento-main\alumed-platform\ALUMED WIDGETS\app.js"
]

for path in paths:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # The previous injection was:
    # if (!estadoSplit.stats) estadoSplit.stats = { totalRespuestas: 0, correctas: 0, racha: 0, maxRacha: 0, temasErrados: {} };
    # estadoSplit.stats.totalRespuestas++;
    # const esCorrecta = (obtenerIndiceCorrecto(q) === estadoSplit.selectedOption);
    # ...
    
    # We will replace "const esCorrecta = (obtenerIndiceCorrecto(q) === estadoSplit.selectedOption);" 
    # with "let esCorrectaLocal = (obtenerIndiceCorrecto(q) === estadoSplit.selectedOption);"
    # But wait, esCorrecta is declared right below it by the previous code:
    # const esCorrecta = (obtenerIndiceCorrecto(q) === estadoSplit.selectedOption);

    # Let's fix this specific block
    bad_block = """  if (!estadoSplit.stats) estadoSplit.stats = { totalRespuestas: 0, correctas: 0, racha: 0, maxRacha: 0, temasErrados: {} };
  estadoSplit.stats.totalRespuestas++;
  const esCorrecta = (obtenerIndiceCorrecto(q) === estadoSplit.selectedOption);
  if (esCorrecta) {
    estadoSplit.stats.correctas++;
    estadoSplit.stats.racha++;
    if (estadoSplit.stats.racha > estadoSplit.stats.maxRacha) estadoSplit.stats.maxRacha = estadoSplit.stats.racha;
  } else {
    estadoSplit.stats.racha = 0;
    const t = q.tema || q.tp || "General";
    estadoSplit.stats.temasErrados[t] = (estadoSplit.stats.temasErrados[t] || 0) + 1;
  }

  const esCorrecta = (obtenerIndiceCorrecto(q) === estadoSplit.selectedOption);"""
    
    good_block = """  if (!estadoSplit.stats) estadoSplit.stats = { totalRespuestas: 0, correctas: 0, racha: 0, maxRacha: 0, temasErrados: {} };
  estadoSplit.stats.totalRespuestas++;
  const esCorrecta = (obtenerIndiceCorrecto(q) === estadoSplit.selectedOption);
  if (esCorrecta) {
    estadoSplit.stats.correctas++;
    estadoSplit.stats.racha++;
    if (estadoSplit.stats.racha > estadoSplit.stats.maxRacha) estadoSplit.stats.maxRacha = estadoSplit.stats.racha;
  } else {
    estadoSplit.stats.racha = 0;
    const t = q.tema || q.tp || "General";
    estadoSplit.stats.temasErrados[t] = (estadoSplit.stats.temasErrados[t] || 0) + 1;
  }
"""

    if bad_block in content:
        content = content.replace(bad_block, good_block)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed syntax in {path}")
