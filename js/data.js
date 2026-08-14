/* ═════════════════════════════════════════════════════════════════
   CONECTA FCM — EDICIÓN DOURADO
   Database & Dataset (Cartelera, Biblioteca, Exámenes, Cátedras, Mapa)
   ═════════════════════════════════════════════════════════════════ */

const CONECTA_DATA = {
  // Cartelera de Avisos en Vivo
  noticias: [
    {
      id: 1,
      titulo: "Publicación de Fechas de Recuperatorios de Parciales 2026",
      catedra: "Anatomía A & B",
      anio: "1er Año",
      tipo: "parcial",
      urgente: true,
      fecha: "01 de Agosto, 2026",
      resumen: "Se definieron los turnos para la mesa del 1er parcial práctico en Anfiteatro. Requisito contar con libreta universitaria al día y guardapolvo blanco.",
      detalleCompleto: "Atención estudiantes de 1er año: La Cátedra de Anatomía informa que las mesas para el primer parcial práctico se llevarán a cabo en el Anfiteatro de Anatomía los días 10 y 11 de agosto. Deberán presentarse con libreta física o DNI y atuendo adecuado."
    },
    {
      id: 2,
      titulo: "Guías Prácticas de Trabajos de Campo de Histología",
      catedra: "Histología y Embriología",
      anio: "1er Año",
      tipo: "catedra",
      urgente: false,
      fecha: "30 de Julio, 2026",
      resumen: "Nuevos preparados histológicos virtuales en formato ultra HD disponibles en la Biblioteca Conecta Dourada.",
      detalleCompleto: "Ya se encuentran subidas las láminas microscópicas correspondientes a Tejido Epitelial, Conectivo y Muscular. Se pueden estudiar usando el visor digital interactivo."
    },
    {
      id: 3,
      titulo: "Turnos para Exámenes Finales - Turno Agosto 2026",
      catedra: "Secretaría Académica",
      anio: "Todos los años",
      tipo: "urgente",
      urgente: true,
      fecha: "29 de Julio, 2026",
      resumen: "La inscripción por SIU Guaraní estará abierta hasta el domingo a las 23:59hs sin excepción.",
      detalleCompleto: "Recordamos verificar la correlatividad de las materias antes de formalizar la inscripción en el SIU. En caso de inconvenientes técnicos dirigirse a la Mesa de Entradas antes del viernes."
    },
    {
      id: 4,
      titulo: "Simposio de Fisiología Médica y Neurociencias",
      catedra: "Fisiología y Biofísica",
      anio: "2do Año",
      tipo: "catedra",
      urgente: false,
      fecha: "28 de Julio, 2026",
      resumen: "Charlas con referentes internacionales sobre neurofisiología aplicada y electrocardiografía básica.",
      detalleCompleto: "Organizado en el Aula Magna de la Facultad. Otorga certificado oficial de participación válido para créditos académicos."
    },
    {
      id: 5,
      titulo: "Aviso de Cátedra: Farmacología Clínica y Posología",
      catedra: "Farmacología I",
      anio: "3er Año",
      tipo: "parcial",
      urgente: false,
      fecha: "25 de Julio, 2026",
      resumen: "Subidas las grillas de evaluación correspondientes al módulo de Antiinfecciosos y Farmacocinética.",
      detalleCompleto: "Disponibles los casos clínicos prácticos para discutir en las comisiones de la próxima semana."
    }
  ],

  // Biblioteca Digital Dourada
  biblioteca: [
    {
      id: "lib-1",
      titulo: "Anatomía Humana — Rouvière & Delmas",
      categoria: "Anatomía",
      anio: "1er Año",
      paginas: 2450,
      formato: "PDF HD",
      descripcion: "Obra de referencia fundamental para el estudio descriptivo, topográfico y funcional del cuerpo humano.",
      downloadUrl: "#",
      resumenIa: "Texto clásico estructurado en tomos: Cabeza y Cuello, Tronco, Miembros. Ideal para parciales prácticos en el anfiteatro."
    },
    {
      id: "lib-2",
      titulo: "Histología: Texto y Atlas — Ross & Pawlina",
      categoria: "Histología",
      anio: "1er Año",
      paginas: 1040,
      formato: "PDF HD",
      descripcion: "Correlación histopatológica con imágenes microscópicas detalladas de alta resolución.",
      downloadUrl: "#",
      resumenIa: "Contiene fotomicrografías explicadas paso a paso con esquemas de fisiología celular integrada."
    },
    {
      id: "lib-3",
      titulo: "Fisiología Médica — Guyton & Hall",
      categoria: "Fisiología",
      anio: "2do Año",
      paginas: 1150,
      formato: "PDF HD",
      descripcion: "El estándar internacional para comprender los mecanismos fisiológicos del organismo humano.",
      downloadUrl: "#",
      resumenIa: "Cubre desde fisiología renal, cardiovascular, respiratoria y neurofisiología con diagramas biomecánicos."
    },
    {
      id: "lib-4",
      titulo: "Bioquímica de Harper",
      categoria: "Bioquímica",
      anio: "2do Año",
      paginas: 820,
      formato: "PDF HD",
      descripcion: "Guía completa de metabolismo, enzimología y genética molecular aplicada a la práctica médica.",
      downloadUrl: "#",
      resumenIa: "Enfoque clínico sobre vías metabólicas, ciclo de Krebs, glucólisis y patologías asociadas a déficits enzimáticos."
    },
    {
      id: "lib-5",
      titulo: "Robbins y Cotran: Patología Estructural y Funcional",
      categoria: "Patología",
      anio: "3er Año",
      paginas: 1400,
      formato: "PDF HD",
      descripcion: "Compendio de patología general y especial con bases fisiopatológicas clínicas.",
      downloadUrl: "#",
      resumenIa: "Análisis de neoplasias, inflamación, patología cardiovascular, renal y respiratoria."
    },
    {
      id: "lib-6",
      titulo: "Goodman & Gilman: Las Bases Farmacológicas",
      categoria: "Farmacología",
      anio: "3er Año",
      paginas: 1420,
      formato: "PDF HD",
      descripcion: "Manual definitivo de farmacodinámica, farmacocinética y terapéutica médica.",
      downloadUrl: "#",
      resumenIa: "Guía esencial de receptores, mecanismo de acción de antibióticos, analgésicos y psicofármacos."
    }
  ],

  // Cronograma de Exámenes FCM
  examenes: [
    {
      materia: "Anatomía A",
      tipo: "1er Parcial Práctico",
      fecha: "2026-08-10",
      hora: "08:00 hs",
      aula: "Anfiteatro Central",
      estado: "Próximo"
    },
    {
      materia: "Histología y Embriología",
      tipo: "2do Parcial Teórico",
      fecha: "2026-08-18",
      hora: "10:30 hs",
      aula: "Aula Magna 1",
      estado: "Próximo"
    },
    {
      materia: "Fisiología Médica",
      tipo: "Examen Final Turno Agosto",
      fecha: "2026-08-25",
      hora: "14:00 hs",
      aula: "Aula 5 - Edificio Central",
      estado: "Confirmado"
    },
    {
      materia: "Bioquímica Médica",
      tipo: "Recuperatorio 1er Módulo",
      fecha: "2026-09-02",
      hora: "09:00 hs",
      aula: "Laboratorios Subsuelo",
      estado: "Programado"
    }
  ],

  // Calculadora de materias FCM
  materiasCalculadora: [
    { id: 1, nombre: "Anatomía Humana", horas: 240, anio: "1er Año" },
    { id: 2, nombre: "Histología y Embriología", horas: 180, anio: "1er Año" },
    { id: 3, nombre: "Biología Celular", horas: 120, anio: "1er Año" },
    { id: 4, nombre: "Fisiología y Biofísica", horas: 260, anio: "2do Año" },
    { id: 5, nombre: "Bioquímica y Biología Molecular", horas: 200, anio: "2do Año" },
    { id: 6, nombre: "Patología General", horas: 220, anio: "3er Año" },
    { id: 7, nombre: "Farmacología Aplicada", horas: 190, anio: "3er Año" },
    { id: 8, nombre: "Semiología y Medicina Interna", horas: 350, anio: "4to Año" }
  ],

  // Ubicaciones de la Facultad (Mapa Interactivo Dourado)
  ubicaciones: [
    {
      id: "map-anfiteatro",
      nombre: "Anfiteatro de Anatomía",
      categoria: "Aulas Prácticas",
      icono: "fa-skull-crossbones",
      piso: "Planta Baja - Pabellón Central",
      descripcion: "Área destinada a disección y estudio de piezas anatómicas de primera mano."
    },
    {
      id: "map-biblioteca",
      nombre: "Biblioteca Central & Sala Parlante",
      categoria: "Estudio",
      icono: "fa-book-open-reader",
      piso: "1er Piso - Sector Oeste",
      descripcion: "Espacio de consulta de libros físicos, acceso a computadoras y red WiFi de alta velocidad."
    },
    {
      id: "map-laboratorios",
      nombre: "Laboratorios de Histología",
      categoria: "Laboratorios",
      icono: "fa-microscope",
      piso: "2do Piso - Edificio Anexo",
      descripcion: "Equipado con microscopios ópticos y cámaras de proyección para observaciones de láminas."
    },
    {
      id: "map-aula-magna",
      nombre: "Aula Magna Dr. Bernardo Houssay",
      categoria: "Conferencias",
      icono: "fa-landmark",
      piso: "Planta Baja - Hall Central",
      descripcion: "Capacidad para 500 personas. Auditorio principal para simposios, actos y clases magistrales."
    },
    {
      id: "map-secretaria",
      nombre: "Secretaría Académica & SIU Guaraní",
      categoria: "Administración",
      icono: "fa-clipboard-check",
      piso: "Planta Baja - Sector Administrativo",
      descripcion: "Trámites de equivalencias, analíticos parciales, libretas universitarias y certificaciones."
    },
    {
      id: "map-hospital",
      nombre: "Pabellón de Prácticas Clínicas",
      categoria: "Hospital",
      icono: "fa-hospital-user",
      piso: "Conexión Hospital de Clínicas",
      descripcion: "Área donde se realizan los rotatorios clínicos y prácticas con simuladores hápticos."
    }
  ]
};
