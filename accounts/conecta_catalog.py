"""
accounts/conecta_catalog.py
Catálogo canónico de Conecta FCM.
Única fuente de verdad para slugs, labels y años.
El backend valida SIEMPRE contra este módulo.
El frontend NUNCA envía label, year ni type — solo slugs.
"""

# ── Categorías institucionales ────────────────────────────────────────────────
INSTITUTIONAL_CATALOG = {
    'asuntos_estudiantiles':  'Asuntos Estudiantiles',
    'direccion_ensenanza':    'Dirección de Enseñanza',
    'secretaria_academica':   'Secretaría Académica',
    'tramites_inscripciones': 'Trámites e Inscripciones',
    'becas':                  'Becas',
    'biblioteca':             'Biblioteca',
    'extension':              'Extensión',
    'investigacion':          'Investigación',
    'bienestar_universitario':'Bienestar Universitario',
    'paros_suspensiones':     'Paros y Suspensiones',
    'cambios_aula':           'Cambios de Aula',
    'cambios_comision':       'Cambios de Comisión',
}

# ── Materias por año ──────────────────────────────────────────────────────────
SUBJECT_CATALOG = {
    1: [
        ('anatomia',                'Anatomía'),
        ('biologia',                'Biología'),
        ('citologia_histo',         'Citología, Histología y Embriología'),
        ('cs_sociales_medicina',    'Ciencias Sociales y Medicina'),
        ('cs_exactas',              'Ciencias Exactas'),
        ('informatica_basica',      'Informática Básica'),
        ('seminario_investigacion', 'Seminario en Investigación Científica'),
    ],
    2: [
        ('bioquimica_molecular',    'Bioquímica y Biología Molecular'),
        ('fisiologia_fisica',       'Fisiología y Física Biológica'),
        ('epidemiologia',           'Epidemiología'),
        ('psicologia_medica',       'Psicología Médica'),
        ('ecologia_humana',         'Ecología Humana y Promoción de la Salud'),
        ('historia_medicina',       'Historia de la Medicina'),
    ],
    3: [
        ('farmacologia_basica',     'Farmacología Básica'),
        ('microbiologia_para',      'Microbiología y Parasitología'),
        ('patologia',               'Patología'),
        ('semiologia',              'Semiología'),
        ('salud_comunitaria',       'Salud y Medicina Comunitaria'),
        ('genetica',                'Genética'),
        ('inmunologia',             'Inmunología'),
        ('ingles_medico',           'Inglés Médico'),
        ('informatica_medica',      'Informática Médica'),
        ('salud_ambiental',         'Salud Ambiental'),
        ('estadistica_salud',       'Estadística Aplicada a Ciencias de la Salud'),
        ('neuroanatomia_semi',      'Neuroanatomía Semiológica'),
    ],
    4: [
        ('medicina_interna_1',      'Medicina Interna I'),
        ('cirugia_1',               'Cirugía I'),
        ('farmacologia_aplicada',   'Farmacología Aplicada'),
        ('infectologia',            'Infectología'),
        ('neurologia',              'Neurología'),
        ('dermatologia',            'Dermatología'),
        ('oftalmologia',            'Oftalmología'),
        ('otorrinolaringologia',    'Otorrinolaringología'),
        ('ortopedia_traumato',      'Ortopedia y Traumatología'),
        ('urologia',                'Urología'),
        ('imagenes_1',              'Diagnóstico y Terapéutica por Imágenes I'),
        ('psiquiatria_1',           'Psiquiatría I'),
        ('salud_publica_1',         'Salud Pública I'),
        ('bioquimica_clinica_1',    'Bioquímica Clínica I'),
        ('filosofia_medica',        'Filosofía Médica'),
        ('nutricion_clinica',       'Nutrición Clínica'),
    ],
    5: [
        ('medicina_interna_2',      'Medicina Interna II'),
        ('cirugia_2',               'Cirugía II'),
        ('pediatria',               'Pediatría'),
        ('ginecologia',             'Ginecología'),
        ('obstetricia',             'Obstetricia'),
        ('psiquiatria_2',           'Psiquiatría II'),
        ('salud_publica_2',         'Salud Pública II'),
        ('imagenes_2',              'Diagnóstico y Terapéutica por Imágenes II'),
        ('deontologia_legal',       'Deontología y Medicina Legal'),
        ('terapia_intensiva',       'Terapia Intensiva'),
        ('toxicologia',             'Toxicología'),
        ('bioetica',                'Bioética'),
        ('bioquimica_clinica_2',    'Bioquímica Clínica II'),
        ('cirugia_torax',           'Cirugía de Tórax'),
        ('calidad_atencion',        'Calidad de la Atención Médica'),
        ('trasplante_organos',      'Trasplante de Órganos'),
        ('enf_poco_frecuentes',     'Enfermedades Poco Frecuentes'),
        ('discapacidad_intelectual','Discapacidad Intelectual'),
    ],
    6: [
        ('practica_final',          'Práctica Final Obligatoria'),
    ],
}

# ── Índices planos para validación rápida ─────────────────────────────────────
ALL_INST_SLUGS    = set(INSTITUTIONAL_CATALOG.keys())
ALL_SUBJECT_SLUGS = {slug for pairs in SUBJECT_CATALOG.values() for slug, _ in pairs}

# Mapa slug → (year, label) para resolución en el backend
SUBJECT_META = {}
for _yr, _pairs in SUBJECT_CATALOG.items():
    for _slug, _label in _pairs:
        SUBJECT_META[_slug] = {'year': _yr, 'label': _label}

# Payload serializable para el GET de la API
def catalog_for_api():
    """Devuelve el catálogo completo listo para serializar como JSON."""
    return {
        'institutional': INSTITUTIONAL_CATALOG,
        'subjects_by_year': {
            str(yr): [{'key': slug, 'label': label} for slug, label in pairs]
            for yr, pairs in SUBJECT_CATALOG.items()
        },
    }
