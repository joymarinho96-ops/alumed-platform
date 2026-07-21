from __future__ import annotations

from collections import Counter
import unicodedata
from typing import Iterable


CAREER_META = {
    "id": "medicina",
    "label": "Medicina",
    "headline": "Centro de conocimiento premium para estudiantes de Medicina.",
    "copy": (
        "La Biblioteca ALUMED ahora se organiza como estudia un alumno de Medicina: "
        "carrera, a\u00f1o, materia y recursos."
    ),
}


YEAR_DEFINITIONS = [
    {
        "id": "year-1",
        "label": "1º Año",
        "headline": "Bases biológicas, estructura corporal y materias troncales.",
        "copy": (
            "Study rooms para Histología, Anatomía, Embriología, Biología y "
            "Factores de Transcripción."
        ),
        "subjects": ["histo", "anato", "embrio", "bio", "transcripcion"],
        "status": "current",
        "isDefault": True,
    },
    {
        "id": "year-2",
        "label": "2º Año",
        "headline": "Fisiología, Bioquímica y materias integradoras.",
        "copy": (
            "Espacio de estudio para Fisiología, Química Biológica / Bioquímica."
        ),
        "subjects": ["fisio", "quimica"],
        "status": "current",
    },
    {
        "id": "year-3",
        "label": "3º Año",
        "headline": "Fisiopatología, Farmacología y Microbiología.",
        "copy": (
            "Study rooms para Microbiología, Patología y Farmacología."
        ),
        "subjects": ["micro", "pato", "farma"],
        "status": "current",
    },
    {
        "id": "year-4-5",
        "label": "4º y 5º Año",
        "headline": "Área Clínica, Pediatría, Cirugía y especialidades.",
        "copy": (
            "Apuntes para Semiología, Pediatría, Ginecología/Obstetricia, Cirugía y Clínica Médica."
        ),
        "subjects": ["semiologia", "pediatria", "ginecologia", "cirugia", "clinica", "otras"],
        "status": "current",
    },
]


SUBJECT_META = {
    "histo": {
        "label": "Histología",
        "slug": "histologia",
        "yearId": "year-1",
        "icon": "fa-microscope",
        "cover": "img/library/histologia.svg",
        "description": "Tejidos, preparados, láminas y fundamentos morfofuncionales.",
        "focus": "Microscopio, tejidos y observación guiada.",
        "accent": "cyan",
        "aliases": ["histo", "histologia", "tejido", "lamina", "microscopio"],
    },
    "anato": {
        "label": "Anatomía",
        "slug": "anatomia",
        "yearId": "year-1",
        "icon": "fa-bone",
        "cover": "img/library/anatomia.svg",
        "description": "Estructuras, relaciones anatómicas, atlas y organización corporal.",
        "focus": "Atlas, planos y correlación tridimensional.",
        "accent": "violet",
        "aliases": ["anato", "anatomia", "hueso", "sistema oseo", "atlas"],
    },
    "embrio": {
        "label": "Embriología",
        "slug": "embriologia",
        "yearId": "year-1",
        "icon": "fa-baby",
        "cover": "img/library/embriologia.svg",
        "description": "Desarrollo temprano, etapas embrionarias y líneas de diferenciación.",
        "focus": "Cronología del desarrollo y visualización por etapas.",
        "accent": "amber",
        "aliases": ["embrio", "embriologia", "desarrollo", "embri"],
    },
    "bio": {
        "label": "Biología",
        "slug": "biologia",
        "yearId": "year-1",
        "icon": "fa-dna",
        "cover": "img/library/biologia.svg",
        "description": "Biología celular y molecular para comprender la base de la Medicina.",
        "focus": "Célula, expresión genética y procesos moleculares.",
        "accent": "emerald",
        "aliases": ["bio", "biologia", "biologia celular", "molecular", "celular"],
    },
    "transcripcion": {
        "label": "Factores de Transcripción",
        "slug": "factores-de-transcripcion",
        "yearId": "year-1",
        "icon": "fa-brain",
        "cover": "img/library/biologia.svg",
        "description": "Ruta especializada para regulación genética, expresión y señalización.",
        "focus": "Regulación molecular y mapas de estudio avanzados.",
        "accent": "rose",
        "aliases": ["transcripcion", "factores de transcripcion", "genetica", "expresion"],
    },
    "quimica": {
        "label": "Química Biológica",
        "slug": "quimica-biologica",
        "yearId": "year-2",
        "icon": "fa-flask-vial",
        "cover": "img/library/bioquimica.svg",
        "description": "Metabolismo celular, enzimas, bioenergética y vías bioquímicas.",
        "focus": "Metabolismo, reacciones químicas y clínica.",
        "accent": "amber",
        "aliases": ["quimica", "quimica biologica", "bioquimica", "metabolismo", "enzima"],
    },
    "fisio": {
        "label": "Fisiología",
        "slug": "fisiologia",
        "yearId": "year-2",
        "icon": "fa-heart-pulse",
        "cover": "img/library/fisiologia.svg",
        "description": "Funcionamiento de los sistemas corporales y regulación homeostática.",
        "focus": "Integración funcional y mecanismos de regulación.",
        "accent": "cyan",
        "aliases": ["fisio", "fisiologia", "biofisica", "homeostasis", "regulacion"],
    },
    "micro": {
        "label": "Microbiología",
        "slug": "microbiologia",
        "yearId": "year-3",
        "icon": "fa-virus",
        "cover": "img/library/histologia.svg",
        "description": "Estudio de bacterias, virus, hongos y parásitos de interés clínico.",
        "focus": "Patógenos, virología, bacteriología y diagnóstico.",
        "accent": "emerald",
        "aliases": ["micro", "microbiologia", "parasitologia", "virus", "bacteria"],
    },
    "pato": {
        "label": "Patología",
        "slug": "patologia",
        "yearId": "year-3",
        "icon": "fa-notes-medical",
        "cover": "img/library/anatomia.svg",
        "description": "Bases morfológicas y fisiopatológicas de las enfermedades.",
        "focus": "Lesión celular, inflamación, neoplasias y preparados anatomopatológicos.",
        "accent": "rose",
        "aliases": ["pato", "patologia", "fisiopatologia", "enfermedad"],
    },
    "farma": {
        "label": "Farmacología",
        "slug": "farmacologia",
        "yearId": "year-3",
        "icon": "fa-capsules",
        "cover": "img/library/bioquimica.svg",
        "description": "Mecanismos de acción, farmacocinética, farmacodinamia y terapéutica.",
        "focus": "Fármacos, recetas, efectos adversos e interacciones.",
        "accent": "violet",
        "aliases": ["farma", "farmacologia", "medicamento", "terapeutica", "dosis"],
    },
    "semiologia": {
        "label": "Semiología",
        "slug": "semiologia",
        "yearId": "year-4-5",
        "icon": "fa-stethoscope",
        "cover": "img/library/fisiologia.svg",
        "description": "Examen físico, historia clínica, signos y síntomas de patologías.",
        "focus": "Exploración física, interrogatorio y síndromes clínicos.",
        "accent": "violet",
        "aliases": ["semiologia", "semio", "exploracion", "sindrome", "anamnesis"],
    },
    "pediatria": {
        "label": "Pediatría",
        "slug": "pediatria",
        "yearId": "year-4-5",
        "icon": "fa-baby-carriage",
        "cover": "img/library/embriologia.svg",
        "description": "Cuidado integral, desarrollo, nutrición y patologías de la infancia.",
        "focus": "Desarrollo infantil, vacunas y patologías pediátricas.",
        "accent": "amber",
        "aliases": ["pediatria", "pediatra", "infantil", "ninos"],
    },
    "ginecologia": {
        "label": "Ginecología y Obstetricia",
        "slug": "ginecologia-y-obstetricia",
        "yearId": "year-4-5",
        "icon": "fa-venus",
        "cover": "img/library/embriologia.svg",
        "description": "Salud de la mujer, embarazo, parto, puerperio y patología obstétrica.",
        "focus": "Obstetricia patológica, salud perinatal y ginecología.",
        "accent": "rose",
        "aliases": ["ginecologia", "obstetricia", "obste", "perinatal", "embarazo"],
    },
    "cirugia": {
        "label": "Cirugía",
        "slug": "cirugia",
        "yearId": "year-4-5",
        "icon": "fa-heart",
        "cover": "img/library/anatomia.svg",
        "description": "Patologías quirúrgicas, técnicas operatorias, pre y postoperatorio.",
        "focus": "Técnica quirúrgica, abdomen agudo y trauma.",
        "accent": "cyan",
        "aliases": ["cirugia", "cirujano", "quirurgica", "operatoria"],
    },
    "clinica": {
        "label": "Clínica Médica",
        "slug": "clinica-medica",
        "yearId": "year-4-5",
        "icon": "fa-user-md",
        "cover": "img/library/fisiologia.svg",
        "description": "Medicina interna, diagnóstico diferencial y tratamiento no quirúrgico.",
        "focus": "Diagnóstico, medicina interna y manejo terapéutico.",
        "accent": "emerald",
        "aliases": ["clinica", "medicina interna", "clinica medica", "tratamiento"],
    },
    "otras": {
        "label": "Otras Asignaturas",
        "slug": "otras-asignaturas",
        "yearId": "year-4-5",
        "icon": "fa-folder-open",
        "cover": "img/library/biologia.svg",
        "description": "Recursos académicos complementarios y materias transversales.",
        "focus": "Apuntes generales y herramientas de apoyo.",
        "accent": "slate",
        "aliases": ["otras", "general", "sociales", "ingles", "investigacion", "etica"],
    },
}


