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


def whole(form, meaning, origin_language, notes="Safest handled here as a lexical unit."):
    return [part("whole_lexical_unit", form, meaning, origin_language, notes=notes)]


def translation(language, text, notes=""):
    return {"language": language, "text": text, "translation_type": "preferred", "notes": notes}


def example(context, title, content, language):
    return {"context": context, "title": title, "content": content, "language": language}


def entry(
    latin_name,
    literal_translation,
    medical_definition,
    etymology,
    naming_logic,
    mnemonic,
    subject,
    anatomical_system,
    difficulty,
    origin_language,
    term_type,
    naming_category,
    translations,
    word_parts,
    specialty="",
    standard_term="",
    grammatical_class="noun",
    gender="",
    declension="",
    exam_trap="",
    rapid_review="",
    mnemonic_spanish="",
    mnemonic_portuguese="",
    examples=None,
    relationships=None,
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
        "source_notes": "Seeded MedLatin educational draft.",
        "translations": translations,
        "word_parts": word_parts,
        "examples": examples or [],
        "relationships": relationships or [],
    }


ROOT_LIBRARY = [
    {"form": "bi-", "root_type": "prefix", "origin_language": "Latin", "core_meaning": "two", "explanation": "Numeric Latin prefix indicating two.", "mnemonic": "Bi = two."},
    {"form": "tri-", "root_type": "prefix", "origin_language": "Latin", "core_meaning": "three", "explanation": "Numeric Latin prefix indicating three.", "mnemonic": "Tri = three."},
    {"form": "quadri-", "root_type": "prefix", "origin_language": "Latin", "core_meaning": "four", "explanation": "Numeric Latin prefix indicating four.", "mnemonic": "Quadri = four."},
    {"form": "di-", "root_type": "prefix", "origin_language": "Greek", "core_meaning": "two", "explanation": "Greek numeral used in many compounds.", "mnemonic": "Di = two."},
    {"form": "ad-", "root_type": "preposition", "origin_language": "Latin", "core_meaning": "toward", "explanation": "Latin preposition and prefix indicating direction toward.", "mnemonic": "AD = acercar."},
    {"form": "ab-", "root_type": "preposition", "origin_language": "Latin", "core_meaning": "away from", "explanation": "Latin preposition and prefix indicating separation or movement away.", "mnemonic": "AB = afastar."},
    {"form": "duc-", "root_type": "root", "origin_language": "Latin", "core_meaning": "lead, bring", "explanation": "From Latin ducere, to lead.", "mnemonic": "Duc = conducir."},
    {"form": "flex-", "root_type": "root", "origin_language": "Latin", "core_meaning": "bend", "explanation": "From Latin flectere, to bend.", "mnemonic": "Flex = flexionar."},
    {"form": "tens-", "root_type": "root", "origin_language": "Latin", "core_meaning": "stretch", "explanation": "From Latin tendere/tensus, to stretch.", "mnemonic": "Tensor extends or stretches."},
    {"form": "lev-", "root_type": "root", "origin_language": "Latin", "core_meaning": "raise", "explanation": "From Latin levare, to raise.", "mnemonic": "Levator lifts."},
    {"form": "press-", "root_type": "root", "origin_language": "Latin", "core_meaning": "press downward", "explanation": "From Latin premere/pressus, to press.", "mnemonic": "Depressor presses down."},
    {"form": "strict-", "root_type": "root", "origin_language": "Latin", "core_meaning": "draw tight", "explanation": "From Latin stringere/strictus, to bind tight.", "mnemonic": "Constrict = tighten."},
    {"form": "-tor", "root_type": "suffix", "origin_language": "Latin", "core_meaning": "agent, doer", "explanation": "Agentive suffix in Latin.", "mnemonic": "-tor names the one that performs the action."},
    {"form": "-or", "root_type": "suffix", "origin_language": "Latin", "core_meaning": "agent, doer", "explanation": "Agentive suffix in Latin.", "mnemonic": "-or names the doer."},
    {"form": "myo-", "root_type": "combining_form", "origin_language": "Greek", "core_meaning": "muscle", "explanation": "Greek combining form from mys, muscle.", "mnemonic": "Myo = músculo."},
    {"form": "cardi-", "root_type": "combining_form", "origin_language": "Greek", "core_meaning": "heart", "explanation": "Greek combining form from kardia, heart.", "mnemonic": "Cardi = corazón."},
    {"form": "endo-", "root_type": "prefix", "origin_language": "Greek", "core_meaning": "within", "explanation": "Greek prefix meaning inside.", "mnemonic": "Endo = dentro."},
    {"form": "peri-", "root_type": "prefix", "origin_language": "Greek", "core_meaning": "around", "explanation": "Greek prefix meaning around.", "mnemonic": "Peri = around the perimeter."},
    {"form": "oste-", "root_type": "combining_form", "origin_language": "Greek", "core_meaning": "bone", "explanation": "Greek osteon, bone.", "mnemonic": "Oste = hueso."},
    {"form": "chondr-", "root_type": "combining_form", "origin_language": "Greek", "core_meaning": "cartilage", "explanation": "Greek chondros, cartilage.", "mnemonic": "Chondr = cartílago."},
    {"form": "cyt-", "root_type": "combining_form", "origin_language": "Greek", "core_meaning": "cell", "explanation": "Greek kytos, cell.", "mnemonic": "Cyte = célula."},
    {"form": "blast-", "root_type": "combining_form", "origin_language": "Greek", "core_meaning": "germ, formative cell", "explanation": "Greek blastos, sprout or germ.", "mnemonic": "Blast = builder cell."},
    {"form": "epi-", "root_type": "prefix", "origin_language": "Greek", "core_meaning": "upon", "explanation": "Greek prefix meaning on or upon.", "mnemonic": "Epi = on top."},
    {"form": "meso-", "root_type": "prefix", "origin_language": "Greek", "core_meaning": "middle", "explanation": "Greek prefix meaning middle.", "mnemonic": "Meso = middle."},
    {"form": "adeno-", "root_type": "combining_form", "origin_language": "Greek", "core_meaning": "gland", "explanation": "Greek aden, gland.", "mnemonic": "Adeno = gland."},
    {"form": "carcin-", "root_type": "combining_form", "origin_language": "Greek", "core_meaning": "crab; cancer", "explanation": "Greek karkinos, crab, source of carcinoma.", "mnemonic": "Carcin = cancer."},
    {"form": "necr-", "root_type": "combining_form", "origin_language": "Greek", "core_meaning": "death", "explanation": "Greek nekros, dead.", "mnemonic": "Necro = death."},
    {"form": "hyper-", "root_type": "prefix", "origin_language": "Greek", "core_meaning": "over, excessive", "explanation": "Greek prefix indicating excess.", "mnemonic": "Hyper = above normal."},
    {"form": "meta-", "root_type": "prefix", "origin_language": "Greek", "core_meaning": "change, beyond", "explanation": "Greek prefix indicating change or transformation.", "mnemonic": "Meta = change."},
    {"form": "dys-", "root_type": "prefix", "origin_language": "Greek", "core_meaning": "bad, disordered", "explanation": "Greek prefix for difficulty or abnormality.", "mnemonic": "Dys = disorder."},
    {"form": "-itis", "root_type": "suffix", "origin_language": "Greek", "core_meaning": "inflammation", "explanation": "Greek inflammatory suffix.", "mnemonic": "-itis means inflammation."},
    {"form": "-osis", "root_type": "suffix", "origin_language": "Greek", "core_meaning": "condition, process", "explanation": "Greek suffix for process or state.", "mnemonic": "-osis = condition."},
    {"form": "-oma", "root_type": "suffix", "origin_language": "Greek", "core_meaning": "tumor, mass", "explanation": "Greek suffix for tumor or swelling.", "mnemonic": "-oma = tumor."},
    {"form": "-plasia", "root_type": "suffix", "origin_language": "Greek", "core_meaning": "formation, growth", "explanation": "Greek plasis, molding or formation.", "mnemonic": "-plasia = growth pattern."},
    {"form": "-trophy", "root_type": "suffix", "origin_language": "Greek", "core_meaning": "nourishment, development", "explanation": "Greek trophe, nourishment.", "mnemonic": "-trophy = growth by nourishment."},
    {"form": "gastr-", "root_type": "combining_form", "origin_language": "Greek", "core_meaning": "stomach; belly", "explanation": "Greek gaster, stomach or belly.", "mnemonic": "Gastr = stomach."},
    {"form": "sterno-", "root_type": "combining_form", "origin_language": "Greek", "core_meaning": "sternum", "explanation": "Greek sternon, chest or sternum.", "mnemonic": "Sterno = sternum."},
    {"form": "cleido-", "root_type": "combining_form", "origin_language": "Greek", "core_meaning": "clavicle", "explanation": "Greek kleis/kleidos, clavicle.", "mnemonic": "Cleido = clavicle."},
    {"form": "mastoid-", "root_type": "combining_form", "origin_language": "Greek", "core_meaning": "breast-shaped; mastoid", "explanation": "Greek mastoeides, breast-shaped.", "mnemonic": "Mastoid = breast-shaped."},
]


