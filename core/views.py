from django.shortcuts import render
from courses.models import Course
from .library_catalog import build_library_payload
from .models import LibraryResource, Announcement, Popup, Testimonial, TestimonialVideo, DigitalBook
from accounts.views import student_auth_required
import urllib.request
import re
import html
from django.core.cache import cache
import ssl
import threading

def scrape_unlp_cartelera():
    url = "https://cartelera.med.unlp.edu.ar/"
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    )
    try:
        # Bypassing SSL validation and using a 3s timeout
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        with urllib.request.urlopen(req, context=ctx, timeout=3) as response:
            encoding = response.headers.get_content_charset() or 'latin-1'
            html_content = response.read().decode(encoding, errors='replace')
        
        cards = []
        card_blocks = re.findall(r'<div class="card card-outline-.*?</div>\s*</div>\s*</div>', html_content, re.DOTALL)
        
        for block in card_blocks:
            date_match = re.search(r'<h5[^>]*>.*?</i>\s*(?P<date>\d{2}/\d{2}/\d{4})</h5>', block, re.DOTALL)
            title_url_match = re.search(r'<h4 class="card-title"><a href="(?P<url>[^"]+)">(?P<title>[^<]+)</a></h4>', block)
            subtitle_match = re.search(r'<h6 class="card-subtitle[^"]*">(?P<subtitle>[^<]*)</h6>', block)
            dept_match = re.search(r'<p class="card-text text-right">(?P<dept>[^<]*)</p>', block)
            
            if date_match and title_url_match:
                title = html.unescape(title_url_match.group('title').strip())
                date = date_match.group('date').strip()
                link = title_url_match.group('url').strip()
                subtitle = html.unescape(subtitle_match.group('subtitle').strip()) if subtitle_match else ""
                dept = html.unescape(dept_match.group('dept').strip()) if dept_match else ""
                
                if link.startswith('/'):
                    link = "https://cartelera.med.unlp.edu.ar" + link
                    
                if subtitle == "-":
                    subtitle = ""
                    
                notice_id = "0"
                id_match = re.search(r'/noticia/(\d+)', link)
                if id_match:
                    notice_id = id_match.group(1)
                    
                cards.append({
                    'id': notice_id,
                    'title': title,
                    'date': date,
                    'url': link,
                    'subtitle': subtitle,
                    'dept': dept
                })
        return cards
    except Exception as e:
        print("Scraping error:", e)
        # Return fallback on error
        return get_fallback_cartelera()

def get_fallback_cartelera():
    return [
        {
            'id': '261',
            'title': 'Relevamiento por los cupos para 3º bimestre y 2º cuatrimestre',
            'date': '03/07/2026',
            'url': 'https://cartelera.med.unlp.edu.ar/noticia/261',
            'subtitle': '',
            'dept': 'Secretaría de Asuntos Estudiantiles'
        },
        {
            'id': '262',
            'title': 'Relevamiento para interna 1 y pediatría',
            'date': '03/07/2026',
            'url': 'https://cartelera.med.unlp.edu.ar/noticia/262',
            'subtitle': '',
            'dept': 'Secretaría de Asuntos Estudiantiles'
        },
        {
            'id': '260',
            'title': 'INSCRIPCIONES SEGUNDO CUATRIMESTRE Y TERCER BIMESTRE',
            'date': '30/06/2026',
            'url': 'https://cartelera.med.unlp.edu.ar/noticia/260',
            'subtitle': '',
            'dept': 'Dirección de Enseñanza - Secretaría Académica'
        },
        {
            'id': '259',
            'title': 'Ingresantes 2026 - Prórroga Entrega de Documentación',
            'date': '30/06/2026',
            'url': 'https://cartelera.med.unlp.edu.ar/noticia/259',
            'subtitle': 'Prórroga Entrega de Documentación',
            'dept': 'Dirección de Enseñanza'
        }
    ]

def run_scrape_in_background():
    try:
        data = scrape_unlp_cartelera()
        if data:
            cache.set('unlp_cartelera_data', data, 600)  # cache for 10 minutes
    except Exception as e:
        print("Background scrape task failed:", e)

def get_cached_cartelera():
    cached_data = cache.get('unlp_cartelera_data')
    if cached_data is not None:
        return cached_data
    
    # Empty cache -> run scraping in background thread to avoid blocking requests
    threading.Thread(target=run_scrape_in_background, daemon=True).start()
    return get_fallback_cartelera()