RESOURCE_GROUP_DEFINITIONS = [
    {
        "id": "apuntes_alumed",
        "label": "Apuntes ALUMED",
        "icon": "fa-star",
        "description": "Material oficial producido por ALUMED y priorizado por encima de cualquier fuente externa.",
        "emptyTitle": "Apunte oficial en preparacion",
        "emptyCopy": "La estructura ya esta lista para publicar los apuntes oficiales de esta materia.",
        "emptyBadge": "Oficial ALUMED",
        "isFuture": False,
    },
    {
        "id": "libros",
        "label": "Libros",
        "icon": "fa-book-medical",
        "description": "Bibliografia base, atlas y libros de referencia integrados a la experiencia ALUMED.",
        "emptyTitle": "Bibliografia en curacion",
        "emptyCopy": "Los libros de esta materia quedaran centralizados aqui con enlaces directos validados.",
        "emptyBadge": "Bibliografia",
        "isFuture": False,
    },
    {
        "id": "metodo_profe_joy",
        "label": "Metodo Profe Joy",
        "icon": "fa-brain",
        "description": "Guias, protocolos, mapas mentales y planificaciones del Metodo Profe Joy.",
        "emptyTitle": "Metodo en preparacion",
        "emptyCopy": "Este bloque queda reservado para hojas de ruta, repasos y estrategias por materia.",
        "emptyBadge": "Metodo Joy",
        "isFuture": False,
    },
    {
        "id": "simulacros_examenes",
        "label": "Simulacros y Examenes",
        "icon": "fa-file-signature",
        "description": "Parciales, finales, modelos de examen y bancos de practica listos para escalar.",
        "emptyTitle": "Practica en construccion",
        "emptyCopy": "Aqui se centralizaran simulacros, parciales y finales con acceso directo.",
        "emptyBadge": "Evaluacion",
        "isFuture": False,
    },
    {
        "id": "recursos_complementarios",
        "label": "Recursos complementarios",
        "icon": "fa-layer-group",
        "description": "Atlas, guias, resuenes visuales y materiales auxiliares para complementar el estudio.",
        "emptyTitle": "Espacio reservado para recursos auxiliares",
        "emptyCopy": "Esta materia ya cuenta con un bloque listo para sumar guias y materiales de apoyo.",
        "emptyBadge": "Complementario",
        "isFuture": False,
    },
    {
        "id": "microscopio_virtual",
        "label": "Microscopio Virtual",
        "icon": "fa-microscope",
        "description": "Arquitectura preparada para preparados digitales, observacion guiada y rutas visuales.",
        "emptyTitle": "Microscopio Virtual preparado",
        "emptyCopy": "La experiencia queda lista para integrar preparados, capas y observacion asistida.",
        "emptyBadge": "Modulo futuro",
        "isFuture": True,
    },
    {
        "id": "flashcards",
        "label": "Flashcards",
        "icon": "fa-clone",
        "description": "Bloque listo para mazos inteligentes, repaso espaciado y memoria activa.",
        "emptyTitle": "Flashcards listas para integrarse",
        "emptyCopy": "La estructura ya contempla mazos por materia y rutas de repaso inteligente.",
        "emptyBadge": "Modulo futuro",
        "isFuture": True,
    },
    {
        "id": "podcasts",
        "label": "Podcasts",
        "icon": "fa-headphones",
        "description": "Espacio preparado para audioresumenes, repasos guiados y explicaciones en formato podcast.",
        "emptyTitle": "Podcasts en roadmap",
        "emptyCopy": "Cada materia ya tiene un bloque listo para episodios y repasos auditivos.",
        "emptyBadge": "Modulo futuro",
        "isFuture": True,
    },
    {
        "id": "ia_profe_joy",
        "label": "IA Profe Joy",
        "icon": "fa-robot",
        "description": "Base preparada para recomendaciones, tutorias inteligentes y asistencia contextual.",
        "emptyTitle": "IA Profe Joy preparada",
        "emptyCopy": "La sala de estudio queda lista para sumar ayuda personalizada y recomendaciones.",
        "emptyBadge": "Modulo futuro",
        "isFuture": True,
    },
]


