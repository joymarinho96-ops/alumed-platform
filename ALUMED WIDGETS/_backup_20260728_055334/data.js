/**
 * ALUMED OS - UNLP (Universidad Nacional de La Plata)
 * Banco de Datos y Lógica del Simulador — Método Profe Joy
 */

const bancoDados = {
  choices: [
    // ─── BIOLOGÍA CELULAR Y MOLECULAR ─────────────────────────────────────────
    {
      id: 1,
      materia: "Biología Celular",
      tema: "Retículo Endoplásmico Liso",
      fuente: "Parcial Unificado UNLP - Biología Celular",
      pagina: "p. 42",
      fragmentoApunte: "El Retículo Endoplásmico Liso (REL) es un sistema de membranas interconectadas desprovisto de ribosomas. En el hepatocito, contiene enzimas de la familia citocromo P450 especializadas en la biotransformación de fármacos y compuestos lipófilos, convirtiéndolos en metabolitos hidrosolubles para su excreción biliar o renal.",
      pergunta: "¿Cuál de las siguientes organelas participa activamente en la desintoxicación de fármacos y compuestos lipófilos en el hepatocito a través del sistema citocromo P450?",
      opcoes: [
        "A) Retículo Endoplásmico Rugoso (RER)",
        "B) Retículo Endoplásmico Liso (REL)",
        "C) Complejo de Golgi",
        "D) Lisosoma primario"
      ],
      correta: 1,
      justificativa: "El REL contiene enzimas especializadas de la familia citocromo P450 encargadas de la inactivación y detoxificación celular en el parénquima hepático.",
      joy: {
        queEs: "El Retículo Endoplásmico Liso (REL) es un sistema de membranas tubulares interconectadas sin ribosomas en su superficie.",
        dondeSe: "Se encuentra en abundancia en hepatocitos, células musculares (donde se llama retículo sarcoplásmico) y células de las glándulas suprarrenales.",
        estructura: "Red de túbulos y cisternas membranosas continuas con el REL pero sin ribosomas — por eso se ve más liso y tubular al microscopio electrónico.",
        funcion: "Detoxificación de fármacos y venenos (vía citocromo P450), síntesis de lípidos y esteroides, almacenamiento y liberación de Ca²⁺ en el músculo.",
        mecanismo: "Las enzimas CYP450 oxidan compuestos lipófilos en reacciones de fase I, haciéndolos más hidrosolubles para que el hígado los pueda eliminar.",
        siFalla: "Si falla el REL hepático → acumulación de fármacos tóxicos en sangre, esteatosis hepática y daño celular por estrés oxidativo.",
        examen: "REL = Sin ribosomas = Lípidos + Detox. Si dice 'citocromo P450' o 'hepatocito' → REL.",
        trampa: "La trampa clásica es confundir el REL con el RER. El RER tiene ribosomas y sintetiza PROTEÍNAS. El REL no tiene ribosomas y maneja LÍPIDOS y DETOXIFICACIÓN.",
        porQueNoCorrectas: [
          "El RER (Retículo Endoplásmico Rugoso) tiene ribosomas en su superficie y se especializa en la síntesis y plegamiento de proteínas, NO en detoxificación.",
          "Esta es la respuesta correcta: el REL contiene las enzimas citocromo P450.",
          "El Complejo de Golgi modifica, empaqueta y envía proteínas y lípidos ya sintetizados, pero NO detoxifica fármacos.",
          "El Lisosoma primario contiene hidrolasas ácidas para degradar macromoléculas propias o extrañas, NO participa en la biotransformación de fármacos lipófilos."
        ]
      }
    },
    {
      id: 2,
      materia: "Biología Celular",
      tema: "Apoptosis - Vía Intrínseca",
      fuente: "Recuperatorio UNLP - Biología Celular",
      pagina: "p. 58",
      fragmentoApunte: "La vía intrínseca de la apoptosis se activa ante daño celular interno (estrés genotóxico, hipoxia). Las proteínas Bax/Bak de la familia Bcl-2 forman poros en la membrana mitocondrial externa, permitiendo la liberación del citocromo c al citosol. Allí, el citocromo c se une a Apaf-1 y procaspasa 9 para formar el apoptosoma, que activa la caspasa 3 efectora.",
      pergunta: "Durante la apoptosis celular (vía intrínseca o mitocondrial), ¿qué evento desencadena directamente la formación del apoptosoma con Apaf-1 y procaspasa 9?",
      opcoes: [
        "A) Liberación de citocromo c al citosol tras la apertura de poros mitocondriales",
        "B) Fosforilación de la proteína Bad mediada por la kinasa Akt",
        "C) Activación de los receptores de muerte de superficie celular Fas/FasL",
        "D) Entrada masiva de iones Calcio al lumen del retículo endoplásmico"
      ],
      correta: 0,
      justificativa: "La salida de citocromo c desde el espacio intermembrana mitocondrial hacia el citosol activa la proteína oligomérica Apaf-1 para reclutar la procaspasa 9.",
      joy: {
        queEs: "El apoptosoma es un complejo proteico en forma de rueda que inicia la cascada de caspasas en la apoptosis intrínseca.",
        dondeSe: "Se forma en el citosol de la célula que está muriendo por señales internas de daño.",
        estructura: "Está compuesto por: citocromo c (mitocondrial) + Apaf-1 (proteína adaptadora) + procaspasa 9 → oligomerizan en una estructura heptamérica.",
        funcion: "Activar la procaspasa 9 → que activa la caspasa 3 → desmantelamiento ordenado de la célula.",
        mecanismo: "Daño → Bax/Bak abren poros en mitocondria → sale citocromo c → se une a Apaf-1 → reclutan procaspasa 9 → apoptosoma activo → caspasa 3 → muerte.",
        siFalla: "Si falla la apoptosis → proliferación celular descontrolada = CÁNCER. Bcl-2 sobreexpresado en linfomas bloquea este proceso.",
        examen: "Apoptosoma = citocromo c + Apaf-1 + procaspasa 9. Vía intrínseca = mitocondria. Vía extrínseca = receptores Fas (externa).",
        trampa: "Fas/FasL es la vía EXTRÍNSECA (activa la caspasa 8). El enunciado pide la vía INTRÍNSECA. Akt fosforila Bad para INHIBIR la apoptosis, no iniciarla.",
        porQueNoCorrectas: [
          "Esta es la respuesta correcta: el citocromo c al unirse con Apaf-1 en el citosol forma el apoptosoma.",
          "La fosforilación de Bad por Akt hace que Bad se inactive (se separe de Bcl-2), lo que PROTEGE a la célula de la apoptosis. Es un mecanismo ANTIAPOPTÓTICO.",
          "Los receptores Fas/FasL son propios de la vía extrínseca e inician la apoptosis activando la procaspasa 8 (no la 9) y no forman el apoptosoma.",
          "La entrada de Ca²⁺ al RE lumen no inicia el apoptosoma. Al contrario, la SALIDA de Ca²⁺ del RE puede señalizar estrés, pero no es el desencadenante directo del apoptosoma."
        ]
      }
    },

    // ─── HISTOLOGÍA Y EMBRIOLOGÍA ─────────────────────────────────────────────
    {
      id: 3,
      materia: "Histología y Embriología",
      tema: "Epitelio Respiratorio",
      fuente: "Parcial 1 UNLP - Histología General",
      pagina: "p. 78",
      fragmentoApunte: "La mucosa traqueobronquial está revestida por un epitelio seudoestratificado cilíndrico ciliado, también llamado epitelio respiratorio. Contiene células ciliadas (mayoritarias), células caliciformes secretoras de moco, células basales (progenitoras) y células de Kulchitsky (enteroendocrinas). Las cilias baten en dirección cefálica para transportar el moco y partículas atrapadas.",
      pergunta: "¿Qué tipo de epitelio caracteriza la mucosa del conducto traqueobronquial en el sistema respiratorio?",
      opcoes: [
        "A) Epitelio cilíndrico simple con microvellosidades rígidas",
        "B) Epitelio plano estratificado no queratinizado",
        "C) Epitelio seudoestratificado cilíndrico ciliado con células caliciformes",
        "D) Epitelio polimorfo de transición (urotelio)"
      ],
      correta: 2,
      justificativa: "La vía aérea traqueobronquial posee un epitelio respiratorio característico: seudoestratificado cilíndrico ciliado con células caliciformes mucíparas.",
      joy: {
        tejido: "Epitelio seudoestratificado cilíndrico ciliado — también llamado 'epitelio respiratorio'.",
        celulas: "① Células ciliadas (mayoritarias) ② Células caliciformes (productoras de moco) ③ Células basales (progenitoras, todas tocan la membrana basal) ④ Células de Kulchitsky (neuroendocrinas).",
        capasOrg: "Parece estratificado porque los núcleos están a distintas alturas, pero TODAS las células tocan la membrana basal → por eso se llama PSEUDO-estratificado.",
        tincion: "Con H-E: se ve una capa de núcleos escalonados en altura, borde luminal con cilias bien visibles (color rosado). Las caliciformes se tiñen pálidas por el moco.",
        funcion: "Las cilias barren el moco con partículas atrapadas hacia arriba (escalera mucociliar). Las caliciformes secretan moco que atrapa polvo y microbios.",
        reconocer: "En la lámina: buscá los núcleos escalonados y el borde apical con cilias. Nunca verás varias capas celulares, solo una fila con núcleos en distintos niveles.",
        examen: "Tráquea y bronquios = epitelio SEUDOESTRATIFICADO ciliado. Alvéolo = epitelio SIMPLE plano. Laringe = plano estratificado. Vejiga = transición.",
        trampa: "La trampa es pensar que 'seudoestratificado' significa que hay muchas capas. NO. Hay una sola capa pero los núcleos se ubican en distintas alturas, dando la ilusión de estratificación.",
        porQueNoCorrectas: [
          "El epitelio cilíndrico simple con microvellosidades cubre el intestino delgado (enterocitos con borde en cepillo). No tiene cilias y no es respiratorio.",
          "El epitelio plano estratificado no queratinizado reviste la boca, faringe, esófago y vagina. No tiene cilias ni caliciformes.",
          "Esta es la respuesta correcta: epitelio seudoestratificado cilíndrico ciliado con caliciformes = mucosa respiratoria.",
          "El urotelio (epitelio de transición) reviste la vejiga y los uréteres, y se caracteriza por células en sombrilla que cambian forma según la distensión."
        ]
      }
    },
    {
      id: 4,
      materia: "Histología y Embriología",
      tema: "Gastrulación - Notocorda",
      fuente: "Parcial 2025 Bloque II UNLP - Embriología",
      pagina: "p. 112",
      fragmentoApunte: "Durante la 3ª semana del desarrollo (gastrulación), la notocorda se forma en la línea media del disco embrionario. Actúa como el organizador primario de Spemann: secreta factores inductores (Noggin, Chordin, Follistatina) que inhiben la señalización BMP-4 en el ectodermo suprayacente, redirigiendo su destino hacia neuroectodermo (placa neural). Este proceso se denomina inducción neural primaria.",
      pergunta: "Durante la 3.ª semana del desarrollo embrionario (gastrulación), ¿qué estructura señalizadora induce la diferenciación de la placa neural a partir del ectodermo suprayacente?",
      opcoes: [
        "A) La alantoides y el conducto onfalomesentérico",
        "B) La notocorda axial y el mesodermo paraxial",
        "C) El saco vitelino secundario",
        "D) Las crestas gonadales embrionarias"
      ],
      correta: 1,
      justificativa: "La notocorda actúa como el organizador primario embrionario, secretando factores inductores (como noggin y chordin) que transforman el ectodermo suprayacente en neuroectodermo (placa neural).",
      joy: {
        estructura: "La notocorda es un bastón mesodermal axial transitorio que aparece en la 3ª semana, forma el eje del embrión y luego desaparece (su remanente es el núcleo pulposo del disco intervertebral).",
        origenEmb: "Deriva del mesodermo axial que migra a través del nodo primitivo (nodo de Hensen) durante la gastrulación.",
        cuandoAparece: "Semana 3 del desarrollo, durante la gastrulación. Persiste temporalmente y guía la formación del tubo neural.",
        etapas: "① Gastrulación (semana 3) → ② Notocorda aparece en línea media → ③ Secreta Noggin/Chordin → ④ Inhibe BMP-4 en ectodermo → ⑤ Ectodermo se convierte en placa neural → ⑥ Placa neural se cierra en tubo neural (semana 4).",
        derivados: "La notocorda en sí desaparece; su influencia da origen al tubo neural (SNC + SNP). El núcleo pulposo es su único remanente en el adulto.",
        reconocer: "En un esquema de semana 3: la notocorda aparece como un bastón en la línea media, entre el ectodermo (arriba) y el endodermo (abajo).",
        examen: "Notocorda = organizador primario = induce placa neural = inducción neural. Semana 3 = gastrulación. Los factores son Noggin, Chordin, Follistatina (inhiben BMP-4).",
        trampa: "La alantoides es un divertículo del saco vitelino involucrado en la hematopoyesis temprana y la formación de la vejiga, NO en la inducción neural. El saco vitelino aporta nutrición y células germinativas, no induce el tubo neural.",
        porQueNoCorrectas: [
          "La alantoides participa en la hematopoyesis temprana y formación de la vejiga urinaria. El conducto onfalomesentérico conecta el intestino al saco vitelino. Ninguno induce la placa neural.",
          "Esta es la respuesta correcta: la notocorda y el mesodermo paraxial inducen la formación de la placa neural por inhibición de BMP-4.",
          "El saco vitelino secundario es un órgano de nutrición provisional y origen de las células germinativas primordiales. No tiene función inductora neural.",
          "Las crestas gonadales se forman más tardíamente (semanas 5-6) y son el primordio de las gónadas. No tienen relación con la inducción neural."
        ]
      }
    },

    // ─── ANATOMÍA CÁTEDRA A ───────────────────────────────────────────────────
    {
      id: 5,
      materia: "Anatomía Cátedra A",
      tema: "Fosa Cubital - Paquete Vasculonervioso",
      fuente: "Parcial Oficial Cátedra A - UNLP",
      pagina: "p. 187",
      fragmentoApunte: "La fosa cubital es una depresión triangular en la cara anterior del codo. Contiene, de lateral a medial: tendón del bíceps braquial, arteria braquial (con venas satélites) y nervio mediano. Más lateralmente se ubica el nervio radial. La vena cefálica y basílica se encuentran superficiales a la aponeurosis bicipital.",
      pergunta: "En la región de la fosa cubital (sangría del codo), ¿cuál es la disposición anatómica del paquete vasculonervioso braquial respecto al tendón del músculo bíceps braquial?",
      opcoes: [
        "A) Lateral al tendón del bíceps: Nervio mediano y arteria radial",
        "B) Medial al tendón del bíceps: Arteria braquial y nervio mediano",
        "C) Posterior al músculo supinador largo: Nervio cubital",
        "D) Anterior a la aponeurosis bicipital: Arteria interósea común"
      ],
      correta: 1,
      justificativa: "El paquete vasculonervioso profundo de la fosa cubital se sitúa medial al tendón del bíceps braquial, integrado por la arteria braquial (con sus venas satélites) y el nervio mediano.",
      joy: {
        queEs: "La fosa cubital es la región triangular en la cara anterior (flexora) del codo, donde se realizan venopunciones y se ausculta la presión arterial braquial.",
        ubicacion: "Cara anterior del codo (pliegue del codo). Límites: supero-lateralmente el braquiorradial, supero-medialmente el pronador redondo, techo la aponeurosis bicipital.",
        partes: "De lateral a medial: Nervio radial (N) → Tendón bíceps (T) → Arteria braquial (A) → Nervio mediano (N). Regla mnemotécnica: N-T-A-N (No Te Ames Nada).",
        relaciones: "La aponeurosis bicipital (lacertus fibrosus) cubre el paquete protegiendo las estructuras profundas. Superficialmente pasan las venas medianas (para la venopunción).",
        irrigInnerv: "La arteria braquial es continuación de la axilar y se bifurca en la fosa en radial y cubital. El nervio mediano viene del plexo braquial (C5-T1).",
        reconocer: "En un pinche cadavérico: buscá el tendón del bíceps como referencia central. MEDIAL a él está la arteria braquial (se palpa como latido). El mediano está medial a la arteria.",
        examen: "Fosa cubital: tendón bíceps es la referencia. Medial = arteria braquial + nervio mediano. Lateral = nervio radial. Superficial = venas medianas.",
        trampa: "El nervio cubital NO pasa por la fosa cubital. Pasa por el canal epitroclear (medial del codo) → por eso se llama 'hueso de la risa'. No confundas cubital con mediano.",
        porQueNoCorrectas: [
          "El nervio mediano y la arteria braquial se ubican MEDIALES al tendón bíceps, no laterales. Lateralmente está el nervio radial.",
          "Correcta: la arteria braquial y el nervio mediano se ubican mediales al tendón del bíceps.",
          "El nervio cubital NO atraviesa la fosa cubital. Rodea el epicóndilo medial (epitróclea) por el canal retropicondíleo para llegar al antebrazo.",
          "La arteria interósea común es una rama de la arteria cubital que se origina distal a la fosa cubital, en el antebrazo."
        ]
      }
    },

    // ─── ANATOMÍA CÁTEDRA B ───────────────────────────────────────────────────
    {
      id: 6,
      materia: "Anatomía Cátedra B",
      tema: "Ventrículo Derecho - Cresta Supraventricular",
      fuente: "Simulacro Cátedra B - UNLP",
      pagina: "p. 204",
      fragmentoApunte: "El ventrículo derecho se divide funcionalmente en dos porciones: la vía de entrada (porción trabeculada, con trabéculas carnosas y músculos papilares) y la vía de salida (infundíbulo o cono arterioso, de paredes lisas). La cresta supraventricular (espolón de Wolff) y la trabécula septomarginal (banda moderadora) separan estas dos porciones.",
      pergunta: "En el corazón humano, ¿qué estructura anatómica limita la vía de entrada (porción trabeculada) de la vía de salida (infundíbulo o cono arterioso) dentro del ventrículo derecho?",
      opcoes: [
        "A) La cresta supraventricular (espolón de Wolff) y la trabécula septomarginal",
        "B) La válvula de Eustaquio de la vena cava inferior",
        "C) La fosa oval del tabique interauricular",
        "D) Las valvas semilunares de la válvula aórtica"
      ],
      correta: 0,
      justificativa: "La cresta supraventricular (espolón de Wolff) y la trabécula septomarginal (banda moderadora) forman la cresta muscular separadora entre la porción de entrada y el cono arterioso del ventrículo derecho.",
      joy: {
        queEs: "La cresta supraventricular (espolón de Wolff) es un reborde muscular interno del ventrículo derecho que separa las dos porciones funcionales de esa cámara.",
        ubicacion: "Cara interna del ventrículo derecho, entre la válvula tricúspide (entrada) y la válvula pulmonar (salida/infundíbulo).",
        partes: "① Vía de entrada: trabeculada, con trabéculas carnosas y músculos papilares que sostienen la tricúspide. ② Vía de salida (infundíbulo/cono): de paredes lisas, lleva al tronco pulmonar.",
        relaciones: "La trabécula septomarginal (banda moderadora) conecta el tabique interventricular con el músculo papilar anterior y conduce la rama derecha del fascículo de His.",
        irrigInnerv: "El ventrículo derecho es irrigado principalmente por la arteria coronaria derecha. La banda moderadora recibe el sistema de conducción eléctrica (fascículo de His → rama derecha).",
        reconocer: "En un preparado cardíaco abierto: al abrir el VD, la cresta supraventricular aparece como un reborde muscular prominente en 'C'. La banda moderadora es una cuerda muscular que cruza de tabique a pared libre.",
        examen: "Cresta supraventricular = separa entrada (trabeculada) de salida (infundíbulo) del VD. La banda moderadora conduce la rama derecha de His.",
        trampa: "La válvula de Eustaquio dirige el flujo de la cava inferior hacia el foramen oval en el FETO. La fosa oval está en el tabique INTERAURICULAR, no interventricular. Las valvas semilunares son de la aorta (VI), no del VD.",
        porQueNoCorrectas: [
          "Correcta: la cresta supraventricular y la trabécula septomarginal son las estructuras que separan las dos porciones del VD.",
          "La válvula de Eustaquio es un repliegue en la desembocadura de la vena cava inferior en la aurícula derecha. En el feto dirigía sangre al foramen oval. No tiene relación con el VD.",
          "La fosa oval es una depresión en el tabique INTERAURICULAR (entre aurículas). No está en el ventrículo derecho.",
          "Las valvas semilunares de la válvula aórtica se ubican en la salida del VENTRÍCULO IZQUIERDO, no del derecho (el VD tiene la válvula pulmonar)."
        ]
      }
    },

    // ─── ANATOMÍA CÁTEDRA C ───────────────────────────────────────────────────
    {
      id: 7,
      materia: "Anatomía Cátedra C",
      tema: "Coronarias - Interventricular Anterior",
      fuente: "Examen Unificado Cátedra C - UNLP",
      pagina: "p. 218",
      fragmentoApunte: "La arteria coronaria izquierda emerge del seno aórtico izquierdo y se divide en: Rama interventricular anterior (RIVA o descendente anterior, DA) que discurre por el surco interventricular anterior, y Rama circunfleja que rodea el surco coronario izquierdo. La RIVA irriga el tabique interventricular anterior (2/3) y la pared anterior del VI, acompañada por la vena cardíaca magna.",
      pergunta: "¿Qué vaso sanguíneo arterial discurre por el surco interventricular anterior acompañado por la vena cardíaca magna (vena coronaria mayor)?",
      opcoes: [
        "A) Arteria coronaria derecha troncal",
        "B) Rama interventricular anterior (descendente anterior) de la arteria coronaria izquierda",
        "C) Arteria circunfleja izquierda",
        "D) Rama marginal derecha de la coronaria derecha"
      ],
      correta: 1,
      justificativa: "La rama interventricular anterior (descendente anterior) emerge del tronco de la coronaria izquierda y desciende por el surco interventricular anterior junto a la vena cardíaca magna.",
      joy: {
        queEs: "La Rama Interventricular Anterior (RIVA) o Descendente Anterior (DA) es la arteria más importante del corazón: irriga la mayor parte del tabique y la pared anterior del ventrículo izquierdo.",
        ubicacion: "Corre por el surco interventricular anterior, desde la bifurcación del tronco coronario izquierdo hasta el ápex cardíaco, donde puede rodearlo.",
        partes: "Tronco coronario izquierdo → se bifurca en: ① RIVA (DA) que baja por el surco anterior ② Circunfleja que rodea el surco auriculoventricular izquierdo.",
        relaciones: "La vena cardíaca magna (mayor) la acompaña en el surco interventricular anterior, drenando al seno coronario. En el surco interventricular posterior va la coronaria derecha con la vena interventricular posterior.",
        irrigInnerv: "La DA irriga: 2/3 anteriores del tabique interventricular, pared anterior del VI, cara anterior del VD. La DA es la 'widow maker' porque su oclusión causa el IAM anterior masivo.",
        reconocer: "En un preparado cardíaco de cara anterior: la DA aparece descendiendo rectamente desde la base hasta el ápex, en la línea del surco interventricular anterior.",
        examen: "Surco interventricular ANTERIOR = DA (rama de la coronaria izquierda) + vena cardíaca magna. Surco interventricular POSTERIOR = coronaria derecha + vena interventricular posterior.",
        trampa: "La arteria circunfleja va por el SURCO AURICULOVENTRICULAR izquierdo (lateral/posterior), NO por el surco interventricular. No la confundas con la DA.",
        porQueNoCorrectas: [
          "La coronaria derecha troncal discurre por el surco auriculoventricular derecho (coronario derecho), no por el surco interventricular anterior.",
          "Correcta: la DA (rama de coronaria izquierda) desciende por el surco interventricular anterior con la vena cardíaca magna.",
          "La arteria circunfleja izquierda rodea el surco auriculoventricular izquierdo hacia la cara posterior. No atraviesa el surco interventricular anterior.",
          "La rama marginal derecha surge de la coronaria derecha y discurre por el borde derecho del corazón hacia el ápex. No está en el surco interventricular anterior."
        ]
      }
    },
    {
      id: 8,
      materia: "Anatomía Cátedra C",
      tema: "Nervios Craneales - Trigémino Motor",
      fuente: "Repaso de Neuroanatomía Cátedra C - UNLP",
      pagina: "p. 243",
      fragmentoApunte: "El nervio trigémino (NC V) es el mayor nervio craneal. Su ramo mandibular (V3) es el único ramo mixto: contiene fibras sensitivas de la piel del mentón/mejilla/lengua anterior y fibras motoras (eferentes viscerales especiales, EVE) para los músculos derivados del 1er arco faríngeo: temporal, masetero, pterigoideos medial y lateral, milohioideo, vientre anterior del digástrico, tensor del tímpano y tensor del velo del paladar.",
      pergunta: "¿Qué ramo nervioso proporciona la inervación motora para los 4 músculos principales de la masticación (temporal, masetero, pterigoideo lateral y pterigoideo medial)?",
      opcoes: [
        "A) Nervio Facial (NC VII)",
        "B) Ramo Mandibular del Nervio Trigémino (NC V3)",
        "C) Nervio Glosofaríngeo (NC IX)",
        "D) Nervio Hipogloso (NC XII)"
      ],
      correta: 1,
      justificativa: "El ramo V3 (mandibular) del nervio trigémino suministra fibras eferentes viscerales especiales (motoras) para la musculatura derivada del primer arco faríngeo (músculos masticadores).",
      joy: {
        queEs: "El ramo mandibular (V3) del trigémino es el único ramo mixto del nervio trigémino: lleva sensibilidad del tercio inferior de la cara Y motricidad para los músculos masticadores.",
        ubicacion: "Sale por el foramen oval de la base del cráneo (fosa infratemporal). Se divide en ramos anteriores (principalmente motores) y posteriores (principalmente sensitivos).",
        partes: "Músculos masticadores inervados por V3: ① Temporal ② Masetero ③ Pterigoideo lateral ④ Pterigoideo medial. Plus: milohioideo, vientre ant. digástrico, tensor tímpano, tensor velo paladar.",
        relaciones: "V3 sale junto a V1 (oftálmico) y V2 (maxilar) desde el ganglio trigeminal (de Gasser). V1 sale por la fisura orbitaria superior, V2 por el foramen redondo, V3 por el foramen oval.",
        irrigInnerv: "Los músculos masticadores son derivados del 1° arco faríngeo (Meckel), por eso su inervación es V3 (fibras EVE = eferentes viscerales especiales del arco braquial).",
        reconocer: "Regla: músculo de la masticación → V3. Si te preguntan por la mejilla o mandíbula sensitiva → también V3. Cara superior (frente) sensitiva → V1. Mejilla media → V2.",
        examen: "NC VII (Facial) = músculos de la EXPRESIÓN facial (fruncir, cerrar ojos, sonreír). NC V3 (Mandibular) = músculos de la MASTICACIÓN. NC XII (Hipogloso) = músculo de la LENGUA.",
        trampa: "El facial (VII) inerva los músculos de la expresión facial (frontalis, orbicularis, buccinador). El hipogloso (XII) inerva la lengua. Muchos confunden 'mandibular' con mandíbula y piensan en el hipogloso.",
        porQueNoCorrectas: [
          "El nervio facial (VII) inerva los músculos de la EXPRESIÓN facial (frontalis, orbicularis oculi/oris, buccinador, platisma). No inerva los masticadores.",
          "Correcta: el ramo mandibular (V3) del trigémino provee la inervación motora de los 4 músculos masticadores.",
          "El nervio glosofaríngeo (IX) inerva el músculo estilofaríngeo y provee sensibilidad a la faringe y al tercio posterior de la lengua (gusto y general). No inerva masticadores.",
          "El nervio hipogloso (XII) es exclusivamente motor para los músculos intrínsecos y extrínsecos de la LENGUA (geniogloso, hiogloso, estilogloso, músculos linguales). No tiene relación con la masticación."
        ]
      }
    }
  ],

  pinches: [
    {
      id: 1,
      materia: "Anatomía Cátedra C",
      fuente: "Pinche de Preparado Anatómico - Cátedra C UNLP",
      imagem: "https://images.unsplash.com/photo-1559757175-5700dde675bc?auto=format&fit=crop&w=600&q=80",
      pergunta: "Identifique la estructura vascular señalada en el preparado cadavérico:",
      respostasAceitas: ["arteria subclavia", "a. subclavia", "subclavia", "arteria subclavia izquierda", "arteria subclavia derecha"]
    },
    {
      id: 2,
      materia: "Histología y Embriología",
      fuente: "Corte Histológico de Microscopía - UNLP",
      imagem: "https://images.unsplash.com/photo-1579154204601-01588f351e67?auto=format&fit=crop&w=600&q=80",
      pergunta: "Identifique el componente del corpúsculo renal señalado en la muestra:",
      respostasAceitas: ["glomerulo", "glomerulo renal", "glomérulo", "glomérulo renal", "ovillo glomerular"]
    },
    {
      id: 3,
      materia: "Anatomía Cátedra A",
      fuente: "Maqueta Anatómica de Tórax - Cátedra A UNLP",
      imagem: "https://images.unsplash.com/photo-1530210124550-912dc1381cb8?auto=format&fit=crop&w=600&q=80",
      pergunta: "Identifique el gran vaso arterial que emerge del ventrículo izquierdo:",
      respostasAceitas: ["aorta", "arteria aorta", "aorta ascendente", "a. aorta", "tronco de la aorta"]
    }
  ],

  orales: [
    {
      id: 1,
      materia: "Histología y Embriología",
      fuente: "Bolillero de Examen Presencial UNLP",
      bolilla: "Bolilla 5: Desarrollo Cardíaco y Circulación Fetal",
      casoClinico: "Paciente recién nacido derivado de la Maternidad que presenta soplo holo-sistólico y leve cianosis diferencial. En el ecocardiograma se constata comunicación interauricular por falla del desarrollo septal.",
      checklist: [
        "1. Describir la secuencia de tabicamiento auricular: Septum primum, ostium primum, ostium secundum y septum secundum.",
        "2. Explicar el mecanismo fisiológico del cierre del foramen oval en los primeros minutos postnacimiento.",
        "3. Comparar las 3 derivaciones vasculares fetales (conducto venoso de Arancio, foramen oval y conducto arterioso de Botal)."
      ]
    },
    {
      id: 2,
      materia: "Biología Celular",
      fuente: "Bolillero de Biología Celular y Molecular UNLP",
      bolilla: "Bolilla 3: Tráfico de Endomembranas y Transporte Vesicular",
      casoClinico: "Línea celular mutante en estudio donde se constata la acumulación anómala de glicoproteínas inactivas en el lumen del retículo endoplásmico por bloqueo del transporte anterógrado.",
      checklist: [
        "1. Diferenciar las cubiertas vesiculares: COP II (anterógrado RER-Golgi), COP I (retrógrado) y Clatrina.",
        "2. Detallar el ciclo de las Rab GTPasas y el acoplamiento mediado por v-SNARE y t-SNARE.",
        "3. Describir las modificaciones postraduccionales de N-glicosilación y O-glicosilación en el aparato de Golgi."
      ]
    },
    {
      id: 3,
      materia: "Anatomía Cátedra C",
      fuente: "Bolillero de Neuroanatomía - Cátedra C UNLP",
      bolilla: "Bolilla 12: Irrigación Encefálica y Círculo Arterial de Willis",
      casoClinico: "Paciente masculino de 64 años consulta por pérdida súbita de fuerza en el miembro superior e inferior derechos, asociada a afasia motora de Broca.",
      checklist: [
        "1. Describir el origen del sistema carotídeo interno y del sistema vertebrobasilar (arterias vertebrales y basilar).",
        "2. Esquematizar la constitución anatómica del Polígono Arterial de Willis y sus arterias comunicantes.",
        "3. Detallar el territorio de irrigación cortico-subcortical de la Arteria Cerebral Media (Silviana)."
      ]
    }
  ]
};

