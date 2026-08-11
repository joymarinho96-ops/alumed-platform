/**
 * ALUMED OS — UNLP (Universidad Nacional de La Plata)
 * data.js — SOLO BANCO DE DATOS. Sin lógica de control.
 *
 * Esquema por pregunta:
 *  id, materia, tema, subtema, fuente, archivo, pagina,
 *  fragmentoApunte, tipoFuente, pergunta, opcoes[], correta,
 *  justificativa, joy{}
 *
 * joy{} adapta sus claves según la materia:
 *  Biología Celular  → queEs, dondeSe, estructura, funcion, mecanismo, siFalla, examen, trampa, porQueNoCorrectas[]
 *  Histología        → tejido, celulas, capasOrg, tincion, funcion, reconocer, examen, trampa, porQueNoCorrectas[]
 *  Embriología       → estructura, origenEmb, cuandoAparece, etapas, derivados, reconocer, examen, trampa, porQueNoCorrectas[]
 *  Anatomía          → queEs, ubicacion, partes, relaciones, irrigInnerv, reconocer, examen, trampa, porQueNoCorrectas[]
 *
 * Si algún campo no pudo ser verificado en los apuntes ALUMED,
 * dejar la clave vacía "" — app.js mostrará el placeholder.
 */

const bancoDados = {
  choices: [

    // ════════════════════════════════════════════════════════════
    //  BIOLOGÍA CELULAR Y MOLECULAR
    // ════════════════════════════════════════════════════════════
    {
      id: 1,
      materia:    "Biología Celular",
      tema:       "Retículo Endoplásmico",
      subtema:    "REL — Detoxificación hepática",
      fuente:     "Parcial Unificado UNLP — Biología Celular",
      archivo:    "CUESTIONES BIOLOGIA ANUAL.pdf",
      pagina:     "",
      tipoFuente: "Examen parcial",
      fragmentoApunte: "El Retículo Endoplásmico Liso (REL) es un sistema de membranas tubulares sin ribosomas. En hepatocitos contiene el sistema citocromo P450, que oxida fármacos lipófilos convirtiéndolos en metabolitos hidrosolubles excretables.",
      pergunta: "¿Cuál de las siguientes organelas participa activamente en la desintoxicación de fármacos y compuestos lipófilos en el hepatocito a través del sistema citocromo P450?",
      opcoes: [
        "A) Retículo Endoplásmico Rugoso (RER)",
        "B) Retículo Endoplásmico Liso (REL)",
        "C) Complejo de Golgi",
        "D) Lisosoma primario"
      ],
      correta: 1,
      justificativa: "El REL posee enzimas CYP450 especializadas en la biotransformación de compuestos lipófilos en el hepatocito.",
      joy: {
        queEs:      "El Retículo Endoplásmico Liso (REL) es una red membranosa tubular sin ribosomas, continua con el RER.",
        dondeSe:    "Abundante en hepatocitos, células musculares lisas/estriadas y corteza suprarrenal.",
        estructura: "Túbulos y cisternas membranosas sin ribosomas. Se conecta con el RER pero morfológicamente es más tubular y menos apilado.",
        funcion:    "① Detoxificación (CYP450) ② Síntesis de lípidos y esteroides ③ Almacenamiento/liberación de Ca²⁺ (músculo → retículo sarcoplásmico).",
        mecanismo:  "CYP450 realiza reacciones de oxidación (Fase I) convirtiendo fármacos lipófilos en metabolitos hidrosolubles → excrección biliar o renal.",
        siFalla:    "Acumulación de fármacos tóxicos, esteatosis hepática y estrés oxidativo celular.",
        examen:     "REL = sin ribosomas = lípidos + detox. Si aparece 'citocromo P450' o 'hepatocito' → la respuesta es REL.",
        trampa:     "El RER tiene ribosomas y sintetiza PROTEÍNAS. El REL no tiene ribosomas y maneja LÍPIDOS y DETOXIFICACIÓN. No los confundas.",
        porQueNoCorrectas: [
          "El RER tiene ribosomas en su superficie y sintetiza proteínas destinadas a secreción o membrana. No interviene en la detoxificación de fármacos lipófilos.",
          "CORRECTA — El REL contiene el sistema citocromo P450 en hepatocitos.",
          "El Complejo de Golgi modifica y empaqueta proteínas y lípidos ya sintetizados, pero no tiene función detoxificante directa.",
          "El lisosoma primario contiene hidrolasas ácidas para degradar macromoléculas. No biotransforma fármacos lipófilos."
        ]
      }
    },

    {
      id: 2,
      materia:    "Biología Celular",
      tema:       "Muerte Celular",
      subtema:    "Apoptosis — Vía intrínseca mitocondrial",
      fuente:     "Recuperatorio UNLP — Biología Celular",
      archivo:    "CUESTIONES BIOLOGIA ANUAL.pdf",
      pagina:     "",
      tipoFuente: "Examen recuperatorio",
      fragmentoApunte: "La vía intrínseca de apoptosis es activada por daño interno. Las proteínas Bax/Bak forman poros en la membrana mitocondrial externa → liberación de citocromo c al citosol → forma el apoptosoma con Apaf-1 y procaspasa 9 → activa caspasa 3 efectora.",
      pergunta: "Durante la apoptosis celular (vía intrínseca o mitocondrial), ¿qué evento desencadena directamente la formación del apoptosoma con Apaf-1 y procaspasa 9?",
      opcoes: [
        "A) Liberación de citocromo c al citosol tras la apertura de poros mitocondriales",
        "B) Fosforilación de la proteína Bad mediada por la kinasa Akt",
        "C) Activación de los receptores de muerte de superficie celular Fas/FasL",
        "D) Entrada masiva de iones Calcio al lumen del retículo endoplásmico"
      ],
      correta: 0,
      justificativa: "El citocromo c liberado al citosol se une a Apaf-1 y recluta la procaspasa 9 para formar el apoptosoma.",
      joy: {
        queEs:      "El apoptosoma es un complejo heptamérico en el citosol que inicia la cascada de caspasas en la apoptosis intrínseca.",
        dondeSe:    "Se ensambla en el citosol de la célula que recibe señales internas de daño (genotóxico, hipoxia, etc.).",
        estructura: "Citocromo c + Apaf-1 + procaspasa 9 → oligomerizan formando una 'rueda de la muerte' de 7 unidades.",
        funcion:    "Activar la caspasa 9 → que activa la caspasa 3 efectora → desmantelamiento ordenado y silencioso de la célula.",
        mecanismo:  "Daño → Bax/Bak abren poros mitocondriales → sale citocromo c → se une a Apaf-1 en el citosol → recluta procaspasa 9 → apoptosoma → caspasa 3 → apoptosis.",
        siFalla:    "Si Bcl-2 bloquea la apertura de poros → no sale citocromo c → no hay apoptosis → posible proliferación tumoral (como en linfoma folicular).",
        examen:     "Apoptosoma = cit c + Apaf-1 + procaspasa 9. Vía intrínseca = mitocondria. Vía extrínseca = receptores Fas → caspasa 8.",
        trampa:     "Fas/FasL activa la CASPASA 8 (vía extrínseca), no la 9. Akt fosforila Bad para INHIBIR la apoptosis. No confundas las dos vías.",
        porQueNoCorrectas: [
          "CORRECTA — El citocromo c liberado al citosol desencadena el ensamblado del apoptosoma.",
          "La fosforilación de Bad por Akt INACTIVA a Bad → Bad no puede liberar a Bcl-2 → se INHIBE la apoptosis. Es un mecanismo de sobrevida celular.",
          "Fas/FasL son receptores de muerte que activan la CASPASA 8 (vía extrínseca). No forman el apoptosoma con Apaf-1.",
          "La entrada de Ca²⁺ al lumen del RE no desencadena el apoptosoma. La SALIDA de Ca²⁺ puede señalizar estrés del RE, pero no es el desencadenante directo."
        ]
      }
    },

    // ════════════════════════════════════════════════════════════
    //  HISTOLOGÍA Y EMBRIOLOGÍA
    // ════════════════════════════════════════════════════════════
    {
      id: 3,
      materia:    "Histología y Embriología",
      tema:       "Histología General — Epitelios",
      subtema:    "Epitelio respiratorio traqueobronquial",
      fuente:     "Parcial 1 UNLP — Histología General",
      archivo:    "CUESTIONES HISTO.pdf",
      pagina:     "",
      tipoFuente: "Examen parcial",
      fragmentoApunte: "La mucosa traqueobronquial está revestida por epitelio seudoestratificado cilíndrico ciliado (epitelio respiratorio). Contiene: células ciliadas (mayoría), células caliciformes mucíparas, células basales (progenitoras) y células de Kulchitsky (neuroendocrinas). Todas tocan la membrana basal, pero no todas alcanzan la luz → aspecto pseudoestratificado.",
      pergunta: "¿Qué tipo de epitelio caracteriza la mucosa del conducto traqueobronquial en el sistema respiratorio?",
      opcoes: [
        "A) Epitelio cilíndrico simple con microvellosidades rígidas",
        "B) Epitelio plano estratificado no queratinizado",
        "C) Epitelio seudoestratificado cilíndrico ciliado con células caliciformes",
        "D) Epitelio polimorfo de transición (urotelio)"
      ],
      correta: 2,
      justificativa: "La vía aérea traqueobronquial tiene el epitelio respiratorio: seudoestratificado cilíndrico ciliado con células caliciformes.",
      joy: {
        tejido:    "Epitelio seudoestratificado cilíndrico ciliado — también llamado 'epitelio respiratorio'.",
        celulas:   "① Ciliadas (mayoritarias) ② Caliciformes (secretoras de moco) ③ Basales (progenitoras, tocan membrana basal) ④ Kulchitsky (neuroendocrinas).",
        capasOrg:  "Una sola capa celular, pero los núcleos se ubican a distintas alturas. TODAS las células tocan la membrana basal → PSEUDO-estratificado.",
        tincion:   "Con H-E: núcleos escalonados en altura + borde apical rosado con cilias. Caliciformes aparecen pálidas por el moco (PAS+ en técnica especial).",
        funcion:   "Cilias baten en dirección cefálica → escalera mucociliar que arrastra polvo/microbios hacia faringe. Caliciformes secretan el moco que atrapa partículas.",
        reconocer: "En la lámina: buscá borde apical ciliado + núcleos escalonados. Si ves varias capas reales de células → es estratificado (no seudo). Las caliciformes se ven pálidas entre las ciliadas.",
        examen:    "Tráquea/bronquios = seudoestratificado ciliado. Alvéolo = simple plano. Laringe = plano estratificado. Vejiga = transición (urotelio).",
        trampa:    "'Seudoestratificado' NO significa muchas capas. Es UNA sola capa con núcleos en distintas alturas. Muchos marcan 'plano estratificado' porque confunden el aspecto escalonado.",
        porQueNoCorrectas: [
          "El cilíndrico simple con microvellosidades rígidas (borde en cepillo) reviste el intestino delgado. No tiene cilias y no es respiratorio.",
          "El plano estratificado no queratinizado reviste boca, faringe, esófago y vagina. No tiene cilias ni caliciformes.",
          "CORRECTA — epitelio seudoestratificado cilíndrico ciliado con caliciformes = mucosa traqueobronquial.",
          "El urotelio (transición) reviste vejiga y uréteres. Sus células 'en sombrilla' cambian forma según la distensión. No tiene cilias."
        ]
      }
    },

    {
      id: 4,
      materia:    "Histología y Embriología",
      tema:       "Embriología — Semana 3",
      subtema:    "Gastrulación — Inducción neural por notocorda",
      fuente:     "Parcial 2025 Bloque II UNLP — Embriología",
      archivo:    "SIMULACRO HyE.pdf",
      pagina:     "",
      tipoFuente: "Simulacro",
      fragmentoApunte: "Semana 3: la notocorda (mesodermo axial) actúa como organizador primario. Secreta Noggin, Chordin y Follistatina, que inhiben BMP-4 en el ectodermo suprayacente → ectodermo se convierte en neuroectodermo (placa neural) → inducción neural primaria.",
      pergunta: "Durante la 3.ª semana del desarrollo embrionario (gastrulación), ¿qué estructura señalizadora induce la diferenciación de la placa neural a partir del ectodermo suprayacente?",
      opcoes: [
        "A) La alantoides y el conducto onfalomesentérico",
        "B) La notocorda axial y el mesodermo paraxial",
        "C) El saco vitelino secundario",
        "D) Las crestas gonadales embrionarias"
      ],
      correta: 1,
      justificativa: "La notocorda secretaa Noggin/Chordin que inhiben BMP-4, transformando el ectodermo en neuroectodermo (placa neural).",
      joy: {
        estructura:     "La notocorda es un bastón mesodermal axial transitorio que define el eje antero-posterior del embrión. En el adulto queda como el núcleo pulposo del disco intervertebral.",
        origenEmb:      "Deriva del mesodermo axial que migra a través del nodo primitivo (nodo de Hensen) durante la gastrulación en la 3ª semana.",
        cuandoAparece:  "Semana 3. Aparece en la línea media del disco embrionario entre el ectodermo y el endodermo.",
        etapas:         "① Gastrulación (sem 3) → ② Notocorda en línea media → ③ Secreta Noggin/Chordin → ④ Inhibe BMP-4 del ectodermo → ⑤ Ectodermo → placa neural → ⑥ Placa neural se cierra en tubo neural (sem 4).",
        derivados:      "La notocorda desaparece casi por completo. Queda el núcleo pulposo (adulto). Su influencia da origen al tubo neural (SNC y SNP).",
        reconocer:      "En esquema de semana 3: bastón en la línea media, dorsal al endodermo y ventral al ectodermo. El ectodermo suprayacente comienza a engrosarse → placa neural.",
        examen:         "Notocorda = organizador primario = induce placa neural. Factores: Noggin, Chordin, Follistatina (inhiben BMP-4). Semana 3 = gastrulación.",
        trampa:         "La alantoides participa en hematopoyesis temprana y formación de vejiga, NO en inducción neural. El saco vitelino aporta nutrición y células germinativas. Las crestas gonadales son de semanas 5-6.",
        porQueNoCorrectas: [
          "La alantoides es un divertículo del saco vitelino involucrado en hematopoyesis y vejiga. El conducto onfalomesentérico conecta intestino y saco vitelino. Ninguno induce la placa neural.",
          "CORRECTA — la notocorda y el mesodermo paraxial inducen la formación de la placa neural inhibiendo BMP-4.",
          "El saco vitelino secundario aporta nutrición provisional y es el origen de las células germinativas primordiales. No tiene función de inducción neural.",
          "Las crestas gonadales se forman en semanas 5-6 y son el primordio de las gónadas. No intervienen en la gastrulación ni en la inducción neural."
        ]
      }
    },

    // ════════════════════════════════════════════════════════════
    //  ANATOMÍA CÁTEDRA A
    // ════════════════════════════════════════════════════════════
    {
      id: 5,
      materia:    "Anatomía Cátedra A",
      tema:       "Miembro Superior — Fosa Cubital",
      subtema:    "Paquete vasculonervioso de la fosa cubital",
      fuente:     "Parcial Oficial Cátedra A — UNLP",
      archivo:    "UNION ANATO C.pdf",
      pagina:     "",
      tipoFuente: "Examen parcial",
      fragmentoApunte: "Fosa cubital: región triangular anterior del codo. Contenido de lateral a medial: nervio radial, tendón del bíceps braquial, arteria braquial (con venas satélites), nervio mediano. Mnemotécnico: N-T-A-N (Nervio-Tendón-Arteria-Nervio).",
      pergunta: "En la región de la fosa cubital (sangría del codo), ¿cuál es la disposición anatómica del paquete vasculonervioso braquial respecto al tendón del músculo bíceps braquial?",
      opcoes: [
        "A) Lateral al tendón del bíceps: Nervio mediano y arteria radial",
        "B) Medial al tendón del bíceps: Arteria braquial y nervio mediano",
        "C) Posterior al músculo supinador largo: Nervio cubital",
        "D) Anterior a la aponeurosis bicipital: Arteria interósea común"
      ],
      correta: 1,
      justificativa: "El paquete vasculonervioso de la fosa cubital (arteria braquial + nervio mediano) es medial al tendón del bíceps braquial.",
      joy: {
        queEs:       "La fosa cubital es la región triangular anterior del codo. Es el lugar de venopunción y auscultación de la presión arterial braquial.",
        ubicacion:   "Cara anterior del codo. Límites: supero-lateral = braquiorradial; supero-medial = pronador redondo; techo = aponeurosis bicipital (lacertus fibrosus).",
        partes:      "De lateral a medial: Nervio radial — Tendón bíceps — Arteria braquial (con venas satélites) — Nervio mediano. Regla: N-T-A-N.",
        relaciones:  "La aponeurosis bicipital (lacertus fibrosus) cubre el paquete profundo. Superficialmente circulan la vena cefálica (lateral) y basílica (medial), usadas para venopunción.",
        irrigInnerv: "Arteria braquial = continuación de la axilar; se bifurca en la fosa en arteria radial y cubital. Nervio mediano = plexo braquial C6-T1.",
        reconocer:   "En el preparado cadavérico: identificar el tendón del bíceps (central, palpable). MEDIAL al tendón = arteria braquial (pulsátil) y nervio mediano (aplanado, blanquecino).",
        examen:      "Medial al tendón bíceps = arteria braquial + nervio mediano. Lateral = nervio radial. Superficial = venas cefálica y basílica.",
        trampa:      "El nervio CUBITAL NO pasa por la fosa cubital. Rodea el epicóndilo medial (hueso de la risa) y va directamente al antebrazo posterior.",
        porQueNoCorrectas: [
          "El nervio mediano y la arteria braquial son MEDIALES al tendón, no laterales. Lateralmente va el nervio radial.",
          "CORRECTA — arteria braquial y nervio mediano son mediales al tendón del bíceps.",
          "El nervio cubital no atraviesa la fosa cubital. Pasa por el canal retro-epicondíleo medial (epitroclear).",
          "La arteria interósea común es rama de la arteria cubital y se origina en el antebrazo, distal a la fosa cubital."
        ]
      }
    },

    // ════════════════════════════════════════════════════════════
    //  ANATOMÍA CÁTEDRA B
    // ════════════════════════════════════════════════════════════
    {
      id: 6,
      materia:    "Anatomía Cátedra B",
      tema:       "Corazón — Ventrículo Derecho",
      subtema:    "Cresta supraventricular y porciones del VD",
      fuente:     "Simulacro Cátedra B — UNLP",
      archivo:    "UNION ANATO C.pdf",
      pagina:     "",
      tipoFuente: "Simulacro",
      fragmentoApunte: "El ventrículo derecho tiene dos porciones: vía de entrada (trabeculada, con músculos papilares y trabéculas carnosas) y vía de salida (infundíbulo o cono arterioso, paredes lisas). La cresta supraventricular (espolón de Wolff) y la trabécula septomarginal (banda moderadora) separan ambas porciones.",
      pergunta: "En el corazón humano, ¿qué estructura anatómica limita la vía de entrada (porción trabeculada) de la vía de salida (infundíbulo o cono arterioso) dentro del ventrículo derecho?",
      opcoes: [
        "A) La cresta supraventricular (espolón de Wolff) y la trabécula septomarginal",
        "B) La válvula de Eustaquio de la vena cava inferior",
        "C) La fosa oval del tabique interauricular",
        "D) Las valvas semilunares de la válvula aórtica"
      ],
      correta: 0,
      justificativa: "La cresta supraventricular y la trabécula septomarginal separan la porción trabeculada del cono arterioso en el VD.",
      joy: {
        queEs:       "La cresta supraventricular (espolón de Wolff) es un reborde muscular interno del VD que divide sus dos porciones funcionales.",
        ubicacion:   "Cara interna del ventrículo derecho, entre la válvula tricúspide (entrada) y la válvula pulmonar (salida).",
        partes:      "① Vía de entrada: trabeculada, con trabéculas carnosas y músculos papilares que sostienen la tricúspide. ② Infundíbulo (cono): paredes lisas, conduce al tronco pulmonar.",
        relaciones:  "La trabécula septomarginal (banda moderadora) conecta tabique interventricular con el músculo papilar anterior. Conduce la rama derecha del fascículo de His.",
        irrigInnerv: "VD irrigado principalmente por la arteria coronaria derecha. La banda moderadora lleva el sistema de conducción (rama derecha del fascículo de His).",
        reconocer:   "En preparado cardíaco abierto por cara anterior: la cresta supraventricular aparece como reborde muscular en 'C'. La banda moderadora es una cuerda muscular que cruza de tabique a pared libre.",
        examen:      "Cresta supraventricular = separa entrada (trabeculada) de salida (infundíbulo) del VD. Banda moderadora = conduce rama derecha de His.",
        trampa:      "Válvula de Eustaquio → aurícula derecha (no VD). Fosa oval → tabique INTERauricular (no interventricular). Valvas semilunares aórticas → VI, no VD.",
        porQueNoCorrectas: [
          "CORRECTA — cresta supraventricular + trabécula septomarginal separan las dos porciones del VD.",
          "La válvula de Eustaquio es un repliegue en la desembocadura de la vena cava inferior en la AURÍCULA derecha. No está en el VD.",
          "La fosa oval está en el tabique INTERauricular (entre aurículas). No tiene relación con el ventrículo derecho.",
          "Las valvas semilunares aórticas están en la salida del VENTRÍCULO IZQUIERDO. El VD tiene la válvula pulmonar."
        ]
      }
    },

    // ════════════════════════════════════════════════════════════
    //  ANATOMÍA CÁTEDRA C
    // ════════════════════════════════════════════════════════════
    {
      id: 7,
      materia:    "Anatomía Cátedra C",
      tema:       "Corazón — Coronarias",
      subtema:    "Arteria interventricular anterior (DA) y vena cardíaca magna",
      fuente:     "Examen Unificado Cátedra C — UNLP",
      archivo:    "UNION ANATO C.pdf",
      pagina:     "",
      tipoFuente: "Examen parcial",
      fragmentoApunte: "La arteria coronaria izquierda emerge del seno aórtico izquierdo y se bifurca en: Rama interventricular anterior (RIVA/DA) que discurre por el surco interventricular anterior junto a la vena cardíaca magna, y Rama circunfleja que rodea el surco coronario izquierdo.",
      pergunta: "¿Qué vaso sanguíneo arterial discurre por el surco interventricular anterior acompañado por la vena cardíaca magna (vena coronaria mayor)?",
      opcoes: [
        "A) Arteria coronaria derecha troncal",
        "B) Rama interventricular anterior (descendente anterior) de la arteria coronaria izquierda",
        "C) Arteria circunfleja izquierda",
        "D) Rama marginal derecha de la coronaria derecha"
      ],
      correta: 1,
      justificativa: "La RIVA (DA) desciende por el surco interventricular anterior acompañada por la vena cardíaca magna.",
      joy: {
        queEs:       "La Rama Interventricular Anterior (RIVA) o Descendente Anterior (DA) es la arteria coronaria más importante: irriga la mayor parte del tabique y cara anterior del VI.",
        ubicacion:   "Corre por el surco interventricular anterior, desde la bifurcación del tronco coronario izquierdo hasta el ápex cardíaco.",
        partes:      "Tronco coronario izquierdo → bifurcación: ① RIVA (surco interventricular anterior) ② Circunfleja (surco coronario izquierdo).",
        relaciones:  "La vena cardíaca magna la acompaña en el surco anterior → drena al seno coronario. En el surco interventricular POSTERIOR va la coronaria derecha con la vena interventricular posterior.",
        irrigInnerv: "DA irriga: 2/3 anteriores del tabique interventricular + pared anterior del VI + cara anterior del VD. Oclusión → IAM anterior masivo ('widow maker').",
        reconocer:   "En preparado cardíaco cara anterior: la DA desciende rectamente en la línea del surco interventricular anterior. La vena cardíaca magna corre paralela a ella.",
        examen:      "Surco interventricular ANTERIOR = DA + vena cardíaca magna. Surco interventricular POSTERIOR = coronaria derecha + vena interventricular posterior.",
        trampa:      "La circunfleja va por el SURCO AURICULOVENTRICULAR izquierdo (lateral/posterior), NO por el surco interventricular. No la confundas con la DA.",
        porQueNoCorrectas: [
          "La coronaria derecha troncal discurre por el surco auriculoventricular DERECHO. No pasa por el surco interventricular anterior.",
          "CORRECTA — la DA desciende por el surco interventricular anterior con la vena cardíaca magna.",
          "La circunfleja izquierda rodea el surco auriculoventricular izquierdo (lateral y posterior). No atraviesa el surco interventricular anterior.",
          "La rama marginal derecha surge de la coronaria derecha y corre por el borde derecho del corazón. No está en el surco interventricular anterior."
        ]
      }
    },

    {
      id: 8,
      materia:    "Anatomía Cátedra C",
      tema:       "Neuroanatomía — Nervios Craneales",
      subtema:    "NC V — Ramo mandibular motor (músculos masticadores)",
      fuente:     "Repaso de Neuroanatomía Cátedra C — UNLP",
      archivo:    "UNION ANATO C.pdf",
      pagina:     "",
      tipoFuente: "Material de repaso",
      fragmentoApunte: "El ramo mandibular (V3) del nervio trigémino es el único ramo mixto. Contiene fibras motoras (eferentes viscerales especiales, EVE) para la musculatura del 1° arco faríngeo: temporal, masetero, pterigoideo lateral y medial, milohioideo, vientre anterior del digástrico, tensor del tímpano y tensor del velo del paladar.",
      pergunta: "¿Qué ramo nervioso proporciona la inervación motora para los 4 músculos principales de la masticación (temporal, masetero, pterigoideo lateral y pterigoideo medial)?",
      opcoes: [
        "A) Nervio Facial (NC VII)",
        "B) Ramo Mandibular del Nervio Trigémino (NC V3)",
        "C) Nervio Glosofaríngeo (NC IX)",
        "D) Nervio Hipogloso (NC XII)"
      ],
      correta: 1,
      justificativa: "El ramo V3 (mandibular) del trigémino provee fibras motoras EVE para los músculos masticadores derivados del 1° arco faríngeo.",
      joy: {
        queEs:       "El ramo mandibular (V3) es el único ramo mixto del trigémino: lleva sensibilidad del tercio inferior de la cara Y motricidad para los músculos masticadores.",
        ubicacion:   "Sale por el foramen oval de la base del cráneo hacia la fosa infratemporal. Se divide en ramos anteriores (principalmente motores) y posteriores (principalmente sensitivos).",
        partes:      "Músculos inervados por V3: ① Temporal ② Masetero ③ Pterigoideo lateral ④ Pterigoideo medial. También: milohioideo, vientre ant. digástrico, tensor tímpano, tensor velo del paladar.",
        relaciones:  "V3 sale junto a V1 (oftálmico, fisura orbitaria superior) y V2 (maxilar, foramen redondo) desde el ganglio trigeminal de Gasser.",
        irrigInnerv: "Los músculos masticadores son derivados del 1° arco faríngeo (cartílago de Meckel). Su inervación motora son fibras EVE (eferentes viscerales especiales).",
        reconocer:   "Regla de arcos faríngeos: 1° arco → músculo masticador → V3. Si es músculo de la expresión → VII. Si es lengua → XII. Si es faringe/esternocleidomastoideo/trapecio → IX/X/XI.",
        examen:      "NC VII = EXPRESIÓN facial. NC V3 = MASTICACIÓN. NC XII = LENGUA (intrínseco/extrínseco). Si el enunciado dice masticar → V3.",
        trampa:      "El facial (VII) inerva los músculos de la expresión (fruncir, cerrar ojos, sonreír). Muchos confunden 'mandibular = mandíbula = hipogloso'. El hipogloso inerva la LENGUA, no los maseteros.",
        porQueNoCorrectas: [
          "El NC VII (facial) inerva los músculos de la EXPRESIÓN facial (frontalis, orbicularis oculi/oris, buccinador, platisma). No inerva los masticadores.",
          "CORRECTA — V3 (mandibular del trigémino) provee la inervación motora de los 4 músculos masticadores.",
          "El NC IX (glosofaríngeo) inerva el músculo estilofaríngeo y provee sensibilidad a la faringe y al 1/3 posterior de la lengua. No inerva masticadores.",
          "El NC XII (hipogloso) inerva exclusivamente los músculos intrínsecos y extrínsecos de la LENGUA. No tiene relación con la masticación."
        ]
      }
    }
  ],

  // ════════════════════════════════════════════════════════════
  //  PINCHES
  // ════════════════════════════════════════════════════════════
  pinches: [
    {
      id: 1,
      materia: "Anatomía Cátedra C",
      fuente:  "Pinche de Preparado Anatómico — Cátedra C UNLP",
      imagem:  "https://images.unsplash.com/photo-1559757175-5700dde675bc?auto=format&fit=crop&w=600&q=80",
      pergunta: "Identifique la estructura vascular señalada en el preparado cadavérico:",
      respostasAceitas: ["arteria subclavia", "a. subclavia", "subclavia", "arteria subclavia izquierda", "arteria subclavia derecha"]
    },
    {
      id: 2,
      materia: "Histología y Embriología",
      fuente:  "Corte Histológico de Microscopía — UNLP",
      imagem:  "https://images.unsplash.com/photo-1579154204601-01588f351e67?auto=format&fit=crop&w=600&q=80",
      pergunta: "Identifique el componente del corpúsculo renal señalado en la muestra:",
      respostasAceitas: ["glomerulo", "glomerulo renal", "glomérulo", "glomérulo renal", "ovillo glomerular"]
    },
    {
      id: 3,
      materia: "Anatomía Cátedra A",
      fuente:  "Maqueta Anatómica de Tórax — Cátedra A UNLP",
      imagem:  "https://images.unsplash.com/photo-1530210124550-912dc1381cb8?auto=format&fit=crop&w=600&q=80",
      pergunta: "Identifique el gran vaso arterial que emerge del ventrículo izquierdo:",
      respostasAceitas: ["aorta", "arteria aorta", "aorta ascendente", "a. aorta", "tronco de la aorta"]
    }
  ],

  // ════════════════════════════════════════════════════════════
  //  ORALES / BOLILLAS
  // ════════════════════════════════════════════════════════════
  orales: [
    {
      id: 1,
      materia: "Histología y Embriología",
      fuente:  "Bolillero de Examen Presencial UNLP",
      bolilla: "Bolilla 5: Desarrollo Cardíaco y Circulación Fetal",
      casoClinico: "Paciente recién nacido con soplo holo-sistólico y leve cianosis diferencial. Ecocardiograma: comunicación interauricular por falla del desarrollo septal.",
      checklist: [
        "1. Describir la secuencia de tabicamiento auricular: Septum primum, ostium primum, ostium secundum y septum secundum.",
        "2. Explicar el mecanismo fisiológico del cierre del foramen oval en los primeros minutos postnacimiento.",
        "3. Comparar las 3 derivaciones vasculares fetales: conducto venoso de Arancio, foramen oval y conducto arterioso de Botal."
      ]
    },
    {
      id: 2,
      materia: "Biología Celular",
      fuente:  "Bolillero de Biología Celular y Molecular UNLP",
      bolilla: "Bolilla 3: Tráfico de Endomembranas y Transporte Vesicular",
      casoClinico: "Línea celular mutante con acumulación anómala de glicoproteínas inactivas en el lumen del RER por bloqueo del transporte anterógrado.",
      checklist: [
        "1. Diferenciar las cubiertas vesiculares: COP II (anterógrado RER→Golgi), COP I (retrógrado) y Clatrina.",
        "2. Detallar el ciclo de las Rab GTPasas y el acoplamiento mediado por v-SNARE y t-SNARE.",
        "3. Describir las modificaciones postraduccionales de N-glicosilación y O-glicosilación en el aparato de Golgi."
      ]
    },
    {
      id: 3,
      materia: "Anatomía Cátedra C",
      fuente:  "Bolillero de Neuroanatomía — Cátedra C UNLP",
      bolilla: "Bolilla 12: Irrigación Encefálica y Círculo Arterial de Willis",
      casoClinico: "Paciente masculino de 64 años con pérdida súbita de fuerza en miembro superior e inferior derechos y afasia motora de Broca.",
      checklist: [
        "1. Describir el origen del sistema carotídeo interno y del sistema vertebrobasilar.",
        "2. Esquematizar la constitución anatómica del Polígono Arterial de Willis y sus arterias comunicantes.",
        "3. Detallar el territorio de irrigación de la Arteria Cerebral Media (Silviana)."
      ]
    }
  ]
};

