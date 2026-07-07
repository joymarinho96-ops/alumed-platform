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
from .models import ChatMessage, Profile
from django.core.management import call_command
from django.contrib import messages
from functools import wraps
from django.urls import reverse

def student_auth_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            next_url = request.get_full_path()
            return redirect(f"{reverse('auth_gate')}?next={next_url}")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def auth_gate_view(request):
    return redirect('https://alumed.wixsite.com/alumed/login')

def login_view(request):
    return redirect('https://alumed.wixsite.com/alumed/login')

def register_view(request):
    return redirect('https://alumed.wixsite.com/alumed/registro')

def logout_view(request):
    logout(request)
    return redirect('home')

@student_auth_required
def student_dashboard_view(request):
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