// ============================================================
// ESTADO GLOBAL DE LA SPA
// ============================================================
let filteredChoices = [...bancoDados.choices];
let currentChoiceIndex = 0;
let selectedOption = null;
let currentMateria = "TODAS";
let currentPincheIndex = 0;
let yaValidado = false;

// ============================================================
// NAVEGACIÓN DE TABS
// ============================================================
function switchTab(tabId) {
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
  const sec = document.getElementById(`tab-${tabId}`);
  const btn = document.getElementById(`btn-${tabId}`);
  if (sec) sec.classList.add('active');
  if (btn) btn.classList.add('active');
}

// ============================================================
// FILTRO POR MATERIA
// ============================================================
function cambiarMateria(materia) {
  currentMateria = materia;
  filteredChoices = materia === "TODAS"
    ? [...bancoDados.choices]
    : bancoDados.choices.filter(q => q.materia === materia);
  currentChoiceIndex = 0;
  loadChoice();
  loadPinche();
}

// ============================================================
// CARGA DE PREGUNTA
// ============================================================
function loadChoice() {
  const fb = document.getElementById('mc-feedback');
  if (fb) { fb.innerHTML = ''; fb.className = 'feedback'; }
  selectedOption = null;
  yaValidado = false;

  if (filteredChoices.length === 0) {
    document.getElementById('mc-pergunta').innerText = "No hay preguntas para esta cátedra.";
    document.getElementById('mc-opcoes').innerHTML = "";
    document.getElementById('mc-counter').innerText = "Pregunta 0 de 0";
    return;
  }

  const q = filteredChoices[currentChoiceIndex];
  document.getElementById('mc-materia').innerText = q.materia;
  const fuenteBadge = document.getElementById('mc-fuente');
  if (fuenteBadge) fuenteBadge.innerHTML = `<i class="fa-solid fa-scroll"></i> ${q.fuente || 'Examen UNLP'}`;
  document.getElementById('mc-pergunta').innerText = q.pergunta;
  document.getElementById('mc-counter').innerText = `Pregunta ${currentChoiceIndex + 1} de ${filteredChoices.length}`;

  const container = document.getElementById('mc-opcoes');
  container.innerHTML = '';
  q.opcoes.forEach((opt, idx) => {
    const btn = document.createElement('button');
    btn.className = 'option-btn';
    btn.id = `opt-${idx}`;
    btn.innerText = opt;
    btn.onclick = () => {
      if (yaValidado) return;
      document.querySelectorAll('.option-btn').forEach(b => b.classList.remove('selected'));
      btn.classList.add('selected');
      selectedOption = idx;
    };
    container.appendChild(btn);
  });
}

