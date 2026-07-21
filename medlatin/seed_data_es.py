from __future__ import annotations
from .services import normalize_text

def part(part_type, form, meaning, origin_language, grammatical_function="", notes=""):
    return {
        "part_type": part_type,
        "form": form,
        "normalized_form": normalize_text(form).replace("-", ""),
        "meaning": meaning,
        "origin_language": origin_language,
        "grammatical_function": grammatical_function,
        "notes": notes,
    }

def whole(form, meaning, origin_language, notes="Manejado como unidad léxica."):
    return [part("whole_lexical_unit", form, meaning, origin_language, notes=notes)]

def translation(language, text, notes=""):
    return {"language": language, "text": text, "translation_type": "preferred", "notes": notes}

def example(context, title, content, language):
    return {"context": context, "title": title, "content": content, "language": language}

def entry(
    latin_name, literal_translation, medical_definition, etymology, naming_logic, mnemonic,
    subject, anatomical_system, difficulty, origin_language, term_type, naming_category,
    translations, word_parts, specialty="", standard_term="", grammatical_class="noun",
    gender="", declension="", exam_trap="", rapid_review="", mnemonic_spanish="",
    mnemonic_portuguese="", examples=None, relationships=None
):
    return {
        "latin_name": latin_name,
        "standard_term": standard_term or latin_name,
        "pronunciation": "",
        "audio_url": "",
        "grammatical_class": grammatical_class,
        "gender": gender,
        "declension": declension,
        "literal_translation": literal_translation,
        "medical_definition": medical_definition,
        "etymology": etymology,
        "naming_logic": naming_logic,
        "naming_category": naming_category,
        "mnemonic": mnemonic,
        "mnemonic_spanish": mnemonic_spanish or mnemonic,
        "mnemonic_portuguese": mnemonic_portuguese or mnemonic,
        "exam_trap": exam_trap,
        "rapid_review": rapid_review,
        "specialty": specialty or subject,
        "subject": subject,
        "anatomical_system": anatomical_system,
        "anatomical_region": "",
        "difficulty": difficulty,
        "origin_language": origin_language,
        "term_type": term_type,
        "validation_status": "ai_draft",
        "source_notes": "Borrador educativo MedLatín.",
        "translations": translations,
        "word_parts": word_parts,
        "examples": examples or [],
        "relationships": relationships or [],
    }

ROOT_LIBRARY = [
    {"form": "bi-", "root_type": "prefix", "origin_language": "Latín", "core_meaning": "dos", "explanation": "Prefijo numérico latino que indica dos.", "mnemonic": "Bi = dos."},
    {"form": "tri-", "root_type": "prefix", "origin_language": "Latín", "core_meaning": "tres", "explanation": "Prefijo numérico latino que indica tres.", "mnemonic": "Tri = tres."},
    {"form": "ad-", "root_type": "preposition", "origin_language": "Latín", "core_meaning": "hacia", "explanation": "Preposición latina que indica dirección hacia algo.", "mnemonic": "AD = acercar."},
    {"form": "ab-", "root_type": "preposition", "origin_language": "Latín", "core_meaning": "lejos de", "explanation": "Preposición latina que indica separación.", "mnemonic": "AB = alejar."},
    {"form": "myo-", "root_type": "combining_form", "origin_language": "Griego", "core_meaning": "músculo", "explanation": "Forma combinada griega de mys, músculo.", "mnemonic": "Myo = músculo."},
    {"form": "cardi-", "root_type": "combining_form", "origin_language": "Griego", "core_meaning": "corazón", "explanation": "Forma combinada griega de kardia, corazón.", "mnemonic": "Cardi = corazón."},
    {"form": "endo-", "root_type": "prefix", "origin_language": "Griego", "core_meaning": "dentro", "explanation": "Prefijo griego que significa adentro.", "mnemonic": "Endo = dentro."},
    {"form": "oste-", "root_type": "combining_form", "origin_language": "Griego", "core_meaning": "hueso", "explanation": "Del griego osteon, hueso.", "mnemonic": "Oste = hueso."},
    {"form": "-itis", "root_type": "suffix", "origin_language": "Griego", "core_meaning": "inflamación", "explanation": "Sufijo inflamatorio griego.", "mnemonic": "-itis significa inflamación."},
    {"form": "-oma", "root_type": "suffix", "origin_language": "Griego", "core_meaning": "tumor", "explanation": "Sufijo griego para masa o tumor.", "mnemonic": "-oma = tumor."},
    {"form": "gastr-", "root_type": "combining_form", "origin_language": "Griego", "core_meaning": "estómago", "explanation": "Del griego gaster, estómago o vientre.", "mnemonic": "Gastr = estómago."},
]