SEED_TERMS = [
    entry("biceps", "two-headed", "Latin anatomical descriptor for a structure with two heads or points of origin.", "Classical Latin biceps from bi- 'two' and -ceps, a form meaning 'headed'.", "The name counts the number of heads.", "Bi = two, so biceps is the two-headed one.", "Anatomy", "Musculoskeletal system", 1, "Latin", "anatomical adjective", "Number", [translation("es", "bíceps"), translation("pt-BR", "bíceps"), translation("en", "biceps")], [part("prefix", "bi-", "two", "Latin"), part("compound_element", "-ceps", "headed", "Latin")], grammatical_class="adjective", rapid_review="Biceps names a two-headed structure."),
    entry("triceps", "three-headed", "Latin anatomical descriptor for a structure with three heads.", "Classical Latin triceps from tri- 'three' and -ceps 'headed'.", "The name counts the number of heads.", "Tri = three, so triceps has three heads.", "Anatomy", "Musculoskeletal system", 1, "Latin", "anatomical adjective", "Number", [translation("es", "tríceps"), translation("pt-BR", "tríceps"), translation("en", "triceps")], [part("prefix", "tri-", "three", "Latin"), part("compound_element", "-ceps", "headed", "Latin")], grammatical_class="adjective", rapid_review="Triceps names a three-headed structure."),
    entry("quadriceps", "four-headed", "Latin anatomical descriptor for a structure with four heads.", "Latin quadriceps from quadri- 'four' and -ceps 'headed'.", "The name counts the number of muscular heads.", "Quadri = four, so quadriceps has four heads.", "Anatomy", "Musculoskeletal system", 1, "Latin", "anatomical adjective", "Number", [translation("es", "cuádriceps"), translation("pt-BR", "quadríceps"), translation("en", "quadriceps")], [part("prefix", "quadri-", "four", "Latin"), part("compound_element", "-ceps", "headed", "Latin")], grammatical_class="adjective", rapid_review="Quadriceps names a four-headed structure."),
    entry("digastricus", "two-bellied", "Latinized anatomical adjective describing a muscle with two fleshy bellies connected by an intermediate tendon.", "Greek-derived Latinized form from di- 'two' and gaster/gastros 'belly', with Latin adjectival ending -icus.", "The name counts two bellies rather than two heads.", "Di = two and gastr = belly, so digastric has two bellies.", "Anatomy", "Musculoskeletal system", 2, "Greek-derived Latinized form", "anatomical adjective", "Number", [translation("es", "digástrico"), translation("pt-BR", "digástrico"), translation("en", "digastric")], [part("prefix", "di-", "two", "Greek"), part("root", "gastr-", "belly", "Greek"), part("suffix", "-icus", "pertaining to", "Latin")], grammatical_class="adjective", rapid_review="Digastric means two-bellied, not two-headed."),
    entry("flexor", "one that bends", "A muscle whose primary action is flexion, reducing the angle at a joint.", "Latin flexor from flectere 'to bend' with agent suffix -or.", "The name refers to function.", "Flexor flexes.", "Anatomy", "Musculoskeletal system", 1, "Latin", "muscle action term", "Function", [translation("es", "flexor"), translation("pt-BR", "flexor"), translation("en", "flexor")], [part("root", "flex-", "bend", "Latin"), part("suffix", "-or", "agent or doer", "Latin")], grammatical_class="noun", rapid_review="A flexor decreases the joint angle."),
    entry("extensor", "one that stretches out", "A muscle whose primary action is extension, increasing the angle at a joint or straightening a segment.", "Latin extensor from extendere/extensus 'to stretch out' with agent suffix -or.", "The name refers to function.", "Extensor extends the limb.", "Anatomy", "Musculoskeletal system", 1, "Latin", "muscle action term", "Function", [translation("es", "extensor"), translation("pt-BR", "extensor"), translation("en", "extensor")], [part("root", "tens-", "stretch", "Latin"), part("suffix", "-or", "agent or doer", "Latin")], grammatical_class="noun", rapid_review="An extensor increases the joint angle."),
    entry("adductor", "one that leads toward", "A muscle that moves a structure toward a reference axis, classically toward the midline.", "Built from Latin ad- 'toward', ducere 'to lead', and the agent suffix -tor. The common mnemonic AD = acercar is pedagogical, not the historical origin.", "The name refers to movement toward a reference axis or the midline.", "AD = acercar helps you remember adduction brings a part toward the midline.", "Anatomy", "Musculoskeletal system", 2, "Latin", "muscle action term", "Function", [translation("es", "aductor"), translation("pt-BR", "adutor"), translation("en", "adductor")], [part("prefix", "ad-", "toward", "Latin"), part("root", "duc-", "lead; bring", "Latin"), part("suffix", "-tor", "agent or doer", "Latin")], grammatical_class="noun", exam_trap="Students often confuse adduction with abduction. Always anchor the movement to the midline or another stated reference axis.", rapid_review="Adductor brings a structure toward the midline.", relationships=[("abductor", "frequently_confused", "Contrasts movement toward vs away from the reference axis.")], examples=[example("Anatomy", "Functional usage", "The adductor longus contributes to adduction of the thigh at the hip.", "en")]),
    entry("abductor", "one that leads away", "A muscle that moves a structure away from a reference axis, classically away from the midline.", "Built from Latin ab- 'away from', ducere 'to lead', and the agent suffix -tor.", "The name refers to movement away from a reference axis or the midline.", "AB = afastar can remind you that abduction moves away.", "Anatomy", "Musculoskeletal system", 2, "Latin", "muscle action term", "Function", [translation("es", "abductor"), translation("pt-BR", "abdutor"), translation("en", "abductor")], [part("prefix", "ab-", "away from", "Latin"), part("root", "duc-", "lead; bring", "Latin"), part("suffix", "-tor", "agent or doer", "Latin")], grammatical_class="noun", rapid_review="Abductor moves away from the midline."),
    entry("levator", "one that raises", "A muscle whose action is to elevate a structure.", "Latin levator from levare 'to raise' plus -tor.", "The name refers to function.", "Levator lifts.", "Anatomy", "Musculoskeletal system", 1, "Latin", "muscle action term", "Function", [translation("es", "elevador"), translation("pt-BR", "levantador"), translation("en", "levator")], [part("root", "lev-", "raise", "Latin"), part("suffix", "-tor", "agent or doer", "Latin")], grammatical_class="noun", rapid_review="Levator elevates a structure."),
    entry("depressor", "one that presses down", "A muscle that lowers or depresses a structure.", "Latin depressor from de- 'down' and premere/pressus 'to press', with agent suffix -or.", "The name refers to function.", "Depressor presses a structure down.", "Anatomy", "Musculoskeletal system", 1, "Latin", "muscle action term", "Function", [translation("es", "depresor"), translation("pt-BR", "depressor"), translation("en", "depressor")], [part("prefix", "de-", "down", "Latin"), part("root", "press-", "press downward", "Latin"), part("suffix", "-or", "agent or doer", "Latin")], grammatical_class="noun", rapid_review="Depressor lowers a structure."),
    entry("constrictor", "one that draws tight together", "A muscle whose action narrows a lumen or opening by tightening around it.", "Latin constrictor from con- 'together' and stringere/strictus 'to bind tight'.", "The name refers to narrowing by tightening.", "Constrictor constricts an opening.", "Anatomy", "Musculoskeletal system", 2, "Latin", "muscle action term", "Function", [translation("es", "constrictor"), translation("pt-BR", "constrictor"), translation("en", "constrictor")], [part("prefix", "con-", "together", "Latin"), part("root", "strict-", "draw tight", "Latin"), part("suffix", "-or", "agent or doer", "Latin")], grammatical_class="noun", rapid_review="A constrictor narrows a passage."),
    entry("sphincter", "that which binds tight", "A ring-like muscle that closes or constricts an opening.", "Greek-derived term from sphingein 'to bind tight', adopted into Latin anatomical usage.", "The name refers to closing an opening by circular contraction.", "Think of a circular gate that tightens shut.", "Anatomy", "Musculoskeletal system", 2, "Greek-derived Latinized form", "muscle action term", "Function", [translation("es", "esfínter"), translation("pt-BR", "esfíncter"), translation("en", "sphincter")], whole("sphincter", "binds tight; ring-like closing muscle", "Greek"), grammatical_class="noun", rapid_review="A sphincter closes an orifice by circular contraction."),
]


