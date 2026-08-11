/**
 * ALUMED OS - Atlas Histológico y Embriológico (FCM - UNLP 2026)
 * Compendio Completo de 40+ Preparados de la Cátedra de Citología, Histología y Embriología UNLP
 */

window.ATLAS_HISTOLOGICO_DATA = [
    // --- TEJIDO EPITELIAL ---
    {
        id: "tp1_mesotelio",
        materia: "Histología y Embriología",
        eje: "histo",
        tp: "TP 01 - Biología Celular y Técnica Histológica",
        titulo: "Epitelio Plano Simple (Mesotelio)",
        nomenclaturaOficial: "Epithelium simplex squamosum (Mesothelium)",
        muestra: "Mesenterio Humano (Extensión con Impregnación Argéntica de Nitrato de Plata y H&E)",
        tecnicaTincion: "Impregnación Argéntica (Nitrato de Plata) + H&E",
        enlaceVirtual: "https://histologyguide.com/slideview/MHS-281-pavement-epithelium/02-slide-1.html",
        tipoImagem: "imagem",
        urlImagem: "/static/atlas_histologico/assets/tejido conectivo laxo areolar.jpg",
        categoria: "epitelial",
        clavesDiagnosticas: [
            "Células pavimentosas aplanadas dispuestas en monocapa continua vista de cara o superficie.",
            "Núcleos celulares ovoides planos de cromatina densa/heterocromática vistos en proyección frontal.",
            "Límites intercelulares poligonales sinuosos evidenciados por precipitación de nitrato de plata en los complejos de unión."
        ],
        pinches: [
            {
                pinId: 1,
                x: 50,
                y: 42,
                titulo: "Núcleos Celulares Pavimentosos",
                pergunta: "Identificar la estructura celular ovoide de cromatina condensada observada de cara en el plano superficial.",
                respostasAceitas: ["núcleo plano", "nucleo plano", "núcleos planos", "nucleos planos", "núcleo de célula mesotelial"],
                conceptoClave: "Representa el núcleo aplanado ovoide de la célula mesotelial visto de superficie, caracterizado por heterocromatina marginal.",
                trampaCatedra: "No confundir los núcleos planos mesoteliales con los núcleos esféricos basófilos de linfocitos migratorios del estroma subyacente."
            }
        ],
        preguntasParcial: [
            {
                q: "¿Cuál es la función histofisiológica del mesotelio en las hojas serosas (peritoneo, pleura, pericardio)?",
                a: "Sintetizar y secretar el fluido seroso lubricante rico en hialuronato que previene la fricción mecánica entre las hojas visceral y parietal."
            }
        ]
    },
    {
        id: "tp2_epitelio_cilindrico",
        materia: "Histología y Embriología",
        eje: "histo",
        tp: "TP 02 - Tejido Epitelial de Revestimiento y Glandular",
        titulo: "Epitelio Cilíndrico Simple con Chapa Estriada y Células Caliciformes",
        nomenclaturaOficial: "Epithelium simplex columnare cum limbo striato et exocrinocytis caliciformibus",
        muestra: "Intestino Delgado / Yeyuno-Íleon (Corte Transversal H&E)",
        tecnicaTincion: "Hematoxilina y Eosina (H&E) — Opcional PAS para mucopolisacáridos",
        enlaceVirtual: "https://histologyguide.com/slideview/MH-016x-small-intestine/04-slide-1.html",
        tipoImagem: "imagem",
        urlImagem: "/static/atlas_histologico/assets/simples cilindrico con caliciforme.jpg",
        categoria: "epitelial",
        clavesDiagnosticas: [
            "Chapa estriada apical (microvellosidades apretadas alineadas de filamentos de actina) altamente refractil eosinófila.",
            "Células caliciformes (glándulas exocrinas unicelulares) con teca apical mucinógena pálida intercaladas homogéneamente.",
            "Núcleos ovoides eurocromáticos dispuestos regularmente en el tercio basal del citoplasma celular (polaridad celular estricta)."
        ],
        pinches: [
            {
                pinId: 1,
                x: 35,
                y: 28,
                titulo: "Chapa Estriada Apical (Limbus Striatus)",
                pergunta: "Identificar la especialización de la membrana plasmática apical indicada por el Pin 1 (borde continuo refractil).",
                respostasAceitas: ["chapa estriada", "chapa estriada apical", "microvellosidades", "microvellosidades apretadas", "limbo estriado"],
                conceptoClave: "Chapa estriada formada por microvellosidades paralelas ordenadas estabilizadas por villina y fimbrina para maximizar el área absortiva.",
                trampaCatedra: "En aparato respiratorio (tráquea) la especialización son cilios móviles; en intestino es chapa estriada."
            },
            {
                pinId: 2,
                x: 62,
                y: 45,
                titulo: "Célula Caliciforme (Exocrinocytus caliciformis)",
                pergunta: "Identificar la glándula unicelular exocrina mucosecretora indicada por el Pin 2.",
                respostasAceitas: ["célula caliciforme", "celula caliciforme", "células caliciformes", "celulas caliciformes"],
                conceptoClave: "Glándula unicelular merocrina cuya teca contiene gránulos de mucinógeno que al lavarse dejan citoplasma pálido.",
                trampaCatedra: "No confundir el espacio pálido de mucinógeno lavado con gotas lipídicas."
            }
        ],
        preguntasParcial: [
            {
                q: "¿Qué tinción histoquímica especial permite evidenciar en rojo magenta a las células caliciformes y a la chapa estriada?",
                a: "La reacción de PAS (Ácido Peryódico de Schiff), que oxida los grupos glicol de los mucopolisacáridos."
            }
        ]
    },

    // --- TEJIDO CONECTIVO ---
    {
        id: "tp3_conectivo_laxo",
        materia: "Histología y Embriología",
        eje: "histo",
        tp: "TP 03 - Tejido Conectivo Propiamente Dicho",
        titulo: "Tejido Conectivo Laxo Areolar",
        nomenclaturaOficial: "Textus conexivus laxus areolaris",
        muestra: "Estroma Subepitelial (Corte H&E)",
        tecnicaTincion: "Hematoxilina y Eosina (H&E)",
        enlaceVirtual: "https://histologyguide.com/",
        tipoImagem: "imagem",
        urlImagem: "/static/atlas_histologico/assets/tejido conectivo laxo areolar.jpg",
        categoria: "conectivo",
        clavesDiagnosticas: [
            "Predominio de sustancia fundamental amorfa hidratada rica en glucosaminoglicanos y proteoglicanos.",
            "Abundante variedad celular (fibroblastos, macrófagos, mastocitos, plasmocitos y linfocitos).",
            "Fibras de colágeno y elásticas dispuestas laxamente sin orientación preferencial."
        ],
        pinches: [],
        preguntasParcial: []
    },
    {
        id: "tp3_conectivo_denso_no_modelado",
        materia: "Histología y Embriología",
        eje: "histo",
        tp: "TP 03 - Tejido Conectivo Propiamente Dicho",
        titulo: "Tejido Conectivo Denso No Modelado (Dermis Profunda)",
        nomenclaturaOficial: "Textus conexivus densus irregularis",
        muestra: "Dermis Reticular de Piel Gruesa (H&E)",
        tecnicaTincion: "Hematoxilina y Eosina (H&E)",
        enlaceVirtual: "https://histologyguide.com/",
        tipoImagem: "imagem",
        urlImagem: "/static/atlas_histologico/assets/tejido conectivo denso no modelado.jpg",
        categoria: "conectivo",
        clavesDiagnosticas: [
            "Predominio masivo de haces gruesos de fibras de colágeno Tipo I entrelazados en múltiples direcciones.",
            "Resistencia mecánica multidireccional a la tracción.",
            "Escasas células (predominio de núcleos de fibroblastos alargados e inactivos o fibrocitos)."
        ],
        pinches: [],
        preguntasParcial: []
    },
    {
        id: "tp3_tendon_modelado",
        materia: "Histología y Embriología",
        eje: "histo",
        tp: "TP 03 - Tejido Conectivo Propiamente Dicho",
        titulo: "Tejido Conectivo Denso Modelado (Tendón)",
        nomenclaturaOficial: "Textus conexivus densus regularis (Tendo)",
        muestra: "Tendón de Mamífero (Corte Longitudinal H&E)",
        tecnicaTincion: "Hematoxilina y Eosina (H&E)",
        enlaceVirtual: "https://histologyguide.com/",
        tipoImagem: "imagem",
        urlImagem: "/static/atlas_histologico/assets/Tejido Conectivo Denso Modelado (Tendón).jpg",
        categoria: "conectivo",
        clavesDiagnosticas: [
            "Haces paralelos apretados de fibras de colágeno Tipo I alineados en la dirección de la tracción.",
            "Filas longitudinales de tendinocitos (fibroblastos especializados) con núcleos basófilos aplanados ordenados en 'filas de perlas'."
        ],
        pinches: [],
        preguntasParcial: []
    },
    {
        id: "tp3_adiposo_unilocular",
        materia: "Histología y Embriología",
        eje: "histo",
        tp: "TP 03 - Tejido Conectivo Especializado",
        titulo: "Tejido Adiposo Unilocular (Grasa Blanca)",
        nomenclaturaOficial: "Textus adiposus unilocularis",
        muestra: "Hipodermis / Tejido Celular Subcutáneo (H&E)",
        tecnicaTincion: "Hematoxilina y Eosina (H&E)",
        enlaceVirtual: "https://histologyguide.com/",
        tipoImagem: "imagem",
        urlImagem: "/static/atlas_histologico/assets/Tejido Adiposo Unilocular (Grasa Blanca).jpg",
        categoria: "conectivo",
        clavesDiagnosticas: [
            "Adipocitos esféricos grandes de 50-100 µm con apariencia en 'anillo de sello'.",
            "Gota lipídica única unilocular vaciada durante la inclusión técnica con solventes orgánicos.",
            "Núcleo plano periférico excéntrico rechazado hacia la membrana plasmática."
        ],
        pinches: [],
        preguntasParcial: []
    },
    {
        id: "tp3_plasmocitos",
        materia: "Histología y Embriología",
        eje: "histo",
        tp: "TP 03 - Células del Tejido Conectivo",
        titulo: "Células Plasmáticas (Plasmocitos)",
        nomenclaturaOficial: "Plasmocytus",
        muestra: "Frotis / Lámina Propia Digestiva (H&E)",
        tecnicaTincion: "Hematoxilina y Eosina (H&E)",
        enlaceVirtual: "https://histologyguide.com/",
        tipoImagem: "imagem",
        urlImagem: "/static/atlas_histologico/assets/Células Plasmáticas (Plasmocitos).jpg",
        categoria: "conectivo",
        clavesDiagnosticas: [
            "Células ovoides con núcleo excéntrico de heterocromatina en 'rueda de carro' o 'carátula de reloj'.",
            "Citoplasma intensamente basófilo por RER hiperdesarrollado con 'halo perinuclear' pálido correspondiente al Aparato de Golgi."
        ],
        pinches: [],
        preguntasParcial: []
    },
    {
        id: "tp3_mastocitos",
        materia: "Histología y Embriología",
        eje: "histo",
        tp: "TP 03 - Células del Tejido Conectivo",
        titulo: "Mastocitos (Células Cebadas)",
        nomenclaturaOficial: "Mastocytus",
        muestra: "Tejido Conectivo Perivascular (Azul de Toluidina)",
        tecnicaTincion: "Azul de Toluidina (Metacromasia)",
        enlaceVirtual: "https://histologyguide.com/",
        tipoImagem: "imagem",
        urlImagem: "/static/atlas_histologico/assets/Mastocitos (Células Cebadas).jpg",
        categoria: "conectivo",
        clavesDiagnosticas: [
            "Gránulos citoplasmáticos basófilos densos con propiedad de metacromasia (cambian el color del reactivo de azul a púrpura/rojo).",
            "Secretan histamina y heparina en respuestas alérgicas e inflamatorias."
        ],
        pinches: [],
        preguntasParcial: []
    },

    // --- CARTÍLAGO Y HUESO ---
    {
        id: "tp4_cartilago_hialino",
        materia: "Histología y Embriología",
        eje: "histo",
        tp: "TP 04 - Tejido Cartilaginoso y Óseo",
        titulo: "Cartílago Hialino y Pericondrio",
        nomenclaturaOficial: "Textus cartilagineus hyalinus",
        muestra: "Anillo Traqueal / Tabique Nasal (H&E)",
        tecnicaTincion: "Hematoxilina y Eosina (H&E)",
        enlaceVirtual: "https://histologyguide.com/",
        tipoImagem: "imagem",
        urlImagem: "/static/atlas_histologico/assets/cartilago.jpg",
        categoria: "cartilago",
        clavesDiagnosticas: [
            "Matriz cartilaginosa basófila vítrea homogénea rica en colágeno Tipo II y proteoglicanos (agrecano).",
            "Condrocitos alojados en lagunas (condroplastos) formando grupos isogénicos coronarios o axiles.",
            "Pericondrio fibroso externo e interno condrógeno."
        ],
        pinches: [],
        preguntasParcial: []
    },
    {
        id: "tp4_hueso_compacto",
        materia: "Histología y Embriología",
        eje: "histo",
        tp: "TP 04 - Tejido Cartilaginoso y Óseo",
        titulo: "Hueso Compacto Desgastado (Sistemas de Havers / Osteonas)",
        nomenclaturaOficial: "Textus osseus compactus (Osteonum)",
        muestra: "Diáfisis de Hueso Largo por Desgaste",
        tecnicaTincion: "Técnica de Desgaste (Seco sin fijador)",
        enlaceVirtual: "https://histologyguide.com/",
        tipoImagem: "imagem",
        urlImagem: "/static/atlas_histologico/assets/hueso.jpg",
        categoria: "hueso",
        clavesDiagnosticas: [
            "Osteonas o Sistemas de Havers constituidos por conducto central de Havers rodeado por 4 a 20 laminillas óseas concéntricas.",
            "Osteoplastos (lagunas óseas) con osteocitos conectados por canalículos calcóforos irradiados.",
            "Conductos transversales de Volkmann perforantes."
        ],
        pinches: [],
        preguntasParcial: []
    },

    // --- TEJIDO NERVIOSO ---
    {
        id: "tp6_medula_espinal",
        materia: "Histología y Embriología",
        eje: "histo",
        tp: "TP 06 - Tejido Nervioso",
        titulo: "Médula Espinal (Sustancia Gris y Blanca)",
        nomenclaturaOficial: "Medulla spinalis",
        muestra: "Corte Transversal de Médula Espinal (H&E / Impregnación Argéntica)",
        tecnicaTincion: "Hematoxilina y Eosina (H&E) / Nissl",
        enlaceVirtual: "https://histologyguide.com/",
        tipoImagem: "imagem",
        urlImagem: "/static/atlas_histologico/assets/medula espinal.jpg",
        categoria: "nervioso",
        clavesDiagnosticas: [
            "Sustancia gris central en forma de 'H' o mariposa con motoneuronas alfa multipolares gigantes en el asta anterior.",
            "Sustancia blanca periférica con axones mielinizados organizados en cordones anteriores, laterales y posteriores.",
            "Conducto del epéndimo central revestido por ependimocitos cúbicos simple."
        ],
        pinches: [],
        preguntasParcial: []
    },
    {
        id: "tp6_cerebelo",
        materia: "Histología y Embriología",
        eje: "histo",
        tp: "TP 06 - Tejido Nervioso",
        titulo: "Corteza Cerebelosa (Células de Purkinje)",
        nomenclaturaOficial: "Cortex cerebelli",
        muestra: "Cerebelo Humano (Impregnación Argéntica de Cajal / H&E)",
        tecnicaTincion: "Impregnación Argéntica / H&E",
        enlaceVirtual: "https://histologyguide.com/",
        tipoImagem: "imagem",
        urlImagem: "/static/atlas_histologico/assets/cerebelo.png",
        categoria: "nervioso",
        clavesDiagnosticas: [
            "Tres capas corticales distintas: Capa Molecular externa pálida, Capa de Células de Purkinje intermedia y Capa Granulosa interna muy densa.",
            "Células de Purkinje piriformes gigantes en fila única con árbol dendrítico frondoso orientado hacia la capa molecular."
        ],
        pinches: [],
        preguntasParcial: []
    },
    {
        id: "tp6_nervio_periferico",
        materia: "Histología y Embriología",
        eje: "histo",
        tp: "TP 06 - Tejido Nervioso",
        titulo: "Nervio Periférico (Corte Transversal y Longitudinal)",
        nomenclaturaOficial: "Nervus periphericus",
        muestra: "Nervio Periférico (H&E / Tetróxido de Osmio)",
        tecnicaTincion: "Hematoxilina y Eosina (H&E)",
        enlaceVirtual: "https://histologyguide.com/",
        tipoImagem: "imagem",
        urlImagem: "/static/atlas_histologico/assets/nervio periferico.jpg",
        categoria: "nervioso",
        clavesDiagnosticas: [
            "Organización en fascículos protegidos por Epineuro (externo), Perineuro (laminar denso) y Endoneuro (alrededor de cada axón).",
            "Axones mielinizados rodeados por vaina de mielina de células de Schwann (imagen en 'huevo frito' o anillo pálido en corte transversal)."
        ],
        pinches: [],
        preguntasParcial: []
    },
    {
        id: "tp6_ganglio_periferico",
        materia: "Histología y Embriología",
        eje: "histo",
        tp: "TP 06 - Tejido Nervioso",
        titulo: "Ganglio Nervioso Periférico",
        nomenclaturaOficial: "Ganglion periphericum",
        muestra: "Ganglio Nervioso (H&E)",
        tecnicaTincion: "Hematoxilina y Eosina (H&E)",
        enlaceVirtual: "https://histologyguide.com/",
        tipoImagem: "imagem",
        urlImagem: "/static/atlas_histologico/assets/ganglio periferico.jpg",
        categoria: "nervioso",
        clavesDiagnosticas: [
            "Somas neuronales grandes pseudomonopolares esféricos rodeados por una corona continua de células satélite (anficitos).",
            "Fascículos de fibras de paso mielínicas interconectadas."
        ],
        pinches: [],
        preguntasParcial: []
    },

    // --- TEJIDO MUSCULAR ---
    {
        id: "tp7_musculo_esqueletico_1",
        materia: "Histología y Embriología",
        eje: "histo",
        tp: "TP 07 - Tejido Muscular",
        titulo: "Tejido Muscular Estriado Esquelético (Corte Longitudinal)",
        nomenclaturaOficial: "Textus muscularis striatus sceletalis",
        muestra: "Músculo Estriado Esquelético (H&E)",
        tecnicaTincion: "Hematoxilina y Eosina (H&E)",
        enlaceVirtual: "https://histologyguide.com/",
        tipoImagem: "imagem",
        urlImagem: "/static/atlas_histologico/assets/muscuo esqueletico 1.jpg",
        categoria: "muscular",
        clavesDiagnosticas: [
            "Fibras musculares cilíndricas multinucleadas largas con estriaciones transversales periódicas (bandas A oscuras y bandas I claras).",
            "Núcleos ovoides planos periféricos dispuestos inmediatamente debajo del sarcolema."
        ],
        pinches: [],
        preguntasParcial: []
    },
    {
        id: "tp7_musculo_esqueletico_2",
        materia: "Histología y Embriología",
        eje: "histo",
        tp: "TP 07 - Tejido Muscular",
        titulo: "Tejido Muscular Estriado Esquelético (Corte Transversal)",
        nomenclaturaOficial: "Textus muscularis striatus sceletalis (Sectio transversalis)",
        muestra: "Músculo Esquelético en Fascículos (H&E)",
        tecnicaTincion: "Hematoxilina y Eosina (H&E)",
        enlaceVirtual: "https://histologyguide.com/",
        tipoImagem: "imagem",
        urlImagem: "/static/atlas_histologico/assets/musculo esqueletico 2.jpg",
        categoria: "muscular",
        clavesDiagnosticas: [
            "Perfiles poligonales de miocitos con núcleos periféricos basófilos.",
            "Organización fascicular envuelta por perimisio y endomisio conectivo con capilares."
        ],
        pinches: [],
        preguntasParcial: []
    },
    {
        id: "tp7_musculo_cardiaco",
        materia: "Histología y Embriología",
        eje: "histo",
        tp: "TP 07 - Tejido Muscular",
        titulo: "Tejido Muscular Estriado Cardíaco (Discos Intercalares)",
        nomenclaturaOficial: "Textus muscularis striatus cardiacus",
        muestra: "Miocardio Ventricular (H&E / Hematoxilina Férrica)",
        tecnicaTincion: "Hematoxilina y Eosina (H&E)",
        enlaceVirtual: "https://histologyguide.com/",
        tipoImagem: "imagem",
        urlImagem: "/static/atlas_histologico/assets/musculo cardiaco.jpg",
        categoria: "muscular",
        clavesDiagnosticas: [
            "Miocardiocitos ramificados o apantallados con 1 o 2 núcleos centrales ovoides y espacio perinuclear claro.",
            "Discos intercalares o trazos escaleriformes (complejos de unión desmosomas/fascia adherens y uniones comunicantes nexos)."
        ],
        pinches: [],
        preguntasParcial: []
    },
    {
        id: "tp7_muscular_externa",
        materia: "Histología y Embriología",
        eje: "histo",
        tp: "TP 07 - Tejido Muscular",
        titulo: "Tejido Muscular Liso (Capa Muscular Orgánica)",
        nomenclaturaOficial: "Textus muscularis nonstriatus (Smooth Muscle)",
        muestra: "Pared Intestinal / Capa Muscular Externa (H&E)",
        tecnicaTincion: "Hematoxilina y Eosina (H&E)",
        enlaceVirtual: "https://histologyguide.com/",
        tipoImagem: "imagem",
        urlImagem: "/static/atlas_histologico/assets/muscular externa.jpg",
        categoria: "muscular",
        clavesDiagnosticas: [
            "Células fusiformes involuntarias sin estriaciones transversales.",
            "Núcleo único central alargado en 'sacacorchos' o habano durante la contracción.",
            "Disposición en capas ortogonales (Circular Interna y Longitudinal Externa)."
        ],
        pinches: [],
        preguntasParcial: []
    },

    // --- SISTEMA CARDIOVASCULAR Y LINFOIDE ---
    {
        id: "tp8_arteria_elastica",
        materia: "Histología y Embriología",
        eje: "histo",
        tp: "TP 08 - Sistema Cardiovascular",
        titulo: "Arteria Elástica de Gran Calibre (Aorta / Pulmonar)",
        nomenclaturaOficial: "Arteria elastotypica (Aorta)",
        muestra: "Pared Aórtica (H&E / Orceína para elastina)",
        tecnicaTincion: "Orceína / H&E",
        enlaceVirtual: "https://histologyguide.com/",
        tipoImagem: "imagem",
        urlImagem: "/static/atlas_histologico/assets/arteria 1.jpg",
        categoria: "cardiovascular",
        clavesDiagnosticas: [
            "Túnica media sumamente desarrollada compuesta por 40 a 70 láminas elásticas concéntricas fenestradas onduladas.",
            "Células musculares lisas dispuestas oblicuamente entre las láminas elásticas."
        ],
        pinches: [],
        preguntasParcial: []
    },
    {
        id: "tp8_zoom_arteria",
        materia: "Histología y Embriología",
        eje: "histo",
        tp: "TP 08 - Sistema Cardiovascular",
        titulo: "Detalle de Túnica Íntima y Endotelio Arterial",
        nomenclaturaOficial: "Tunica intima arterialis",
        muestra: "Pared Arterial a Gran Aumento (H&E)",
        tecnicaTincion: "Hematoxilina y Eosina (H&E)",
        enlaceVirtual: "https://histologyguide.com/",
        tipoImagem: "imagem",
        urlImagem: "/static/atlas_histologico/assets/zoom arteria tunica intima.jpg",
        categoria: "cardiovascular",
        clavesDiagnosticas: [
            "Endotelio plano simple continuo apoyado en capa subendotelial conectiva.",
            "Membrana Elástica Interna destacada como banda refractil serpentina ondulada."
        ],
        pinches: [],
        preguntasParcial: []
    },
    {
        id: "tp8_ganglio_linfatico",
        materia: "Histología y Embriología",
        eje: "histo",
        tp: "TP 08 - Órganos Linfoides",
        titulo: "Ganglio Linfático (Nodus Lymphoideus)",
        nomenclaturaOficial: "Nodus lymphoideus / Lymphonodus",
        muestra: "Ganglio Linfático (H&E)",
        tecnicaTincion: "Hematoxilina y Eosina (H&E)",
        enlaceVirtual: "https://histologyguide.com/",
        tipoImagem: "imagem",
        urlImagem: "/static/atlas_histologico/assets/ganglio linfatico.jpg",
        categoria: "linfoide",
        clavesDiagnosticas: [
            "Corteza externa con folículos linfoides primarios y secundarios (centro germinativo claro de proliferación B).",
            "Paracorteza dependiente de Linfocitos T y Médula con cordones y senos medulares."
        ],
        pinches: [],
        preguntasParcial: []
    },
    {
        id: "tp8_bazo_general",
        materia: "Histología y Embriología",
        eje: "histo",
        tp: "TP 08 - Órganos Linfoides",
        titulo: "Bazo (Pulpa Blanca y Pulpa Roja)",
        nomenclaturaOficial: "Splen / Lien",
        muestra: "Bazo Humano (H&E)",
        tecnicaTincion: "Hematoxilina y Eosina (H&E)",
        enlaceVirtual: "https://histologyguide.com/",
        tipoImagem: "imagem",
        urlImagem: "/static/atlas_histologico/assets/bazo.jpg",
        categoria: "linfoide",
        clavesDiagnosticas: [
            "Órgano linfoide encapsulado sin división en corteza y médula.",
            "Pulpa Blanca (nodulillos de Malpighi con arteriola central excéntrica y vaina linfática periarterial PALS).",
            "Pulpa Roja (cordones de Billroth y senos venosos esplénicos para hemocateresis)."
        ],
        pinches: [],
        preguntasParcial: []
    },
    {
        id: "tp8_bazo_pulpa_blanca",
        materia: "Histología y Embriología",
        eje: "histo",
        tp: "TP 08 - Órganos Linfoides",
        titulo: "Detalle de Pulpa Blanca Esplénica y Arteriola Central",
        nomenclaturaOficial: "Pulpa alba splenica",
        muestra: "Nodulillo Linfoide Esplénico a Gran Aumento (H&E)",
        tecnicaTincion: "Hematoxilina y Eosina (H&E)",
        enlaceVirtual: "https://histologyguide.com/",
        tipoImagem: "imagem",
        urlImagem: "/static/atlas_histologico/assets/bazo pulpa blanca.jpg",
        categoria: "linfoide",
        clavesDiagnosticas: [
            "Arteriola folicular excéntrica característica indispensable para diferenciar el bazo de un folículo ganglionar.",
            "Corona folicular y zona marginal rica en macrófagos y células presentadoras de antígeno."
        ],
        pinches: [],
        preguntasParcial: []
    },
    {
        id: "tp8_timo_hassall",
        materia: "Histología y Embriología",
        eje: "histo",
        tp: "TP 08 - Órganos Linfoides Primarios",
        titulo: "Timo y Corpúsculos de Hassall",
        nomenclaturaOficial: "Thymus (Corpusculum thymicum)",
        muestra: "Médula Tímica (H&E)",
        tecnicaTincion: "Hematoxilina y Eosina (H&E)",
        enlaceVirtual: "https://histologyguide.com/",
        tipoImagem: "imagem",
        urlImagem: "/static/atlas_histologico/assets/corpusculo de hassal timo.jpg",
        categoria: "linfoide",
        clavesDiagnosticas: [
            "Organización lobulillar con corteza basófila oscura (timocitos apretados) y médula clara.",
            "Corpúsculos de Hassall o tímicos en la médula: estructuras concéntricas epidermoides eosinófilas formadas por células epitelio-reticulares Tipo VI queratinizadas."
        ],
        pinches: [],
        preguntasParcial: []
    }
];

if (typeof bancoDados !== 'undefined') {
    bancoDados.atlas = window.ATLAS_HISTOLOGICO_DATA;
}