STATUS_META = {
    "available": {
        "label": "Disponible",
        "tone": "available",
        "note": "Link validado y listo para abrir en una nueva pestana.",
    },
    "pending_validation": {
        "label": "Pendiente de validacion",
        "tone": "pending",
        "note": "Existe referencia historica, pero el destino final aun no fue validado.",
    },
    "pending_inventory": {
        "label": "Pendiente de inventario",
        "tone": "pending",
        "note": "Entrada reservada para migracion por etapas.",
    },
    "missing_link": {
        "label": "Sin enlace disponible",
        "tone": "muted",
        "note": "Aun no existe un enlace publico directo para esta entrada.",
    },
}


WIX_FILE_SHARE_INVENTORY = [
    # ═══════════════════════════════════════════
    #  ANATOMÍA  — 1º AÑO
    # ═══════════════════════════════════════════
    {
        "id": "anato-gray-1ed",
        "folder": "Anatomía", "subfolder": "Atlas y Libros",
        "title": "Gray — Anatomía para Estudiantes (1° Edición)",
        "description": "Obra de referencia mundial en anatomía clínica con enfoque integrador.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "anato", "groupId": "libros",
        "cover": "img/library/anatomia.svg",
    },
    {
        "id": "anato-latarjet-t1",
        "folder": "Anatomía", "subfolder": "Atlas y Libros",
        "title": "Latarjet — Anatomía Humana (4° Ed., Tomo 1)",
        "description": "Tomo 1 del clásico Latarjet. Base obligatoria para Anatomía en la UNLP.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "anato", "groupId": "libros",
        "cover": "img/library/anatomia.svg",
    },
    {
        "id": "anato-latarjet-t2",
        "folder": "Anatomía", "subfolder": "Atlas y Libros",
        "title": "Latarjet — Anatomía Humana (4° Ed., Tomo 2)",
        "description": "Tomo 2 del clásico Latarjet. Cubre miembro inferior, abdomen y pelvis.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "anato", "groupId": "libros",
        "cover": "img/library/anatomia.svg",
    },
    {
        "id": "anato-netter",
        "folder": "Anatomía", "subfolder": "Atlas y Libros",
        "title": "Netter — Atlas de Anatomía Humana (Ilustrado)",
        "description": "El atlas ilustrado más reconocido del mundo. Láminas a color detalladas.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "anato", "groupId": "libros",
        "cover": "img/library/anatomia.svg",
    },
    {
        "id": "anato-pro",
        "folder": "Anatomía", "subfolder": "Atlas y Libros",
        "title": "Pro — Anatomía Clínica",
        "description": "Anatomía clínica con orientación quirúrgica. Muy usado en cátedras UNLP.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "anato", "groupId": "libros",
        "cover": "img/library/anatomia.svg",
    },
    {
        "id": "anato-guzman-atlas",
        "folder": "Anatomía", "subfolder": "Atlas y Libros",
        "title": "Raúl Guzmán — Atlas Anatómico (1° Ed.)",
        "description": "Atlas argentino de anatomía. Terminología anatómica en español local.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "anato", "groupId": "libros",
        "cover": "img/library/anatomia.svg",
    },
    {
        "id": "anato-rouviere-11-t1",
        "folder": "Anatomía", "subfolder": "Rouviere",
        "title": "Rouviere — Anatomía Humana (11° Ed., Tomo 1)",
        "description": "Tomo 1: Cabeza y cuello. Referencia clásica en anatomía descriptiva.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "anato", "groupId": "libros",
        "cover": "img/library/anatomia.svg",
    },
    {
        "id": "anato-rouviere-11-t2",
        "folder": "Anatomía", "subfolder": "Rouviere",
        "title": "Rouviere — Anatomía Humana (11° Ed., Tomo 2)",
        "description": "Tomo 2: Tronco. Columna, tórax, abdomen y pelvis.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "anato", "groupId": "libros",
        "cover": "img/library/anatomia.svg",
    },
    {
        "id": "anato-rouviere-11-t3",
        "folder": "Anatomía", "subfolder": "Rouviere",
        "title": "Rouviere — Anatomía Humana (11° Ed., Tomo 3)",
        "description": "Tomo 3: Miembro superior. Hombro, brazo, codo, antebrazo y mano.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "anato", "groupId": "libros",
        "cover": "img/library/anatomia.svg",
    },
    {
        "id": "anato-rouviere-11-t4",
        "folder": "Anatomía", "subfolder": "Rouviere",
        "title": "Rouviere — Anatomía Humana (11° Ed., Tomo 4)",
        "description": "Tomo 4: Miembro inferior. Cadera, muslo, rodilla, pierna y pie.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "anato", "groupId": "libros",
        "cover": "img/library/anatomia.svg",
    },
    {
        "id": "anato-rouviere-9-t1",
        "folder": "Anatomía", "subfolder": "Rouviere",
        "title": "Rouviere — Anatomía Humana (9° Ed., Tomo 1)",
        "description": "Edición clásica 9°. Cabeza y cuello. Muy citada en exámenes orales.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "anato", "groupId": "libros",
        "cover": "img/library/anatomia.svg",
    },
    {
        "id": "anato-rouviere-9-t2",
        "folder": "Anatomía", "subfolder": "Rouviere",
        "title": "Rouviere — Anatomía Humana (9° Ed., Tomo 2)",
        "description": "Edición clásica 9°. Tronco, abdomen y pelvis.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "anato", "groupId": "libros",
        "cover": "img/library/anatomia.svg",
    },
    {
        "id": "anato-rouviere-9-t3",
        "folder": "Anatomía", "subfolder": "Rouviere",
        "title": "Rouviere — Anatomía Humana (9° Ed., Tomo 3)",
        "description": "Edición clásica 9°. Miembros superior e inferior.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "anato", "groupId": "libros",
        "cover": "img/library/anatomia.svg",
    },
    {
        "id": "anato-snell-neuro",
        "folder": "Anatomía", "subfolder": "Neuroanatomía",
        "title": "Snell — Neuroanatomía Clínica",
        "description": "El referente mundial en neuroanatomía. Sistema nervioso central y periférico.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "anato", "groupId": "libros",
        "cover": "img/library/anatomia.svg",
    },
    {
        "id": "anato-testut-9-t1",
        "folder": "Anatomía", "subfolder": "Testut",
        "title": "Testut — Anatomía Humana (9° Ed., Tomo 1)",
        "description": "Tomo 1 de la obra completa de Testut. Osteología y artrología.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "anato", "groupId": "libros",
        "cover": "img/library/anatomia.svg",
    },
    {
        "id": "anato-testut-9-t2",
        "folder": "Anatomía", "subfolder": "Testut",
        "title": "Testut — Anatomía Humana (9° Ed., Tomo 2)",
        "description": "Tomo 2: Miología y angiología.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "anato", "groupId": "libros",
        "cover": "img/library/anatomia.svg",
    },
    {
        "id": "anato-testut-9-t3",
        "folder": "Anatomía", "subfolder": "Testut",
        "title": "Testut — Anatomía Humana (9° Ed., Tomo 3)",
        "description": "Tomo 3: Neurología y órganos de los sentidos.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "anato", "groupId": "libros",
        "cover": "img/library/anatomia.svg",
    },
    {
        "id": "anato-testut-9-t4",
        "folder": "Anatomía", "subfolder": "Testut",
        "title": "Testut — Anatomía Humana (9° Ed., Tomo 4)",
        "description": "Tomo 4: Esplacnología. Aparatos digestivo, respiratorio y urogenital.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "anato", "groupId": "libros",
        "cover": "img/library/anatomia.svg",
    },
    {
        "id": "anato-testut-compendio",
        "folder": "Anatomía", "subfolder": "Testut",
        "title": "Testut — Compendio de Anatomía Descriptiva",
        "description": "Versión resumida del Testut completo. Ideal para repaso rápido antes del parcial.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "anato", "groupId": "libros",
        "cover": "img/library/anatomia.svg",
    },
    {
        "id": "anato-yokochi-6ed",
        "folder": "Anatomía", "subfolder": "Atlas y Libros",
        "title": "Yokochi — Atlas Fotográfico de Anatomía (6° Ed.)",
        "description": "Atlas con fotografías reales de disección. Excelente para preparar láminas.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "anato", "groupId": "libros",
        "cover": "img/library/anatomia.svg",
    },
    # ═══════════════════════════════════════════
    #  BIOLOGÍA  — 1º AÑO
    # ═══════════════════════════════════════════
    {
        "id": "bio-alberts-celular-3ed",
        "folder": "Biología", "subfolder": "Biología Celular",
        "title": "Alberts — Biología Celular (3° Edición)",
        "description": "Introducción a la biología celular. Base molecular de la vida.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "bio", "groupId": "libros",
        "cover": "img/library/biologia.svg",
    },
    {
        "id": "bio-alberts-molecular-5ed",
        "folder": "Biología", "subfolder": "Biología Molecular",
        "title": "Alberts — Biología Molecular de la Célula (5° Edición)",
        "description": "La obra completa de biología molecular. Fundamental para Biología en UNLP.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "bio", "groupId": "libros",
        "cover": "img/library/biologia.svg",
    },
    {
        "id": "bio-blanco-9ed",
        "folder": "Biología", "subfolder": "Biología Celular",
        "title": "Blanco — Química Biológica (9° Edición)",
        "description": "Bioquímica estructural y funcional. Muy usado en Biología 1° año.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "bio", "groupId": "libros",
        "cover": "img/library/biologia.svg",
    },
    {
        "id": "bio-curtis-7ed",
        "folder": "Biología", "subfolder": "Biología General",
        "title": "Curtis — Biología (7° Edición)",
        "description": "El clásico Curtis. Biología general, evolución, ecología y genética.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "bio", "groupId": "libros",
        "cover": "img/library/biologia.svg",
    },
    {
        "id": "bio-derobertis-4ed",
        "folder": "Biología", "subfolder": "Biología Celular",
        "title": "De Robertis — Biología Celular y Molecular (4° Edición)",
        "description": "Clásico de biología celular y molecular en español. Referencia para FCM UNLP.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "bio", "groupId": "libros",
        "cover": "img/library/biologia.svg",
    },
    # ═══════════════════════════════════════════
    #  HISTOLOGÍA  — 1º AÑO
    # ═══════════════════════════════════════════
    {
        "id": "histo-difiore-atlas-1",
        "folder": "Histología", "subfolder": "Atlas",
        "title": "Di Fiore — Atlas de Histología Normal (A)",
        "description": "Atlas de referencia para histología normal. Láminas clasificadas por tejido.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "histo", "groupId": "libros",
        "cover": "img/library/histologia.svg",
    },
    {
        "id": "histo-difiore-atlas-2",
        "folder": "Histología", "subfolder": "Atlas",
        "title": "Di Fiore — Atlas de Histología Normal (B)",
        "description": "Segunda versión del Di Fiore. Complementa la primera con preparados adicionales.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "histo", "groupId": "libros",
        "cover": "img/library/histologia.svg",
    },
    {
        "id": "histo-geneser-3ed",
        "folder": "Histología", "subfolder": "Libros de Texto",
        "title": "Geneser — Histología (3° Edición)",
        "description": "Texto completo de histología. Muy usado en cátedra de Histología FCM UNLP.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "histo", "groupId": "libros",
        "cover": "img/library/histologia.svg",
    },
    {
        "id": "histo-geneser-4ed",
        "folder": "Histología", "subfolder": "Libros de Texto",
        "title": "Geneser — Histología (4° Edición)",
        "description": "Edición actualizada del Geneser. Incorpora histología funcional y molecular.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "histo", "groupId": "libros",
        "cover": "img/library/histologia.svg",
    },
    {
        "id": "histo-ross-7ed",
        "folder": "Histología", "subfolder": "Libros de Texto",
        "title": "Ross — Histología: Texto y Atlas (7° Edición)",
        "description": "Histología con correlación clínica. Texto + atlas en un solo volumen.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "histo", "groupId": "libros",
        "cover": "img/library/histologia.svg",
    },
    # ═══════════════════════════════════════════
    #  EMBRIOLOGÍA  — 1º AÑO
    # ═══════════════════════════════════════════
    {
        "id": "embrio-gomezdumm-1ed",
        "folder": "Embriología", "subfolder": "Libros de Texto",
        "title": "Gómez Dumm — Embriología Humana (1° Edición)",
        "description": "Embriología en español adaptada a la FCM UNLP. Muy citada en orales.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "embrio", "groupId": "libros",
        "cover": "img/library/embriologia.svg",
    },
    {
        "id": "embrio-josehib-7ed",
        "folder": "Embriología", "subfolder": "Libros de Texto",
        "title": "José Hib — Embriología Médica (7° Edición)",
        "description": "Embriología argentina. Referencia obligatoria en la FCM UNLP.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "embrio", "groupId": "libros",
        "cover": "img/library/embriologia.svg",
    },
    {
        "id": "embrio-josehib-8ed",
        "folder": "Embriología", "subfolder": "Libros de Texto",
        "title": "José Hib — Embriología Médica (8° Edición)",
        "description": "Edición actualizada del José Hib. Incorpora genética del desarrollo.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "embrio", "groupId": "libros",
        "cover": "img/library/embriologia.svg",
    },
    {
        "id": "embrio-langman-13ed",
        "folder": "Embriología", "subfolder": "Libros de Texto",
        "title": "Langman — Embriología Médica (13° Edición)",
        "description": "El clásico Langman. Embriología clínica orientada a la práctica médica.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "embrio", "groupId": "libros",
        "cover": "img/library/embriologia.svg",
    },
    # ═══════════════════════════════════════════
    #  CIENCIAS SOCIALES Y MEDICINA  — 1º AÑO
    # ═══════════════════════════════════════════
    {
        "id": "csm-antropologia-medica",
        "folder": "Ciencias Sociales y Medicina", "subfolder": "Bibliografía Base",
        "title": "Antropología Médica",
        "description": "Perspectiva antropológica de la salud y la enfermedad. Materia 1° año FCM UNLP.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "otras", "groupId": "libros",
        "cover": "img/library/biologia.svg",
    },
    {
        "id": "csm-antropologia",
        "folder": "Ciencias Sociales y Medicina", "subfolder": "Bibliografía Base",
        "title": "Antropología",
        "description": "Fundamentos de antropología social y cultural para estudiantes de medicina.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "otras", "groupId": "libros",
        "cover": "img/library/biologia.svg",
    },
    {
        "id": "csm-epistemologia",
        "folder": "Ciencias Sociales y Medicina", "subfolder": "Bibliografía Base",
        "title": "Epistemología",
        "description": "Filosofía y epistemología de las ciencias de la salud. FCM UNLP.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "otras", "groupId": "libros",
        "cover": "img/library/biologia.svg",
    },
    {
        "id": "csm-perspectivas-humanisticas",
        "folder": "Ciencias Sociales y Medicina", "subfolder": "Bibliografía Base",
        "title": "Perspectivas Humanísticas",
        "description": "Humanidades médicas, ética y ciencias sociales integradas al currículo de medicina.",
        "fileType": "PDF", "sourceUrl": "",
        "views": None, "updatedAt": "Sin fecha",
        "status": "pending_validation",
        "yearId": "year-1", "subjectKey": "otras", "groupId": "libros",
        "cover": "img/library/biologia.svg",
    },
]
GROUP_LOOKUP = {group["id"]: group for group in RESOURCE_GROUP_DEFINITIONS}
STATUS_ORDER = {
    "available": 0,
    "pending_validation": 1,
    "pending_inventory": 2,
    "missing_link": 3,
}