// ============================================================
// VALIDACIÓN — MÉTODO PROFE JOY
// ============================================================
function validarChoice() {
  if (selectedOption === null || yaValidado) return;
  yaValidado = true;

  const q = filteredChoices[currentChoiceIndex];
  const fb = document.getElementById('mc-feedback');
  if (!fb) return;

  const esCorrecta = selectedOption === q.correta;
  const letras = ['A', 'B', 'C', 'D'];
  const letraElegida = letras[selectedOption];
  const letraCorrecta = letras[q.correta];

  // Colorear opciones
  document.querySelectorAll('.option-btn').forEach((btn, idx) => {
    btn.classList.remove('selected');
    if (idx === q.correta) btn.classList.add('correct-reveal');
    else if (idx === selectedOption) btn.classList.add('wrong-reveal');
  });

  // Guardar en localStorage
  guardarEnLocalStorage(q, selectedOption, esCorrecta);

  // Generar el panel Joy
  fb.innerHTML = generarPanelJoy(q, selectedOption, esCorrecta, letraElegida, letraCorrecta);
  fb.className = 'feedback joy-active';
}

// ============================================================
// GENERADOR DEL PANEL JOY (adaptado por materia)
// ============================================================
function generarPanelJoy(q, seleccionado, esCorrecta, letraElegida, letraCorrecta) {
  const j = q.joy || {};
  const materia = q.materia || '';
  const tema = q.tema || '';

  // Verificar si hay datos Joy
  const sinDatos = Object.keys(j).length === 0;
  if (sinDatos) {
    return `
      <div class="joy-panel ${esCorrecta ? 'joy-correct' : 'joy-incorrect'}">
        <div class="joy-header">
          ${esCorrecta
            ? `<span class="joy-verdict correct-text">✨ ¡Correcto! Marcaste <strong>${letraElegida}</strong>.</span>`
            : `<span class="joy-verdict incorrect-text">❌ Incorrecto. Marcaste <strong>${letraElegida}</strong>. Correcta: <strong>${letraCorrecta}</strong>.</span>`
          }
        </div>
        <div class="joy-section">
          <p>${q.justificativa || 'Este punto todavía no fue localizado en los apuntes ALUMED cargados.'}</p>
        </div>
        ${renderJoyActions(q)}
      </div>`;
  }

  // Secciones según materia
  let seccionesHTML = '';

  if (materia.includes('Biología')) {
    seccionesHTML = `
      ${joyBlock('🔬', '¿Qué es?', j.queEs)}
      ${joyBlock('📍', '¿Dónde se encuentra?', j.dondeSe)}
      ${joyBlock('🏗️', 'Estructura', j.estructura)}
      ${joyBlock('⚙️', 'Función', j.funcion)}
      ${joyBlock('🔄', 'Mecanismo básico', j.mecanismo)}
      ${joyBlock('💥', '¿Qué ocurre si falla?', j.siFalla)}`;
  } else if (materia.includes('Histología') && !materia.toLowerCase().includes('embrio')) {
    seccionesHTML = `
      ${joyBlock('🧫', 'Tejido / Órgano', j.tejido)}
      ${joyBlock('🔬', 'Células principales', j.celulas)}
      ${joyBlock('📋', 'Capas y organización', j.capasOrg)}
      ${joyBlock('🎨', 'Tinción y características visuales', j.tincion)}
      ${joyBlock('⚙️', 'Función', j.funcion)}
      ${joyBlock('👁️', 'Cómo reconocerlo en la lámina', j.reconocer)}`;
  } else if (materia.includes('Embriología') || materia.includes('Histología')) {
    // Embriología puede venir como "Histología y Embriología"
    const esEmbrio = j.origenEmb || j.cuandoAparece || j.etapas || j.derivados;
    if (esEmbrio) {
      seccionesHTML = `
        ${joyBlock('🥚', '¿Qué estructura es?', j.estructura || j.queEs)}
        ${joyBlock('🌱', 'Origen embrionario', j.origenEmb)}
        ${joyBlock('📅', '¿Cuándo aparece?', j.cuandoAparece)}
        ${joyBlock('🔄', 'Etapas y transformaciones', j.etapas)}
        ${joyBlock('🌿', 'Derivados', j.derivados)}
        ${joyBlock('👁️', 'Cómo reconocerla en un esquema', j.reconocer)}`;
    } else {
      seccionesHTML = `
        ${joyBlock('🧫', 'Tejido / Órgano', j.tejido)}
        ${joyBlock('🔬', 'Células principales', j.celulas)}
        ${joyBlock('📋', 'Capas y organización', j.capasOrg)}
        ${joyBlock('🎨', 'Tinción', j.tincion)}
        ${joyBlock('⚙️', 'Función', j.funcion)}
        ${joyBlock('👁️', 'Cómo reconocerlo', j.reconocer)}`;
    }
  } else if (materia.includes('Anatomía')) {
    seccionesHTML = `
      ${joyBlock('🦴', '¿Qué es?', j.queEs)}
      ${joyBlock('📍', 'Ubicación', j.ubicacion)}
      ${joyBlock('🔧', 'Partes', j.partes)}
      ${joyBlock('🔗', 'Relaciones', j.relaciones)}
      ${joyBlock('🩸', 'Irrigación e inervación', j.irrigInnerv)}
      ${joyBlock('👁️', 'Cómo reconocerlo en un pinche', j.reconocer)}`;
  }

  // Por qué incorrectas
  let incorrectasHTML = '';
  if (j.porQueNoCorrectas && Array.isArray(j.porQueNoCorrectas)) {
    const letras = ['A', 'B', 'C', 'D'];
    const items = j.porQueNoCorrectas.map((txt, i) => {
      if (i === q.correta) return `<li class="incorrecta-item correcta-item"><strong>${letras[i]})</strong> ✅ Esta es la correcta.</li>`;
      return `<li class="incorrecta-item"><strong>${letras[i]})</strong> ${txt}</li>`;
    }).join('');
    incorrectasHTML = `
      <div class="joy-no-correctas">
        <div class="joy-section-title"><i class="fa-solid fa-magnifying-glass"></i> ¿Por qué tu opción no es correcta?</div>
        <ul>${items}</ul>
      </div>`;
  }

  // Fuente
  const fuenteHTML = (q.fuente || q.pagina) ? `
    <div class="joy-fuente">
      <i class="fa-solid fa-book-open"></i>
      Basado en: <strong>${q.fuente || '—'}</strong>${q.pagina ? ` — ${q.pagina}` : ''}
      ${q.fragmentoApunte ? `<button class="btn-fragmento" onclick="abrirFragmento(${q.id})"><i class="fa-solid fa-file-lines"></i> Ver fragmento del apunte</button>` : ''}
    </div>` : '';

  return `
    <div class="joy-panel ${esCorrecta ? 'joy-correct' : 'joy-incorrect'}">

      <div class="joy-header">
        ${esCorrecta
          ? `<div class="joy-verdict correct-text"><i class="fa-solid fa-circle-check"></i> ¡Correcto! Marcaste <strong>${letraElegida}</strong>. ¡Esa es la respuesta exacta!</div>`
          : `<div class="joy-verdict incorrect-text"><i class="fa-solid fa-circle-xmark"></i> Incorrecto. Marcaste <strong>${letraElegida}</strong>. &nbsp;|&nbsp; Respuesta correcta: <strong class="correct-letter">${letraCorrecta}</strong>.</div>`
        }
        ${tema ? `<div class="joy-tema-tag"><i class="fa-solid fa-tag"></i> ${tema}</div>` : ''}
      </div>

      <div class="joy-metodo-header">
        <i class="fa-solid fa-brain"></i> Entendamos juntos — <strong>Método Profe Joy</strong>
      </div>

      <div class="joy-sections">
        ${seccionesHTML}
      </div>

      ${incorrectasHTML}

      <div class="joy-exam-row">
        <div class="joy-clave">
          <i class="fa-solid fa-key"></i> <strong>La clave para el examen</strong>
          <p>${j.examen || 'Este punto todavía no fue localizado en los apuntes ALUMED cargados.'}</p>
        </div>
        <div class="joy-trampa">
          <i class="fa-solid fa-triangle-exclamation"></i> <strong>Ojo con la trampa</strong>
          <p>${j.trampa || '—'}</p>
        </div>
      </div>

      ${fuenteHTML}
      ${renderJoyActions(q)}
    </div>`;
}