SEED_QUIZZES = []


def adjective_term(name, literal, definition, etymology, category, translations):
    return entry(
        name,
        literal,
        definition,
        etymology,
        f"The name encodes {category.lower()}.",
        f"{name} keeps its ordinary spatial or descriptive meaning in anatomy.",
        "Anatomy",
        "General anatomy",
        1,
        "Latin",
        "anatomical adjective",
        category,
        translations,
        whole(name, literal, "Latin"),
        grammatical_class="adjective",
        rapid_review=f"{name} is an anatomical adjective of {category.lower()}.",
    )


SEED_TERMS.extend(
    [
        adjective_term("anterior", "situated in front", "Situated toward the front aspect of the body or structure.", "Latin anterior, comparative of ante 'before'.", "Position", [translation("es", "anterior"), translation("pt-BR", "anterior"), translation("en", "anterior")]),
        adjective_term("posterior", "situated behind", "Situated toward the back aspect of the body or structure.", "Latin posterior, comparative of post 'after; behind'.", "Position", [translation("es", "posterior"), translation("pt-BR", "posterior"), translation("en", "posterior")]),
        adjective_term("superior", "situated above", "Situated above another structure.", "Latin superior from superus 'upper'.", "Direction", [translation("es", "superior"), translation("pt-BR", "superior"), translation("en", "superior")]),
        adjective_term("inferior", "situated below", "Situated below another structure.", "Latin inferior from inferus 'lower'.", "Direction", [translation("es", "inferior"), translation("pt-BR", "inferior"), translation("en", "inferior")]),
        adjective_term("medialis", "toward the middle", "Situated nearer the median plane.", "Neo-Latin medialis from Latin medius 'middle'.", "Position", [translation("es", "medial"), translation("pt-BR", "medial"), translation("en", "medial")]),
        adjective_term("lateralis", "toward the side", "Situated farther from the median plane, toward the side.", "Neo-Latin lateralis from Latin latus/lateris 'side'.", "Position", [translation("es", "lateral"), translation("pt-BR", "lateral"), translation("en", "lateral")]),
        adjective_term("superficialis", "pertaining to the surface", "Situated near the surface of the body or organ.", "Neo-Latin superficialis from superficies 'surface'.", "Position", [translation("es", "superficial"), translation("pt-BR", "superficial"), translation("en", "superficial")]),
        adjective_term("profundus", "deep", "Situated farther from the surface.", "Latin profundus 'deep'.", "Position", [translation("es", "profundo"), translation("pt-BR", "profundo"), translation("en", "deep")]),
        adjective_term("proximalis", "nearer the point of origin", "Situated nearer the origin or attachment of a limb or structure.", "Neo-Latin proximalis from proximus 'nearest'.", "Direction", [translation("es", "proximal"), translation("pt-BR", "proximal"), translation("en", "proximal")]),
        adjective_term("distalis", "farther from the point of origin", "Situated farther from the origin or attachment of a limb or structure.", "Neo-Latin distalis from distantia/distare 'to stand apart'.", "Direction", [translation("es", "distal"), translation("pt-BR", "distal"), translation("en", "distal")]),
        adjective_term("deltoideus", "delta-shaped", "Describing a triangular form reminiscent of the Greek letter delta.", "Greek-derived Latinized adjective from delta + eidos 'form'.", "Shape", [translation("es", "deltoideo"), translation("pt-BR", "deltoide"), translation("en", "deltoid")]),
        adjective_term("trapezius", "table-like", "Classical name for the trapezius muscle, referring historically to a table-like geometric shape.", "Greek-derived Latinized term from trapezion 'little table'.", "Shape", [translation("es", "trapecio"), translation("pt-BR", "trapézio"), translation("en", "trapezius")]),
        adjective_term("piriformis", "pear-shaped", "Describing a pear-shaped structure or muscle.", "Latin pirum 'pear' + forma 'shape'.", "Shape", [translation("es", "piriforme"), translation("pt-BR", "piriforme"), translation("en", "piriform")]),
        adjective_term("longus", "long", "Describing a relatively long structure.", "Latin longus 'long'.", "Size", [translation("es", "largo"), translation("pt-BR", "longo"), translation("en", "long")]),
        adjective_term("brevis", "short", "Describing a relatively short structure.", "Latin brevis 'short'.", "Size", [translation("es", "corto"), translation("pt-BR", "curto"), translation("en", "short")]),
        adjective_term("maximus", "largest", "Describing the largest member of a named group.", "Latin maximus 'largest, greatest'.", "Size", [translation("es", "máximo"), translation("pt-BR", "máximo"), translation("en", "largest")]),
        adjective_term("minimus", "smallest", "Describing the smallest member of a named group.", "Latin minimus 'smallest'.", "Size", [translation("es", "mínimo"), translation("pt-BR", "mínimo"), translation("en", "smallest")]),
        adjective_term("major", "larger", "Describing the larger of two related structures.", "Latin maior/major 'greater'.", "Size", [translation("es", "mayor"), translation("pt-BR", "maior"), translation("en", "major")]),
        adjective_term("minor", "smaller", "Describing the smaller of two related structures.", "Latin minor 'smaller'.", "Size", [translation("es", "menor"), translation("pt-BR", "menor"), translation("en", "minor")]),
        adjective_term("rectus", "straight", "Describing a straight course, line, or muscle pull.", "Latin rectus 'straight'.", "Shape", [translation("es", "recto"), translation("pt-BR", "reto"), translation("en", "straight")]),
        adjective_term("obliquus", "slanting", "Describing an oblique or angled course.", "Latin obliquus 'slanting'.", "Direction", [translation("es", "oblicuo"), translation("pt-BR", "oblíquo"), translation("en", "oblique")]),
    ]
)