SEED_TERMS = [
    entry(
        "biceps", "de dos cabezas", 
        "Descriptor anatómico latino para una estructura con dos cabezas o puntos de origen.", 
        "Del latín clásico biceps, de bi- 'dos' y -ceps 'cabeza'.", 
        "El nombre cuenta el número de cabezas.", 
        "Bi = dos, por lo que el bíceps es el de dos cabezas.", 
        "Anatomía", "Sistema Musculoesquelético", 1, "Latín", "adjetivo anatómico", "Número", 
        [translation("es", "bíceps"), translation("pt-BR", "bíceps"), translation("en", "biceps")], 
        [part("prefix", "bi-", "dos", "Latín"), part("compound_element", "-ceps", "cabeza", "Latín")], 
        grammatical_class="adjetivo", rapid_review="Bíceps nombra una estructura de dos cabezas."
    ),
    entry(
        "myocardium", "músculo del corazón", 
        "La capa muscular del corazón que se contrae para bombear sangre.", 
        "Del griego myo- 'músculo' y kardia 'corazón'.", 
        "Combina el tipo de tejido con el órgano.", 
        "Myo = músculo, cardi = corazón.", 
        "Histología", "Sistema Cardiovascular", 1, "Griego", "sustantivo anatómico", "Estructura", 
        [translation("es", "miocardio"), translation("pt-BR", "miocárdio"), translation("en", "myocardium")], 
        [part("root", "myo-", "músculo", "Griego"), part("root", "cardi-", "corazón", "Griego"), part("suffix", "-um", "estructura", "Latín")], 
        grammatical_class="sustantivo", rapid_review="El miocardio es el músculo cardíaco."
    ),
    entry(
        "osteoblast", "célula formadora de hueso", 
        "Célula responsable de la formación de hueso.", 
        "Del griego osteon 'hueso' y blastos 'germen o célula formativa'.", 
        "Blast significa construir.", 
        "Blast construye hueso.", 
        "Histología", "Sistema Esquelético", 1, "Griego", "tipo de célula", "Función", 
        [translation("es", "osteoblasto"), translation("pt-BR", "osteoblasto"), translation("en", "osteoblast")], 
        [part("root", "oste-", "hueso", "Griego"), part("suffix", "-blast", "célula formativa", "Griego")], 
        grammatical_class="sustantivo", rapid_review="Osteoblasto construye hueso."
    ),
    entry(
        "gastritis", "inflamación del estómago", 
        "Inflamación de la mucosa gástrica.", 
        "Del griego gaster 'estómago' e -itis 'inflamación'.", 
        "Combina órgano y proceso patológico.", 
        "-itis siempre es inflamación.", 
        "Patología", "Sistema Digestivo", 1, "Griego", "patología", "Proceso Patológico", 
        [translation("es", "gastritis"), translation("pt-BR", "gastrite"), translation("en", "gastritis")], 
        [part("root", "gastr-", "estómago", "Griego"), part("suffix", "-itis", "inflamación", "Griego")], 
        grammatical_class="sustantivo", rapid_review="Gastritis es inflamación estomacal."
    ),
    entry(
        "adductor", "el que acerca", 
        "Músculo que mueve una estructura hacia el eje de referencia o línea media.", 
        "Del latín ad- 'hacia' y ducere 'guiar'.", 
        "El nombre se refiere a la función de acercar.", 
        "AD = acercar.", 
        "Anatomía", "Sistema Musculoesquelético", 1, "Latín", "músculo", "Función", 
        [translation("es", "aductor"), translation("pt-BR", "adutor"), translation("en", "adductor")], 
        [part("prefix", "ad-", "hacia", "Latín"), part("root", "duc-", "guiar", "Latín"), part("suffix", "-tor", "agente", "Latín")], 
        grammatical_class="sustantivo", rapid_review="El aductor acerca hacia la línea media."
    ),
]

SEED_QUIZZES = [
    {
        "title": "Lógica Básica Anatómica",
        "subject": "Anatomía",
        "difficulty": 1,
        "description": "Diferencias básicas entre función y posición.",
        "questions": [
            {
                "question_type": "multiple_choice", 
                "prompt": "¿Qué término significa 'el que acerca' hacia la línea media?", 
                "options": ["adductor", "abductor", "extensor", "flexor"], 
                "correct_answer": {"value": "adductor"}, 
                "term_slug": "adductor", 
                "explanation": "Ad- significa hacia (acercar)."
            },
            {
                "question_type": "multiple_choice", 
                "prompt": "¿Qué descriptor señala una estructura de dos cabezas?", 
                "options": ["biceps", "triceps", "quadriceps", "digastricus"], 
                "correct_answer": {"value": "biceps"}, 
                "term_slug": "biceps", 
                "explanation": "Bi- indica dos."
            }
        ],
    },
    {
        "title": "Raíces de Patología",
        "subject": "Patología",
        "difficulty": 2,
        "description": "Raíces griegas comunes en patología.",
        "questions": [
            {
                "question_type": "multiple_choice", 
                "prompt": "¿Qué sufijo señala inflamación?", 
                "options": ["-oma", "-itis", "-plasia", "-trophy"], 
                "correct_answer": {"value": "-itis"}, 
                "explanation": "-itis es el sufijo inflamatorio."
            },
            {
                "question_type": "multiple_choice", 
                "prompt": "¿Qué significa osteoblasto?", 
                "options": ["célula que destruye hueso", "célula que construye hueso", "tumor óseo", "inflamación ósea"], 
                "correct_answer": {"value": "célula que construye hueso"}, 
                "term_slug": "osteoblast", 
                "explanation": "Blast significa construir o germinar."
            }
        ],
    },
]