// Helper: bloque de sección Joy individual
function joyBlock(emoji, titulo, contenido) {
  if (!contenido) return '';
  return `
    <div class="joy-block">
      <div class="joy-block-title">${emoji} ${titulo}</div>
      <div class="joy-block-body">${contenido}</div>
    </div>`;
}

// Helper: botones de acción post-corrección
function renderJoyActions(q) {
  return `
    <div class="joy-actions">
      <button class="btn-action btn-flashcard" onclick="crearFlashcard(${q.id})">
        <i class="fa-solid fa-layer-group"></i> Crear flashcard
      </button>
      <button class="btn-action btn-repaso" onclick="agregarRepaso(${q.id})">
        <i class="fa-solid fa-rotate"></i> Agregar a repaso de errores
      </button>
      <button class="btn-action btn-parecida" onclick="practicarParecida(${q.id})">
        <i class="fa-solid fa-shuffle"></i> Practicar otra parecida
      </button>
    </div>`;
}

// ============================================================
// MODAL FRAGMENTO DEL APUNTE
// ============================================================
function abrirFragmento(qId) {
  const q = bancoDados.choices.find(x => x.id === qId);
  if (!q) return;
  const modal = document.getElementById('fragmento-modal');
  const titulo = document.getElementById('fragmento-titulo');
  const cuerpo = document.getElementById('fragmento-cuerpo');
  const fuente = document.getElementById('fragmento-fuente');

  titulo.innerText = q.tema || q.materia;
  cuerpo.innerText = q.fragmentoApunte || 'Este punto todavía no fue localizado en los apuntes ALUMED cargados.';
  fuente.innerText = `${q.fuente || ''}${q.pagina ? ' — ' + q.pagina : ''}`;
  modal.classList.add('open');
}

