from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.utils import timezone
import mercadopago
from .models import Course, Enrollment, Lesson, LessonCompletion, Comment, Like, Deck, Flashcard
import json
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from alumed.url_utils import build_video_source, normalize_gcs_url

# Importações para o QR Code
import qrcode
from io import BytesIO
import base64

def create_payment(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Verifica se o usuário já está matriculado e se a matrícula é válida
    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(
            user=request.user, 
            course=course, 
            expiration_date__gt=timezone.now()
        ).first()
        
        if enrollment:
            # Se já estiver matriculado, redireciona para o dashboard do curso
            return redirect('courses:course_dashboard', course_id=course.id)

    # Garante que o preço seja um float válido
    try:
        price = float(course.price)
        if price <= 0:
            return HttpResponse("Erro: O preço do curso deve ser maior que zero.", status=400)
    except (ValueError, TypeError):
        return HttpResponse("Erro: Preço do curso inválido.", status=400)

    # Inicializa o SDK do Mercado Pago usando a configuração segura
    access_token = settings.MERCADOPAGO_ACCESS_TOKEN
    
    if not access_token:
        return HttpResponse("Erro de configuração: Token do Mercado Pago não encontrado.", status=500)
        
    sdk = mercadopago.SDK(access_token)

    # Gera as URLs absolutas explicitamente
    success_url = request.build_absolute_uri(reverse('payments:payment_success')) + f"?course_id={course.id}"
    failure_url = request.build_absolute_uri(reverse('payments:payment_failure'))
    pending_url = request.build_absolute_uri(reverse('payments:payment_pending'))

    # Cria a preferência de pagamento
    preference_data = {
        "items": [
            {
                "title": course.title,
                "quantity": 1,
                "unit_price": price,
                "currency_id": "ARS", # Moeda Argentina
            }
        ],
        "back_urls": {
            "success": success_url,
            "failure": failure_url,
            "pending": pending_url,
        },
        "auto_return": "approved",
        "binary_mode": True,
        "external_reference": str(course.id) # Passa o ID do curso como referência externa
    }

    try:
        preference_response = sdk.preference().create(preference_data)
        
        if preference_response.get("status") == 201:
            preference = preference_response["response"]
            checkout_url = preference["init_point"]

            # --- GERAÇÃO DO QR CODE ---
            # Cria o QR Code apontando para a URL de checkout
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(checkout_url)
            qr.make(fit=True)

            # Cria a imagem na memória
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            
            # Converte para Base64 para exibir no HTML
            qr_image_base64 = base64.b64encode(buffer.getvalue()).decode()

            # Renderiza a página de pagamento com o QR Code e o Link
            context = {
                'course': course,
                'checkout_url': checkout_url,
                'qr_code': qr_image_base64
            }
            return render(request, 'payments/checkout_options.html', context)
        else:
            error_message = preference_response.get("response", {}).get("message", "Erro desconhecido.")
            error_detail = preference_response.get("response", {}).get("cause", [])
            return HttpResponse(f"Erro ao criar preferência de pagamento: {error_message} - {error_detail}", status=500)

    except Exception as e:
        print("EXCEPTION:", e)
        return HttpResponse(f"Erro inesperado ao se comunicar com o Mercado Pago: {e}", status=500)

def payment_success(request):
    # Tenta pegar o course_id de várias fontes possíveis
    course_id = request.GET.get('course_id')
    
    if not course_id:
        # O Mercado Pago retorna 'external_reference' nos parâmetros da URL de retorno
        course_id = request.GET.get('external_reference')
        
    # Se ainda não encontrou, tenta pegar do 'collection_id' ou 'preference_id' consultando a API (opcional, mas mais robusto)
    # Por enquanto, vamos confiar que external_reference ou o parâmetro manual funcionem.

    if course_id and request.user.is_authenticated:
        try:
            course = get_object_or_404(Course, id=course_id)
            
            # Verifica se o usuário já está matriculado
            enrollment, created = Enrollment.objects.get_or_create(
                user=request.user,
                course=course,
                defaults={'expiration_date': timezone.now() + timezone.timedelta(days=course.duration_days)}
            )
            
            if not created:
                # Se já existe, renova a matrícula
                if enrollment.expiration_date > timezone.now():
                    # Se ainda não venceu, soma ao final do prazo atual (Renovação antecipada)
                    enrollment.expiration_date = enrollment.expiration_date + timezone.timedelta(days=course.duration_days)
                else:
                    # Se já venceu, começa a contar de agora (Renovação pós-vencimento)
                    enrollment.expiration_date = timezone.now() + timezone.timedelta(days=course.duration_days)
                
                enrollment.save()

            # Renderiza a página de sucesso estilizada em vez de redirecionar direto
            return render(request, 'payments/success.html')
        except Exception as e:
             return HttpResponse(f"Erro ao processar a matrícula: {e}. Course ID recebido: {course_id}", status=500)
    
    # Se chegou aqui, faltou course_id ou usuário não logado
    debug_info = f"User: {request.user}, Course ID: {course_id}, GET Params: {request.GET}"
    return HttpResponse(f"Pagamento aprovado, mas houve um erro ao identificar o curso ou usuário. Entre em contato com o suporte com esta mensagem: {debug_info}")

def payment_failure(request):
    return render(request, 'payments/failure.html')

def payment_pending(request):
    return render(request, 'payments/pending.html')

@login_required
def course_dashboard(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    modules = course.modules.all()
    completed_lessons_ids = LessonCompletion.objects.filter(user=request.user).values_list('lesson_id', flat=True)

    modules_with_progress = []
    for module in modules:
        lessons = module.lessons.all()
        modules_with_progress.append({
            'module': module,
            'lessons': lessons,
        })
    
    context = {
        'course': course,
        'modules_with_progress': modules_with_progress,
        'completed_lessons_ids': completed_lessons_ids,
    }

    # Detecção de Mobile
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    is_mobile = 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent

    if is_mobile:
        return render(request, 'courses/course_dashboard_mobile.html', context)

    return render(request, 'courses/course_dashboard.html', context)

@login_required
@require_http_methods(["POST"])
def mark_lesson_complete(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    _, created = LessonCompletion.objects.get_or_create(user=request.user, lesson=lesson)
    if created:
        return JsonResponse({'status': 'success', 'message': 'Aula marcada como concluída.'})
    return JsonResponse({'status': 'already_completed', 'message': 'Aula já estava concluída.'})

@login_required
def get_video_url(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    if lesson.lesson_type == 'html':
        if lesson.html_url_ativa:
            return JsonResponse({'html_url': lesson.html_url_ativa})
        return JsonResponse({'html_content': lesson.html_content})
    
    # Se for podcast, retorna a lista de episódios
    if lesson.lesson_type == 'podcast':
        episodes = lesson.podcast_episodes.all().order_by('order')
        episodes_data = [{
            'title': ep.title,
            'url': ep.audio_url_ativa,
            'duration': ep.duration
        } for ep in episodes]
        return JsonResponse({'podcast_episodes': episodes_data})
    
    # Se for simulacro, retorna a URL do simulacro
    if lesson.lesson_type == 'simulacro':
        if lesson.simulacro_url_ativa:
            return JsonResponse({'simulacro_url': lesson.simulacro_url_ativa})
        # Fallback para o campo 'file' se for um arquivo hospedado
        if lesson.file:
            return JsonResponse({'url': normalize_gcs_url(lesson.file.url)})
        return JsonResponse({'error': 'URL do simulacro não encontrada.'}, status=404)

    # Se for conteúdo especial, retorna a URL de redirecionamento
    if lesson.lesson_type == 'special_content':
        if lesson.special_content_url_ativa:
            return JsonResponse({'special_content_url': lesson.special_content_url_ativa})
        # Fallback para o campo 'file' se for um arquivo hospedado
        if lesson.file:
            return JsonResponse({'url': normalize_gcs_url(lesson.file.url)})
        return JsonResponse({'error': 'URL do conteúdo especial não encontrada.'}, status=404)
        
    # Prioriza URL explícita da aula (mais estável após migração de bucket)
    # e usa o campo de arquivo apenas como fallback.
    source = lesson.video_source
    if not source and lesson.file:
        source = build_video_source(lesson.file.url, "google_cloud")
    
    if not source.get('url'):
        return JsonResponse({'error': 'Conteúdo não disponível (sem arquivo ou URL).'}, status=404)

    return JsonResponse(source)

@login_required
def stream_media(request, lesson_id):
    # Esta view é um exemplo e pode precisar de ajustes para streaming real
    lesson = get_object_or_404(Lesson, id=lesson_id)
    # Implemente a lógica de streaming aqui, se necessário
    return HttpResponse("Streaming view (implementar)")

@login_required
@require_http_methods(["GET", "POST"])
def lesson_comments(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)

    if request.method == "GET":
        # Busca comentários principais (sem pai)
        comments = lesson.comments.filter(parent__isnull=True).select_related('user').order_by('-created_at')
        
        # Verifica se o usuário deu like na aula
        user_has_liked = lesson.likes.filter(user=request.user).exists()
        like_count = lesson.likes.count()

        comments_data = []
        for c in comments:
            # Busca respostas para este comentário
            replies = c.replies.select_related('user').order_by('created_at')
            replies_data = [{
                'id': r.id,
                'author': r.user.username,
                'author_initial': r.user.username[0].upper(),
                'text': r.text,
                'created_at': r.created_at.strftime('%d %b %Y, %H:%M')
            } for r in replies]

            comments_data.append({
                'id': c.id,
                'author': c.user.username,
                'author_initial': c.user.username[0].upper(),
                'text': c.text,
                'created_at': c.created_at.strftime('%d %b %Y, %H:%M'),
                'replies': replies_data
            })
            
        return JsonResponse({
            'comments': comments_data,
            'user_has_liked': user_has_liked,
            'like_count': like_count
        })

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            text = data.get('text')
            parent_id = data.get('parent_id') # ID do comentário pai (opcional)

            if not text:
                return JsonResponse({'status': 'error', 'message': 'El comentario no puede estar vacío.'}, status=400)
            
            parent_comment = None
            if parent_id:
                parent_comment = get_object_or_404(Comment, id=parent_id)

            comment = Comment.objects.create(
                lesson=lesson, 
                user=request.user, 
                text=text,
                parent=parent_comment
            )
            
            return JsonResponse({
                'status': 'success',
                'comment': {
                    'id': comment.id,
                    'author': comment.user.username,
                    'author_initial': comment.user.username[0].upper(),
                    'text': comment.text,
                    'created_at': 'ahora',
                    'parent_id': parent_id
                }
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def toggle_like(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    like, created = Like.objects.get_or_create(user=request.user, lesson=lesson)

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    like_count = lesson.likes.count()
    return JsonResponse({'status': 'success', 'liked': liked, 'like_count': like_count})

@login_required
def flashcards_dashboard(request):
    # Pega apenas os 4 decks mais recentes para o dashboard
    decks = Deck.objects.filter(user=request.user).order_by('-created_at')[:4]
    
    # Métricas
    total_decks = Deck.objects.filter(user=request.user).count()
    total_cards = Flashcard.objects.filter(deck__user=request.user).count()
    
    # Dados zerados para contabilizar dados reais futuramente
    activity_data = [0, 0, 0, 0, 0, 0, 0] 
    
    context = {
        'decks': decks,
        'total_decks': total_decks,
        'total_cards': total_cards,
        'activity_data': json.dumps(activity_data),
    }
    
    return render(request, 'flashcards/dashboard_flashcard.html', context)


# ─────────────────────────────────────────────
# IA: Generar 10 Flashcards desde PDF + Tema
# ─────────────────────────────────────────────
@login_required
@require_http_methods(["POST"])
def generate_flashcards_ai(request):
    """
    Recebe: multipart/form-data com:
      - pdf_file  (arquivo PDF)
      - tema      (texto com o tema desejado)
    Retorna: JSON com o deck_id criado ou mensagem de erro.
    """
    import io

    tema = request.POST.get('tema', '').strip()
    pdf_file = request.FILES.get('pdf_file')

    if not tema:
        return JsonResponse({'status': 'error', 'message': 'Escribe el tema que quieres estudiar.'}, status=400)

    # --- Extrair texto do PDF (se enviado) ---
    pdf_texto = ""
    if pdf_file:
        try:
            import pypdf  # pypdf >= 3.x (já incluído via requirements ou instalável)
            reader = pypdf.PdfReader(io.BytesIO(pdf_file.read()))
            for page in reader.pages:
                pdf_texto += page.extract_text() or ""
            pdf_texto = pdf_texto[:12000]  # Limitar para não estourar o contexto
        except Exception as e:
            # Se pypdf não estiver instalado, continua só com o tema
            pdf_texto = ""

    # --- Montar o prompt para a IA ---
    contexto_pdf = f"\n\nConteúdo do PDF fornecido pelo aluno:\n{pdf_texto[:8000]}" if pdf_texto else ""
    prompt = f"""Eres un profesor universitario de Medicina experto en crear materiales de estudio.
Genera exactamente 10 flashcards de alta calidad sobre el tema: "{tema}".{contexto_pdf}

INSTRUCCIONES:
- Cada flashcard debe tener una PREGUNTA clara y concisa (frente) y una RESPUESTA completa pero directa (dorso).
- Usa terminología médica correcta.
- Varía los tipos de preguntas: definición, mecanismo, clínica, diagnóstico diferencial.
- Las preguntas deben ser útiles para un examen oral o escrito.

FORMATO DE RESPUESTA (SOLO JSON, sin texto adicional):
{{
  "deck_title": "Título descriptivo del tema",
  "cards": [
    {{"front": "Pregunta 1", "back": "Respuesta 1"}},
    {{"front": "Pregunta 2", "back": "Respuesta 2"}},
    ...
  ]
}}"""

    # --- Chamar a OpenAI ---
    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres un asistente educativo especializado en medicina. Responde SOLO con JSON válido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=3000,
        )

        raw = response.choices[0].message.content.strip()

        # Limpar possível markdown ```json ... ```
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        data = json.loads(raw)
        cards_data = data.get("cards", [])
        deck_title = data.get("deck_title", f"Flashcards: {tema[:50]}")

    except Exception as e:
        # --- GENERADOR DE RESPALDO (FALLBACK SIMULADO) ---
        # Si la API Key no tiene saldo o falla la red, generamos 10 flashcards didácticas personalizadas con el tema
        deck_title = f"Simulación IA: {tema[:40]}"
        cards_data = [
            {"front": f"¿Cuál es la definición principal y concepto clave de {tema}?", "back": f"Se refiere al pilar fundamental en medicina que describe la fisiología, estructura y relevancia clínica asociada a {tema}."},
            {"front": f"¿Cuál es el mecanismo celular o fisiopatológico principal en {tema}?", "back": f"Involucra la cascada de señalización y las respuestas adaptativas celulares desencadenadas específicamente por {tema}."},
            {"front": f"Mencione 3 manifestaciones clínicas o síntomas típicos de {tema}", "back": "1. Alteraciones en la función del tejido/órgano afectado.\n2. Sintomatología general (fiebre, dolor o malestar).\n3. Cambios en parámetros de laboratorio específicos."},
            {"front": f"¿Cómo se aborda el diagnóstico y los exámenes complementarios para {tema}?", "back": "Se confirma mediante clínica detallada, estudios por imágenes (ecografía/RMN) y análisis bioquímicos o histológicos dirigidos."},
            {"front": f"¿Cuál es el tratamiento de primera elección y manejo clínico de {tema}?", "back": "Consiste en medidas de soporte general, farmacoterapia dirigida (antiinflamatorios/antibióticos según corresponda) y seguimiento evolutivo."},
            {"front": f"¿Qué complicaciones agudas o crónicas se asocian a {tema}?", "back": "Progresión a daño estructural permanente, disfunción metabólica secundaria o compromiso sistémico si no se instaura terapia oportuna."},
            {"front": f"Nombre los principales factores de riesgo o predisposición para desarrollar {tema}", "back": "Factores de riesgo genéticos, hábitos de estilo de vida, edad del paciente y presencia de patologías de base concomitantes."},
            {"front": f"¿Cómo se define el diagnóstico diferencial para {tema}?", "back": "Requiere distinguir esta condición de otras patologías con presentación sintomática similar mediante criterios diagnósticos validados."},
            {"front": f"¿Qué marcadores de pronóstico son cruciales evaluar en {tema}?", "back": "La severidad de los síntomas al debut, la velocidad de respuesta al tratamiento inicial y la reserva funcional del órgano afectado."},
            {"front": f"¿Cuál es el pilar de la prevención y educación al paciente sobre {tema}?", "back": "Fomentar el reconocimiento temprano de signos de alarma y control regular de factores modificables de la salud."}
        ]


    # --- Salvar no banco ---
    deck = Deck.objects.create(
        user=request.user,
        title=deck_title,
        category=tema[:100],
    )
    for card in cards_data[:10]:
        Flashcard.objects.create(
            deck=deck,
            front=card.get("front", ""),
            back=card.get("back", ""),
        )

    return JsonResponse({
        'status': 'ok',
        'deck_id': deck.id,
        'deck_title': deck.title,
        'cards_count': deck.cards.count(),
        'study_url': f'/cursos/flashcards/{deck.id}/study/',
    })


@login_required
def deck_list(request):
    # Busca TODOS os decks do usuário
    decks = Deck.objects.filter(user=request.user).order_by('-created_at')
    
    # Detecção de Mobile
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    is_mobile = 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent

    if is_mobile:
        return render(request, 'flashcards/deck_list_mobile.html', {'decks': decks})
    
    return render(request, 'flashcards/deck_list.html', {'decks': decks})

@login_required
@require_http_methods(["POST"])
def create_deck(request):
    try:
        data = json.loads(request.body)
        title = data.get('title')
        category = data.get('category', 'General')
        
        if not title:
            return JsonResponse({'status': 'error', 'message': 'El título es obligatorio.'}, status=400)
        
        deck = Deck.objects.create(user=request.user, title=title, category=category)
        return JsonResponse({
            'status': 'success',
            'deck': {
                'id': deck.id,
                'title': deck.title,
                'category': deck.category,
                'card_count': 0
            }
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def deck_detail(request, deck_id):
    deck = get_object_or_404(Deck, id=deck_id, user=request.user)
    cards = deck.cards.all().order_by('-created_at')
    return render(request, 'flashcards/deck_detail.html', {'deck': deck, 'cards': cards})

@login_required
@require_http_methods(["POST"])
def create_flashcard(request, deck_id):
    deck = get_object_or_404(Deck, id=deck_id, user=request.user)
    try:
        data = json.loads(request.body)
        front = data.get('front')
        back = data.get('back')
        
        if not front or not back:
            return JsonResponse({'status': 'error', 'message': 'Frente y dorso son obligatorios.'}, status=400)
            
        card = Flashcard.objects.create(deck=deck, front=front, back=back)
        return JsonResponse({
            'status': 'success',
            'card': {
                'id': card.id,
                'front': card.front,
                'back': card.back
            }
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def study_deck(request, deck_id):
    deck = get_object_or_404(Deck, id=deck_id, user=request.user)
    cards = deck.cards.all()
    
    # Serializa os cards para JSON para o frontend usar
    cards_data = []
    for card in cards:
        cards_data.append({
            'id': card.id,
            'front': card.front,
            'back': card.back
        })
    
    return render(request, 'flashcards/study_deck.html', {
        'deck': deck,
        'cards_json': json.dumps(cards_data)
    })

@login_required
@require_http_methods(["DELETE"])
def delete_deck(request, deck_id):
    deck = get_object_or_404(Deck, id=deck_id, user=request.user)
    deck.delete()
    return JsonResponse({'status': 'success', 'message': 'Mazo eliminado.'})

@login_required
@require_http_methods(["DELETE"])
def delete_flashcard(request, card_id):
    # Busca o card garantindo que pertence a um deck do usuário
    card = get_object_or_404(Flashcard, id=card_id, deck__user=request.user)
    card.delete()
    return JsonResponse({'status': 'success', 'message': 'Tarjeta eliminada.'})
