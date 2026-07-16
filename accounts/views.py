from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Q, Count
from .forms import CustomUserCreationForm, ProfileUpdateForm
from courses.models import Course, Lesson, LessonCompletion, Enrollment
from core.models import Announcement, Event, Product
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from datetime import datetime
from .models import (ChatMessage, Profile, AccessProduct, UserAccess,
                     ConectaPreference, ConectaSubscription, ConectaConsentEvent,
                     AcademicEvent)
from django.core.management import call_command
from django.contrib import messages
from functools import wraps
from django.urls import reverse

def student_auth_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            next_url = request.get_full_path()
            return redirect(f"{reverse('login')}?next={next_url}")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def has_product_access(user, product_slug):
    """
    Verifica se um usuario tem acesso ativo a um AccessProduct (ex: CONECTA_FCM).
    Independente de Enrollment de cursos.
    Staff sempre tem acesso.
    """
    if user.is_staff:
        return True
    return UserAccess.objects.filter(
        user=user,
        product__slug=product_slug,
        is_active=True,
    ).filter(
        Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
    ).exists()


def conecta_access_required(view_func):
    """Protege views do Conecta FCM. Requer login + UserAccess(CONECTA_FCM) ativo."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            next_url = request.get_full_path()
            return redirect(f"{reverse('login')}?next={next_url}")
        if not has_product_access(request.user, 'CONECTA_FCM'):
            return redirect('conecta_landing')
        return view_func(request, *args, **kwargs)
    return _wrapped

import jwt
import hashlib
import time
import logging
from django.conf import settings
from django.http import HttpResponseForbidden
from django.utils.http import url_has_allowed_host_and_scheme

logger = logging.getLogger(__name__)

def auth_gate_view(request):
    token = request.GET.get('token')
    next_url = request.GET.get('next', 'student_dashboard')

    # Si no hay token, redirigir al login oficial en Wix
    if not token:
        wix_login_url = 'https://alumed.wixsite.com/alumed/login'
        return redirect(wix_login_url)

    # 1. Validar la firma y expiración del JWT
    sso_secret = getattr(settings, 'ALUMED_SSO_SECRET', None)
    if not sso_secret:
        logger.error("ALUMED_SSO_SECRET no está configurado en settings.py.")
        return HttpResponseForbidden("Error de configuración del servidor (SSO Secret faltante).")

    try:
        # decode valida firma, exp e iat automáticamente
        payload = jwt.decode(
            token,
            sso_secret,
            algorithms=['HS256'],
            options={"require": ["exp", "iat"]}
        )
    except jwt.ExpiredSignatureError:
        logger.warning("Intento de inicio de sesión con token JWT expirado.")
        return HttpResponseForbidden("El enlace de inicio de sesión ha expirado (validez de 5 minutos). Por favor, intenta de nuevo desde Wix.")
    except (jwt.DecodeError, jwt.InvalidSignatureError) as e:
        logger.warning(f"Error de firma o decodificación del token JWT: {str(e)}")
        return HttpResponseForbidden("Firma de token inválida o corrupta.")
    except jwt.InvalidTokenError as e:
        logger.warning(f"Error general en validación de token JWT: {str(e)}")
        return HttpResponseForbidden("Token de acceso inválido.")

    # 2. Protección contra Replay Attacks usando caché local
    token_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()
    cache_key = f"sso_token:{token_hash}"
    if cache.get(cache_key):
        logger.warning("Intento de reutilización de token detectado (Replay Attack).")
        return HttpResponseForbidden("Este enlace de acceso único ya ha sido utilizado. Por favor, genera uno nuevo desde Wix.")

    # Registrar en caché por el tiempo restante de vida del token
    now = time.time()
    remaining_seconds = payload['exp'] - now
    if remaining_seconds > 0:
        cache.set(cache_key, True, timeout=int(remaining_seconds))

    # 3. Extraer información del usuario
    wix_member_id = payload.get('wix_member_id')
    email = payload.get('email')
    first_name = payload.get('first_name', '')
    last_name = payload.get('last_name', '')

    if not email:
        return HttpResponseForbidden("El token de acceso no contiene una dirección de correo válida.")

    email_clean = email.lower().strip()

    # 4. Buscar o crear el usuario en Django
    user = User.objects.filter(email__iexact=email_clean).first()
    
    if not user:
        # Wix es la autoridad, si el token es válido creamos el usuario localmente
        username_base = email_clean.split('@')[0]
        username = ''.join(c for c in username_base if c.isalnum() or c in ['_', '-'])[:150]
        
        # Evitar colisión de nombres
        original_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{original_username}{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=email_clean,
            first_name=first_name,
            last_name=last_name
        )
        logger.info(f"Usuario {username} ({email_clean}) creado automáticamente vía SSO de Wix.")

    # 5. Asegurar perfil y vincular wix_member_id
    profile, created = Profile.objects.get_or_create(user=user)
    if profile.wix_member_id != wix_member_id:
        profile.wix_member_id = wix_member_id
        profile.save()
        logger.info(f"Perfil del usuario {user.username} vinculado con wix_member_id: {wix_member_id}")

    # 6. Iniciar sesión local en Django
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    logger.info(f"Inicio de sesión exitoso vía SSO para {user.username}.")

    # 7. Validar seguridad del redireccionamiento (evitar Open Redirect)
    is_safe = url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure()
    )

    if not is_safe:
        logger.warning(f"Redireccionamiento inseguro bloqueado: '{next_url}'. Redirigiendo a dashboard.")
        next_url = 'student_dashboard'

    return redirect(next_url)

from django.contrib.auth.forms import AuthenticationForm

def login_view(request):
    if request.user.is_authenticated:
        return redirect('student_dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'student_dashboard')
                return redirect(next_url)
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('student_dashboard')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('student_dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

def student_dashboard_view(request):
    # Usuarios no autenticados van al inicio (sin bloqueo de login)
    if not request.user.is_authenticated:
        from django.shortcuts import redirect
        return redirect('home')
    # Busca TODAS as matrículas, ordenadas por expiração (as que vencem primeiro ou já venceram aparecem antes)
    enrollments = Enrollment.objects.filter(user=request.user).order_by('expiration_date')
    courses_with_progress = []
    
    total_lessons_completed = LessonCompletion.objects.filter(user=request.user).count()
    
    # Calcula o tempo total de estudo somando a duração das aulas completadas
    completed_lessons_duration = LessonCompletion.objects.filter(
        user=request.user
    ).aggregate(total_duration=Sum('lesson__duration_in_minutes'))['total_duration'] or 0

    for enrollment in enrollments:
        course = enrollment.course
        total_lessons = Lesson.objects.filter(module__course=course).count()
        completed_lessons = LessonCompletion.objects.filter(user=request.user, lesson__module__course=course).count()
        progress = (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0
        
        # Verifica se está expirado
        is_expired = enrollment.expiration_date < timezone.now()
        
        courses_with_progress.append({
            'course': course,
            'progress': progress,
            'completed_lessons': completed_lessons,
            'total_lessons': total_lessons,
            'days_remaining': (enrollment.expiration_date - timezone.now()).days,
            'is_expired': is_expired, # Nova flag
            'expiration_date': enrollment.expiration_date
        })

    # Estatísticas gerais (apenas cursos ativos contam para "Cursos Inscritos")
    active_courses_count = enrollments.filter(expiration_date__gte=timezone.now()).count()
    
    # Converte minutos para horas (arredondado)
    estimated_study_hours = int(completed_lessons_duration / 60)

    # Busca os avisos ativos
    announcements = Announcement.objects.filter(is_active=True).order_by('-created_at')

    # --- NOVO: Lógica para o Card "Continuar de Onde Parou" ---
    last_completion = LessonCompletion.objects.filter(user=request.user).order_by('-completed_at').first()
    last_lesson = None
    next_lesson = None
    
    if last_completion:
        last_lesson = last_completion.lesson
        # Tenta encontrar a próxima aula no mesmo módulo
        next_in_module = Lesson.objects.filter(
            module=last_lesson.module, 
            id__gt=last_lesson.id
        ).order_by('id').first()
        
        if next_in_module:
            next_lesson = next_in_module
        else:
            # Se acabou o módulo, tenta o primeiro do próximo módulo
            next_module = last_lesson.module.course.modules.filter(id__gt=last_lesson.module.id).order_by('id').first()
            if next_module:
                next_lesson = next_module.lessons.order_by('id').first()
    
    # Se não tiver nenhuma conclusão, pega a primeira aula do primeiro curso matriculado
    if not next_lesson and enrollments.exists():
        first_course = enrollments.first().course
        first_module = first_course.modules.order_by('id').first()
        if first_module:
            next_lesson = first_module.lessons.order_by('id').first()

    # --- NOVO: Lógica para o Card "Próximas Conquistas" (Gamificação Simples) ---
    # Níveis: Novato (0-5), Estudioso (6-20), Mestre (21-50), Lenda (50+)
    next_achievement = {
        'title': 'Novato',
        'target': 5,
        'current': total_lessons_completed,
        'icon': 'fa-seedling'
    }
    
    if total_lessons_completed >= 5:
        next_achievement = {
            'title': 'Estudioso',
            'target': 20,
            'current': total_lessons_completed,
            'icon': 'fa-book-reader'
        }
    if total_lessons_completed >= 20:
        next_achievement = {
            'title': 'Mestre',
            'target': 50,
            'current': total_lessons_completed,
            'icon': 'fa-graduation-cap'
        }
    if total_lessons_completed >= 50:
        next_achievement = {
            'title': 'Lenda',
            'target': 100, # Próximo alvo arbitrário
            'current': total_lessons_completed,
            'icon': 'fa-crown'
        }
        
    achievement_progress = min(100, int((next_achievement['current'] / next_achievement['target']) * 100))

    # --- LÓGICA DO CALENDÁRIO ---
    events = Event.objects.all()
    events_list = []
    for event in events:
        # Garante que as datas sejam strings ISO (YYYY-MM-DD)
        start_str = event.start_date.strftime('%Y-%m-%d') if event.start_date else ''
        end_str = event.end_date.strftime('%Y-%m-%d') if event.end_date else start_str

        events_list.append({
            'title': event.title,
            'start': start_str,
            'end': end_str,
            'type': event.event_type,
        })
    
    # Converte a lista para uma string JSON segura
    events_json = json.dumps(events_list, cls=DjangoJSONEncoder)

    # Busca exames futuros para a lista de agenda
    upcoming_exams = Event.objects.filter(
        event_type='exam', 
        start_date__gte=timezone.now().date()
    ).order_by('start_date')

    # --- NOTIFICAÇÕES INTELIGENTES ---
    # Verifica se há avisos criados DEPOIS da última visualização do usuário
    profile = request.user.profile
    last_view = profile.last_announcement_view_time
    
    has_new_announcements = Announcement.objects.filter(
        is_active=True, 
        created_at__gt=last_view
    ).exists()
    
    # Atualiza o tempo de visualização para AGORA (já que o usuário está vendo o dashboard)
    profile.last_announcement_view_time = timezone.now()
    profile.save()

    # --- CHATMED NOTIFICATIONS ---
    unread_msgs = ChatMessage.objects.filter(receiver=request.user, is_read=False).order_by('-timestamp')
    unread_messages_count = unread_msgs.count()
    latest_message_sender = None
    if unread_msgs.exists():
        latest_message_sender = unread_msgs.first().sender.username

    chatmed_pending_rows = list(
        ChatMessage.objects
        .filter(receiver=request.user, is_read=False)
        .values('sender_id', 'sender__username', 'sender__first_name', 'sender__last_name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    chatmed_pending = []
    for row in chatmed_pending_rows:
        full_name = f"{row.get('sender__first_name', '')} {row.get('sender__last_name', '')}".strip()
        display_name = full_name if full_name else row.get('sender__username', '')
        chatmed_pending.append({
            'sender_id': row['sender_id'],
            'display_name': display_name,
            'count': row['count'],
        })
    
    context = {
        'courses_with_progress': courses_with_progress,
        'active_courses_count': active_courses_count,
        'total_lessons_completed': total_lessons_completed,
        'estimated_study_hours': estimated_study_hours,
        'announcements': announcements,
        'next_lesson': next_lesson, # Passa a próxima aula para o template
        'next_achievement': next_achievement, # Passa dados da conquista
        'achievement_progress': achievement_progress,
        'events_json': events_json,
        'upcoming_exams': upcoming_exams, # Passa os exames futuros
        'has_new_announcements': has_new_announcements,
        'unread_messages_count': unread_messages_count,
        'latest_message_sender': latest_message_sender,
        'chatmed_pending': chatmed_pending,
    }
    return render(request, 'accounts/student_dashboard.html', context)


@conecta_access_required
def conecta_dashboard_view(request):
    """Dashboard Conecta FCM — Centro de control de la vida universitaria. Requer UserAccess(CONECTA_FCM)."""

    # Cartelera en vivo
    from core.views import get_cached_cartelera
    cartelera_notices = get_cached_cartelera()

    # Upcoming exams from calendar events
    upcoming_exams = Event.objects.filter(
        event_type='exam',
        start_date__gte=timezone.now().date()
    ).order_by('start_date')[:5]

    # All events for calendar
    events = Event.objects.all()
    events_list = []
    for event in events:
        start_str = event.start_date.strftime('%Y-%m-%d') if event.start_date else ''
        end_str = event.end_date.strftime('%Y-%m-%d') if event.end_date else start_str
        events_list.append({
            'title': event.title,
            'start': start_str,
            'end': end_str,
            'type': event.event_type,
        })
    events_json = json.dumps(events_list, cls=DjangoJSONEncoder)

    # Smart notification count (new announcements)
    profile = request.user.profile
    last_view = profile.last_announcement_view_time
    new_notices_count = len([n for n in cartelera_notices]) if cartelera_notices else 0
    has_new_announcements = Announcement.objects.filter(
        is_active=True,
        created_at__gt=last_view
    ).exists()

    # La Plata weather (reuse cache key from status bar if available)
    weather_data = cache.get('laplata_weather', {
        'temp': '--',
        'desc': 'La Plata',
        'wind': '--',
        'rain': '--',
    })

    context = {
        'cartelera_notices': cartelera_notices,
        'upcoming_exams': upcoming_exams,
        'events_json': events_json,
        'new_notices_count': new_notices_count,
        'has_new_announcements': has_new_announcements,
        'weather_data': weather_data,
    }
    return render(request, 'accounts/conecta_dashboard.html', context)


@student_auth_required
def mis_cursos_view(request):
    """Redireciona diretamente para a pagina de cursos no Wix."""
    return redirect('https://www.alumedestudiantes.com/miscursos')


@student_auth_required
def students_list_view(request):
    # Busca todos os usuários (alunos e staff)
    # Ordena staff primeiro, depois por data de entrada
    students = User.objects.all().order_by('-is_staff', '-date_joined')
    
    students_data = []
    for student in students:
        # Busca os cursos ativos do aluno
        active_enrollments = Enrollment.objects.filter(
            user=student, 
            expiration_date__gte=timezone.now()
        ).select_related('course')
        
        courses = [enrollment.course for enrollment in active_enrollments]
        
        # Tenta pegar o perfil para a foto
        try:
            profile = student.profile
        except:
            profile = None

        students_data.append({
            'user': student,
            'profile': profile,
            'courses': courses,
            'enrollment_count': len(courses)
        })

    context = {
        'students_data': students_data
    }
    return render(request, 'accounts/students_list.html', context)

@student_auth_required
def account_details_view(request):
    if request.method == 'POST':
        # Tenta obter o perfil existente ou cria um novo
        profile, created = Profile.objects.get_or_create(user=request.user)
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            # Se for AJAX, retorna o partial atualizado
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                # Re-renderiza o partial com os dados atualizados
                enrollments = Enrollment.objects.filter(user=request.user).order_by('-expiration_date')
                enrollments_data = []
                now = timezone.now()
                warning_threshold = now + timedelta(days=30)
                for enrollment in enrollments:
                    status = 'active'
                    if enrollment.expiration_date < now:
                        status = 'expired'
                    elif enrollment.expiration_date <= warning_threshold:
                        status = 'warning'
                    enrollments_data.append({
                        'course': enrollment.course,
                        'expiration_date': enrollment.expiration_date,
                        'status': status
                    })
                context = {
                    'enrollments_data': enrollments_data,
                    'user': request.user # Garante que o usuário atualizado seja passado
                }
                return render(request, 'accounts/account_details.html', context)
            else:
                return redirect('home')
    
    # Busca todas as matrículas, inclusive as vencidas
    enrollments = Enrollment.objects.filter(user=request.user).order_by('-expiration_date')
    
    enrollments_data = []
    now = timezone.now()
    warning_threshold = now + timedelta(days=30)

    for enrollment in enrollments:
        status = 'active'
        if enrollment.expiration_date < now:
            status = 'expired'
        elif enrollment.expiration_date <= warning_threshold:
            status = 'warning'
        
        enrollments_data.append({
            'course': enrollment.course,
            'expiration_date': enrollment.expiration_date,
            'status': status
        })

    context = {
        'enrollments_data': enrollments_data,
    }
    
    # Se for AJAX, retorna apenas o template parcial
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'accounts/account_details.html', context)
        
    # Se for acesso direto, retorna a página completa (que estende base.html)
    # Precisamos adicionar os cursos para o fundo da home não quebrar
    courses = Course.objects.all().order_by('-id')
    context['courses'] = courses
    return render(request, 'accounts/account_details_page.html', context)

def session_conflict_view(request):
    if request.method == 'POST':
        if 'logout' in request.POST:
            logout(request)
            return redirect('login')
        elif 'stay' in request.POST:
            # Se o usuário escolhe ficar, atualizamos o cache para que ESTA sessão seja a válida
            # Isso vai deslogar a outra sessão (a "nova" que tinha entrado)
            if request.user.is_authenticated:
                cache_key = f"user_session_{request.user.id}"
                cache.set(cache_key, request.session.session_key, timeout=None)
                return redirect('home')
    
    return render(request, 'accounts/session_conflict.html')

# --- VIEW DO PAINEL DE ADMINISTRAÇÃO ---
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard_view(request):
    if request.method == 'POST':
        if 'send_mass_email' in request.POST:
            subject = request.POST.get('subject')
            message_body = request.POST.get('message_body')
            
            if subject and message_body:
                try:
                    call_command('send_mass_message', subject, message_body)
                    messages.success(request, 'Correos enviados con éxito a todos los alumnos activos.')
                except Exception as e:
                    messages.error(request, f'Error al enviar correos: {e}')
            else:
                messages.error(request, 'Por favor, complete el asunto y el mensaje.')
            return redirect('admin_dashboard')

    # Estatísticas Gerais
    total_students = User.objects.filter(is_staff=False).count()
    total_courses = Course.objects.count()
    
    # Novos cadastros no mês atual
    now = timezone.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    new_signups_month = User.objects.filter(date_joined__gte=start_of_month).count()

    # Simulação de uso da IA (pode ser substituído por dados reais se tiver um modelo de log)
    ia_queries_today = 127 # Placeholder

    context = {
        'total_students': total_students,
        'total_courses': total_courses,
        'new_signups_month': new_signups_month,
        'ia_queries_today': ia_queries_today,
    }
    return render(request, 'accounts/admin_dashboard.html', context)

# --- CHATMED VIEWS ---

@student_auth_required
def chatmed_view(request):
    # Limpa mensagens antigas ao acessar a view
    ChatMessage.cleanup_old_messages()
    
    # Lista todos os usuários (alunos e staff) exceto o atual.
    users = User.objects.exclude(id=request.user.id).order_by('-is_staff', 'first_name', 'username')

    unread_rows = (
        ChatMessage.objects
        .filter(receiver=request.user, is_read=False)
        .values('sender_id')
        .annotate(unread_count=Count('id'))
    )
    unread_map = {row['sender_id']: row['unread_count'] for row in unread_rows}

    users_data = []
    for user in users:
        last_msg = (
            ChatMessage.objects
            .filter(Q(sender=request.user, receiver=user) | Q(sender=user, receiver=request.user))
            .order_by('-timestamp')
            .first()
        )
        full_name = f"{user.first_name} {user.last_name}".strip()
        display_name = full_name if full_name else user.username
        users_data.append({
            'id': user.id,
            'username': user.username,
            'display_name': display_name,
            'is_staff': user.is_staff,
            'photo_url': user.profile.photo.url if hasattr(user, 'profile') and user.profile.photo else '',
            'unread_count': unread_map.get(user.id, 0),
            'last_message': last_msg.content if last_msg else '',
            'last_timestamp': last_msg.timestamp.strftime('%H:%M') if last_msg else '',
        })
    
    initial_user_id = request.GET.get('user_id')
    try:
        initial_user_id = int(initial_user_id) if initial_user_id else None
    except (TypeError, ValueError):
        initial_user_id = None

    context = {
        'users': users,
        'users_data': users_data,
        'initial_user_id': initial_user_id,
    }
    return render(request, 'accounts/chatmed.html', context)

@student_auth_required
def get_messages(request, user_id):
    other_user = User.objects.get(id=user_id)
    
    # Busca mensagens entre os dois usuários
    messages = ChatMessage.objects.filter(
        Q(sender=request.user, receiver=other_user) | 
        Q(sender=other_user, receiver=request.user)
    ).order_by('timestamp')
    
    # Marca como lidas as mensagens recebidas
    ChatMessage.objects.filter(sender=other_user, receiver=request.user, is_read=False).update(is_read=True)
    
    messages_data = []
    for msg in messages:
        messages_data.append({
            'sender_id': msg.sender.id,
            'content': msg.content,
            'timestamp': msg.timestamp.strftime('%H:%M'),
            'is_me': msg.sender.id == request.user.id
        })
        
    return JsonResponse({'messages': messages_data})

@student_auth_required
def send_message(request):
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver_id')
        content = request.POST.get('content')
        
        if receiver_id and content:
            receiver = User.objects.get(id=receiver_id)
            ChatMessage.objects.create(
                sender=request.user,
                receiver=receiver,
                content=content
            )
            return JsonResponse({'status': 'success'})
            
    return JsonResponse({'status': 'error'}, status=400)

@student_auth_required
def check_unread_messages(request):
    """Endpoint leve para verificar mensagens não lidas via AJAX"""
    unread_msgs = ChatMessage.objects.filter(receiver=request.user, is_read=False).order_by('-timestamp')
    count = unread_msgs.count()
    
    latest_sender = None
    if unread_msgs.exists():
        latest_sender = unread_msgs.first().sender.username

    by_user = list(
        ChatMessage.objects
        .filter(receiver=request.user, is_read=False)
        .values('sender_id', 'sender__username', 'sender__first_name', 'sender__last_name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
        
    return JsonResponse({
        'count': count,
        'latest_sender': latest_sender
        ,'by_user': by_user
    })

@student_auth_required
def alumed_store_view(request):
    products = Product.objects.filter(is_active=True)
    
    context = {
        'products': products
    }
    return render(request, 'accounts/store.html', context)


# ── Conecta FCM — Preferences API v2 ─────────────────────────────────────────
# Endpoint unico: GET/POST /conecta/api/preferences/
# Seguridad: login_required, CSRF, opera solo sobre request.user
# Fuente de verdad: BD Django. localStorage = cache visual solamente.

from .conecta_catalog import catalog_for_api, ALL_INST_SLUGS, ALL_SUBJECT_SLUGS
from .models import _normalize_e164
from django.db import transaction
import re as _re2

_MAX_INST     = 12
_MAX_SUBJECTS = 60


def _get_client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR', '')
    return xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR', '')


def _validate_payload(data):
    """Valida el payload del POST. Retorna (errors_dict, cleaned_data)."""
    errors  = {}
    cleaned = {}

    inst_raw = data.get('institutional', [])
    if not isinstance(inst_raw, list):
        errors['institutional'] = 'Debe ser una lista de slugs.'
    elif len(inst_raw) > _MAX_INST:
        errors['institutional'] = f'Maximo {_MAX_INST} categorias.'
    else:
        unknown = [s for s in inst_raw if s not in ALL_INST_SLUGS]
        if unknown:
            errors['institutional'] = f'Slugs desconocidos: {unknown}'
        else:
            cleaned['institutional'] = list(set(inst_raw))

    subj_raw = data.get('subjects', [])
    if not isinstance(subj_raw, list):
        errors['subjects'] = 'Debe ser una lista de slugs.'
    elif len(subj_raw) > _MAX_SUBJECTS:
        errors['subjects'] = f'Maximo {_MAX_SUBJECTS} materias.'
    else:
        unknown = [s for s in subj_raw if s not in ALL_SUBJECT_SLUGS]
        if unknown:
            errors['subjects'] = f'Slugs desconocidos: {unknown}'
        else:
            cleaned['subjects'] = list(set(subj_raw))

    wa_raw  = data.get('whatsapp_number', '').strip()
    wa_norm = _normalize_e164(wa_raw) if wa_raw else ''
    if wa_raw and not _re2.match(r'^\+[0-9]{10,15}$', wa_norm):
        errors['whatsapp_number'] = 'Numero invalido. Usar formato E.164.'
    else:
        cleaned['whatsapp_number'] = wa_norm

    em_raw = data.get('alert_email', '').strip().lower()
    if em_raw and not _re2.match(r'^[^@]+@[^@]+\.[^@]+$', em_raw):
        errors['alert_email'] = 'Email invalido.'
    else:
        cleaned['alert_email'] = em_raw

    wa_active  = bool(data.get('whatsapp_active', False))
    em_active  = bool(data.get('email_active',    False))
    cal_active = bool(data.get('calendar_active', False))

    if wa_active and not cleaned.get('whatsapp_number', ''):
        errors['whatsapp_active'] = 'No se puede activar WhatsApp sin numero valido.'
    if em_active and not cleaned.get('alert_email', ''):
        errors['email_active'] = 'No se puede activar Email sin direccion valida.'

    cleaned['whatsapp_active']  = wa_active
    cleaned['email_active']     = em_active
    cleaned['calendar_active']  = cal_active
    cleaned['consent_granted']  = bool(data.get('consent_granted', False))
    cleaned['revoke_consent']   = bool(data.get('revoke_consent',  False))

    return errors, cleaned


@login_required
def conecta_preferences(request):
    """GET  -> devuelve preferencias + catalogo completo.
       POST -> valida y persiste preferencias de forma transaccional."""

    if request.method == 'GET':
        user = request.user
        try:
            pref = user.conecta_preference
            pref_data = {
                'whatsapp_number': pref.whatsapp_number,
                'alert_email':     pref.alert_email,
                'whatsapp_active': pref.whatsapp_active,
                'email_active':    pref.email_active,
                'calendar_active': pref.calendar_active,
                'consent_granted': pref.consent_granted,
                'consent_at':      pref.consent_at.isoformat() if pref.consent_at else None,
                'consent_version': pref.consent_version,
            }
        except ConectaPreference.DoesNotExist:
            pref_data = {}

        subs          = ConectaSubscription.objects.filter(user=user, enabled=True).values('type', 'key')
        institutional = [s['key'] for s in subs if s['type'] == 'institutional']
        subjects      = [s['key'] for s in subs if s['type'] == 'subject']

        return JsonResponse({
            'ok': True,
            'preferences':   pref_data,
            'subscriptions': {'institutional': institutional, 'subjects': subjects},
            'catalog':       catalog_for_api(),
        })

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, ValueError) as exc:
            return JsonResponse({'ok': False, 'errors': {'json': str(exc)}}, status=400)

        errors, cleaned = _validate_payload(data)
        if errors:
            return JsonResponse({'ok': False, 'errors': errors}, status=400)

        user = request.user
        ip   = _get_client_ip(request)
        ua   = request.META.get('HTTP_USER_AGENT', '')[:300]

        with transaction.atomic():
            pref, _ = ConectaPreference.objects.get_or_create(user=user)
            pref.whatsapp_number = cleaned['whatsapp_number'] or pref.whatsapp_number
            pref.alert_email     = cleaned['alert_email']     or pref.alert_email
            pref.whatsapp_active = cleaned['whatsapp_active']
            pref.email_active    = cleaned['email_active']
            pref.calendar_active = cleaned['calendar_active']

            if cleaned['revoke_consent']:
                pref.revoke_consent(ip=ip, ua=ua)
            elif cleaned['consent_granted'] and not pref.consent_granted:
                channels = ','.join(filter(None, [
                    'whatsapp' if cleaned['whatsapp_active'] else '',
                    'email'    if cleaned['email_active']    else '',
                    'calendar' if cleaned['calendar_active'] else '',
                ]))
                pref.consent_granted  = True
                pref.consent_at       = timezone.now()
                pref.consent_version  = ConectaPreference.CONSENT_VERSION
                pref.consent_channels = channels
                pref.save()
                ConectaConsentEvent.objects.create(
                    user=user, action='granted',
                    version=ConectaPreference.CONSENT_VERSION,
                    channels=channels,
                    whatsapp=pref.whatsapp_number,
                    email=pref.alert_email,
                    ip_address=ip, user_agent=ua,
                )
            else:
                pref.save()

            new_inst = set(cleaned.get('institutional', []))
            ConectaSubscription.objects.filter(
                user=user, type='institutional'
            ).exclude(key__in=new_inst).update(enabled=False)
            for slug in new_inst:
                ConectaSubscription.objects.update_or_create(
                    user=user, type='institutional', key=slug,
                    defaults={'enabled': True}
                )

            new_subj = set(cleaned.get('subjects', []))
            ConectaSubscription.objects.filter(
                user=user, type='subject'
            ).exclude(key__in=new_subj).update(enabled=False)
            for slug in new_subj:
                ConectaSubscription.objects.update_or_create(
                    user=user, type='subject', key=slug,
                    defaults={'enabled': True}
                )

        return JsonResponse({
            'ok': True,
            'message': 'Preferencias guardadas correctamente.',
            'institutional_count': ConectaSubscription.objects.filter(
                user=user, type='institutional', enabled=True).count(),
            'subject_count': ConectaSubscription.objects.filter(
                user=user, type='subject', enabled=True).count(),
        })

    return JsonResponse({'ok': False, 'error': 'Method not allowed'}, status=405)


# ══════════════════════════════════════════════════════════════════
# 📅  ACADEMIC EVENTS API
# ══════════════════════════════════════════════════════════════════

@login_required
def api_events_list(request):
    """GET → lista eventos do usuário em JSON."""
    events = AcademicEvent.objects.filter(user=request.user)
    # Filtro opcional por tipo
    etype = request.GET.get('type')
    if etype:
        events = events.filter(event_type=etype)
    # Filtro por mês/ano
    month = request.GET.get('month')
    year  = request.GET.get('year')
    if month and year:
        events = events.filter(
            start_datetime__month=month,
            start_datetime__year=year,
        )
    return JsonResponse({'ok': True, 'events': [e.to_dict() for e in events]})


@login_required
def api_events_create(request):
    """POST → cria novo evento acadêmico."""
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'ok': False, 'error': 'JSON inválido'}, status=400)

    # Validações mínimas
    title       = data.get('title', '').strip()
    event_type  = data.get('event_type', '').strip()
    start_str   = data.get('start_datetime', '').strip()
    if not title:
        return JsonResponse({'ok': False, 'error': 'El título es obligatorio.'}, status=400)
    if not event_type:
        return JsonResponse({'ok': False, 'error': 'El tipo de evento es obligatorio.'}, status=400)
    if not start_str:
        return JsonResponse({'ok': False, 'error': 'La fecha y hora son obligatorias.'}, status=400)

    valid_types = [c[0] for c in AcademicEvent.TYPE_CHOICES]
    if event_type not in valid_types:
        return JsonResponse({'ok': False, 'error': 'Tipo de evento inválido.'}, status=400)

    def parse_dt(s):
        if not s:
            return None
        for fmt in ('%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M', '%Y-%m-%d'):
            try:
                from django.utils import timezone as tz
                naive = datetime.strptime(s, fmt)
                return tz.make_aware(naive)
            except ValueError:
                continue
        return None

    start_dt = parse_dt(start_str)
    if not start_dt:
        return JsonResponse({'ok': False, 'error': 'Formato de fecha inválido.'}, status=400)

    event = AcademicEvent.objects.create(
        user                  = request.user,
        title                 = title,
        subject               = data.get('subject', '').strip(),
        event_type            = event_type,
        start_datetime        = start_dt,
        end_datetime          = parse_dt(data.get('end_datetime', '')),
        location              = data.get('location', '').strip(),
        notes                 = data.get('notes', '').strip(),
        registration_open_at  = parse_dt(data.get('registration_open_at', '')),
        registration_deadline = parse_dt(data.get('registration_deadline', '')),
        status                = 'upcoming',
    )
    return JsonResponse({'ok': True, 'event': event.to_dict()}, status=201)


@login_required
def api_events_update(request, pk):
    """POST → edita evento existente (só o dono)."""
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Method not allowed'}, status=405)
    try:
        event = AcademicEvent.objects.get(pk=pk, user=request.user)
    except AcademicEvent.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Evento no encontrado.'}, status=404)
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'ok': False, 'error': 'JSON inválido'}, status=400)

    def parse_dt(s):
        if not s:
            return None
        for fmt in ('%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M', '%Y-%m-%d'):
            try:
                from django.utils import timezone as tz
                return tz.make_aware(datetime.strptime(s, fmt))
            except ValueError:
                continue
        return None

    if 'title'       in data: event.title       = data['title'].strip()
    if 'subject'     in data: event.subject      = data['subject'].strip()
    if 'event_type'  in data: event.event_type   = data['event_type']
    if 'location'    in data: event.location     = data['location'].strip()
    if 'notes'       in data: event.notes        = data['notes'].strip()
    if 'status'      in data: event.status       = data['status']
    if 'start_datetime'        in data: event.start_datetime        = parse_dt(data['start_datetime'])
    if 'end_datetime'          in data: event.end_datetime          = parse_dt(data['end_datetime'])
    if 'registration_open_at'  in data: event.registration_open_at  = parse_dt(data['registration_open_at'])
    if 'registration_deadline' in data: event.registration_deadline = parse_dt(data['registration_deadline'])
    event.save()
    return JsonResponse({'ok': True, 'event': event.to_dict()})


@login_required
def api_events_delete(request, pk):
    """POST → deleta evento (só o dono)."""
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Method not allowed'}, status=405)
    try:
        event = AcademicEvent.objects.get(pk=pk, user=request.user)
    except AcademicEvent.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Evento no encontrado.'}, status=404)
    google_id = event.google_event_id
    event.delete()
    return JsonResponse({'ok': True, 'google_event_id': google_id})


@login_required
def api_events_status(request, pk):
    """POST → atualiza status/confirmação de inscrição."""
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Method not allowed'}, status=405)
    try:
        event = AcademicEvent.objects.get(pk=pk, user=request.user)
    except AcademicEvent.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Evento no encontrado.'}, status=404)
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'ok': False, 'error': 'JSON inválido'}, status=400)

    if 'status'                    in data: event.status                    = data['status']
    if 'registration_confirmed'    in data: event.registration_confirmed    = data['registration_confirmed']
    if 'inscription_alert_dismissed' in data: event.inscription_alert_dismissed = data['inscription_alert_dismissed']
    event.save()
    return JsonResponse({'ok': True, 'event': event.to_dict()})


@login_required
def api_events_gcal(request, pk):
    """POST → sincroniza evento com Google Calendar do usuário."""
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Method not allowed'}, status=405)
    try:
        event = AcademicEvent.objects.get(pk=pk, user=request.user)
    except AcademicEvent.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Evento no encontrado.'}, status=404)

    # Verificar se Google socialaccount está disponível
    try:
        from allauth.socialaccount.models import SocialToken, SocialApp
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build as gcal_build
        has_gcal = True
    except ImportError:
        has_gcal = False

    if not has_gcal:
        return JsonResponse({
            'ok': False,
            'proximamente': True,
            'message': 'Google Calendar — Próximamente. La integración estará disponible pronto.',
        })

    # Verificar se app Google está configurado
    try:
        app = SocialApp.objects.get(provider='google')
    except SocialApp.DoesNotExist:
        return JsonResponse({
            'ok': False,
            'proximamente': True,
            'message': 'Google Calendar — Próximamente.',
        })

    # Obter token do usuário
    try:
        token_obj = SocialToken.objects.get(account__user=request.user, account__provider='google')
    except SocialToken.DoesNotExist:
        return JsonResponse({
            'ok': False,
            'needs_oauth': True,
            'message': 'Necesitás conectar tu cuenta de Google primero.',
        })

    creds = Credentials(
        token         = token_obj.token,
        refresh_token = token_obj.token_secret,
        client_id     = app.client_id,
        client_secret = app.secret,
        token_uri     = 'https://oauth2.googleapis.com/token',
    )
    service = gcal_build('calendar', 'v3', credentials=creds)

    # Construir evento Google
    end_dt = event.end_datetime or (event.start_datetime + timedelta(hours=2))
    gcal_event = {
        'summary':     event.title,
        'description': f"{event.subject}\n\n{event.notes}".strip(),
        'location':    event.location,
        'start':       {'dateTime': event.start_datetime.isoformat(), 'timeZone': 'America/Argentina/Buenos_Aires'},
        'end':         {'dateTime': end_dt.isoformat(),               'timeZone': 'America/Argentina/Buenos_Aires'},
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 60},
                {'method': 'popup', 'minutes': 1440},
            ],
        },
    }
    # Lembrete 10 dias para finais/parciais
    if event.event_type in ('final', 'parcial', 'inscripcion', 'simulacro'):
        gcal_event['reminders']['overrides'].append(
            {'method': 'popup', 'minutes': 10 * 1440}
        )

    try:
        if event.google_event_id:
            # Atualizar evento existente
            result = service.events().update(
                calendarId='primary',
                eventId=event.google_event_id,
                body=gcal_event,
            ).execute()
        else:
            # Criar novo evento
            result = service.events().insert(
                calendarId='primary',
                body=gcal_event,
            ).execute()

        event.google_event_id   = result.get('id', '')
        event.google_calendar_id = 'primary'
        event.google_synced_at  = timezone.now()
        event.save(update_fields=['google_event_id', 'google_calendar_id', 'google_synced_at'])

        return JsonResponse({'ok': True, 'google_event_id': event.google_event_id,
                             'message': '¡Agregado a Google Calendar!'})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)


# ══════════════════════════════════════════════════════════════════
# 📋  PLANEJAMENTO ACADÊMICO — página dedicada
# ══════════════════════════════════════════════════════════════════

@login_required
def planejamento_view(request):
    """Página completa de planejamento acadêmico com todos os eventos."""
    from django.utils import timezone as tz
    now  = tz.now()
    user = request.user

    # Atualizar status automaticamente
    upcoming_events = AcademicEvent.objects.filter(
        user=user, start_datetime__gte=now
    ).order_by('start_datetime')

    past_events = AcademicEvent.objects.filter(
        user=user, start_datetime__lt=now, status__in=['upcoming', 'pending', 'open']
    )
    past_events.update(status='done')

    # Alertas de inscrição (faltam ≤10 dias, não dispensado)
    alerts = [e for e in upcoming_events if e.needs_inscription_alert]

    # Verificar Google Calendar disponibilidade
    gcal_available = False
    try:
        from allauth.socialaccount.models import SocialApp, SocialToken
        gcal_available = (
            SocialApp.objects.filter(provider='google').exists() and
            SocialToken.objects.filter(account__user=user, account__provider='google').exists()
        )
    except Exception:
        pass

    context = {
        'upcoming_events':  list(upcoming_events),
        'past_events':      list(AcademicEvent.objects.filter(
                                 user=user, start_datetime__lt=now
                             ).order_by('-start_datetime')[:20]),
        'alerts':           alerts,
        'gcal_available':   gcal_available,
        'events_json':      json.dumps(
                                [e.to_dict() for e in AcademicEvent.objects.filter(user=user)],
                                cls=DjangoJSONEncoder
                            ),
        'now':              now,
    }
    return render(request, 'accounts/planejamento.html', context)
