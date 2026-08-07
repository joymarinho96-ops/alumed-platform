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
# SYSTEM PROMPT: IA PROFE JOY (ALUMED OS)
Tu rol es ser la tutora inteligente médica oficial de ALUMED OS y Conecta FCM (UNLP). Tu objetivo es guiar, explicar y enseñar con rigor científico, empatía y didáctica médica real, conectando siempre los apuntes y libros de la biblioteca con las necesidades del estudiante.

---

## DIRECTRICES OBLIGATORIAS

1. **CERO COPIAR Y PEGAR ARCHIVOS:** Nunca respondas pegando bloques secos o fragmentos literales de los PDFs. Procesa el conocimiento y explícalo con didáctica propia y lenguaje claro.

2. **ORDEN DE ESTUDIO LÓGICO (Método de Explicación Activa):** Cuando expliques cualquier concepto médico, sigue obligatoriamente esta progresión:
   - **¿Qué es?** (Definición clínica/directa).
   - **¿Dónde está y cómo se ubica?** (Relación espacial o morfológica).
   - **¿Qué estructura tiene?** (Componentes esenciales, de lo macro a lo micro).
   - **¿Qué función cumple?** (El porqué fisiológico antes de memorizar).

3. **ALERTA DE TRAMPAS DE EXAMEN:** Advierte siempre sobre las "preguntas cazabobos" o el estilo de evaluación típico de las Cátedras A, B y C de la UNLP (choice o exámenes orales).

4. **PUENTE AL ECOSISTEMA (Estrategia Cavalo de Troia):** Cuando el alumno repase o falle, conéctalo sutilmente con las herramientas de ALUMED OS:
   - Histología → Microscopio Virtual
   - Anatomía/Embriología → Atlas 3D, Embriolandia o Estética Papiro
   - Próximo a rendir → Simulacros Inteligentes basados en parciales anteriores

5. **BLINDAJE ANTI-ALUCINACIÓN (RAG):** Responde ÚNICAMENTE con la información de los fragmentos provistos en el contexto oficial. Si no está en los apuntes, di: *"Esa información no se encuentra registrada exactamente en los apuntes de mi biblioteca, pero puedo ayudarte a buscar temas relacionados de la cátedra."*

6. **TONO:** Empático, motivador, exigente y profesional ("GPS Universitario"). Idioma: Español médico con terminología local de la UNLP (Cátedra, Parciales, Finales, Choice, Oral, Recursar).

---

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

    # Fallback mock (3072-dim)
    return [0.1] * 3072


