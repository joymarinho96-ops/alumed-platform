/**
 * Script Auxiliar convert_pdf.js (Node.js / Auxiliar de Parsing)
 * Procesa PDFs de exámenes parciales pasados de UBA Medicina
 * y genera/actualiza el archivo data.js.
 */

const fs = require('fs');
const path = require('path');

// Mapeo de archivos PDF esperados a sus materias de UBA Medicina
const PDF_MAP = {
  "CUESTIONES BIOLOGIA ANUAL (7) (2).pdf": "Biología Celular",
  "Perguntas provas BIO_250703_194830 (3) (1).pdf": "Biología Celular",
  "HISTO 30 PARC SIN REPETIR 1F NOV.pdf": "Histología y Embriología",
  "HISTO TODOS.pdf": "Histología y Embriología",
  "SIMULACRO HyE PARCIAL 1 (2).pdf": "Histología y Embriología",
  "CUESTIONES HISTO 1º CUADRIMESTRE - @ALUMEDINSTITUTO_211006_194327[1].pdf": "Histología y Embriología",
  "HECK HYE FINAL (1).pdf": "Histología y Embriología",
  "PARCIALES REALES HISTOYEMBRIO 2025. BLOQUE II PDF.pdf": "Histología y Embriología",
  "UNION ANATO C.pdf": "Anatomía Cátedra C"
};

console.log("==================================================");
console.log("ALUMED | Convertidor y Parser de Parciales PDF");
console.log("==================================================");
console.log("Para usar en navegador: abre index.html y usa la pestaña 'Cargar PDF'.");
console.log("Para usar en CLI: asegúrate de instalar pdf-parse (npm install pdf-parse).");