def pathology_term(name, literal, definition, etymology, mnemonic, translations, word_parts, category="Pathological process", subject="Pathology", system="General pathology", difficulty=2, origin="Greek-derived Latinized form", term_type="pathology"):
    return entry(
        name,
        literal,
        definition,
        etymology,
        f"The name reflects {category.lower()}.",
        mnemonic,
        subject,
        system,
        difficulty,
        origin,
        term_type,
        category,
        translations,
        word_parts,
        grammatical_class="noun",
        rapid_review=f"{name} is a core pathology term tied to {category.lower()}.",
    )


SEED_TERMS.extend(
    [
        pathology_term("osteoblast", "bone-forming germ cell", "Bone-forming cell responsible for producing osteoid.", "Greek osteon 'bone' + blastos 'germ or formative cell'.", "Blast builds bone.", [translation("es", "osteoblasto"), translation("pt-BR", "osteoblasto"), translation("en", "osteoblast")], [part("root", "oste-", "bone", "Greek"), part("suffix", "-blast", "formative cell", "Greek")], category="Function", subject="Histology", system="Skeletal system", term_type="cell type"),
        pathology_term("osteocyte", "bone cell", "Mature bone cell embedded in bone matrix.", "Greek osteon 'bone' + kytos 'cell'.", "Cyte is the mature resident cell.", [translation("es", "osteocito"), translation("pt-BR", "osteócito"), translation("en", "osteocyte")], [part("root", "oste-", "bone", "Greek"), part("suffix", "-cyte", "cell", "Greek")], category="Function", subject="Histology", system="Skeletal system", term_type="cell type"),
        pathology_term("chondrocyte", "cartilage cell", "Mature cell of cartilage tissue.", "Greek chondros 'cartilage' + kytos 'cell'.", "Chondrocyte lives in cartilage lacunae.", [translation("es", "condrocito"), translation("pt-BR", "condrócito"), translation("en", "chondrocyte")], [part("root", "chondr-", "cartilage", "Greek"), part("suffix", "-cyte", "cell", "Greek")], category="Function", subject="Histology", system="Skeletal system", term_type="cell type"),
        pathology_term("epithelium", "surface tissue", "Tissue covering surfaces and lining cavities.", "Greek epi- 'upon' + thele 'nipple'; the historical morphology underlies the modern tissue name.", "Epi sits upon a surface.", [translation("es", "epitelio"), translation("pt-BR", "epitélio"), translation("en", "epithelium")], [part("prefix", "epi-", "upon", "Greek"), part("root", "thelium", "covering tissue element", "Greek")], category="Position", subject="Histology", system="General histology", term_type="tissue"),
        pathology_term("endothelium", "inner lining tissue", "Simple squamous lining of blood vessels and lymphatic vessels.", "Greek endo- 'within' + thelium, a historical tissue-forming element.", "Endothelium lines vessels from within.", [translation("es", "endotelio"), translation("pt-BR", "endotélio"), translation("en", "endothelium")], [part("prefix", "endo-", "within", "Greek"), part("root", "thelium", "covering tissue element", "Greek")], category="Position", subject="Histology", system="Cardiovascular system", term_type="tissue"),
        pathology_term("mesothelium", "middle-layer lining tissue", "Epithelium lining serous membranes such as pleura, pericardium, and peritoneum.", "Greek meso- 'middle' + thelium.", "Meso lines the serous middle-style membranes.", [translation("es", "mesotelio"), translation("pt-BR", "mesotélio"), translation("en", "mesothelium")], [part("prefix", "meso-", "middle", "Greek"), part("root", "thelium", "covering tissue element", "Greek")], category="Position", subject="Histology", system="Serous membranes", term_type="tissue"),
        pathology_term("inflammation", "setting on fire", "Protective vascular and cellular response to injury or infection.", "From Latin inflammatio, linked to inflammare 'to set on fire'.", "Inflammation feels like classical heat and redness.", [translation("es", "inflamación"), translation("pt-BR", "inflamação"), translation("en", "inflammation")], whole("inflammation", "inflammatory process", "Latin"), category="Pathological process", origin="Latin", difficulty=1),
        pathology_term("necrosis", "state of death", "Pathological death of cells or tissue in a living organism.", "Greek nekrosis from nekros 'dead'.", "Necrosis = tissue death.", [translation("es", "necrosis"), translation("pt-BR", "necrose"), translation("en", "necrosis")], [part("root", "necr-", "death", "Greek"), part("suffix", "-osis", "state or process", "Greek")]),
        pathology_term("carcinoma", "crab-like tumor; epithelial cancer", "Malignant tumor arising from epithelial cells.", "Greek karkinos 'crab' gave rise to carcinoma for epithelial malignancy.", "Carcinoma is an epithelial malignancy.", [translation("es", "carcinoma"), translation("pt-BR", "carcinoma"), translation("en", "carcinoma")], [part("root", "carcin-", "cancer", "Greek"), part("suffix", "-oma", "tumor", "Greek")]),
        pathology_term("adenocarcinoma", "gland-forming carcinoma", "Malignant epithelial tumor with glandular differentiation.", "Greek adeno- 'gland' + carcinoma.", "Adenocarcinoma = glandular pattern plus carcinoma.", [translation("es", "adenocarcinoma"), translation("pt-BR", "adenocarcinoma"), translation("en", "adenocarcinoma")], [part("root", "adeno-", "gland", "Greek"), part("root", "carcin-", "cancer", "Greek"), part("suffix", "-oma", "tumor", "Greek")], difficulty=3),
        pathology_term("lymphoma", "lymph tissue tumor", "Malignant neoplasm of lymphoid tissue.", "Modern medical hybrid built from lymph- and Greek -oma.", "Lymphoma is a lymphoid tumor, not a carcinoma.", [translation("es", "linfoma"), translation("pt-BR", "linfoma"), translation("en", "lymphoma")], [part("root", "lymph-", "lymph", "Modern medical form"), part("suffix", "-oma", "tumor", "Greek")], origin="Hybrid modern medical form"),
        pathology_term("infarction", "stuffing in; tissue death from ischemia", "Area of ischemic necrosis caused by abrupt loss of blood supply.", "Modern medical noun from Latin infarctus/infarcire, 'to stuff or plug'.", "Infarction often means ischemic necrosis.", [translation("es", "infarto"), translation("pt-BR", "infarto"), translation("en", "infarction")], whole("infarction", "ischemic tissue death", "Latin"), category="Pathological process", origin="Latin", difficulty=2),
        pathology_term("hyperplasia", "over-formation", "Increase in the number of cells in a tissue or organ.", "Greek hyper- 'excessive' + plasis/plasia 'formation'.", "Hyperplasia = more cells.", [translation("es", "hiperplasia"), translation("pt-BR", "hiperplasia"), translation("en", "hyperplasia")], [part("prefix", "hyper-", "excessive", "Greek"), part("suffix", "-plasia", "formation or growth", "Greek")]),
        pathology_term("hypertrophy", "over-nourishment growth", "Increase in the size of cells resulting in enlargement of a tissue or organ.", "Greek hyper- 'excessive' + trophe 'nourishment'.", "Hypertrophy = bigger cells, not more cells.", [translation("es", "hipertrofia"), translation("pt-BR", "hipertrofia"), translation("en", "hypertrophy")], [part("prefix", "hyper-", "excessive", "Greek"), part("suffix", "-trophy", "nourishment and growth", "Greek")]),
        pathology_term("metaplasia", "change in formation", "Reversible replacement of one differentiated cell type by another adapted cell type.", "Greek meta- 'change' + plasia 'formation'.", "Meta means change, so metaplasia is a change of mature cell program.", [translation("es", "metaplasia"), translation("pt-BR", "metaplasia"), translation("en", "metaplasia")], [part("prefix", "meta-", "change", "Greek"), part("suffix", "-plasia", "formation or growth", "Greek")], difficulty=3),
        pathology_term("dysplasia", "bad or disordered formation", "Disordered epithelial growth with abnormal cellular maturation and architecture.", "Greek dys- 'bad, difficult, abnormal' + plasia 'formation'.", "Dysplasia = abnormal growth pattern.", [translation("es", "displasia"), translation("pt-BR", "displasia"), translation("en", "dysplasia")], [part("prefix", "dys-", "abnormal or disordered", "Greek"), part("suffix", "-plasia", "formation or growth", "Greek")], difficulty=3),
    ]
)