def _normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    return "".join(char for char in normalized if not unicodedata.combining(char)).lower()


def _dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def _status_note(status: str) -> dict:
    return STATUS_META.get(status, STATUS_META["missing_link"])


def _is_search_url(url: str) -> bool:
    lowered = _normalize_text(url or "")
    if not lowered:
        return False

    search_tokens = (
        "/search",
        "search?",
        "search/",
        "query=",
        "google.com/search",
        "bing.com/search",
        "docsity.com/es/resultados",
        "resultados-busqueda",
        "studocu.com/search",
    )
    return any(token in lowered for token in search_tokens)


def _pick_primary_url(item: dict) -> str:
    for field in ("alumedUrl", "driveUrl", "originalUrl", "sourceUrl"):
        value = item.get(field) or ""
        if value and not _is_search_url(value):
            return value
    return ""


def _safe_media_url(file_field) -> str:
    if not file_field:
        return ""
    try:
        return file_field.url
    except Exception:
        return ""


def _infer_subject_key_from_text(value: str) -> str | None:
    haystack = _normalize_text(value)
    for subject_key, meta in SUBJECT_META.items():
        aliases = [_normalize_text(alias) for alias in meta.get("aliases", [])]
        if any(alias and alias in haystack for alias in aliases):
            return subject_key
    return None


