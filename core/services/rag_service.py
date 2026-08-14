"""
core/services/rag_service.py
-----------------------------
Serviço RAG (Retrieval-Augmented Generation) para a Profe Joy IA.
Realiza busca por similaridade vetorial no Supabase via RPC 'match_documentos'
e constrói os prompts enriquecidos com trechos acadêmicos dos livros e resumos.
"""

import logging
import os
from openai import OpenAI
from supabase import create_client

logger = logging.getLogger(__name__)

# Configurações do ambiente Supabase & OpenAI
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")


def get_supabase_client():
    """Retorna instância do cliente Supabase."""
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            return create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception as e:
            logger.warning(f"Erro ao inicializar Supabase client: {e}")
    return None


def get_openai_client():
    """Retorna instância do cliente OpenAI."""
    if OPENAI_API_KEY:
        try:
            return OpenAI(api_key=OPENAI_API_KEY)
        except Exception as e:
            logger.warning(f"Erro ao inicializar OpenAI client: {e}")
    return None


def buscar_contexto_academico(pergunta_estudante: str, materia: str = "Todos", top_k: int = 3, threshold: float = 0.25) -> list[dict]:
    """
    Vetoriza a pergunta do aluno usando text-embedding-3-small e executa
    a busca semântica na função RPC 'match_documentos' do Supabase.
    """
    supabase = get_supabase_client()
    openai_client = get_openai_client()

    if not supabase or not openai_client:
        logger.warning("Supabase ou OpenAI client não configurados para RAG.")
        return []

    try:
        # 1. Gerar o embedding de 1536 dimensões da pergunta do aluno
        response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=pergunta_estudante[:9000]
        )
        query_vector = response.data[0].embedding

        # 2. Chamar a função RPC 'match_documentos' no Supabase pgvector
        response_db = supabase.rpc(
            "match_documentos",
            {
                "query_embedding": query_vector,
                "match_threshold": threshold,
                "match_count": top_k,
                "filter_materia": materia
            }
        ).execute()

        return response_db.data or []

    except Exception as e:
        logger.error(f"Erro na busca vetorial RAG no Supabase: {e}")
        return []


def montar_prompt_profe_joy(pergunta_estudante: str, materia: str = "Todos"):
    """
    Busca o contexto relevante e monta o prompt da Profe Joy com referências às fontes.
    """
    chunks_relevantes = buscar_contexto_academico(pergunta_estudante, materia=materia)

    contexto_livros = ""
    links_para_mostrar = []

    for i, doc in enumerate(chunks_relevantes, 1):
        titulo = doc.get("titulo", "Fonte Acadêmica")
        url = doc.get("url_origem", "")
        conteudo = doc.get("conteudo_chunk", "")
        sim = doc.get("similarity", 0)

        contexto_livros += f"\n--- Fonte {i}: {titulo} (Similaridade: {sim:.0%}) ---\n{conteudo}\n"
        if url and (titulo, url) not in links_para_mostrar:
            links_para_mostrar.append((titulo, url))

    if not contexto_livros:
        contexto_livros = "Nenhum fragmento de livro exatamente igual encontrado no banco. Use seu conhecimento geral de Medicina com a Didática Profe Joy."

    system_instruction = (
        "Eres la Profe Joy IA, tutora inteligente de medicina integrada en ESTATUTO / ALUMED OS. "
        "Usa los fragmentos de libros oficiales para responder al alumno de forma pedagógica, empática y precisa.\n"
        f"CONTEXTO ACADÉMICO OFICIAL:\n{contexto_livros}"
    )

    return system_instruction, links_para_mostrar