function cerrarFragmento() {
  const modal = document.getElementById('fragmento-modal');
  modal.classList.remove('open');
}

// ============================================================
// LOCAL STORAGE — PERSISTENCIA
// ============================================================
function guardarEnLocalStorage(q, seleccionado, esCorrecta) {
  const letras = ['A', 'B', 'C', 'D'];
  const registro = {
    id: q.id,
    pregunta: q.pergunta,
    materia: q.materia,
    tema: q.tema || '',
    fuente: q.fuente || '',
    pagina: q.pagina || '',
    alternativaElegida: letras[seleccionado],
    alternativaCorrecta: letras[q.correta],
    explicacion: q.justificativa,
    esCorrecta: esCorrecta,
    fecha: new Date().toISOString(),
    intentos: 1
  };

  // Guardar en historial general
  let historial = JSON.parse(localStorage.getItem('alumed_historial') || '[]');
  const existeIdx = historial.findIndex(r => r.id === q.id);
  if (existeIdx >= 0) {
    historial[existeIdx].intentos++;
    historial[existeIdx].esCorrecta = esCorrecta;
    historial[existeIdx].fecha = registro.fecha;
  } else {
    historial.push(registro);
  }
  localStorage.setItem('alumed_historial', JSON.stringify(historial));

  // Si es incorrecta, también al repaso
  if (!esCorrecta) {
    agregarRepaso(q.id, registro);
  }
}