def home(request):
    """Renderiza a página inicial."""
    courses = Course.objects.all().order_by('-id')
    library_resources = LibraryResource.objects.all()
    announcements = Announcement.objects.filter(is_active=True).order_by('-created_at')
    active_popup = Popup.objects.filter(is_active=True).first()
    testimonials = Testimonial.objects.all()
    testimonial_videos = TestimonialVideo.objects.all()
    cartelera_notices = get_cached_cartelera()[:4]
    
    context = {
        'courses': courses,
        'library_resources': library_resources,
        'announcements': announcements,
        'active_popup': active_popup,
        'testimonials': testimonials,
        'testimonial_videos': testimonial_videos,
        'cartelera_notices': cartelera_notices,
    }
    return render(request, 'base.html', context)


def unlp(request):
    courses = Course.objects.filter(title__icontains='UNLP')
    return render(request, 'courses/unlp.html', {'courses': courses})


def uba(request):
    courses = Course.objects.filter(title__icontains='UBA')
    return render(request, 'courses/uba.html', {'courses': courses})


def barcelo(request):
    courses = Course.objects.filter(title__icontains='Barcelo') | Course.objects.filter(title__icontains='Barceló')
    return render(request, 'courses/barcelo.html', {'courses': courses})


def premed(request):
    courses = Course.objects.filter(title__icontains='PREMED')
    return render(request, 'courses/premed.html', {'courses': courses})


def grupos(request):
    return render(request, 'courses/groups.html')


def microscopio_virtual(request):
    return render(request, 'core/microscopio_virtual.html')


def anatomia_3d(request):
    return render(request, 'core/anatomia_3d.html')


def cronograma_finales(request):
    cartelera_notices = get_cached_cartelera()
    return render(request, 'core/cronograma_finales.html', {'cartelera_notices': cartelera_notices})


def info_util(request):
    return render(request, 'core/info_util.html')


def facultad(request):
    return render(request, 'core/facultad.html')


def mapa_facultad_view(request):
    return render(request, 'core/mapa_facultad.html')


def biblioteca(request):
    """Renderiza a Biblioteca de IA (RAG) sem redirecionar."""
    return render(request, 'biblioteca_ia.html')

def simulacros_view(request, materia=None):
    """Renderiza el portal de simulacros público (Caballo de Troya)."""
    return render(request, 'simulacros.html', {'materia_preseleccionada': materia})

def checkout_intensivo(request, curso):
    """Redirige al checkout del intensivo correspondiente."""
    return render(request, 'simulacros.html')  # Mock view for now



def cronograma_tps(request):
    return render(request, 'core/cronograma_tps.html')


def plan_estudios(request):
    return render(request, 'core/plan_estudios.html')


def apoyo_psicologico(request):
    return render(request, 'core/apoyo_psicologico.html')


def comisiones(request):
    return render(request, 'core/comisiones.html')


def club(request):
    return render(request, 'core/club.html')


def favoritos(request):
    return render(request, 'core/favoritos.html')


def cartelera_view(request):
    cartelera_notices = get_cached_cartelera()
    return render(request, 'core/cartelera.html', {'cartelera_notices': cartelera_notices})


def conecta_fcm_view(request):
    cartelera_notices = get_cached_cartelera()
    return render(request, 'core/conecta_fcm.html', {
        'cartelera_notices': cartelera_notices,
    })


def conecta_landing_view(request):
    """
    Conecta FCM — redireciona sempre para o dashboard (acesso publico, sem login).
    """
    from django.shortcuts import redirect as _redirect
    return _redirect('conecta_dashboard')


def becas_view(request):
    """
    Página de Becas y Beneficios Estudiantiles — UNLP / FCM.
    Muestra CUDE, Boleto Educativo, Libreta Universitaria y Comedor.
    Acceso libre — sin necesidad de login.
    """
    return render(request, 'core/becas.html')

from django.http import JsonResponse
from courses.models import SimulacroQuestion
import random

import json
from core.profe_joy_views import _get_api_client

