const fs = require('fs');

let code = fs.readFileSync('app.js', 'utf8');

// Replace extra brace
code = code.replace("  }\n}\n}\n\nfunction loadChoice()", "  }\n}\n\nfunction loadChoice()");
code = code.replace("  }\n}\n}\nfunction loadChoice()", "  }\n}\nfunction loadChoice()");

fs.writeFileSync('app.js', code, 'utf8');
console.log("Brace syntax repair complete.");
