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
from django.http import JsonResponse
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


def _get_api_client():
    """Retorna o tipo de cliente ativo e sua instância (openai ou gemini)."""
    openai_key = os.environ.get('OPENAI_API_KEY') or getattr(settings, 'OPENAI_API_KEY', '')
    gemini_key = os.environ.get('GEMINI_API_KEY') or getattr(settings, 'GEMINI_API_KEY', '')

    if gemini_key:
        import google.generativeai as genai
        genai.configure(api_key=gemini_key)
        return 'gemini', genai

    if openai_key:
        from openai import OpenAI
        return 'openai', OpenAI(api_key=openai_key)

    return 'mock', None


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Similaridade de cosseno entre dois vetores."""
    min_len = min(len(a), len(b))
    if min_len == 0:
        return 0.0
    dot = sum(a[i] * b[i] for i in range(min_len))
    norm_a = math.sqrt(sum(x * x for x in a[:min_len]))
    norm_b = math.sqrt(sum(y * y for y in b[:min_len]))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _embed_query(client_type, client, question: str) -> list[float]:
    if client_type == 'gemini':
        result = client.embed_content(
            model="models/text-embedding-004",
            content=question,
            task_type="retrieval_query"
        )
        return result['embedding']
    elif client_type == 'openai':
        resp = client.embeddings.create(
            model='text-embedding-3-small',
            input=question[:2000],
        )
        return resp.data[0].embedding
    else:
        # Mock embedding (tamanho 1536)
        return [0.1] * 1536


def _find_relevant_chunks(question_embedding: list[float], question: str = '', top_k: int = TOP_K) -> list[ProfeJoyChunk]:
    """Busca os chunks mais similares à pergunta. Usa palavra-chave como fallback se for mock."""
    all_chunks = ProfeJoyChunk.objects.all()
    if not all_chunks.exists():
        return []

    # Se for mock, faz busca simples por palavra-chave
    if len(all_chunks.exclude(embedding=[])) == 0 or question_embedding == [0.1] * 1536:
        scored = []
        words = [w.lower() for w in question.split() if len(w) > 3]
        for chunk in all_chunks:
            score = 0
            for word in words:
                if word in chunk.content.lower():
                    score += 1
                if word in chunk.title.lower():
                    score += 2
            scored.append((score, chunk))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [chunk for score, chunk in scored[:top_k] if score > 0]

    # Busca semântica real
    scored = []
    for chunk in all_chunks.exclude(embedding=[]):
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
        client_type, client = _get_api_client()

        # 1. Embed a pergunta
        q_embedding = _embed_query(client_type, client, question)

        # 2. Buscar chunks relevantes
        relevant = _find_relevant_chunks(q_embedding, question)

        # Se não achou nada relevante e estamos em mock, pega qualquer um para simular
        if not relevant and client_type == 'mock':
            relevant = list(ProfeJoyChunk.objects.all()[:2])

        if not relevant:
            return JsonResponse({
                'answer': '🤔 Não encontrei materiais relevantes para essa pergunta.',
                'sources': [],
                'chunks_used': 0,
            })

        # 3. Construir contexto
        context = _build_context(relevant)
        system  = SYSTEM_PROMPT.format(context=context)

        # 4. Chamar LLM correspondente (Gemini, OpenAI ou Mock)
        if client_type == 'gemini':
            model = client.GenerativeModel(
                model_name="gemini-2.0-flash",
                system_instruction=system
            )
            
            contents = []
            for msg in history[-6:]:
                role = 'user' if msg.get('role') == 'user' else 'model'
                contents.append({'role': role, 'parts': [msg.get('content', '')]})
            contents.append({'role': 'user', 'parts': [question]})
            
            response = model.generate_content(
                contents=contents,
                generation_config={"temperature": 0.3}
            )
            answer = response.text
        elif client_type == 'openai':
            messages = [{'role': 'system', 'content': system}]
            for msg in history[-6:]:
                if msg.get('role') in ('user', 'assistant') and msg.get('content'):
                    messages.append({'role': msg['role'], 'content': msg['content']})
            messages.append({'role': 'user', 'content': question})

            response = client.chat.completions.create(
                model='gpt-4o-mini',
                messages=messages,
                temperature=0.3,
                max_tokens=1000,
            )
            answer = response.choices[0].message.content
        else:
            # Fallback Mock Inteligente
            first_chunk = relevant[0]
            answer = f"🤖 [MOCK DEMO] Com base no material **{first_chunk.title}**:\n\n{first_chunk.content[:250]}...\n\n*(Nota: O servidor está rodando em modo demonstração local porque nenhuma chave de API válida ou com saldo da OpenAI/Gemini foi detectada. Cadastre as chaves para ter respostas reais completas!)*"

        # 5. Montar fontes únicas
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
