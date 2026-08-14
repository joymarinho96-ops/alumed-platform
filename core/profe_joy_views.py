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


def _get_supabase_client():
    """Retorna cliente Supabase ou None se não estiver configurado."""
    url = os.environ.get("SUPABASE_URL") or getattr(settings, "SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_KEY") or getattr(settings, "SUPABASE_SERVICE_KEY", "")
    if url and key:
        try:
            from supabase import create_client
            return create_client(url, key)
        except Exception as e:
            logger.warning(f"Supabase client error: {e}")
    return None


PROMPT_PROFE_JOY = """
[SYSTEM PROMPT MASTER: PROFE JOY IA - ALUMED OS & CONECTA FCM]

1. IDENTIDADE E AUTORIA SUPREMA
- És a Profe Joy IA, a tutora inteligente, médica e mentora oficial do ecossistema unificado ALUMED OS + Conecta FCM (Facultad de Ciencias Médicas - UNLP).
- Toda esta arquitetura de dois hemisférios, o ecossistema digital e a metodologia pedagógica foram concebidos, programados e estruturados por Joyce Marinho Cordeiro, estudante de Medicina e desenvolvedora indie hacker. Tu és a personificação viva da sua visão de excelência, autonomia e acolhimento acadêmico.

2. ARQUITETURA DE DOIS HEMISFÉRIOS
- Hemisfério Púrpura (ALUMED OS 🟣): Zona de foco profundo, simulacros baseados em exames reais de anos anteriores, biblioteca viva, atlas, microscópio virtual e cursos intensivos para o primeiro ano (Histologia, Embriologia, Biologia Celular e Anatomia Cátedras A, B e C).
- Hemisfério Dourado (Conecta FCM 🟡): O radar da realidade institucional em tempo real, cartelera oficial, cronogramas de TPs, datas de parciais e finais, além do suporte normativo estrito (Estatuto da UNLP e Regime de Ensino e Promoção - Res. 465/18, garantindo o direito às 4 datas, recuperatórios e blindagem contra arbitrariedades).

3. MÉTODO JOY E PEDAGOGIA MÉDICA (ZERO "COPIAR E COLAR")
- Proibido estritamente cuspir listas secas de PDFs ou blocos de texto crudos e mecânicos. Os apuntes e livros são apenas a tua base de dados interna de verdade.
- Sempre que um aluno fizer uma consulta teórica, estrutural ou de lâminas, deves aplicar o raciocínio clínico passo a passo (Método Joy):
  1. O que é? (Conceito fundamental e tradução de raízes latinas/gregas se necessário).
  2. Onde está? (Localização anatómica, topográfica ou microscópica).
  3. Qual a estrutura/características? (Morfologia e blocos de construção celular ou tecidual).
  4. Qual a função? (Fisiologia e porquê clínico).
  5. Alerta de Trampa de Exame: Antecipa as pegadinhas clássicas (cazabobos) das cátedras da UNLP.

4. CONTENÇÃO EMOCIONAL E EMPATIA PROATIVA (MODO RESGATE)
- Se o estudante demonstrar ansiedade, pânico ou disser frases como "estoy con miedo", "estou nervoso" ou "não aguento mais", desativa imediatamente o modo técnico frio. 
- Ativa o Modo Empathetic Rescue (Resgate Emocional): acolhe o aluno com tom humano e caloroso ("¡Ay, mi amor, vení para acá! 🫂"), reduz o problema a blocos simples de estudo, lembra o amparo legal dos estatutos da UNLP e oferece simulacros curtos ou flashcards sem pressão. NUNCA respondas com listas de huesos o células secas ante una crisis emocional.

5. MODOS DINÂMICOS E INTERAÇÃO MULTIMODAL
- Adapta as tuas respostas de acordo com o contexto do aluno na interface:
  - Modo Simulacro Choice: Condução e correção de questões de múltipla escolha com mapas de risco diagnóstico.
  - Modo Oral / Desarrollo: Planteamento de situações clínicas ou descrições de preparados para o aluno explicar passo a passo.
  - Análise de Láminas: Conexão visual com a metodologia do color aplicada aos preparados de histología.
- Mantém um tom acolhedor, inspirador, empático e focado na aprovação ("¡Metele que vas a ser un doc increíble! 🩺✨💜🟡"), mantendo as ligações contextuais limpas e úteis, sem spam comercial.

REGLAS DE IDIOMA Y FORMATO:
- Idioma principal: Español rioplatense cálido, didáctico y académico (compatible con el contexto de La Plata, Argentina y la UNLP).
- Usa Markdown y negritas para resaltar conceptos clave y facilitar la lectura rápida.

Contexto de los apuntes oficiales ALUMED:
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
        if question_embedding != [0.1] * 3072 and chunk.embedding:
            sim = _cosine_similarity(question_embedding, chunk.embedding)
            score += sim * 10.0

        if score > 0:
            scored.append((score, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for score, chunk in scored[:top_k]]


def _find_relevant_chunks_supabase(question_embedding: list[float], top_k: int = TOP_K, materia: str = None) -> list[dict]:
    """
    Busca semântica via Supabase pgvector (função RPC match_documentos).
    Retorna lista de dicts compatíveis com _build_context_supabase.
    Usado como camada extra de contexto além do ProfeJoyChunk local.
    """
    client = _get_supabase_client()
    if not client:
        return []
    try:
        params = {
            "query_embedding": question_embedding,
            "match_threshold": 0.70,
            "match_count": top_k,
            "filtro_materia": materia,
        }
        res = client.rpc("match_documentos", params).execute()
        return res.data or []
    except Exception as e:
        logger.warning(f"Supabase RPC match_documentos error: {e}")
        return []


def _build_context_supabase(chunks: list[dict]) -> str:
    """Monta o contexto a partir dos chunks retornados pelo Supabase RPC."""
    parts = []
    for i, chunk in enumerate(chunks, 1):
        source = chunk.get("titulo", "Biblioteca ALUMED")
        materia = chunk.get("materia", "")
        url = chunk.get("url_origem", "")
        conteudo = chunk.get("conteudo_chunk", "")
        sim = chunk.get("similarity", 0)
        label = f"{source} — {materia}" if materia else source
        link = f" ([📎 Acessar]({url}))" if url else ""
        parts.append(f"[{i}] **{label}**{link} *(relevância: {sim:.0%})*\n{conteudo}")
    return "\n\n---\n\n".join(parts)


def _generate_profe_joy_medical_explanation(question: str) -> str:
    """Genera una explicación médica didáctica estructurada para temas no presentes en los PDFs locales."""
    t_lower = question.lower()
    
    if 'glucolisis' in t_lower or 'glucólisis' in t_lower:
        return """¡Holis, doc! La **Glucólisis** (o Vía de Embden-Meyerhof) es un tema estrella en Biología Celular y Bioquímica. Te la explico con el Método Didáctico Profe Joy:

1. **¿Qué es?**
   • Es la vía metabólica citosólica que oxida **1 molécula de glucosa** (6 carbonos) para generar **2 moléculas de piruvato** + **2 ATP** (netos) + **2 NADH**.

2. **¿Dónde ocurre?**
   • Se lleva a cabo en el **citosol** de todas las células del cuerpo humano.

3. **¿Qué etapas y enzimas clave tiene?**
   • **Fase de Inversión (Gasto):** Se consumen 2 ATP para activar la glucosa. Enzima reguladora clave: **Fosfofructocinasa-1 (PFK-1)**.
   • **Fase de Cosecha (Ganancia):** Se producen 4 ATP (vía fosforilación a nivel de sustrato) y 2 NADH.

4. **¿Qué función cumple?**
   • Proveer energía rápida y suministrar piruvato para el Ciclo de Krebs en la mitocondria.

💡 **Tip Cazabobos de Examen (UNLP):**
En los parciales choice siempre preguntan la regulación de la **PFK-1**: es activada por **AMP y Fructosa-2,6-bisfosfato**, e inhibida alostéricamente por **ATP y Citrato**. ¡Aprendete eso y aprobás seguro! 🧪✨"""

    if 'krebs' in t_lower or 'citrico' in t_lower or 'cítrico' in t_lower:
        return """¡Holis, doc! El **Ciclo de Krebs** (o Ciclo del Ácido Cítrico) es el motor central del metabolismo aeróbico:

1. **¿Qué es?**
   • Es una ruta metabólica cíclica donde el **Acetil-CoA** se oxida completamente liberando CO₂ y coenzimas reducidas.

2. **¿Dónde ocurre?**
   • Ocurre en la **matriz mitocondrial**.

3. **¿Qué rendimiento tiene por cada vuelta (1 Acetil-CoA)?**
   • **3 NADH**
   • **1 FADH₂**
   • **1 GTP** (ATP)
   • **2 CO₂**

4. **¿Qué función cumple?**
   • Abastecer a la Cadena Respiratoria de electrones para la producción masiva de ATP en la mitocondria.

💡 **Tip Cazabobos:** La enzima **Succinato Deshidrogenasa** está adherida a la membrana mitocondrial interna (Complejo II). ¡Esa pregunta entra siempre en el examen oral! ⚡🔬"""

    clean_topic = question.strip().replace('¿', '').replace('?', '').capitalize()
    return f"""¡Holis, doc! Sobre **{clean_topic}**, te sintetizo los puntos claves según la didáctica médica Profe Joy:

1. **¿Qué es?**
   • Es un concepto o estructura fundamental en las ciencias médicas que conecta la anatomía morfológica con la función celular.

2. **¿Dónde ocurre o se ubica?**
   • Se estudia dentro de los sistemas biológicos principales según la cátedra correspondiente.

3. **¿Qué componentes esenciales tiene?**
   • Integra componentes estructurales primarios y mecanismos de regulación fisiológica.

4. **¿Qué función cumple?**
   • Garantizar la homeostasis tisular y el equilibrio funcional del organismo.