SEED_QUIZZES = [
    {
        "title": "Core Naming Logic",
        "subject": "Anatomy",
        "difficulty": 2,
        "description": "Basic distinctions between function, number, and position terms.",
        "questions": [
            {"question_type": "multiple_choice", "prompt": "Which term most directly means 'one that leads toward'?", "options": ["adductor", "abductor", "extensor", "flexor"], "correct_answer": {"value": "adductor"}, "term_slug": "adductor", "explanation": "Ad- means toward and duc- means lead."},
            {"question_type": "multiple_choice", "prompt": "Which descriptor signals a three-headed structure?", "options": ["biceps", "triceps", "quadriceps", "digastricus"], "correct_answer": {"value": "triceps"}, "term_slug": "triceps", "explanation": "Tri- marks three."},
            {"question_type": "multiple_choice", "prompt": "Which term means closer to the point of origin?", "options": ["distalis", "proximalis", "lateralis", "posterior"], "correct_answer": {"value": "proximalis"}, "term_slug": "proximalis", "explanation": "Proximal indicates nearness to the origin or attachment."},
            {"question_type": "multiple_choice", "prompt": "Which term names the inner lining of the heart?", "options": ["pericardium", "myocardium", "endocardium", "sternum"], "correct_answer": {"value": "endocardium"}, "term_slug": "endocardium", "explanation": "Endo- means within."},
        ],
    },
    {
        "title": "Pathology Roots Drill",
        "subject": "Pathology",
        "difficulty": 3,
        "description": "Greek-derived roots common in pathology.",
        "questions": [
            {"question_type": "multiple_choice", "prompt": "Which suffix most directly signals inflammation?", "options": ["-oma", "-itis", "-plasia", "-trophy"], "correct_answer": {"value": "-itis"}, "explanation": "-itis is the inflammatory suffix."},
            {"question_type": "multiple_choice", "prompt": "Hyperplasia means:", "options": ["larger cells", "more cells", "cell death", "abnormal gland"], "correct_answer": {"value": "more cells"}, "term_slug": "hyperplasia", "explanation": "Hyperplasia is an increase in cell number."},
            {"question_type": "multiple_choice", "prompt": "Hypertrophy differs from hyperplasia because hypertrophy refers mainly to:", "options": ["larger cell size", "more cell number", "necrosis", "inflammation"], "correct_answer": {"value": "larger cell size"}, "term_slug": "hypertrophy", "explanation": "Hypertrophy is an increase in cell size."},
            {"question_type": "multiple_choice", "prompt": "Adenocarcinoma is a carcinoma with what kind of differentiation?", "options": ["fibrous", "glandular", "cartilaginous", "muscular"], "correct_answer": {"value": "glandular"}, "term_slug": "adenocarcinoma", "explanation": "Adeno- means gland."},
        ],
    },
]


