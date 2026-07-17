"""
Views do Profe Joy IA — RAG chat endpoint.
POST /profe-joy/chat/   → responde perguntas com base nos materiais ingeridos.
GET  /profe-joy/        → página do chat (standalone).
"""
import json
import logging
import math
import os

from django.conf import settings
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render

from accounts.models import ProfeJoyChunk

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Você é a **Profe Joy**, assistente de estudos da FCM-UNLP (Faculdade de Ciências Médicas da Universidade Nacional de La Plata).

Seu papel é ajudar os alunos de medicina a estudar e entender os materiais da faculdade.

Regras:
- Responda **sempre em Português** (a língua do sistema é PT-BR).
- Se o aluno perguntar em espanhol, responda em espanhol.
- Base suas respostas EXCLUSIVAMENTE no contexto fornecido abaixo.
- Se a informação não estiver no contexto, diga honestamente: "Não encontrei esse conteúdo nos materiais cadastrados."
- Seja didática, clara e use exemplos quando possível.
- Use emojis com moderação para tornar a resposta mais amigável.
- Cite a fonte do material quando relevante.

Contexto dos materiais:
{context}
"""

TOP_K = 5  # número de chunks mais relevantes a buscar


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Similaridade de cosseno entre dois vetores."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _get_openai_client():
    from openai import OpenAI
    key = os.environ.get('OPENAI_API_KEY') or getattr(settings, 'OPENAI_API_KEY', '')
    if not key:
        raise ValueError('OPENAI_API_KEY não configurada!')
    return OpenAI(api_key=key)


def _embed_query(client, question: str) -> list[float]:
    resp = client.embeddings.create(
        model='text-embedding-3-small',
        input=question[:2000],
    )
    return resp.data[0].embedding


def _find_relevant_chunks(question_embedding: list[float], top_k: int = TOP_K) -> list[ProfeJoyChunk]:
    """Busca os chunks mais similares à pergunta por similaridade de cosseno."""
    all_chunks = ProfeJoyChunk.objects.exclude(embedding=[]).only(
        'id', 'title', 'content', 'source_url', 'embedding', 'year', 'subject'
    )

    scored = []
    for chunk in all_chunks:
        if not chunk.embedding:
            continue
        score = _cosine_similarity(question_embedding, chunk.embedding)
        scored.append((score, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk in scored[:top_k]]


def _build_context(chunks: list) -> str:
    parts = []
    for i, chunk in enumerate(chunks, 1):
        source = chunk.title
        if chunk.subject:
            source += f' — {chunk.subject}'
        parts.append(f'[{i}] **{source}**\n{chunk.content}')
    return '\n\n---\n\n'.join(parts)


@csrf_exempt
@require_http_methods(['POST'])
def profe_joy_chat(request):
    """
    Endpoint principal do chat.
    Body JSON: { "question": "...", "history": [...] (opcional) }
    """
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'error': 'JSON inválido'}, status=400)

    question = (body.get('question') or '').strip()
    history  = body.get('history', [])  # lista de {role, content}

    if not question:
        return JsonResponse({'error': 'Pergunta vazia'}, status=400)

    # Verifica se temos materiais
    total_chunks = ProfeJoyChunk.objects.count()
    if total_chunks == 0:
        return JsonResponse({
            'answer': (
                '📚 Ainda não há materiais cadastrados na base de conhecimento do Profe Joy. '
                'Solicite ao administrador que faça upload de PDFs!'
            ),
            'sources': [],
            'chunks_used': 0,
        })

    try:
        client = _get_openai_client()

        # 1. Embed a pergunta
        q_embedding = _embed_query(client, question)

        # 2. Buscar chunks relevantes
        relevant = _find_relevant_chunks(q_embedding)

        if not relevant:
            return JsonResponse({
                'answer': '🤔 Não encontrei materiais relevantes para essa pergunta.',
                'sources': [],
                'chunks_used': 0,
            })

        # 3. Construir contexto
        context = _build_context(relevant)
        system  = SYSTEM_PROMPT.format(context=context)

        # 4. Montar mensagens
        messages = [{'role': 'system', 'content': system}]
        # Adiciona histórico (máx. 6 turnos)
        for msg in history[-6:]:
            if msg.get('role') in ('user', 'assistant') and msg.get('content'):
                messages.append({'role': msg['role'], 'content': msg['content']})
        messages.append({'role': 'user', 'content': question})

        # 5. Chamar GPT
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=messages,
            temperature=0.3,
            max_tokens=1000,
        )
        answer = response.choices[0].message.content

        # 6. Montar fontes únicas
        sources = []
        seen = set()
        for chunk in relevant:
            key = chunk.title
            if key not in seen:
                seen.add(key)
                sources.append({
                    'title':   chunk.title,
                    'subject': chunk.subject,
                    'url':     chunk.source_url,
                })

        return JsonResponse({
            'answer':      answer,
            'sources':     sources,
            'chunks_used': len(relevant),
        })

    except Exception as exc:
        logger.error(f'ProfeJoy chat error: {exc}', exc_info=True)
        return JsonResponse({'error': f'Erro interno: {str(exc)}'}, status=500)


def profe_joy_page(request):
    """Página standalone do chat Profe Joy."""
    total = ProfeJoyChunk.objects.count()
    materials = ProfeJoyChunk.objects.values('title', 'subject', 'year') \
                    .distinct().order_by('title')[:20]
    return render(request, 'profe_joy.html', {
        'total_chunks': total,
        'materials': materials,
    })


def profe_joy_stats(request):
    """API de estatísticas para o admin."""
    from django.db.models import Count
    stats = {
        'total_chunks': ProfeJoyChunk.objects.count(),
        'total_materials': ProfeJoyChunk.objects.values('title').distinct().count(),
        'by_year': list(
            ProfeJoyChunk.objects.values('year')
            .annotate(count=Count('id'))
            .order_by('year')
        ),
    }
    return JsonResponse(stats)