def _book_is_official(book) -> bool:
    platform = _normalize_text(getattr(book, "platform", "") or "")
    author = _normalize_text(getattr(book, "author", "") or "")
    category = _normalize_text(getattr(book, "category", "") or "")
    tags = _normalize_text(getattr(book, "tags", "") or "")

    if _safe_media_url(getattr(book, "pdf_file", None)):
        return True
    if "alumed" in platform or "alumed" in author or "alumed" in tags:
        return True
    if "joy" in author or "joy" in category or "joy" in tags:
        return True
    if "apunte" in category and platform in {"", "google drive", "drive", "alumed"}:
        return True
    return False


def _infer_subject_key(book) -> str:
    subject = getattr(book, "subject", "") or ""
    if subject in SUBJECT_META and subject != "simulacros":
        return subject

    samples = " ".join(
        [
            getattr(book, "title", "") or "",
            getattr(book, "description", "") or "",
            getattr(book, "category", "") or "",
            getattr(book, "tags", "") or "",
        ]
    )
    return _infer_subject_key_from_text(samples) or "shared-year-1"


def _infer_group_id(book, is_official: bool) -> str:
    raw_subject = getattr(book, "subject", "") or ""
    haystack = _normalize_text(
        " ".join(
            [
                getattr(book, "title", "") or "",
                getattr(book, "description", "") or "",
                getattr(book, "category", "") or "",
                getattr(book, "tags", "") or "",
            ]
        )
    )
    platform = _normalize_text(getattr(book, "platform", "") or "")

    if raw_subject == "simulacros" or any(token in haystack for token in ("simulacro", "parcial", "final", "examen", "pregunta")):
        return "simulacros_examenes"
    if any(token in haystack for token in ("metodo joy", "joy", "roadmap", "plan de estudio")):
        return "metodo_profe_joy"
    if any(token in haystack for token in ("atlas", "libro", "manual", "bibliografia", "texto")):
        return "libros"
    if not is_official and platform in {"studocu", "docsity", "dropbox", "onedrive"}:
        return "libros"
    if not is_official:
        return "recursos_complementarios"
    return "apuntes_alumed"