function crearFlashcard(qId) {
  const q = bancoDados.choices.find(x => x.id === qId);
  if (!q) return;
  let flashcards = JSON.parse(localStorage.getItem('alumed_flashcards') || '[]');
  if (flashcards.find(f => f.id === q.id)) {
    mostrarToast('Ya existe esta flashcard en tu mazo 🃏');
    return;
  }
  flashcards.push({
    id: q.id,
    frente: q.pergunta,
    dorso: q.opcoes[q.correta] + '\n\n' + q.justificativa,
    materia: q.materia,
    tema: q.tema || ''
  });
  localStorage.setItem('alumed_flashcards', JSON.stringify(flashcards));
  mostrarToast('✅ Flashcard creada y guardada en tu mazo');
}

function agregarRepaso(qId, registroExtra) {
  const q = bancoDados.choices.find(x => x.id === qId);
  if (!q) return;
  let repaso = JSON.parse(localStorage.getItem('alumed_errores') || '[]');
  if (!repaso.find(r => r.id === q.id)) {
    repaso.push(registroExtra || { id: q.id, pregunta: q.pergunta, materia: q.materia, tema: q.tema || '' });
    localStorage.setItem('alumed_errores', JSON.stringify(repaso));
    mostrarToast('📌 Agregado a tu sesión de repaso de errores');
  } else {
    mostrarToast('Ya está en tu lista de repaso');
  }
}

