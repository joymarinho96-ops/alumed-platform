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

        if not questions and base_subject == "Anatomía":
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