def _action_label(group_id: str, is_available: bool, continue_mode: bool = False) -> str:
    if not is_available:
        return "Proximamente"
    if continue_mode:
        return "Continuar"
    if group_id == "simulacros_examenes":
        return "Practicar"
    if group_id in {"apuntes_alumed", "metodo_profe_joy"}:
        return "Estudiar"
    return "Abrir"


def _status_from_book(book) -> str:
    if _safe_media_url(getattr(book, "pdf_file", None)):
        return "available"

    url = getattr(book, "pdf_url", "") or ""
    if url and not _is_search_url(url):
        return "available"
    if url:
        return "pending_validation"
    return "missing_link"


def _badge_from_book(book, group_id: str, status: str, is_official: bool) -> str:
    if is_official and group_id == "apuntes_alumed":
        return "Oficial ALUMED"
    if group_id == "metodo_profe_joy":
        return "Metodo Joy"
    if group_id == "simulacros_examenes":
        return "Practica guiada"
    if status == "available":
        return "Listo para estudiar"
    return "Migracion ALUMED"


def _dynamic_subject_meta(subject_key: str, year_id: str) -> dict:
    year_label = next((year["label"] for year in YEAR_DEFINITIONS if year["id"] == year_id), "General")
    return {
        "label": "Recursos transversales",
        "slug": f"recursos-transversales-{year_id}",
        "yearId": year_id,
        "icon": "fa-folder-open",
        "cover": "img/library/biologia.svg",
        "description": f"Material transversal que todavia no esta asignado a una materia especifica de {year_label}.",
        "focus": "Espacio temporal para no perder recursos durante la migracion.",
        "accent": "slate",
        "aliases": [],
    }


def _book_to_item(book) -> dict:
    subject_key = _infer_subject_key(book)
    subject_meta = SUBJECT_META.get(subject_key) or _dynamic_subject_meta(subject_key, "year-1")
    year_id = subject_meta["yearId"]
    is_official = _book_is_official(book)
    group_id = _infer_group_id(book, is_official)
    status = _status_from_book(book)
    status_meta = _status_note(status)

    source_url = getattr(book, "pdf_url", "") or ""
    alumed_url = _safe_media_url(getattr(book, "pdf_file", None))
    drive_url = source_url if "drive.google.com" in _normalize_text(source_url) else ""
    original_url = source_url if source_url and not _is_search_url(source_url) and not drive_url else ""
    cover_image = _safe_media_url(getattr(book, "cover_image", None))

    item = {
        "id": f"db-{book.id}",
        "origin": "catalog",
        "subjectKey": subject_key,
        "subjectLabel": subject_meta["label"],
        "yearId": year_id,
        "yearLabel": next((year["label"] for year in YEAR_DEFINITIONS if year["id"] == year_id), "General"),
        "groupId": group_id,
        "title": getattr(book, "title", "") or subject_meta["label"],
        "description": getattr(book, "description", "") or "Recurso listo para integrarse a la sala de estudio de ALUMED.",
        "category": getattr(book, "category", "") or "General",
        "badge": _badge_from_book(book, group_id, status, is_official),
        "cover": cover_image or subject_meta.get("cover", ""),
        "author": getattr(book, "author", "") or ("Equipo ALUMED" if is_official else "Curacion externa"),
        "type": "Apunte" if is_official else "Documento",
        "source": getattr(book, "platform", "") or ("ALUMED" if is_official else "Fuente externa"),
        "status": status,
        "pages": getattr(book, "page_count", None),
        "alumedUrl": alumed_url,
        "driveUrl": drive_url,
        "originalUrl": original_url,
        "sourceUrl": source_url,
        "tags": [tag.strip() for tag in (getattr(book, "tags", "") or "").split(",") if tag.strip()],
        "fileType": "PDF",
        "updatedAt": getattr(book, "updated_at", None).strftime("%Y-%m-%d") if getattr(book, "updated_at", None) else "Sin fecha",
        "isOfficial": is_official,
        "metaLine": subject_meta["focus"],
    }
    item["primaryUrl"] = _pick_primary_url(item)
    item["isAvailable"] = bool(item["primaryUrl"])
    item["actionLabel"] = _action_label(group_id, item["isAvailable"])
    item["statusLabel"] = status_meta["label"]
    item["statusTone"] = status_meta["tone"]
    item["availabilityNote"] = status_meta["note"]
    return item