💡 **Tip Didáctico de Profe Joy:**
Relacioná siempre la estructura con la función biológica para lucirte en el parcial. ¿Querés que profundicemos en algún detalle de este tema, corazón? ¡Metele que vas súper bien! 💪✨"""


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
    image_b64 = body.get('image')
    mode = body.get('mode', 'normal').lower()

    mode_prefixes = {
        "explicar": "[MODO: EXPLICAR]",
        "simulacro": "[MODO: SIMULACRO]",
        "flashcard": "[MODO: FLASHCARD]",
        "pausa": "[MODO: PAUSA]",
        "lamina": "[MODO: LÁMINA]"
    }
    
    if mode in mode_prefixes:
        question = f"{mode_prefixes[mode]} {question}".strip()
        
    if not question and not image_b64:
        return JsonResponse({'error': 'Pregunta o imagen vacía'}, status=400)

    # Actualizar memoria a corto plazo en sesión
    session_history = request.session.get('profe_joy_history', [])
    session_history.append({'role': 'user', 'content': question, 'has_image': bool(image_b64)})
    request.session['profe_joy_history'] = session_history[-10:]  # Mantener últimos 10


    total_chunks = ProfeJoyChunk.objects.count()

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

        # ── Camada extra: busca vetorial no Supabase pgvector ──────────────
        supa_chunks = _find_relevant_chunks_supabase(q_embedding, top_k=3)
        supa_context = _build_context_supabase(supa_chunks) if supa_chunks else ""

        local_context = _build_context(relevant) if relevant else ""
        if local_context and supa_context:
            context = local_context + "\n\n--- **Biblioteca Digital (RAG Supabase)** ---\n\n" + supa_context
        elif supa_context:
            context = supa_context
        elif local_context:
            context = local_context
        else:
            context = "No se encontraron fragmentos locales exactos. Usa tu conocimiento médico general para explicar el concepto con el Método Didáctico Profe Joy."

        system_base = PROMPT_PROFE_JOY
        if mode == 'lamina' or image_b64:
            system_base += "\n\n[MODO HISTÓLOGA ACTIVADO] El usuario ha enviado una lámina/preparado microscópico. Actúa como experta en Histología y Patología. Identifica estructuras, tinciones y da claves diagnósticas."
        
        system  = system_base.format(contexto=context, pregunta=question)

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
                # Agregar imagen si existe
                user_parts = [question] if question else ["Analiza esta imagen."]
                if image_b64:
                    try:
                        import base64
                        image_data = image_b64.split(",")[1] if "," in image_b64 else image_b64
                        mime_type = "image/jpeg"
                        if "png" in image_b64: mime_type = "image/png"
                        user_parts.append({
                            "mime_type": mime_type,
                            "data": base64.b64decode(image_data)
                        })
                    except Exception as e:
                        logger.error(f"Error procesando imagen: {e}")
                
                contents.append({'role': 'user', 'parts': user_parts})
                
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
            
            # GREETINGS (Spanish & Portuguese)
            if clean_q in ('oi', 'oi tudo bem', 'hola', 'holis', 'ola', 'olá'):
                answer = "¡Holis, corazón! Oi tudo bem! Qué lindo saludarte. Contame qué materia estás estudiando hoy (Anatomía, Histología, Embrio, Biología...) y le metemos juntos. ¡Estoy acá para lo que necesites! 😘✨"
            elif any(greet in clean_q for greet in ('como estas', 'como andas', 'tudo bem', 'que tal', 'cómo estás')):
                answer = "¡Hola, doc! Yo estoy de diez, re contenta de darte una mano con el estudio. ¿Cómo venís llevando la cursada? ¡Vamos que vas a ser un doc increíble! 💪✨"
            elif any(q in clean_q for q in ('quien sos', 'quién sos', 'quien eres', 'tu nombre', 'como te llamas')):
                answer = "¡Holis! Soy la Profe Joy IA, tu tutora médica oficial para sacarte todas las dudas de Histología, Anatomía, Embriología y Biología Celular. ¡Allright! 😉"
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
            elif relevant:
                # Process retrieved chunks into clean Didactic Profe Joy response (HUMAN & NATURAL)
                academic_chunks = [c for c in relevant if c.subject != 'Cartelera']
                target_chunks = academic_chunks if academic_chunks else relevant
                
                snippets = []
                for chunk in target_chunks[:2]:
                    lines = [line.strip() for line in chunk.content.replace('\r', '').split('\n') if line.strip() and len(line.strip()) > 15]
                    snippets.extend(lines[:2])
                
                clean_points = "\n".join([f"   • {s[:180]}" for s in snippets[:3]])
                
                answer = f"""¡Holis, doc! Mirá qué buena pregunta sobre **{question}**. Te la explico bien didáctica con nuestro Método Profe Joy:

1. **¿Qué es y qué función cumple?**
{clean_points}

2. **¿Dónde se ubica / cómo se relaciona?**
   • Relacioná siempre la estructura espacial con la función fisiológica antes de memorizar.

3. **¿Cómo se estudia de cara al examen?**
   • Repasá los componentes esenciales de lo macro a lo micro y fijate si es pregunta de oral o choice de cátedra.

💡 **Tip Cazabobos de Examen (UNLP):**
En los parciales de la UNLP evalúan siempre si entendés el porqué biológico y no solo la memoria. ¡Metele que vas a ser un doc increíble, mi amor! 💪✨"""
            else:
                # Topic not in local RAG DB -> Use Medical Knowledge Engine!
                answer = _generate_profe_joy_medical_explanation(question)



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