// ════════════════════════════════════════════════════════════
//  CALENDARIO DE PARCIALES — 1er Año UNLP 2026
//  Datos centralizados. Joyce puede actualizar hora, modalidad,
//  aula, estado y observacion sin tocar la lógica.
//  Días verificados con Python datetime para 2026.
// ════════════════════════════════════════════════════════════
const parciales = [

  // ── BIOLOGÍA ──────────────────────────────────────────────
  {
    id:             "bio-p1",
    materia:        "Biología",
    colorKey:       "bio",
    instancia:      "1.º Parcial",
    esPeriodo:      false,
    esEstimado:     true,
    editable:       false,
    // Día verificado: sábado 20 de junio de 2026 ✅
    fechaInicio:    "2026-06-20",
    fechaFin:       null,
    hora:           null,
    modalidad:      null,
    aula:           null,
    estado:         "estimada",
    textoPublico:   "Primera fecha probable a partir del sábado 20 de junio. No es fecha definitiva: es el inicio probable del período de evaluación.",
    observacion:    "Fecha estimada — sujeta a confirmación."
  },

  // ── ANATOMÍA A ────────────────────────────────────────────
  {
    id:             "anato-a-p1",
    materia:        "Anatomía A",
    colorKey:       "anatoa",
    instancia:      "1.º Parcial",
    esPeriodo:      false,
    esEstimado:     false,
    editable:       false,
    // Día verificado: lunes 11 de mayo de 2026 ✅
    fechaInicio:    "2026-05-11",
    fechaFin:       null,
    hora:           null,
    modalidad:      null,
    aula:           null,
    estado:         "pendiente",
    textoPublico:   null,
    observacion:    "Confirmación pendiente de horario y modalidad."
  },

  // ── ANATOMÍA B ────────────────────────────────────────────
  // Sin día exacto confirmado. Rango estimado: fines de mayo → mediados de junio.
  {
    id:             "anato-b-p1",
    materia:        "Anatomía B",
    colorKey:       "anatob",
    instancia:      "1.º Parcial",
    esPeriodo:      true,
    esEstimado:     true,
    editable:       false,
    // Rango estimado — NO inventar un día exacto. Sábado no confirmado.
    fechaInicio:    "2026-05-25",
    fechaFin:       "2026-06-15",
    hora:           null,
    modalidad:      null,
    aula:           null,
    estado:         "estimada",
    textoPublico:   "Fines de mayo → mediados de junio. No existe un día exacto confirmado para este período.",
    observacion:    "Fecha estimada — sujeta a confirmación. No asignar fecha puntual."
  },

  // ── ANATOMÍA C ────────────────────────────────────────────
  {
    id:             "anato-c-p1",
    materia:        "Anatomía C",
    colorKey:       "anatoc",
    instancia:      "1.º Parcial",
    esPeriodo:      false,
    esEstimado:     false,
    editable:       false,
    // Día verificado: sábado 11 de julio de 2026 ✅
    fechaInicio:    "2026-07-11",
    fechaFin:       null,
    hora:           null,
    modalidad:      null,
    aula:           null,
    estado:         "confirmada",
    textoPublico:   null,
    observacion:    ""
  },

  // ── HISTOLOGÍA Y EMBRIOLOGÍA — TURNO 1 ───────────────────
  // Días verificados: lunes 6 → viernes 10 de julio de 2026 ✅
  {
    id:             "hye-p1-t1",
    materia:        "Histología y Embriología",
    colorKey:       "hye",
    instancia:      "1.º Parcial — Turno 1",
    esPeriodo:      true,
    esEstimado:     false,
    editable:       true,
    fechaInicio:    "2026-07-06",
    fechaFin:       "2026-07-10",
    hora:           null,
    modalidad:      null,
    aula:           null,
    estado:         "periodo-informado",
    textoPublico:   "Lunes 6 al viernes 10 de julio. Tu día y horario específico dentro de este período están por confirmar.",
    observacion:    "Asignación individual pendiente. Cargá tu fecha cuando te la informen."
  },

  // ── HISTOLOGÍA Y EMBRIOLOGÍA — TURNO 2 ───────────────────
  // Días verificados: lunes 13 → viernes 17 de julio de 2026 ✅
  {
    id:             "hye-p1-t2",
    materia:        "Histología y Embriología",
    colorKey:       "hye",
    instancia:      "1.º Parcial — Turno 2",
    esPeriodo:      true,
    esEstimado:     false,
    editable:       true,
    fechaInicio:    "2026-07-13",
    fechaFin:       "2026-07-17",
    hora:           null,
    modalidad:      null,
    aula:           null,
    estado:         "periodo-informado",
    textoPublico:   "Lunes 13 al viernes 17 de julio. Tu día y horario específico dentro de este período están por confirmar.",
    observacion:    "Asignación individual pendiente. Cargá tu fecha cuando te la informen."
  },

  // ── HISTOLOGÍA Y EMBRIOLOGÍA — TURNO 3 ───────────────────
  // Días verificados: lunes 3 → viernes 7 de agosto de 2026 ✅
  {
    id:             "hye-p1-t3",
    materia:        "Histología y Embriología",
    colorKey:       "hye",
    instancia:      "1.º Parcial — Turno 3",
    esPeriodo:      true,
    esEstimado:     false,
    editable:       true,
    fechaInicio:    "2026-08-03",
    fechaFin:       "2026-08-07",
    hora:           null,
    modalidad:      null,
    aula:           null,
    estado:         "periodo-informado",
    textoPublico:   "Lunes 3 al viernes 7 de agosto. Tu día y horario específico dentro de este período están por confirmar.",
    observacion:    "Asignación individual pendiente. Cargá tu fecha cuando te la informen."
  },

  // ── HISTOLOGÍA Y EMBRIOLOGÍA — TURNO 4 ───────────────────
  // Días verificados: lunes 10 → viernes 14 de agosto de 2026 ✅
  {
    id:             "hye-p1-t4",
    materia:        "Histología y Embriología",
    colorKey:       "hye",
    instancia:      "1.º Parcial — Turno 4",
    esPeriodo:      true,
    esEstimado:     false,
    editable:       true,
    fechaInicio:    "2026-08-10",
    fechaFin:       "2026-08-14",
    hora:           null,
    modalidad:      null,
    aula:           null,
    estado:         "periodo-informado",
    textoPublico:   "Lunes 10 al viernes 14 de agosto. Tu día y horario específico dentro de este período están por confirmar.",
    observacion:    "Asignación individual pendiente. Cargá tu fecha cuando te la informen."
  }
];