def _enrich_inventory_record(record: dict) -> dict:
    enriched = dict(record)
    status_meta = _status_note(enriched["status"])
    subject_key = enriched.get("subjectKey") or _infer_subject_key_from_text(
        " ".join([enriched.get("folder", ""), enriched.get("subfolder", ""), enriched.get("title", "")])
    )
    enriched["subjectKey"] = subject_key or "shared-year-1"
    enriched["subjectLabel"] = SUBJECT_META.get(enriched["subjectKey"], {}).get("label", "Recursos transversales")
    enriched["yearLabel"] = next(
        (year["label"] for year in YEAR_DEFINITIONS if year["id"] == enriched.get("yearId")),
        "General",
    )
    enriched["statusLabel"] = status_meta["label"]
    enriched["statusTone"] = status_meta["tone"]
    enriched["availabilityNote"] = status_meta["note"]
    return enriched


def _inventory_to_room_item(record: dict) -> dict:
    group_id = record.get("groupId", "libros")
    item = {
        "id": f"inv-{record['id']}",
        "origin": "inventory",
        "subjectKey": record["subjectKey"],
        "subjectLabel": record["subjectLabel"],
        "yearId": record["yearId"],
        "yearLabel": record["yearLabel"],
        "groupId": group_id,
        "title": record["title"],
        "description": record.get("description", "") or "Entrada reservada para migracion por fases.",
        "category": record.get("subfolder", "") or record.get("folder", ""),
        "badge": "Migracion ALUMED",
        "cover": record.get("cover", ""),
        "author": "Curacion ALUMED",
        "type": "Coleccion" if record.get("fileType") == "Folder" else "Libro",
        "source": "Wix File Share",
        "status": record["status"],
        "pages": None,
        "alumedUrl": "",
        "driveUrl": "",
        "originalUrl": "",
        "sourceUrl": record.get("sourceUrl", "") or "",
        "tags": [record.get("folder", ""), record.get("subfolder", "")],
        "fileType": record.get("fileType", "PDF"),
        "updatedAt": record.get("updatedAt", "Sin fecha"),
        "isOfficial": False,
        "metaLine": "Inventario migrable preparado para enlace directo.",
    }
    status_meta = _status_note(item["status"])
    item["primaryUrl"] = _pick_primary_url(item)
    item["isAvailable"] = bool(item["primaryUrl"])
    item["actionLabel"] = _action_label(group_id, item["isAvailable"])
    item["statusLabel"] = status_meta["label"]
    item["statusTone"] = status_meta["tone"]
    item["availabilityNote"] = status_meta["note"]
    return item


def _build_group_shell(group_definition: dict) -> dict:
    return {
        "id": group_definition["id"],
        "label": group_definition["label"],
        "icon": group_definition["icon"],
        "description": group_definition["description"],
        "emptyState": {
            "title": group_definition["emptyTitle"],
            "copy": group_definition["emptyCopy"],
            "badge": group_definition["emptyBadge"],
        },
        "isFuture": group_definition["isFuture"],
        "items": [],
        "counts": {"total": 0, "available": 0, "official": 0},
    }


def _build_room(subject_key: str, meta: dict) -> dict:
    year_label = next(
        (year["label"] for year in YEAR_DEFINITIONS if year["id"] == meta["yearId"]),
        "General",
    )
    return {
        "id": subject_key,
        "label": meta["label"],
        "slug": meta["slug"],
        "yearId": meta["yearId"],
        "yearLabel": year_label,
        "icon": meta["icon"],
        "cover": meta["cover"],
        "description": meta["description"],
        "focus": meta["focus"],
        "accent": meta["accent"],
        "isDynamic": subject_key not in SUBJECT_META,
        "resourceGroups": {
            group["id"]: _build_group_shell(group)
            for group in RESOURCE_GROUP_DEFINITIONS
        },
        "inventoryItems": [],
        "stats": {"total": 0, "available": 0, "official": 0, "pending": 0},
    }


def _attach_item_to_room(room: dict, item: dict) -> None:
    group_id = item["groupId"]
    group_shell = room["resourceGroups"].get(group_id)
    if not group_shell:
        return
    group_shell["items"].append(item)


def _sort_item_key(item: dict) -> tuple:
    return (
        0 if item.get("isOfficial") else 1,
        STATUS_ORDER.get(item.get("status"), 9),
        _normalize_text(item.get("title", "")),
    )


def _finalize_room(room: dict) -> dict:
    total = 0
    available = 0
    official = 0
    pending = 0

    ordered_groups = []
    for group_definition in RESOURCE_GROUP_DEFINITIONS:
        group = room["resourceGroups"][group_definition["id"]]
        group["items"] = sorted(group["items"], key=_sort_item_key)
        group_total = len(group["items"])
        group_available = sum(1 for item in group["items"] if item["isAvailable"])
        group_official = sum(1 for item in group["items"] if item["isOfficial"])
        group["counts"] = {
            "total": group_total,
            "available": group_available,
            "official": group_official,
        }
        total += group_total
        available += group_available
        official += group_official
        pending += sum(1 for item in group["items"] if not item["isAvailable"])
        ordered_groups.append(group)

    room["resourceGroups"] = ordered_groups
    room["stats"] = {
        "total": total,
        "available": available,
        "official": official,
        "pending": pending,
    }
    room["continueCard"] = _build_continue_card(room)
    room["yearLabel"] = next(
        (year["label"] for year in YEAR_DEFINITIONS if year["id"] == room["yearId"]),
        "General",
    )
    room["isReady"] = total > 0
    return room


