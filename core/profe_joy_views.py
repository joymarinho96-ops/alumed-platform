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

PROMPT_PROFE_JOY = """
Tu eres la Profe Joy, la tutora inteligente médica oficial del ecosistema ALUMED OS (integrando la profundidad clínica del Instituto Alumed y la realidad académica del Conecta FCM de la UNLP). Tu propósito es guiar, enseñar y desafiar al estudiante de medicina con una didáctica humana, rigor científico y foco práctico, eliminando respuestas robóticas de "copiar y pegar" archivos.

---

## 🧠 Directrices Estrictas de Comportamiento Pedagógico

1. **Cero Copiar y Pegar Archivos:** Nunca respondas únicamente pegando bloques secos de texto o PDFs de apuntes. Los documentos y libros de la biblioteca son tu fuente de verdad interna, pero debes procesar el conocimiento y explicarlo con tus propias palabras.
2. **Metodología de Explicación Activa (Paso a Paso):** Cada vez que expliques un concepto (ej. Histología, Anatomía, Embriología o Biología), sigue obligatoriamente la progresión lógica:
   - **¿Qué es?** (Definición clara y directa).
   - **¿Dónde está y cómo se ubica?** (Relación espacial macroscópica o microscópica).
   - **¿Qué estructura/características tiene?** (Componentes esenciales).
   - **¿Qué función cumple?** (El porqué biológico y fisiológico antes de memorizar).
3. **Anticipación de Trampas de Examen (Cátedras UNLP):** Siempre que sea pertinente, alerta al alumno sobre las "preguntas cazabobos" o trampas clásicas evaluadas en las Cátedras A, B o C de Anatomía y en las comisiones de Histología/Biología de la FCM UNLP.
4. **Puente Interactivo en el Ecosistema:** Conecta dinámicamente las dudas del alumno con las herramientas de ALUMED OS. Si falla o tiene dudas sobre un tejido o estructura, sugiere de forma fluida:
   - *"¿Querés que repasemos esto con un flashcard rápido?"*
   - *"¿Lo visualizamos en el microscopio virtual / atlas 3D?"*
   - *"¿Practicamos una pregunta tipo parcial choice de este tema?"*

---

## 🎨 Tono y Estilo
- **Tono:** Empático, exigente, acogedor y enfocado (con la esencia de quien entiende la rutina pesada de un estudiante de medicina en la UNLP).
- **Idioma:** Español médico claro, académico y accesible, con toques amigables y profesionales.
- **Identidad Visual / Estética:** Respeta siempre el ecosistema unificado (Zona de Foco Púrpura/Rojo y Radar Académico Dorado).

Contexto oficial recuperado de la base de datos:
{contexto}

Pregunta del alumno:
{pregunta}
"""

TOP_K = 5  # número de chunks mais relevantes a buscar


def _get_api_client():
    """Retorna o tipo de cliente ativo e sua instância (openai, gemini, ou fastembed)."""
    # Sempre usamos o fastembed para o embedding grátis Open Source
    # e usamos OpenAI/Gemini apenas para gerar o texto da resposta LLM.
    
    openai_key = os.environ.get('OPENAI_API_KEY') or getattr(settings, 'OPENAI_API_KEY', '')
    gemini_key = os.environ.get('GEMINI_API_KEY') or getattr(settings, 'GEMINI_API_KEY', '')

    if gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            return 'gemini', genai
        except ImportError:
            logger.warning("google.generativeai package not found. Falling back to DB.")

    if openai_key:
        try:
            from openai import OpenAI
            return 'openai', OpenAI(api_key=openai_key)
        except ImportError:
            logger.warning("openai package not found. Falling back to DB.")

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
    """Usa Gemini gemini-embedding-001 (dim=3072) para embeddear la pregunta.
    Fallback a mock si Gemini no esta disponible."""
    import requests as req
    gemini_key = os.environ.get('GEMINI_API_KEY') or getattr(settings, 'GEMINI_API_KEY', '')
    if gemini_key:
        try:
            url = "https://generativelanguage.googleapis.com/v1/models/gemini-embedding-001:embedContent"
            payload = {
                "model": "models/gemini-embedding-001",
                "content": {"parts": [{"text": question[:9000]}]},
                "taskType": "RETRIEVAL_QUERY"
            }
            resp = req.post(url, json=payload, params={"key": gemini_key}, timeout=10)
            resp.raise_for_status()
            return resp.json()["embedding"]["values"]
        except Exception as e:
            logger.warning(f"Gemini embedding fallo: {e}. Usando mock...")

    # Fallback mock (3072-dim para coincidir con gemini-embedding-001)
    return [0.1] * 3072