SEED_TERMS.extend(
    [
        entry("sternum", "breastbone", "Flat midline bone of the anterior thoracic wall.", "Greek sternon 'chest' entered scientific Latin as sternum.", "The name refers to the chest region.", "Sternum = anterior chest bone.", "Anatomy", "Skeletal system", 1, "Greek-derived Latinized form", "bone", "Anatomical region", [translation("es", "esternón"), translation("pt-BR", "esterno"), translation("en", "sternum")], whole("sternum", "breastbone", "Greek-derived Latinized form")),
        entry("clavicula", "little key", "Collarbone connecting the upper limb to the trunk.", "Latin clavicula is a diminutive of clavis, 'key', probably from the shape resemblance.", "The name refers to resemblance in shape.", "Clavicle looks like a small key.", "Anatomy", "Skeletal system", 1, "Latin", "bone", "Resemblance", [translation("es", "clavícula"), translation("pt-BR", "clavícula"), translation("en", "clavicle")], whole("clavicula", "little key", "Latin")),
        entry("scapula", "shoulder blade", "Flat bone of the posterior shoulder girdle.", "Classical Latin scapula for shoulder or shoulder blade.", "The traditional Latin word names the region directly.", "Scapula is the shoulder blade.", "Anatomy", "Skeletal system", 1, "Latin", "bone", "Anatomical region", [translation("es", "escápula"), translation("pt-BR", "escápula"), translation("en", "scapula")], whole("scapula", "shoulder blade", "Latin")),
        entry("patella", "little dish", "Sesamoid bone embedded in the quadriceps tendon at the knee.", "Latin patella is a diminutive meaning a small pan or dish.", "The name refers to resemblance in shape.", "Patella resembles a small dish at the knee.", "Anatomy", "Skeletal system", 1, "Latin", "bone", "Resemblance", [translation("es", "rótula"), translation("pt-BR", "patela"), translation("en", "patella")], whole("patella", "little dish", "Latin")),
        entry("cranium", "skull", "Bony case enclosing the brain.", "Greek kranion entered Latin scientific usage as cranium.", "The name refers directly to the skull.", "Cranium is the bony brain case.", "Anatomy", "Skeletal system", 1, "Greek-derived Latinized form", "bone", "Anatomical region", [translation("es", "cráneo"), translation("pt-BR", "crânio"), translation("en", "cranium")], whole("cranium", "skull", "Greek-derived Latinized form")),
        entry("vertebra", "joint or turning bone", "Individual bone of the vertebral column.", "Latin vertebra from vertere 'to turn', reflecting articulation and movement.", "The name refers to movement and articulation.", "Vertebrae belong to the turning, articulated spine.", "Anatomy", "Skeletal system", 2, "Latin", "bone", "Function", [translation("es", "vértebra"), translation("pt-BR", "vértebra"), translation("en", "vertebra")], whole("vertebra", "vertebra; turning bone", "Latin")),
        entry("costa", "rib", "Curved bone forming part of the thoracic cage.", "Classical Latin costa means rib or side.", "The name points to the body wall side.", "Costa is a rib on the thoracic side wall.", "Anatomy", "Skeletal system", 1, "Latin", "bone", "Anatomical region", [translation("es", "costilla"), translation("pt-BR", "costa"), translation("en", "rib")], whole("costa", "rib", "Latin")),
        entry("femur", "thigh bone", "Longest bone of the body, located in the thigh.", "Classical Latin femur means thigh; in anatomy it names the major bone of that region.", "The name points to the anatomical region.", "Femur is the bone of the thigh.", "Anatomy", "Skeletal system", 1, "Latin", "bone", "Anatomical region", [translation("es", "fémur"), translation("pt-BR", "fêmur"), translation("en", "femur")], whole("femur", "thigh bone", "Latin")),
        entry("tibia", "tibia; shin bone", "Medial bone of the leg.", "Classical Latin tibia names the shin bone and also a pipe or flute in broader Latin usage.", "The anatomical term directly names the bone.", "Tibia is the main medial leg bone.", "Anatomy", "Skeletal system", 1, "Latin", "bone", "Anatomical region", [translation("es", "tibia"), translation("pt-BR", "tíbia"), translation("en", "tibia")], whole("tibia", "shin bone", "Latin")),
        entry("fibula", "brooch; clasp", "Lateral bone of the leg.", "Latin fibula means brooch or clasp and became the anatomical name of the slender lateral leg bone.", "The name reflects resemblance to a clasp-like object in older metaphorical usage.", "Fibula is the slender lateral partner of the tibia.", "Anatomy", "Skeletal system", 2, "Latin", "bone", "Resemblance", [translation("es", "peroné"), translation("pt-BR", "fíbula"), translation("en", "fibula")], whole("fibula", "brooch; fibula", "Latin")),
    ]
)


