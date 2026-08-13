/**
 * ALUMED OS - Atlas Histológico y Embriológico (FCM - UNLP 2026)
 * Dataset de Máximo Rigor Científico y Criterios Histológicos Oficiales
 * Cátedra de Citología, Histología y Embriología — FCM UNLP
 */

window.ATLAS_HISTOLOGICO_DATA = [
    {
        id: "tp1_mesotelio",
        materia: "Histología y Embriología",
        eje: "histo",
        tp: "TP 01 - Biología Celular y Técnica Histológica",
        titulo: "Epitelio Plano Simple (Mesotelio)",
        nomenclaturaOficial: "Epithelium simplex squamosum (Mesothelium)",
        muestra: "Mesenterio Humano (Preparado por Extensión con Impregnación Argéntica de Nitrato de Plata y H&E)",
        tecnicaTincion: "Impregnación Argéntica (Nitrato de Plata) + Hematoxilina y Eosina (H&E)",
        enlaceVirtual: "https://histologyguide.com/slideview/MHS-281-pavement-epithelium/02-slide-1.html?x=5086&y=4287&z=50.000",
        tipoImagem: "imagem",
        urlImagem: "https://histologyguide.com/slideimages/MHS-281-pavement-epithelium/02-slide-1.jpg",
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
                a: "Sintetizar y secretar el fluido seroso lubricante rico en hialuronato que previene la fricción mecánica entre las hojas visceral y parietal durante la motilidad de los órganos cavitarios."
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
        enlaceVirtual: "https://histologyguide.com/slideview/MH-016x-small-intestine/04-slide-1.html?x=20504&y=12614&z=25.000",
        tipoImagem: "imagem",
        urlImagem: "https://histologyguide.com/slideimages/MH-016x-small-intestine/04-slide-1.jpg",
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
                trampaCatedra: "En aparato respiratorio (tráquea) la especialización son cilios móviles (microtúbulos 9+2); en intestino es chapa estriada (microfilamentos de actina)."
            },
            {
                pinId: 2,
                x: 62,
                y: 45,
                titulo: "Célula Caliciforme (Exocrinocytus caliciformis)",
                pergunta: "Identificar la glándula unicelular exocrina mucosecretora indicada por el Pin 2.",
                respostasAceitas: ["célula caliciforme", "celula caliciforme", "células caliciformes", "celulas caliciformes", "exocrinocytus caliciformis"],
                conceptoClave: "Glándula unicelular merocrina cuya teca contiene gránulos de mucinógeno que al lavarse en la técnica de rutina dejan el citoplasma pálido/negativo.",
                trampaCatedra: "No confundir el espacio pálido de mucinógeno lavado con gotas lipídicas ni con artefactos de retracción técnica."
            }
        ],
        preguntasParcial: [
            {
                q: "¿Qué tinción histoquímica especial permite evidenciar en rojo magenta a las células caliciformes y a la chapa estriada?",
                a: "La reacción de PAS (Ácido Peryódico de Schiff), que oxida los grupos glicol vecinos de los mucopolisacáridos y del glucocálix formando aldehídos reactivos al reactivo de Schiff."
            }
        ]
    },
    {
        id: "tp3_tendon_modelado",
        materia: "Histología y Embriología",
        eje: "histo",
        tp: "TP 03 - Tejido Conectivo Propiamente Dicho",
        titulo: "Tejido Conectivo Denso Modelado o Regular (Tendón)",
        nomenclaturaOficial: "Textus conexivus densus regularis (Tendo)",
        muestra: "Tendón de Mamífero (Corte Longitudinal H&E)",
        tecnicaTincion: "Hematoxilina y Eosina (H&E)",
        enlaceVirtual: "https://histologyguide.com/slideview/MH-032-tendon/02-slide-1.html",
        tipoImagem: "imagem",
        urlImagem: "https://histologyguide.com/slideimages/MH-032-tendon/02-slide-1.jpg",
        categoria: "conectivo",
        clavesDiagnosticas: [
            "Haces gruesos de fibras de colágeno tipo I paralelos orientados estrictamente en el eje de tracción mecánica.",
            "Filas alineadas longitudinales de tendinocitos (fibroblastos especializados) con núcleos heterocromáticos aplanados en forma de hendidura.",
            "Escasa sustancia fundamental amorfa e irrigación vascular mínima intra-fascicular (nutrición por endotendón)."
        ],
        pinches: [
            {
                pinId: 1,
                x: 48,
                y: 38,
                titulo: "Haces Paralelos de Colágeno Tipo I",
                pergunta: "Identificar las fibras proteicas gruesas eosinófilas dispuestas en haces paralelos compactos.",
                respostasAceitas: ["fibras de colageno", "fibras de colágeno", "colageno tipo i", "colageno", "haces de colageno"],
                conceptoClave: "Fibras de colágeno tipo I ensambladas en tropocolágeno lineal que otorgan resistencia mecánica a las fuerzas de tracción unidireccionales.",
                trampaCatedra: "Diferenciar la orientación estrictamente paralela del tendón de la disposición entrecruzada tridimensional de la dermis reticular (conectivo denso no modelado)."
            },
            {
                pinId: 2,
                x: 72,
                y: 60,
                titulo: "Núcleos de Tendinocitos (Fibroblastos alineados)",
                pergunta: "Identificar los núcleos aplanados basófilos dispuestos en hileras longitudinales entre las fibras.",
                respostasAceitas: ["tendinocito", "tendinocitos", "fibroblasto", "fibroblastos", "núcleos de tendinocitos"],
                conceptoClave: "Los tendinocitos son fibroblastos maduros aplanados que sintetizan el colágeno tipo I y presentan prolongaciones citoplasmáticas en alera.",
                trampaCatedra: "Observar que los núcleos aparecen 'aplastados' longitudinalmente entre los haces colágenos, a diferencia del conectivo laxo donde los fibroblastos son estrellados."
            }
        ],
        preguntasParcial: [
            {
                q: "¿Por qué el tendón presenta una intensa acidofilia/eosinofilia al microscopio óptico?",
                a: "Debido a la alta densidad de cadenas polipeptídicas de colágeno tipo I ricas en aminoácidos con grupos amino libres (básicos) que reaccionan con la eosina (colorante ácido)."
            }
        ]
    },
    {
        id: "tp4_hueso_osteona",
        materia: "Histología y Embriología",
        eje: "histo",
        tp: "TP 04 - Tejido Cartilaginoso y Óseo",
        titulo: "Hueso Compacto Desgastado (Sistema de Havers / Osteona)",
        nomenclaturaOficial: "Systemum Haversi / Osteonum (Textus osseus compactus)",
        muestra: "Corte Transversal de Diáfisis de Hueso Largo Desgastado por Fricción (Sin Descalcificar)",
        tecnicaTincion: "Desgaste Seco por Fricción / Montaje en Bálsamo (Muestra Histológica Seca)",
        enlaceVirtual: "https://histologyguide.com/slideview/MH-044-ground-bone/05-slide-1.html?x=21030&y=11431&z=50.000",
        tipoImagem: "imagem",
        urlImagem: "https://histologyguide.com/slideimages/MH-044-ground-bone/05-slide-1.jpg",
        categoria: "especializado",
        clavesDiagnosticas: [
            "Conducto de Havers (Canalis centralis) vascular neutro rodeado concéntricamente por 4 a 20 laminillas óseas calcificadas.",
            "Osteoplastos o lagunas óseas lenticulares oscuras dispuestas concéntricamente entre las laminillas de matriz extracelular mineralizada.",
            "Canalículos calcóforos radiales finos ramificados que conectan las lagunas adyacentes con el conducto vascular central."
        ],
        pinches: [
            {
                pinId: 1,
                x: 50,
                y: 50,
                titulo: "Conducto de Havers Central (Canalis centralis)",
                pergunta: "Identificar el canal vascular central de la osteona rodeado por laminillas concéntricas.",
                respostasAceitas: ["conducto de havers", "canal de havers", "conducto haversiano", "havers", "canalis centralis"],
                conceptoClave: "Aloja capilares sanguíneos continuos y fibras nerviosas amielínicas revestidos por endostio para la nutrición de la osteona.",
                trampaCatedra: "No confundir los conductos de Havers (longitudinales paralelos al eje del hueso) con los conductos perforantes de Volkmann (transversales u oblicuos sin laminillas concéntricas)."
            }
        ],
        preguntasParcial: [
            {
                q: "¿Cómo se comunican metabólica y funcionalmente los osteocitos alojados en lagunas distantes dentro de la osteona?",
                a: "A través de las prolongaciones citoplasmáticas que discurren por los canalículos calcóforos, las cuales están interconectadas mediante uniones comunicantes o en hendidura (gap junction / conexinas)."
            }
        ]
    },
    {
        id: "tp5_medula_espinal",
        materia: "Histología y Embriología",
        eje: "histo",
        tp: "TP 05 - Tejido Nervioso y Sistema Nervioso Central",
        titulo: "Médula Espinal (Sustancia Gris y Sustancia Blanca)",
        nomenclaturaOficial: "Medulla spinalis (Substantia grisea et substantia alba)",
        muestra: "Médula Espinal de Mamífero (Corte Transversal H&E)",
        tecnicaTincion: "Hematoxilina y Eosina (H&E) — Opcional Impregnación de Nissl / Klüver-Barrera",
        enlaceVirtual: "https://histologyguide.com/slideview/MHS-240-spinal-cord/06-slide-1.html?x=45000&y=28000&z=50.000",
        tipoImagem: "imagem",
        urlImagem: "https://histologyguide.com/slideimages/MHS-240-spinal-cord/06-slide-1.jpg",
        categoria: "nervioso",
        clavesDiagnosticas: [
            "Sustancia gris central en disposición de 'H' o mariposa rodeando al epéndimo (conducto central ependimario).",
            "Motoneuronas multipolares somáticas gigantes (alfa) en el asta anterior de la sustancia gris con gránulos de Nissl basófilos.",
            "Sustancia blanca periférica constituida por axones mielínicos rodeados de un halo claro artefactual por lavado de la vaina de mielina."
        ],
        pinches: [
            {
                pinId: 1,
                x: 42,
                y: 56,
                titulo: "Motoneurona Multipolar Somática (Asta Anterior)",
                pergunta: "Identificar el soma neuronal multipolar gigante con gránulos de Nissl ubicado en el asta anterior de la sustancia gris.",
                respostasAceitas: ["motoneurona", "motoneurona multipolar", "neurona motora", "motoneurona alfa", "soma neuronal multipolar"],
                conceptoClave: "Neurona motora somática eferente multipolar con pericarión estrellado, núcleo grande vesicular eucromático y nucléolo prominente.",
                trampaCatedra: "La sustancia de Nissl (RER) se distribuye en todo el pericarión y dendritas, pero está rigurosamente ausente en el cono axónico (cono de implantación)."
            }
        ],
        preguntasParcial: [
            {
                q: "¿Qué estructura ultraestructural representa la sustancia de Nissl visible al microscopio óptico?",
                a: "Corresponde a masivos cúmulos paralelos de Retículo Endoplásmico Rugoso (RER) y polirribosomas libres dedicados a la intensa síntesis de neurotransmisores y proteínas de citoesqueleto."
            }
        ]
    },
    {
        id: "tp6_musculo_cardiaco",
        materia: "Histología y Embriología",
        eje: "histo",
        tp: "TP 06 - Tejido Muscular Estriado y Liso",
        titulo: "Tejido Muscular Estriado Cardíaco (Miocardio)",
        nomenclaturaOficial: "Textus muscularis striatus cardiacus (Myocardiocytus)",
        muestra: "Corazón Humano (Corte Longitudinal H&E)",
        tecnicaTincion: "Hematoxilina y Eosina (H&E)",
        enlaceVirtual: "https://histologyguide.com/slideview/MH-054-cardiac-muscle/04-slide-1.html?x=35000&y=25000&z=75.000",
        tipoImagem: "imagem",
        urlImagem: "https://histologyguide.com/slideimages/MH-054-cardiac-muscle/04-slide-1.jpg",
        categoria: "muscular",
        clavesDiagnosticas: [
            "Miocardiocitos ramificados en aparente pantalón con 1 o 2 núcleos centrales ovoides eucromáticos.",
            "Discos intercalares o trazos escaleriformes transversales fuertemente eosinófilos en las uniones intercelulares.",
            "Abundante tejido conectivo intersticial (endomisio) altamente vascularizado con capilares fenestrados."
        ],
        pinches: [
            {
                pinId: 1,
                x: 55,
                y: 48,
                titulo: "Disco Intercalar / Trazo Escaleriforme",
                pergunta: "Identificar la estructura de unión escalar transversal propia del tejido cardíaco.",
                respostasAceitas: ["disco intercalar", "discos intercalares", "banda escaleriforme", "trazo escaleriforme", "discus intercalatus"],
                conceptoClave: "Sitio de acoplamiento mecánico y eléctrico formado por componente transversal (fascia adherens y desmosomas) y componente longitudinal (uniones comunicantes gap).",
                trampaCatedra: "No confundir el núcleo central único del miocardiocito con los múltiples núcleos subsarcolemales periféricos de la fibra muscular esquelética."
            }
        ],
        preguntasParcial: [
            {
                q: "¿Cuál es la función histofisiológica del componente longitudinal del disco intercalar?",
                a: "Contener las uniones en hendidura o comunicantes (gap / conexones) que proveen baja resistencia eléctrica para la rápida propagación del potencial de acción acoplando funcionalmente a los miocardiocitos en un sincitio funcional."
            }
        ]
    },
    {
        id: "tp7_ganglio_linfatico",
        materia: "Histología y Embriología",
        eje: "histo",
        tp: "TP 07 - Orgános Linfoide y Sistema Inmune",
        titulo: "Ganglio Linfático (Nodus Lymphoideus)",
        nomenclaturaOficial: "Nodus lymphoideus / Lymphonodus",
        muestra: "Ganglio Linfático Humano (Corte Histológico H&E)",
        tecnicaTincion: "Hematoxilina y Eosina (H&E)",
        enlaceVirtual: "https://histologyguide.com/slideview/MH-082-lymph-node/02-slide-1.html",
        tipoImagem: "imagem",
        urlImagem: "https://histologyguide.com/slideimages/MH-082-lymph-node/02-slide-1.jpg",
        categoria: "linfoide",
        clavesDiagnosticas: [
            "Cápsula de tejido conectivo denso no modelado con seno subcapsular marginal inmediatamente por debajo.",
            "Corteza externa rica en folículos linfoides secundarios (centro germinativo claro y manto/corona oscura de linfocitos B).",
            "Paracorteza profunda timodependiente (linfocitos T) y médula interna con cordones y senos medulares."
        ],
        pinches: [
            {
                pinId: 1,
                x: 30,
                y: 25,
                titulo: "Seno Subcapsular Marginal",
                pergunta: "Identificar el espacio linfático subcapsular continuo revestido por endotelio incompleto.",
                respostasAceitas: ["seno subcapsular", "seno marginal", "seno subcapsular marginal", "sinus subcapsularis"],
                conceptoClave: "Primer espacio de filtración linfática al que drenan los vasos linfáticos aferentes con presencia de macrófagos fijos.",
                trampaCatedra: "Diferenciar el ganglio linfático (órgano encapsulado con corteza periférica y médula central) del bazo (pulpa blanca y pulpa roja sin corteza)."
            }
        ],
        preguntasParcial: [
            {
                q: "¿Qué tipo celular y vaso sanguíneo especializado caracterizan a la paracorteza del ganglio linfático?",
                a: "Dominan los Linfocitos T reactivos e inmunocompetentes y las Vénulas de Endotelio Alto (HEV / High Endothelial Venules) encargadas del extravasamiento por diapedesis de los linfocitos circulantes."
            }
        ]
    },
    {
        id: "tp8_aorta_elastica",
        materia: "Histología y Embriología",
        eje: "histo",
        tp: "TP 08 - Sistema Cardiovascular y Vasos Sanguíneos",
        titulo: "Arteria Elástica de Gran Calibre (Aorta)",
        nomenclaturaOficial: "Arteria elastotypica (Aorta)",
        muestra: "Aorta Humana (Corte Transversal con Tinción de Orceína / H&E)",
        tecnicaTincion: "Tinción de Orceína para Fibras Elásticas + H&E",
        enlaceVirtual: "https://histologyguide.com/slideview/MH-065-aorta/02-slide-1.html",
        tipoImagem: "imagem",
        urlImagem: "https://histologyguide.com/slideimages/MH-065-aorta/02-slide-1.jpg",
        categoria: "cardiovascular",
        clavesDiagnosticas: [
            "Túnica media sumamente desarrollada compuesta por 40 a 70 láminas elásticas concéntricas fenestradas onduladas.",
            "Células musculares lisas dispuestas oblicuamente entre las láminas elásticas responsables de sintetizar la elastina.",
            "Túnica adventicia delgada con presencia de vasa vasorum e irrigación nutricia para la mitad externa de la media."
        ],
        pinches: [
            {
                pinId: 1,
                x: 50,
                y: 45,
                titulo: "Láminas Elásticas Concéntricas Fenestradas",
                pergunta: "Identificar las estructuras laminares onduladas teñidas de pardo/violáceo que conforman la túnica media.",
                respostasAceitas: ["laminas elásticas", "láminas elásticas", "laminas elasticas", "fibras elasticas", "lamellae elasticae"],
                conceptoClave: "Láminas de elastina fenestrada sintetizadas por miocitos lisos que amortiguan hidráulicamente la sístole cardíaca.",
                trampaCatedra: "En orceína las láminas elásticas destacan como bandas onduladas oscuras; no confundir con fibras de colágeno."
            }
        ],
        preguntasParcial: [
            {
                q: "¿Cómo se denomina el fenómeno hemodinámico que permite a las láminas elásticas mantener un flujo sanguíneo anterógrado continuo en diástole?",
                a: "Efecto Windkessel o acoplamiento elástico de la aorta."
            }
        ]
    },
    {
        id: "tp9_frotis_sangre",
        materia: "Histología y Embriología",
        eje: "histo",
        tp: "TP 09 - Sangre, Hematopoyesis y Elementos Figurados",
        titulo: "Frotis de Sangre Periférica Humana",
        nomenclaturaOficial: "Extensum sanguinis (Erythrocytus et Leucocytus)",
        muestra: "Extendido o Frotis de Sangre Humana en Capa Fina",
        tecnicaTincion: "Coloración Hematológica de Romanowsky (Giemsa / Wright / May-Grünwald)",
        enlaceVirtual: "https://histologyguide.com/galleryview/07-peripheral-blood.html",
        tipoImagem: "imagem",
        urlImagem: "https://histologyguide.com/slideimages/MHS-277-blood-smear/01-slide-1.jpg",
        categoria: "sangre",
        clavesDiagnosticas: [
            "Predominio masivo de eritrocitos anucleados discoidales bicóncavos de 7.5 µm con palidez central por concentración hemoglobínica.",
            "Leucocitos granulocitos (Neutrófilos multilobulados 3-5 lób., Eosinófilos bilobulados con gránulos eosinófilos refractiles).",
            "Agranulocitos (Linfocitos de núcleo redondo denso y escaso citoplasma basófilo) y Plaquetas anucleadas (trombocitos)."
        ],
        pinches: [
            {
                pinId: 1,
                x: 40,
                y: 50,
                titulo: "Eritrocito Humano Anucleado (Erythrocytus)",
                pergunta: "Identificar el elemento figurado anucleado bicóncavo utilizado como 'micrómetro de campo' histológico.",
                respostasAceitas: ["eritrocito", "eritrocitos", "glóbulo rojo", "globulo rojo", "hematie", "erythrocytus"],
                conceptoClave: "Célula anucleada sin orgánulos repleta de hemoglobina con diámetro constante de 7.5 a 7.8 µm.",
                trampaCatedra: "Los eritrocitos de mamíferos son anucleados; los eritrocitos nucleados en el humano adulto representan un hallazgo patológico (eritroblastos circulantes)."
            }
        ],
        preguntasParcial: [
            {
                q: "¿Qué porcentaje relativo normal representan los leucocitos neutrófilos en la fórmula leucocitaria relativa del adulto?",
                a: "Representan entre el 55% y el 70% del total de leucocitos sanguíneos circulantes."
            }
        ]
    },
    {
        id: "tp12_placenta_anexos",
        materia: "Histología y Embriología",
        eje: "embrio",
        tp: "TP 12 - Embriología: Placenta, Cordón Umbilical y Anexos Feto-Maternos",
        titulo: "Placenta Humana a Término y Circulación Umbilical",
        nomenclaturaOficial: "Placenta hemochorialis et funiculus umbilicalis",
        muestra: "Placenta Humana a Término con Vellosidades Coriónicas Libres y Cordón Umbilical (H&E)",
        tecnicaTincion: "Hematoxilina y Eosina (H&E)",
        enlaceVirtual: "https://histologyguide.com/galleryview/14-gastrointestinal-tract.html",
        tipoImagem: "imagem",
        urlImagem: "https://histologyguide.com/slideimages/MH-148-placenta/01-slide-1.jpg",
        categoria: "embrio",
        clavesDiagnosticas: [
            "Cordón umbilical con 2 arterias umbilicales (sangre desoxigenada fetal) y 1 vena umbilical única (sangre oxigenada fetal) inmersos en Gelatina de Wharton.",
            "Vellosidades coriónicas terciarias a término sumergidas en el espacio intervelloso lleno de sangre materna (placenta hemocorial).",
            "Barrera placentaria a término delgada formada por sincitiotrofoblasto, endotelio capilar fetal y membrana basal fusionada."
        ],
        pinches: [
            {
                pinId: 1,
                x: 52,
                y: 48,
                titulo: "Vena Umbilical Única (Vena umbilicalis)",
                pergunta: "Identificar el vaso umbilical único de pared amplia que transporta sangre rica en O2 y nutrientes hacia el embrión/feto.",
                respostasAceitas: ["vena umbilical", "la vena umbilical", "veia umbilical", "vena umbilicalis"],
                conceptoClave: "Vaso funcional único que conduce sangre arterial oxigenada proveniente de los espacios intervellosos placentarios hacia el sistema venoso fetal.",
                trampaCatedra: "Pregunta clásica de examen: El cordón umbilical posee 2 ARTERIAS umbilicales (sangre venosa desoxigenada) y 1 VENA umbilical (sangre arterial oxigenada)."
            },
            {
                pinId: 4,
                x: 68,
                y: 32,
                titulo: "Espacio Intervelloso Placentario (Cavum intervillosum)",
                pergunta: "Identificar la laguna hemática materna donde se bañan directamente las vellosidades coriónicas fetales.",
                respostasAceitas: ["espacio intervelloso", "espacios intervellosos", "lagunas intervellosas", "cavum intervillosum"],
                conceptoClave: "Espacio vascular sin endotelio materno alimentado por las arterias espirales uterinas para el intercambio gaseoso y metabólico transplacentario.",
                trampaCatedra: "¡Recordar la regla de oro de la cátedra! La sangre materna y fetal NUNCA se mezclan; están separadas por la barrera placentaria."
            }
        ],
        preguntasParcial: [
            {
                q: "¿Qué estratos celulares constituyen exactamente la barrera placentaria a término (3er trimestre)?",
                a: "1) Sincitiotrofoblasto apical continuo, 2) Escaso/delgado citotrofoblasto / lámina basal fusionada, 3) Estroma o tejido conectivo coriónico mínimo, y 4) Endotelio de los capilares fetales endoteliales."
            }
        ]
    }
];

if (typeof bancoDados !== 'undefined') {
    bancoDados.atlas = window.ATLAS_HISTOLOGICO_DATA;
}