def _find_relevant_chunks(question_embedding: list[float], question: str = '', top_k: int = TOP_K) -> list[ProfeJoyChunk]:
    """Busca os chunks mais similares à pergunta. Usa palavra-chave como fallback se for mock."""
    lowered_q = question.lower()
    notices_keywords = [
        'cartelera', 'aviso', 'fecha', 'inscripcion', 'inscripción', 'calendario', 
        'horario', 'trámite', 'tramite', 'beca', 'novedad', 'novedades', 
        'noticia', 'noticias', 'anuncio', 'anuncios', 'comisión', 'comisiones',
        'tp', 'tps', 'parcial', 'final', 'examen', 'exámenes'
    ]
    is_notices_query = any(kw in lowered_q for kw in notices_keywords)

    all_chunks = ProfeJoyChunk.objects.all()
    if not all_chunks.exists():
        return []

    # Filter subset based on query type
    if is_notices_query:
        chunks_subset = all_chunks.filter(title__startswith="Cartelera")
        if not chunks_subset.exists():
            chunks_subset = all_chunks
    else:
        chunks_subset = all_chunks.filter(title__startswith="Libro")
        if not chunks_subset.exists():
            chunks_subset = all_chunks

    # Se for mock, faz busca simples por palavra-chave
    if len(chunks_subset.exclude(embedding=[])) == 0 or question_embedding == [0.1] * 384:
        scored = []
        words = [w.lower() for w in question.split() if len(w) > 3]
        for chunk in chunks_subset:
            score = 0
            for word in words:
                if word in chunk.content.lower():
                    score += 1
                if word in chunk.title.lower():
                    score += 2
            scored.append((score, chunk))
        scored.sort(key=lambda x: x[0], reverse=True)
        
        results = [chunk for score, chunk in scored[:top_k] if score > 0]
        if not results:
            # Fallback a los 2 primeros chunks del subconjunto si no hubo coincidencia por palabra clave
            results = list(chunks_subset[:2])
        return results

    # Busca semântica real
    scored = []
    for chunk in chunks_subset.exclude(embedding=[]):
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

        # 1. Embed a pergunta (com fallback de segurança para mock se falhar)
        try:
            q_embedding = _embed_query(client_type, client, question)
        except Exception as embed_exc:
            logger.warning(f"Erro no embedding ({client_type}), usando fallback mock: {embed_exc}")
            client_type = 'mock'
            client = None
            q_embedding = [0.1] * 384

        # 2. Buscar chunks relevantes
        relevant = _find_relevant_chunks(q_embedding, question)

        if not relevant:

            return JsonResponse({
                'answer': '🤔 Não encontrei materiais relevantes para essa pergunta.',
                'sources': [],
                'chunks_used': 0,
            })

        # 3. Construir contexto
        context = _build_context(relevant)
        system  = PROMPT_PROFE_JOY.format(contexto=context, pregunta=question)

        # 4. Chamar LLM correspondente (Gemini, OpenAI ou Mock) com try-except de segurança
        answer = None
        if client_type == 'gemini':
            try:
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
            except Exception as gemini_exc:
                logger.error(f"Erro na API Gemini: {gemini_exc}")
                client_type = 'mock'

        if client_type == 'openai' and answer is None:
            try:
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
            except Exception as openai_exc:
                logger.error(f"Erro na API OpenAI: {openai_exc}")
                client_type = 'mock'

        if client_type == 'mock' or answer is None:
            # Conversational offline mock for Profe Joy
            import re
            clean_q = re.sub(r'[¿?¡!,.]', '', question.lower().strip())
            
            # GREETINGS & INTROS
            if any(greet in clean_q for greet in ('hola', 'holis', 'buen dia', 'buenos dias', 'buenas tardes', 'buenas noches')):
                answer = "¡Holis, corazón! Qué lindo saludarte. ¿Cómo andás? Contame qué materia estás estudiando hoy (Anatomía, Histo, Embrio, Biología...) y le metemos juntos. ¡Estoy eh! 😘"
            elif any(q in clean_q for q in ('como estas', 'como andas', 'como andas', 'todo bien', 'que tal', 'cómo estás', 'cómo andás')):
                answer = "¡Hola, doc! Yo estoy de diez, re contenta de poder darte una mano con el estudio. ¿Y vos cómo venís llevando la cursada? ¿Te sentís con pilas? ¡Vamos que vos podés, mis amores! ¿Pudiste? 💪"
            elif any(q in clean_q for q in ('quien sos', 'quién sos', 'quien eres', 'quién eres', 'tu nombre', 'como te llamas')):
                answer = "¡Holis! Soy la Profe Joy, tu profesora compañera para ayudarte a sacarte todas las dudas de Histología, Anatomía, Embriología y Biología. Estoy acá para bancarte en este camino de medicina. ¡Allright! 😉"
            elif any(q in clean_q for q in ('gracias', 'muchas gracias', 'genia', 'crack', 'gloria')):
                answer = "¡De nada, corazón! Es un placer enorme ayudarte. A seguir metiéndole garra que vas a ser un doc increíble. ¡Cualquier duda me chiflás, estoy eh! 🥰"
            else:
                # Academic or other queries - wrap the retrieved chunk in a warm Profe Joy message
                parts = []
                parts.append("¡Hola, doc! Con respecto a tu consulta, mirá lo que encontré en los apuntes oficiales para vos:\n")
                
                for idx, chunk in enumerate(relevant[:2], 1):
                    source_info = chunk.title
                    if chunk.subject:
                        source_info += f" ({chunk.subject})"
                    parts.append(f"📌 **De la fuente: {source_info}**\n{chunk.content}\n")
                
                parts.append("¿Quedó claro, sí o no? ¡Metele que vas súper bien, mi amor! ¡Estoy acá eh! 💪✨")
                answer = "\n".join(parts)



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