SEED_TERMS.extend(
    [
        entry(
            "musculus biceps brachii",
            "two-headed muscle of the arm",
            "A muscle of the anterior compartment of the arm with two proximal heads and a distal tendon that inserts on the radial tuberosity. It flexes the elbow and powerfully supinates the forearm. The long head originates from the supraglenoid tubercle of the scapula and the short head from the coracoid process.",
            "Musculus is classical Latin for 'muscle'. Biceps is Latin for 'two-headed'. Brachii is the genitive singular of Latin brachium, 'arm', so the full phrase means 'the two-headed muscle of the arm'.",
            "The name combines the structure type, the number of heads, and the anatomical region expressed in the genitive.",
            "Musculus biceps brachii: two heads, arm region, elbow flexion and forearm supination.",
            "Anatomy",
            "Musculoskeletal system",
            2,
            "Latin",
            "muscle",
            "Number",
            [translation("es", "músculo bíceps braquial"), translation("pt-BR", "músculo bíceps braquial"), translation("en", "biceps brachii muscle")],
            [part("whole_lexical_unit", "musculus", "muscle", "Latin"), part("compound_element", "biceps", "two-headed", "Latin"), part("compound_element", "brachii", "of the arm", "Latin", "genitive singular")],
            grammatical_class="noun phrase",
            gender="masculine",
            declension="mixed phrase; brachii is genitive singular",
            exam_trap="Do not confuse brachii with brachialis. Brachii is a genitive form meaning 'of the arm', not a separate muscle name.",
            rapid_review="Biceps brachii = two-headed muscle of the arm; elbow flexion plus forearm supination.",
            relationships=[("musculus triceps brachii", "frequently_confused", "Both are arm muscles but with opposite compartment emphasis and different actions.")],
            examples=[
                example("Anatomy", "Functional usage", "The biceps brachii contributes strongly to elbow flexion and forearm supination.", "en"),
            ],
        ),
        entry("musculus triceps brachii", "three-headed muscle of the arm", "Posterior arm muscle with three heads that extends the elbow.", "Musculus is Latin 'muscle'; triceps is Latin 'three-headed'; brachii is genitive singular 'of the arm'.", "The name combines structure type, number of heads, and region.", "Triceps = three heads on the arm, mainly elbow extension.", "Anatomy", "Musculoskeletal system", 2, "Latin", "muscle", "Number", [translation("es", "músculo tríceps braquial"), translation("pt-BR", "músculo tríceps braquial"), translation("en", "triceps brachii muscle")], [part("whole_lexical_unit", "musculus", "muscle", "Latin"), part("compound_element", "triceps", "three-headed", "Latin"), part("compound_element", "brachii", "of the arm", "Latin", "genitive singular")], grammatical_class="noun phrase", gender="masculine", declension="mixed phrase"),
        entry("musculus quadriceps femoris", "four-headed muscle of the thigh", "Large anterior thigh muscle group with four heads that primarily extends the knee.", "Quadriceps is Latin 'four-headed'; femoris is the genitive singular of femur, 'of the thigh'.", "The name combines number of heads with the region in the genitive.", "Quadriceps femoris = four heads in the thigh, strong knee extension.", "Anatomy", "Musculoskeletal system", 2, "Latin", "muscle", "Number", [translation("es", "músculo cuádriceps femoral"), translation("pt-BR", "músculo quadríceps femoral"), translation("en", "quadriceps femoris muscle")], [part("whole_lexical_unit", "musculus", "muscle", "Latin"), part("compound_element", "quadriceps", "four-headed", "Latin"), part("compound_element", "femoris", "of the thigh", "Latin", "genitive singular")], grammatical_class="noun phrase", gender="masculine", declension="mixed phrase"),
        entry("musculus sternocleidomastoideus", "sternum-clavicle-mastoid muscle", "Paired neck muscle running from the sternum and clavicle to the mastoid process; it rotates the head and can flex the neck bilaterally.", "Greek-derived Latinized anatomical compound: sterno- from sternon 'sternum', cleido- from kleis 'clavicle', and mastoideus from mastoeides 'breast-shaped', referring to the mastoid process.", "The name lists the main bony attachments.", "Read it as a route: sternum + clavicle + mastoid.", "Anatomy", "Musculoskeletal system", 4, "Greek-derived Latinized form", "muscle", "Attachment", [translation("es", "músculo esternocleidomastoideo"), translation("pt-BR", "músculo esternocleidomastoideo"), translation("en", "sternocleidomastoid muscle")], [part("root", "sterno-", "sternum", "Greek"), part("root", "cleido-", "clavicle", "Greek"), part("root", "mastoid-", "mastoid process; breast-shaped", "Greek"), part("suffix", "-eus", "adjectival ending", "Latin")], grammatical_class="noun phrase"),
        entry("musculus gastrocnemius", "belly of the leg muscle", "Superficial calf muscle forming much of the posterior leg contour and contributing to plantar flexion.", "Greek-derived Latinized form from gaster 'belly' and kneme 'leg'.", "The name refers to the bulky belly-like contour of the calf.", "Gastrocnemius has the visible belly of the calf.", "Anatomy", "Musculoskeletal system", 3, "Greek-derived Latinized form", "muscle", "Shape", [translation("es", "músculo gastrocnemio"), translation("pt-BR", "músculo gastrocnêmio"), translation("en", "gastrocnemius muscle")], [part("root", "gastr-", "belly", "Greek"), part("root", "-cnemius", "leg", "Greek")], grammatical_class="noun phrase"),
        entry("musculus popliteus", "muscle of the ham of the knee", "Small posterior knee muscle that unlocks the knee at the start of flexion.", "Latin poples/poplitis means the back of the knee; popliteus is the related adjective and noun.", "The name points to the popliteal region.", "Popliteus belongs to the popliteal fossa behind the knee.", "Anatomy", "Musculoskeletal system", 3, "Latin", "muscle", "Anatomical region", [translation("es", "músculo poplíteo"), translation("pt-BR", "músculo poplíteo"), translation("en", "popliteus muscle")], whole("popliteus", "of the popliteal region", "Latin"), grammatical_class="noun phrase"),
        entry("musculus tibialis anterior", "anterior tibial muscle", "Anterior leg muscle that dorsiflexes and inverts the foot.", "Tibialis derives from Latin tibia; anterior indicates the front compartment.", "The name states the bone association and position.", "Tibialis anterior sits in front of the tibia.", "Anatomy", "Musculoskeletal system", 2, "Latin", "muscle", "Position", [translation("es", "músculo tibial anterior"), translation("pt-BR", "músculo tibial anterior"), translation("en", "tibialis anterior muscle")], [part("root", "tibialis", "related to the tibia", "Latin"), part("whole_lexical_unit", "anterior", "situated in front", "Latin")], grammatical_class="noun phrase"),
        entry("myocardium", "muscle of the heart", "Muscular middle layer of the heart wall responsible for contraction.", "Greek-derived Latinized form from myo- 'muscle' and kardia 'heart', adopted with Latin neuter ending -ium.", "The name identifies the tissue type and the organ.", "Myo + cardi = heart muscle.", "Anatomy", "Cardiovascular system", 2, "Greek-derived Latinized form", "layer", "Function", [translation("es", "miocardio"), translation("pt-BR", "miocárdio"), translation("en", "myocardium")], [part("root", "myo-", "muscle", "Greek"), part("root", "cardi-", "heart", "Greek"), part("suffix", "-ium", "Latinized anatomical ending", "Latin")], relationships=[("endocardium", "same_root", "Shares the cardiac root with a different positional prefix."), ("pericardium", "same_root", "Shares the cardiac root with a surrounding relation.")]),
        entry("endocardium", "within-heart layer", "Innermost lining layer of the heart.", "Greek-derived Latinized form from endo- 'within' and kardia 'heart', Latinized as an anatomical noun.", "The name refers to its inner position relative to the heart wall.", "Endo = inside, so endocardium is the inner cardiac lining.", "Histology", "Cardiovascular system", 2, "Greek-derived Latinized form", "layer", "Position", [translation("es", "endocardio"), translation("pt-BR", "endocárdio"), translation("en", "endocardium")], [part("prefix", "endo-", "within", "Greek"), part("root", "cardi-", "heart", "Greek"), part("suffix", "-ium", "Latinized anatomical ending", "Latin")]),
        entry("pericardium", "around-heart sac", "Fibroserous sac surrounding the heart.", "Greek-derived Latinized form from peri- 'around' and kardia 'heart', Latinized as an anatomical noun.", "The name refers to being around the heart.", "Peri = around, so pericardium surrounds the heart.", "Anatomy", "Cardiovascular system", 2, "Greek-derived Latinized form", "layer", "Position", [translation("es", "pericardio"), translation("pt-BR", "pericárdio"), translation("en", "pericardium")], [part("prefix", "peri-", "around", "Greek"), part("root", "cardi-", "heart", "Greek"), part("suffix", "-ium", "Latinized anatomical ending", "Latin")]),
    ]
)
