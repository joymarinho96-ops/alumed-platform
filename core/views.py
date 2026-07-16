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
    books = DigitalBook.objects.all().order_by('subject', 'title')
    library_payload = build_library_payload(books)
    return render(
        request,
        'core/biblioteca.html',
        {
            'library_payload': library_payload,
            'library_summary': library_payload['summary'],
        },
    )


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
    Landing publica do Conecta FCM.
    Nao requer login — mostra funcionalidades e CTA 'Activar mi Conecta'.
    Se o usuario ja tem acesso, redireciona direto para o dashboard.
    """
    from django.shortcuts import redirect as _redirect
    if request.user.is_authenticated:
        # Verifica se ja tem acesso
        from accounts.views import has_product_access
        if has_product_access(request.user, 'CONECTA_FCM'):
            return _redirect('conecta_dashboard')
    return render(request, 'core/conecta_landing.html')


def becas_view(request):
    """
    Página de Becas y Beneficios Estudiantiles — UNLP / FCM.
    Muestra CUDE, Boleto Educativo, Libreta Universitaria y Comedor.
    Acceso libre — sin necesidad de login.
    """
    return render(request, 'core/becas.html')