function practicarParecida(qId) {
  const q = bancoDados.choices.find(x => x.id === qId);
  if (!q) return;

  // Filtrar por misma materia/tema, excluyendo la actual
  let candidatos = filteredChoices.filter(c =>
    c.id !== qId &&
    (c.materia === q.materia || c.tema === q.tema)
  );

  // Si no hay por tema, cualquiera de la materia
  if (candidatos.length === 0) {
    candidatos = filteredChoices.filter(c => c.id !== qId && c.materia === q.materia);
  }

  // Si todavía no hay, cualquiera del banco completo
  if (candidatos.length === 0) {
    candidatos = filteredChoices.filter(c => c.id !== qId);
  }

  if (candidatos.length === 0) { mostrarToast('No hay más preguntas disponibles'); return; }

  const aleatorio = candidatos[Math.floor(Math.random() * candidatos.length)];
  currentChoiceIndex = filteredChoices.findIndex(c => c.id === aleatorio.id);
  loadChoice();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ============================================================
// TOAST DE NOTIFICACIÓN
// ============================================================
function mostrarToast(msg) {
  let toast = document.getElementById('alumed-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'alumed-toast';
    toast.className = 'alumed-toast';
    document.body.appendChild(toast);
  }
  toast.innerText = msg;
  toast.classList.add('visible');
  setTimeout(() => toast.classList.remove('visible'), 3000);
}

// ============================================================
// NAVEGACIÓN ENTRE PREGUNTAS
// ============================================================
function nextChoice() {
  if (currentChoiceIndex < filteredChoices.length - 1) {
    currentChoiceIndex++;
    loadChoice();
  }
}

function prevChoice() {
  if (currentChoiceIndex > 0) {
    currentChoiceIndex--;
    loadChoice();
  }
}

// ============================================================
// PINCHES
// ============================================================
function materiaActualPinches() {
  return currentMateria === "TODAS"
    ? bancoDados.pinches
    : bancoDados.pinches.filter(p => p.materia === currentMateria);
}

function loadPinche() {
  const fp = materiaActualPinches();
  if (fp.length === 0) {
    document.getElementById('pinch-pergunta').innerText = "No hay muestras anatómicas para esta cátedra.";
    return;
  }
  const p = fp[currentPincheIndex % fp.length];
  document.getElementById('pinch-materia').innerText = p.materia;
  const pFuente = document.getElementById('pinch-fuente');
  if (pFuente) pFuente.innerHTML = `<i class="fa-solid fa-microscope"></i> ${p.fuente || 'Preparado UNLP'}`;
  document.getElementById('pinch-img').src = p.imagem;
  document.getElementById('pinch-pergunta').innerText = p.pergunta;
}

function validarPinche() {
  const fp = materiaActualPinches();
  if (fp.length === 0) return;
  const p = fp[currentPincheIndex % fp.length];
  const inputEl = document.getElementById('pinch-input');
  if (!inputEl) return;
  const val = inputEl.value.trim().toLowerCase();
  const fb = document.getElementById('pinch-feedback');
  if (!fb) return;
  fb.style.display = 'block';
  if (p.respostasAceitas.map(r => r.toLowerCase()).includes(val)) {
    fb.className = 'feedback correct';
    fb.innerText = '🎯 ¡Excelente! Estructura anatómica correctamente identificada.';
  } else {
    fb.className = 'feedback incorrect';
    fb.innerText = `❌ Incorrecto. Términos anatómicos válidos: ${p.respostasAceitas.join(', ')}`;
  }
}

function nextPinche() {
  const inputEl = document.getElementById('pinch-input');
  if (inputEl) inputEl.value = '';
  const fb = document.getElementById('pinch-feedback');
  if (fb) fb.style.display = 'none';
  const fp = materiaActualPinches();
  if (fp.length > 0) {
    currentPincheIndex = (currentPincheIndex + 1) % fp.length;
    loadPinche();
  }
}

// ============================================================
// ORAL / BOLILLAS
// ============================================================
function sortearOral() {
  const rawOrales = currentMateria === "TODAS"
    ? bancoDados.orales
    : bancoDados.orales.filter(b => b.materia === currentMateria);

  if (rawOrales.length === 0) {
    alert('No hay bolillas para la cátedra seleccionada.');
    return;
  }
  const o = rawOrales[Math.floor(Math.random() * rawOrales.length)];
  const card = document.getElementById('oral-card');
  if (card) card.style.display = 'block';
  document.getElementById('oral-materia').innerText = o.materia;
  const oFuente = document.getElementById('oral-fuente');
  if (oFuente) oFuente.innerHTML = `<i class="fa-solid fa-graduation-cap"></i> ${o.fuente || 'Bolillero UNLP'}`;
  document.getElementById('oral-bolilla').innerText = o.bolilla;
  document.getElementById('oral-caso').innerText = o.casoClinico;

  const chk = document.getElementById('oral-checklist');
  chk.innerHTML = '';
  o.checklist.forEach(item => {
    chk.innerHTML += `<label><input type="checkbox"> ${item}</label>`;
  });
}

// ============================================================
// INIT
// ============================================================
window.onload = () => {
  loadChoice();
  loadPinche();

  // Cerrar modal al hacer clic fuera
  const modal = document.getElementById('fragmento-modal');
  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) cerrarFragmento();
    });
  }
};