def api_get_simulacro_questions(request, subject):
    try:
        slug_map = {
            'histologia': 'Histología',
            'embriologia': 'Embriología',
            'anatomia': 'Anatomía',
            'biologia': 'Biología',
            'anatomia-a': 'Anatomía Cátedra A',
            'anatomia-b': 'Anatomía Cátedra B',
            'anatomia-c': 'Anatomía Cátedra C',
            'histo-embrio': 'Histología',
            'bioquimica': 'Bioquímica',
        }
        mapped_subject = slug_map.get(subject, subject)
        
        # Leer Modalidad y Cantidad
        modality = request.GET.get('modality', 'choice')
        try:
            qty = int(request.GET.get('qty', 10))
        except ValueError:
            qty = 10

        # 1. Intentar Generar con Motor RAG / IA
        client_type, client = _get_api_client()
        if client_type != 'mock' and client is not None:
            try:
                prompt = f"""Eres Profe Joy, tutora IA de medicina de ALUMED OS. 
Genera exactamente {qty} preguntas del tema {mapped_subject} (nivel parcial universitario).
Modalidad: {modality} (si es 'oral', las preguntas deben ser planteos de casos clínicos o preparados; si es 'choice', preguntas directas).
Devuelve ÚNICAMENTE un objeto JSON estricto con la siguiente clave "questions" que contenga la lista de preguntas, sin texto extra:
{{
  "questions": [
    {{
      "question_text": "Texto de la pregunta...",
      "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
      "correct_option": "A",
      "explanation": "..."
    }}
  ]
}}"""

                if client_type == 'gemini':
                    model = client.GenerativeModel('gemini-1.5-pro')
                    response = model.generate_content(prompt)
                    resp_text = response.text.replace('```json', '').replace('```', '').strip()
                    data = json.loads(resp_text)
                    return JsonResponse({'questions': data.get('questions', [])})

                elif client_type == 'openai':
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": prompt}],
                        response_format={ "type": "json_object" }
                    )
                    resp_text = response.choices[0].message.content
                    data = json.loads(resp_text)
                    return JsonResponse({'questions': data.get('questions', [])})
                    
            except Exception as e:
                print("AI Generation failed, falling back to DB:", e)
                pass # Fallback to DB

        # 2. Fallback a la Base de Datos Local
        base_subject = mapped_subject.split(' ')[0]
        questions = []
        try:
            qs = list(SimulacroQuestion.objects.filter(subject__icontains=base_subject))
            if len(qs) > qty:
                questions = random.sample(qs, qty)
            else:
                questions = qs
        except Exception as e:
            print("DB fallback failed:", e)
            pass

        if not questions and mapped_subject == "Anatomía Cátedra C":
            questions = [
                type('obj', (object,), {
                    'id': 1,
                    'question_text': "¿Cuál de los siguientes pares craneales emerge de la cara posterior del tronco encefálico (mesencéfalo)?",
                    'option_a': "Nervio Oculomotor (III)",
                    'option_b': "Nervio Troclear (IV)",
                    'option_c': "Nervio Trigémino (V)",
                    'option_d': "Nervio Abducens (VI)",
                    'correct_option': "B",
                    'explanation': "El nervio troclear o patético (IV par craneal) es el único que emerge de la cara posterior del tronco encefálico."
                }),
                type('obj', (object,), {
                    'id': 2,
                    'question_text': "En relación a la irrigación del corazón, la arteria descendente anterior es rama terminal de:",
                    'option_a': "Arteria Coronaria Derecha",
                    'option_b': "Arteria Circunfleja",
                    'option_c': "Arteria Coronaria Izquierda",
                    'option_d': "Seno Coronario",
                    'correct_option': "C",
                    'explanation': "La arteria coronaria izquierda se bifurca rápidamente en descendente anterior (interventricular anterior) y circunfleja."
                }),
                type('obj', (object,), {
                    'id': 3,
                    'question_text': "¿Qué estructura atraviesa el hiato aórtico del diafragma junto con la arteria aorta?",
                    'option_a': "Nervio vago derecho",
                    'option_b': "Vena cava inferior",
                    'option_c': "Conducto torácico",
                    'option_d': "Esófago",
                    'correct_option': "C",
                    'explanation': "Por el hiato aórtico del diafragma pasan la aorta descendente y el conducto torácico (y a veces la vena ácigos)."
                }),
                type('obj', (object,), {
                    'id': 4,
                    'question_text': "El ligamento cruzado anterior de la rodilla se inserta distalmente en:",
                    'option_a': "Área intercondílea anterior de la tibia",
                    'option_b': "Cóndilo medial del fémur",
                    'option_c': "Cabeza del peroné",
                    'option_d': "Tuberosidad de la tibia",
                    'correct_option': "A",
                    'explanation': "El LCA se inserta distalmente en el área intercondílea anterior de la tibia."
                }),
                type('obj', (object,), {
                    'id': 5,
                    'question_text': "El lóbulo de la ínsula se encuentra en la profundidad de la cisura de:",
                    'option_a': "Rolando (Central)",
                    'option_b': "Silvio (Lateral)",
                    'option_c': "Calcarina",
                    'option_d': "Parieto-occipital",
                    'correct_option': "B",
                    'explanation': "El lóbulo de la ínsula está oculto en el fondo del surco lateral o cisura de Silvio."
                })
            ]
            
        elif not questions and mapped_subject == "Anatomía Cátedra A":
            questions = [
                type('obj', (object,), {
                    'id': 1,
                    'question_text': "El polígono de Willis (Círculo arterial cerebral) se forma principalmente por la anastomosis de:",
                    'option_a': "Arterias vertebrales y arterias cerebelosas.",
                    'option_b': "Arterias carótidas externas y arterias vertebrales.",
                    'option_c': "Arterias carótidas internas y arterias vertebrales (sistema vertebrobasilar).",
                    'option_d': "Arterias meníngeas medias y carótidas internas.",
                    'correct_option': "C",
                    'explanation': "El polígono de Willis resulta de la unión de los sistemas carotídeo interno y vertebrobasilar en la base del cerebro."
                }),
                type('obj', (object,), {
                    'id': 2,
                    'question_text': "En la vía piramidal (haz corticoespinal), la decusación de la mayor parte de las fibras ocurre a nivel de:",
                    'option_a': "La protuberancia.",
                    'option_b': "El bulbo raquídeo (pirámides bulbares).",
                    'option_c': "La médula espinal (comisura blanca anterior).",
                    'option_d': "El mesencéfalo (pedúnculos cerebrales).",
                    'correct_option': "B",
                    'explanation': "El 75-90% de las fibras del haz corticoespinal se decusan en el límite inferior del bulbo raquídeo (decusación piramidal)."
                }),
                type('obj', (object,), {
                    'id': 3,
                    'question_text': "La vena porta hepática se forma típicamente por la unión de:",
                    'option_a': "Vena mesentérica superior y tronco esplenomesentérico (vena esplénica + VMI).",
                    'option_b': "Vena cava inferior y vena esplénica.",
                    'option_c': "Venas hepáticas derecha e izquierda.",
                    'option_d': "Vena gástrica izquierda y vena mesentérica superior.",
                    'correct_option': "A",
                    'explanation': "La vena porta se forma detrás del cuello del páncreas por la confluencia de la vena mesentérica superior y el tronco esplenomesentérico."
                }),
                type('obj', (object,), {
                    'id': 4,
                    'question_text': "¿Qué estructura forma el límite anterior del foramen epiploico (Hiato de Winslow)?",
                    'option_a': "Vena cava inferior.",
                    'option_b': "Peritoneo parietal posterior.",
                    'option_c': "Pedículo hepático (en el borde libre del epiplón menor).",
                    'option_d': "Lóbulo caudado del hígado.",
                    'correct_option': "C",
                    'explanation': "El límite anterior del foramen omental está dado por el ligamento hepatoduodenal que contiene al pedículo hepático."
                }),
                type('obj', (object,), {
                    'id': 5,
                    'question_text': "El bronquio principal derecho se diferencia del izquierdo en que es:",
                    'option_a': "Más largo, más horizontal y de menor calibre.",
                    'option_b': "Más corto, más vertical y de mayor calibre.",
                    'option_c': "Más largo, más vertical y de mayor calibre.",
                    'option_d': "Más corto, más horizontal y de menor calibre.",
                    'correct_option': "B",
                    'explanation': "El bronquio derecho es más corto, ancho y vertical (casi continuación de la tráquea), lo que facilita que los cuerpos extraños se alojen allí."
                })
            ]
            
        elif not questions and mapped_subject == "Anatomía Cátedra B":
            questions = [
                type('obj', (object,), {
                    'id': 1,
                    'question_text': "El nervio mediano se forma a partir de:",
                    'option_a': "El fascículo posterior del plexo braquial exclusivamente.",
                    'option_b': "La unión de una raíz del fascículo lateral y una raíz del fascículo medial.",
                    'option_c': "La unión de las raíces C5 y C6.",
                    'option_d': "El fascículo medial del plexo braquial exclusivamente.",
                    'correct_option': "B",
                    'explanation': "El nervio mediano se forma por delante de la arteria axilar por la unión de la raíz lateral (del fascículo lateral) y la raíz medial (del fascículo medial)."
                }),
                type('obj', (object,), {
                    'id': 2,
                    'question_text': "¿Cuál de los siguientes músculos NO pertenece al manguito de los rotadores?",
                    'option_a': "Supraespinoso.",
                    'option_b': "Infraespinoso.",
                    'option_c': "Redondo mayor.",
                    'option_d': "Subescapular.",
                    'correct_option': "C",
                    'explanation': "El manguito rotador está formado por el supraespinoso, infraespinoso, redondo menor y subescapular. El redondo mayor no forma parte de este complejo."
                }),
                type('obj', (object,), {
                    'id': 3,
                    'question_text': "En la articulación coxofemoral, el ligamento más potente y que evita la hiperextensión de la cadera es:",
                    'option_a': "Ligamento iliofemoral (Y de Bertin).",
                    'option_b': "Ligamento pubofemoral.",
                    'option_c': "Ligamento isquiofemoral.",
                    'option_d': "Ligamento redondo (de la cabeza del fémur).",
                    'correct_option': "A",
                    'explanation': "El ligamento iliofemoral tiene forma de Y o V invertida; es el ligamento más fuerte del cuerpo y su función principal es limitar la extensión de la cadera."
                }),
                type('obj', (object,), {
                    'id': 4,
                    'question_text': "La arteria mesentérica inferior irriga principalmente:",
                    'option_a': "Yeyuno, íleon y mitad derecha del colon.",
                    'option_b': "Duodeno y páncreas.",
                    'option_c': "Estómago y bazo.",
                    'option_d': "Tercio distal del colon transverso, colon descendente, colon sigmoideo y parte superior del recto.",
                    'correct_option': "D",
                    'explanation': "La AMI se encarga de la irrigación del intestino grueso izquierdo (derivados del intestino posterior embrionario)."
                }),
                type('obj', (object,), {
                    'id': 5,
                    'question_text': "¿Qué arterias forman la curvatura menor del estómago (Círculo arterial de la curvatura menor)?",
                    'option_a': "Arteria gástrica derecha (pilórica) y arteria gástrica izquierda (coronaria estomáquica).",
                    'option_b': "Arteria gastroomental derecha e izquierda.",
                    'option_c': "Arterias gástricas cortas.",
                    'option_d': "Arteria esplénica y arteria hepática común.",
                    'correct_option': "A",
                    'explanation': "El arco vascular de la curvatura menor está formado por la anastomosis entre la arteria gástrica izquierda (rama del tronco celíaco) y la derecha (rama de la hepática propia)."
                }),
                type('obj', (object,), {
                    'id': 6,
                    'question_text': "¿Cuáles son los tendones que conforman la llamada 'pata de ganso' en la cara medial de la tibia?",
                    'option_a': "Sartorio, Recto interno (Grácil) y Semitendinoso.",
                    'option_b': "Semimembranoso, Semitendinoso y Bíceps femoral.",
                    'option_c': "Sartorio, Recto anterior y Vasto interno.",
                    'option_d': "Recto interno, Semimembranoso y Aductor mayor.",
                    'correct_option': "A",
                    'explanation': "La pata de ganso está formada por las inserciones distales de los músculos Sartorio, Recto interno (Grácil) y Semitendinoso."
                }),
                type('obj', (object,), {
                    'id': 7,
                    'question_text': "El nervio musculocutáneo, responsable de la inervación del compartimento anterior del brazo, perfora al músculo:",
                    'option_a': "Bíceps braquial.",
                    'option_b': "Coracobraquial.",
                    'option_c': "Braquial anterior.",
                    'option_d': "Deltoides.",
                    'correct_option': "B",
                    'explanation': "El nervio musculocutáneo es conocido como el nervio perforante de Casserio porque atraviesa el vientre del músculo coracobraquial."
                }),
                type('obj', (object,), {
                    'id': 8,
                    'question_text': "El seno del tarso es un conducto anatómico formado por la articulación de los huesos:",
                    'option_a': "Astrágalo y Calcáneo.",
                    'option_b': "Astrágalo y Escafoides (Navicular).",
                    'option_c': "Calcáneo y Cuboides.",
                    'option_d': "Tibia y Astrágalo.",
                    'correct_option': "A",
                    'explanation': "El seno del tarso se encuentra entre el surco del astrágalo y el surco del calcáneo, en la articulación subastragalina."
                }),
                type('obj', (object,), {
                    'id': 9,
                    'question_text': "La porción larga del músculo tríceps braquial tiene su origen (inserción proximal) en:",
                    'option_a': "El tubérculo supraglenoideo de la escápula.",
                    'option_b': "El tubérculo infraglenoideo de la escápula.",
                    'option_c': "La corredera bicipital del húmero.",
                    'option_d': "La apófisis coracoides de la escápula.",
                    'correct_option': "B",
                    'explanation': "El tríceps braquial tiene tres cabezas; su porción larga se inserta en el tubérculo infraglenoideo de la escápula."
                }),
                type('obj', (object,), {
                    'id': 10,
                    'question_text': "La arteria femoral es la continuación directa de la arteria:",
                    'option_a': "Ilíaca interna (Hipogástrica).",
                    'option_b': "Ilíaca externa.",
                    'option_c': "Obturatriz.",
                    'option_d': "Femoral profunda.",
                    'correct_option': "B",
                    'explanation': "La arteria ilíaca externa pasa por debajo del ligamento inguinal (arco crural) y a partir de ese punto cambia su nombre a arteria femoral."
                })
            ]
            
        elif not questions and base_subject == "Biología":
            questions = [
                type('obj', (object,), {
                    'id': 1,
                    'question_text': "El siguiente dispositivo consta de dos compartimentos (A y B) separados por una membrana M. En A se coloca sacarosa 200 mM y en B NaCl 100 mM. ¿Qué ocurre si M es impermeable a la sacarosa y al Na+, y el coeficiente de reflexión para Cl- es 0,5?",
                    'option_a': "La solución A es hiperosmolar respecto a la B, habrá flujo de agua hacia B.",
                    'option_b': "La solución A es isoosmolar respecto a la B. La solución A es hipertónica respecto a la B y se observará un incremento del volumen del compartimiento A.",
                    'option_c': "La solución A es hiperosmolar y habrá incremento de volumen en A.",
                    'option_d': "La solución A es isoosmolar y habrá flujo neto de agua hacia B.",
                    'correct_option': "B",
                    'explanation': "Ambas soluciones tienen 200 mOsm/L (isoosmolar). Como el coeficiente de reflexión del Cl- es 0.5, la osmolaridad efectiva de B es 150 mOsm/L y de A es 200 mOsm/L, por lo que A es hipertónica y atrae agua."
                }),
                type('obj', (object,), {
                    'id': 2,
                    'question_text': "En A hay sacarosa 150 mM y en B NaCl 100 mM. Si M es impermeable a sacarosa y Na+, y el coeficiente de reflexión para Cl- es 0,5 (σ = 0,5). Señale lo correcto:",
                    'option_a': "La solución A es hipoosmolar respecto a la B, pero es isotónica respecto a la solución B y no existirá ósmosis.",
                    'option_b': "La solución A es hiperosmolar respecto a la B y existirá ósmosis hacia B.",
                    'option_c': "La solución A es hipoosmolar respecto a la B y es hipotónica respecto a B.",
                    'option_d': "La solución A es isoosmolar respecto a la B y habrá ósmosis hacia A.",
                    'correct_option': "A",
                    'explanation': "La osmolaridad de A es 150 y B es 200 (A es hipoosmolar). La osmolaridad efectiva de A es 150, y la de B es 100(1) + 100(0.5) = 150. Por ende, son isotónicas y no hay ósmosis."
                }),
                type('obj', (object,), {
                    'id': 3,
                    'question_text': "¿Qué organela celular es la principal responsable de la síntesis de ATP mediante la fosforilación oxidativa?",
                    'option_a': "Retículo Endoplasmático Liso",
                    'option_b': "Aparato de Golgi",
                    'option_c': "Mitocondria",
                    'option_d': "Lisosoma",
                    'correct_option': "C",
                    'explanation': "La mitocondria posee la cadena de transporte de electrones y la ATP sintasa en su membrana interna, produciendo la mayor parte del ATP celular."
                }),
                type('obj', (object,), {
                    'id': 4,
                    'question_text': "¿Cuál es el componente lipídico más abundante en las membranas biológicas eucariotas?",
                    'option_a': "Triglicéridos",
                    'option_b': "Fosfolípidos",
                    'option_c': "Colesterol",
                    'option_d': "Esfingolípidos",
                    'correct_option': "B",
                    'explanation': "Los fosfolípidos forman la bicapa lipídica básica de todas las membranas biológicas debido a su naturaleza anfipática."
                }),
                type('obj', (object,), {
                    'id': 5,
                    'question_text': "Durante qué fase del ciclo celular se produce la replicación del ADN?",
                    'option_a': "Fase G1",
                    'option_b': "Fase S",
                    'option_c': "Fase G2",
                    'option_d': "Fase M",
                    'correct_option': "B",
                    'explanation': "Durante la fase S (Síntesis) del ciclo celular se replica el ADN, duplicando el material genético de la célula."
                })
            ]
            
        elif not questions and base_subject == "Histología":
            questions = [
                type('obj', (object,), {
                    'id': 1,
                    'question_text': "Las fibras elásticas están constituidas por una estructura central:",
                    'option_a': "Amorfa denominada elaunina y fibrillas externas de fibrilina.",
                    'option_b': "De fibrillas denominadas fibrilina y una masa amorfa externa de elastina.",
                    'option_c': "Amorfa denominada elaunina y fibrillas externas de elastina.",
                    'option_d': "Amorfa denominada elastina y fibrillas externas de fibrilina.",
                    'correct_option': "D",
                    'explanation': "Las fibras elásticas tienen un núcleo central amorfo de elastina rodeado por una red de microfibrillas de fibrilina."
                }),
                type('obj', (object,), {
                    'id': 2,
                    'question_text': "La corteza del cerebelo:",
                    'option_a': "Es central y con forma ramificada.",
                    'option_b': "Tiene células de Purkinje en su capa media.",
                    'option_c': "Es periférica y lisa.",
                    'option_d': "Está conformada solo por fibras.",
                    'correct_option': "B",
                    'explanation': "La corteza cerebelosa se divide en 3 capas: molecular (externa), de Purkinje (media) y granulosa (interna)."
                }),
                type('obj', (object,), {
                    'id': 3,
                    'question_text': "En el ganglio linfático:",
                    'option_a': "A través de las vénulas de endotelio alto ingresan los linfocitos de la sangre.",
                    'option_b': "Los vasos linfáticos aferentes desembocan directamente en los senos medulares.",
                    'option_c': "Las vénulas de endotelio alto se encuentran predominantemente en la corteza externa.",
                    'option_d': "La linfa entra a través de los vasos aferentes a través del hilio.",
                    'correct_option': "A",
                    'explanation': "Las vénulas de endotelio alto (HEV) ubicadas en la paracorteza permiten el ingreso de los linfocitos circulantes al ganglio."
                }),
                type('obj', (object,), {
                    'id': 4,
                    'question_text': "Marque la opción correcta, las células musculares lisas:",
                    'option_a': "Son multinucleadas y sus núcleos están en la periferia.",
                    'option_b': "Están interconectadas por uniones de hendidura.",
                    'option_c': "Se ramifican en pantalón.",
                    'option_d': "Sus medios de unión conforman discos intercalares.",
                    'correct_option': "B",
                    'explanation': "Las células musculares lisas se comunican mecánica y eléctricamente a través de uniones en hendidura (gap junctions)."
                }),
                type('obj', (object,), {
                    'id': 5,
                    'question_text': "¿Qué célula de la glía del SNC se encarga de realizar la cicatrización en el tejido nervioso?",
                    'option_a': "Oligodendrocito.",
                    'option_b': "Astrocito.",
                    'option_c': "Epéndimo.",
                    'option_d': "Célula Satélite.",
                    'correct_option': "B",
                    'explanation': "Los astrocitos son los responsables de la gliosis reactiva, formando la cicatriz glial tras una lesión en el sistema nervioso central."
                })
            ]
            
        elif not questions and base_subject == "Embriología":
            questions = [
                type('obj', (object,), {
                    'id': 1,
                    'question_text': "Indique cómo se denomina el proceso por el cual el espermatozoide adquiere movilidad anterógrada y dónde ocurre:",
                    'option_a': "Capacitación, y ocurre en el epidídimo.",
                    'option_b': "Capacitación, y ocurre en el túbulo seminífero.",
                    'option_c': "Maduración, y ocurre en el epidídimo.",
                    'option_d': "Reacción acrosómica, y ocurre en la ampolla uterina.",
                    'correct_option': "C",
                    'explanation': "La maduración espermática ocurre en el epidídimo (especialmente en la cola) y es el proceso mediante el cual los espermatozoides adquieren la capacidad de movimiento."
                }),
                type('obj', (object,), {
                    'id': 2,
                    'question_text': "La capacitación de un espermatozoide ocurre principalmente por:",
                    'option_a': "Cambios en la polaridad del acrosoma por enzimas prostáticas.",
                    'option_b': "Pérdida de colesterol de la membrana plasmática en el tracto genital femenino.",
                    'option_c': "Adición de colesterol a la membrana en el tracto genital masculino.",
                    'option_d': "Pérdida de la cola del espermatozoide en la cavidad uterina.",
                    'correct_option': "B",
                    'explanation': "Durante la capacitación en el tracto femenino, se elimina colesterol y glicoproteínas de la membrana plasmática del espermatozoide, preparándolo para la reacción acrosómica."
                }),
                type('obj', (object,), {
                    'id': 3,
                    'question_text': "Indique qué eventos favorecen el transporte de espermatozoides en el tracto genital femenino:",
                    'option_a': "Acidez vaginal intensa.",
                    'option_b': "Contracciones musculares del útero y trompas estimuladas por prostaglandinas y oxitocina.",
                    'option_c': "Relajación total de la musculatura uterina.",
                    'option_d': "Cierre del canal cervical y aumento de la viscosidad del moco.",
                    'correct_option': "B",
                    'explanation': "Las prostaglandinas del semen y la oxitocina liberada por la mujer estimulan las contracciones del miometrio y las trompas, facilitando el ascenso espermático."
                }),
                type('obj', (object,), {
                    'id': 4,
                    'question_text': "El acrosoma es una modificación de cuál de estas organelas celulares:",
                    'option_a': "Aparato de Golgi.",
                    'option_b': "Lisosomas.",
                    'option_c': "Mitocondrias.",
                    'option_d': "Retículo endoplasmático rugoso.",
                    'correct_option': "A",
                    'explanation': "El acrosoma se forma a partir de vesículas provenientes del Aparato de Golgi durante la espermiogénesis, y contiene enzimas vitales para la fecundación."
                }),
                type('obj', (object,), {
                    'id': 5,
                    'question_text': "¿En qué porción de las trompas de Falopio suele ocurrir normalmente la fecundación?",
                    'option_a': "En el istmo.",
                    'option_b': "En la porción intramural (intersticial).",
                    'option_c': "En la ampolla.",
                    'option_d': "En las fimbrias del infundíbulo.",
                    'correct_option': "C",
                    'explanation': "La fecundación ocurre más frecuentemente en la región de la ampolla (tercio externo) de la trompa uterina."
                }),
                type('obj', (object,), {
                    'id': 6,
                    'question_text': "La anfimixis es la...",
                    'option_a': "Telofase de la primera división mitótica.",
                    'option_b': "Telofase de la primera división meiótica.",
                    'option_c': "Metafase de la primera división mitótica.",
                    'option_d': "Metafase de la primera división meiótica.",
                    'correct_option': "C",
                    'explanation': "La anfimixis corresponde a la metafase de la primera división mitótica de la cigota, donde se alinean los cromosomas maternos y paternos."
                }),
                type('obj', (object,), {
                    'id': 7,
                    'question_text': "¿Cuáles son las dos cavidades que se originan durante la 2da semana de gestación?",
                    'option_a': "Amniótica de ubicación ventral y saco de Yolk de ubicación dorsal.",
                    'option_b': "Celoma intraembrionario ventral y saco vitelino dorsal.",
                    'option_c': "Amniótica de ubicación dorsal y saco vitelino de ubicación ventral.",
                    'option_d': "Amniótica de ubicación ventral y saco vitelino de ubicación dorsal.",
                    'correct_option': "C",
                    'explanation': "En el disco bilaminar, la cavidad amniótica se forma dorsalmente (sobre el epiblasto) y el saco vitelino ventralmente (bajo el hipoblasto)."
                }),
                type('obj', (object,), {
                    'id': 8,
                    'question_text': "La neurulación se extiende desde la diferenciación del ectodermo en neuroepitelio, hasta el día:",
                    'option_a': "30, con el cierre del neuroporo posterior.",
                    'option_b': "27, con el cierre del neuroporo anterior.",
                    'option_c': "27, con el cierre del neuroporo posterior.",
                    'option_d': "25, con el cierre del neuroporo posterior.",
                    'correct_option': "C",
                    'explanation': "El proceso de neurulación finaliza con el cierre del neuroporo caudal o posterior, que ocurre alrededor del día 27-28."
                }),
                type('obj', (object,), {
                    'id': 9,
                    'question_text': "¿De dónde provienen las células que van a formar la notocorda?",
                    'option_a': "Del ectodermo y migran a través de la fosita primitiva.",
                    'option_b': "Del epiblasto y migran a través del nódulo de Hensen.",
                    'option_c': "Surgen del endodermo durante el proceso notocordal.",
                    'option_d': "Del epiblasto y migran a través de la región caudal de la línea primitiva.",
                    'correct_option': "B",
                    'explanation': "Las células notocordales derivan del epiblasto y se invaginan a nivel de la fosita primitiva en el nódulo de Hensen, extendiéndose cefálicamente."
                }),
                type('obj', (object,), {
                    'id': 10,
                    'question_text': "¿Qué factor produce la notocorda para que la parte ventromedial del somita se diferencie a esclerotoma?",
                    'option_a': "WNT",
                    'option_b': "Brachyury",
                    'option_c': "SHH (Sonic Hedgehog)",
                    'option_d': "BMP-4",
                    'correct_option': "C",
                    'explanation': "La notocorda y la placa del piso del tubo neural secretan SHH, el cual induce a la región ventromedial del somita a convertirse en esclerotoma."
                })
            ]
        
        data = []
        for q in questions:
            data.append({
                'id': q.id,
                'question_text': q.question_text,
                'options': {
                    'A': q.option_a,
                    'B': q.option_b,
                    'C': q.option_c,
                    'D': q.option_d
                },
                'correct_option': q.correct_option,
                'explanation': q.explanation
            })
        return JsonResponse({'ok': True, 'subject': subject, 'questions': data})
    except Exception as outer_e:
        import traceback
        return JsonResponse({'error_msg': str(outer_e), 'traceback': traceback.format_exc()}, status=500)


def guia_supervivencia_view(request):
    return render(request, 'accounts/guia_supervivencia.html')