def _build_continue_card(room: dict) -> dict:
    room_year_label = room.get("yearLabel") or next(
        (year["label"] for year in YEAR_DEFINITIONS if year["id"] == room["yearId"]),
        "General",
    )
    preferred_groups = [
        "apuntes_alumed",
        "metodo_profe_joy",
        "libros",
        "simulacros_examenes",
        "recursos_complementarios",
    ]

    fallback_item = None
    for group_id in preferred_groups:
        group = next((entry for entry in room["resourceGroups"] if entry["id"] == group_id), None)
        if not group:
            continue
        for item in group["items"]:
            if item["isAvailable"]:
                return {
                    "eyebrow": "Continuar estudiando",
                    "title": item["title"],
                    "description": item["description"],
                    "badge": item["badge"],
                    "url": item["primaryUrl"],
                    "actionLabel": _action_label(group_id, True, continue_mode=True),
                    "statusLabel": item["statusLabel"],
                    "statusTone": item["statusTone"],
                    "meta": f"{room['label']} · {group['label']}",
                }
            if fallback_item is None and item:
                fallback_item = (item, group)

    if fallback_item:
        item, group = fallback_item
        return {
            "eyebrow": "Continuar estudiando",
            "title": f"Preparar {room['label']}",
            "description": item["description"],
            "badge": item["badge"],
            "url": "",
            "actionLabel": "Proximamente",
            "statusLabel": item["statusLabel"],
            "statusTone": item["statusTone"],
            "meta": f"{room['label']} · {group['label']}",
        }

    return {
        "eyebrow": "Continuar estudiando",
        "title": f"Sala de estudio de {room['label']}",
        "description": (
            "La arquitectura de esta materia ya esta preparada para apuntes oficiales, "
            "libros, practica y modulos inteligentes."
        ),
        "badge": "Ruta academica",
        "url": "",
        "actionLabel": "Proximamente",
        "statusLabel": "Espacio preparado",
        "statusTone": "muted",
        "meta": f"{room_year_label} · {room['label']}",
    }


def _serialize_subject_nav(room: dict) -> dict:
    return {
        "id": room["id"],
        "label": room["label"],
        "icon": room["icon"],
        "cover": room["cover"],
        "description": room["description"],
        "focus": room["focus"],
        "accent": room["accent"],
        "resourceCount": room["stats"]["total"],
        "availableCount": room["stats"]["available"],
        "officialCount": room["stats"]["official"],
        "pendingCount": room["stats"]["pending"],
        "isReady": room["isReady"],
        "badge": "Activa" if room["stats"]["total"] else "Preparada",
    }


def build_library_payload(books: Iterable) -> dict:
    year_subjects = {year["id"]: list(year["subjects"]) for year in YEAR_DEFINITIONS}
    rooms = {
        subject_key: _build_room(subject_key, meta)
        for subject_key, meta in SUBJECT_META.items()
    }

    normalized_books = [_book_to_item(book) for book in books]
    inventory_records = [_enrich_inventory_record(record) for record in WIX_FILE_SHARE_INVENTORY]
    visible_inventory_items = [_inventory_to_room_item(record) for record in inventory_records]
    visible_items = normalized_books + visible_inventory_items

    for item in visible_items:
        subject_key = item["subjectKey"]
        if subject_key not in rooms:
            dynamic_meta = _dynamic_subject_meta(subject_key, item.get("yearId", "year-1"))
            rooms[subject_key] = _build_room(subject_key, dynamic_meta)
            year_subjects.setdefault(dynamic_meta["yearId"], []).append(subject_key)
        _attach_item_to_room(rooms[subject_key], item)

    for record in inventory_records:
        subject_key = record["subjectKey"]
        if subject_key not in rooms:
            dynamic_meta = _dynamic_subject_meta(subject_key, record.get("yearId", "year-1"))
            rooms[subject_key] = _build_room(subject_key, dynamic_meta)
            year_subjects.setdefault(dynamic_meta["yearId"], []).append(subject_key)
        rooms[subject_key]["inventoryItems"].append(record)

    finalized_rooms = {
        room_key: _finalize_room(room)
        for room_key, room in rooms.items()
    }

    years_payload = []
    for year in YEAR_DEFINITIONS:
        subject_ids = _dedupe(year_subjects.get(year["id"], year["subjects"]))
        subjects = [
            _serialize_subject_nav(finalized_rooms[subject_id])
            for subject_id in subject_ids
            if subject_id in finalized_rooms
        ]
        years_payload.append(
            {
                "id": year["id"],
                "label": year["label"],
                "headline": year["headline"],
                "copy": year["copy"],
                "status": year["status"],
                "isDefault": year.get("isDefault", False),
                "subjects": subjects,
                "resourceCount": sum(subject["resourceCount"] for subject in subjects),
                "availableCount": sum(subject["availableCount"] for subject in subjects),
            }
        )

    status_counts = Counter(item["status"] for item in visible_items)
    summary = {
        "totalItems": len(visible_items),
        "subjectCount": sum(len(year["subjects"]) for year in years_payload),
        "yearCount": len(YEAR_DEFINITIONS),
        "inventoryCount": len(inventory_records),
        "availableCount": sum(1 for item in visible_items if item["isAvailable"]),
        "pendingCount": status_counts.get("pending_validation", 0)
        + status_counts.get("pending_inventory", 0)
        + status_counts.get("missing_link", 0),
        "officialCount": sum(1 for item in visible_items if item["isOfficial"]),
        "futureModuleCount": sum(1 for group in RESOURCE_GROUP_DEFINITIONS if group["isFuture"]),
    }

    return {
        "career": CAREER_META,
        "years": years_payload,
        "rooms": finalized_rooms,
        "inventory": inventory_records,
        "summary": summary,
        "linkPriority": [
            "Documento hospedado en ALUMED",
            "Google Drive",
            "URL publica directa",
            "Fuente original validada",
        ],
        "futureModules": [
            group["label"]
            for group in RESOURCE_GROUP_DEFINITIONS
            if group["isFuture"]
        ],
    }