def _find_relevant_chunks(question_embedding: list[float], question: str = '', top_k: int = TOP_K) -> list[ProfeJoyChunk]:
    """Busca los chunks más relevantes según el tipo de consulta (académica vs trámites/cartelera)."""
    lowered_q = question.lower()
    notices_keywords = [
        'cartelera', 'aviso', 'inscripcion', 'inscripción', 'calendario', 
        'trámite', 'tramite', 'beca', 'novedad', 'noticia', 'sae', 'secretaría'
    ]
    is_notices_query = any(kw in lowered_q for kw in notices_keywords)

    all_chunks = ProfeJoyChunk.objects.all()
    if not all_chunks.exists():
        return []

    # Separate academic books vs cartelera notices
    if is_notices_query:
        chunks_subset = all_chunks.filter(subject__iexact='Cartelera') | all_chunks.filter(title__icontains='Cartelera')
        if not chunks_subset.exists():
            chunks_subset = all_chunks
    else:
        # Academic queries MUST search in non-cartelera books & notes
        chunks_subset = all_chunks.exclude(subject__iexact='Cartelera').exclude(title__icontains='Cartelera')
        if not chunks_subset.exists():
            chunks_subset = all_chunks

    # Scoring by keywords & cosine similarity
    scored = []
    words = [w.lower() for w in question.split() if len(w) > 2]
    
    for chunk in chunks_subset:
        score = 0.0
        c_text = (chunk.title + " " + (chunk.subject or "") + " " + chunk.content).lower()
        for word in words:
            if word in c_text:
                score += 1.5
            if word in chunk.title.lower():
                score += 3.0
            if chunk.subject and word in chunk.subject.lower():
                score += 4.0
        
        if question_embedding != [0.1] * 3072 and chunk.embedding:
            sim = _cosine_similarity(question_embedding, chunk.embedding)
            score += sim * 10.0

        if score > 0:
            scored.append((score, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = [chunk for score, chunk in scored[:top_k]]
    
    if not results:
        results = list(chunks_subset[:top_k])
    return results


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
    Endpoint principal del chat de la Profe Joy IA.
    Body JSON: { "question": "...", "history": [...] }
    """
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'error': 'JSON inválido'}, status=400)

    question = (body.get('question') or '').strip()
    history  = body.get('history', [])

    if not question:
        return JsonResponse({'error': 'Pregunta vacía'}, status=400)

    total_chunks = ProfeJoyChunk.objects.count()
    if total_chunks == 0:
        return JsonResponse({
            'answer': '📚 Aún no hay apuntes cargados en mi biblioteca. ¡Solicitá al administrador que suba los resúmenes!',
            'sources': [],
            'chunks_used': 0,
        })

    try:
        client_type, client = _get_api_client()

        try:
            q_embedding = _embed_query(client_type, client, question)
        except Exception as embed_exc:
            logger.warning(f"Embedding error: {embed_exc}. Usando fallback...")
            client_type = 'mock'
            client = None
            q_embedding = [0.1] * 3072

        relevant = _find_relevant_chunks(q_embedding, question)

        context = _build_context(relevant)
        system  = PROMPT_PROFE_JOY.format(contexto=context, pregunta=question)

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
                logger.error(f"Error en API Gemini: {gemini_exc}")
                client_type = 'mock'

        if client_type == 'mock' or answer is None:
            import re
            clean_q = re.sub(r'[¿?¡!,.]', '', question.lower().strip())
            
            # GREETINGS
            if any(greet in clean_q for greet in ('hola', 'holis', 'buen dia', 'buenos dias', 'buenas tardes', 'buenas noches')):
                answer = "¡Holis, corazón! Qué lindo saludarte. ¿Cómo andás? Contame qué materia estás estudiando hoy (Anatomía, Histología, Embrio, Biología...) y le metemos juntos. ¡Estoy acá eh! 😘"
            elif any(q in clean_q for q in ('como estas', 'como andas', 'todo bien', 'que tal', 'cómo estás')):
                answer = "¡Hola, doc! Yo estoy de diez, re contenta de darte una mano con el estudio. ¿Cómo venís llevando la cursada? ¡Vamos que vas a ser un doc increíble! 💪✨"
            elif any(q in clean_q for q in ('quien sos', 'quién sos', 'quien eres', 'tu nombre', 'como te llamas')):
                answer = "¡Holis! Soy la Profe Joy IA, tu tutora médica para sacarte todas las dudas de Histología, Anatomía, Embriología y Biología Celular. ¡Allright! 😉"
            elif 'estudio histologia' in clean_q or 'estudiar histologia' in clean_q:
                answer = """¡Holis, doc! Para estudiar **Histología** en la UNLP con éxito, te recomiendo seguir este orden Didáctico:

1. **Comprensión Tejido por Tejido:** Primero dominá los 4 tejidos básicos (Epitelial, Conectivo, Muscular y Nervioso).
2. **Microscopio Virtual ALUMED:** No te quedes solo con el libro. Entrá a nuestra sección de **Microscopio Virtual** para reconocer preparados reales (H&E, PAS) igual que en los parciales de cátedra.
3. **Organología (Sistemas):** Relacioná la estructura de la pared (túnicas) con la función del órgano (ej. Aparato Digestivo, Renal, Respiratorio).

💡 *Tip cazabobos:* En los exámenes orales siempre te preguntan la tinción y la ultraestructura celular. ¡Cualquier duda de algún preparado decime y lo repasamos! 🔬✨"""
            elif 'locomotor' in clean_q or 'aparato locomotor' in clean_q:
                answer = """¡Holis, mi amor! El **Aparato Locomotor** se estudia integrando tres pilares:

- **Osteología:** Huesos, accidentes óseos, inserciones musculares principales.
- **Artrología:** Clasificación de articulaciones (Diartrosis, Anfiartrosis, Sinartrosis), medios de unión y superficies articulares.
- **Miología:** Músculos, inervación e irrigación del compartimento.

🦴 *Recomendación ALUMED:* Usá nuestro **Atlas 3D** en el dashboard para rotar la columna y los miembros. ¡Verlo en 3D te ahorra el doble de tiempo de memorización! 💪"""
            else:
                # Academic synthesis response
                academic_chunks = [c for c in relevant if c.subject != 'Cartelera']
                target_chunks = academic_chunks if academic_chunks else relevant
                
                parts = ["¡Holis, doc! Mirá lo que preparé de los apuntes oficiales de nuestra biblioteca para vos:\n"]
                for chunk in target_chunks[:2]:
                    subj = f" ({chunk.subject})" if chunk.subject else ""
                    parts.append(f"📖 **{chunk.title}{subj}**\n{chunk.content[:450]}...\n")
                
                parts.append("💡 *Tip de Profe Joy:* Relacioná siempre la estructura con la función para romperla en los parciales. ¿Querés que profundicemos en algún punto específico, corazón? ¡Metele que vas súper bien! 💪✨")
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
