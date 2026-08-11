const fs = require('fs');

let code = fs.readFileSync('app.js', 'utf8');

// Replace duplicate braces in prepararEntrenamiento
const prepFixed = `function prepararEntrenamiento(tabId, materia, btnEl) {
  // 1. Switch Tab UI
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
  const sec = document.getElementById(\`tab-\${tabId}\`);
  if (sec) sec.classList.add('active');
  if (btnEl) btnEl.classList.add('active');

  // 2. Set Materia and Filter with Fallbacks
  if (materia) {
    currentMateria = materia;
    
    // Strict match
    filteredChoices = (bancoDados.choices || []).filter(q => q.materia === materia);
    
    // Fallback if no questions for specific catedra
    if (filteredChoices.length === 0) {
       if (materia.includes("Anatomía")) {
           filteredChoices = (bancoDados.choices || []).filter(q => q.materia && q.materia.includes("Anatomía"));
       } else {
           filteredChoices = bancoDados.choices || [];
       }
    }
    
    currentChoiceIndex = 0;
    
    if (tabId === 'choices' || tabId === 'oral') {
      loadChoice();
    }
    if (tabId === 'pinches') {
      loadPinche();
    }
  }
}`;

code = code.replace(/function prepararEntrenamiento\(tabId, materia, btnEl\) \{[\s\S]*?function loadChoice\(\)/, prepFixed + "\n\nfunction loadChoice()");

fs.writeFileSync('app.js', code, 'utf8');
console.log("App syntax repair complete.");
