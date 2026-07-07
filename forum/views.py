from django.shortcuts import render, get_object_or_404, redirect
from accounts.views import student_auth_required
from .models import Topic, Reply, SUBJECT_CHOICES
from .forms import TopicForm, ReplyForm
from django.contrib import messages
from django.db.models import Count

@student_auth_required
def topic_list(request):
    active_subject = request.GET.get('materia')
    
    if not active_subject:
        # User has not selected a subject yet, render the selector
        # Calculate counts for each subject
        counts_query = Topic.objects.values('subject').annotate(count=Count('id'))
        counts_map = {item['subject']: item['count'] for item in counts_query}
        
        # Build list of subjects with details and testimonial count
        subjects_data = []
        for key, name in SUBJECT_CHOICES:
            subjects_data.append({
                'key': key,
                'name': name,
                'count': counts_map.get(key, 0)
            })
            
        return render(request, 'forum/materia_selector.html', {
            'subjects': subjects_data
        })
        
    # User has selected a subject, filter testimonials for that subject
    # Get active subject display name
    active_subject_name = dict(SUBJECT_CHOICES).get(active_subject, "Testimonios")
    
    topics = Topic.objects.filter(subject=active_subject).order_by('-created_at')
    
    return render(request, 'forum/topic_list.html', {
        'topics': topics,
        'active_subject': active_subject,
        'active_subject_name': active_subject_name
    })

@student_auth_required
def topic_detail(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    replies = topic.replies.all().order_by('created_at')
    
    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.topic = topic
            reply.author = request.user
            reply.save()
            messages.success(request, '¡Respuesta publicada con éxito!')
            return redirect('forum:topic_detail', topic_id=topic.id)
    else:
        form = ReplyForm()

    return render(request, 'forum/topic_detail.html', {
        'topic': topic,
        'replies': replies,
        'form': form
    })

@student_auth_required
def create_topic(request):
    active_subject = request.GET.get('materia', 'histologia')
    if request.method == 'POST':
        form = TopicForm(request.POST, request.FILES)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.author = request.user
            topic.subject = active_subject
            topic.save()
            messages.success(request, '¡Testimonio publicado con éxito!')
            return redirect(f"/foro/?materia={active_subject}")
    else:
        form = TopicForm()
    
    return render(request, 'forum/create_topic.html', {
        'form': form,
        'active_subject': active_subject
    })

