"""
vectorizer.py
-------------
Lê o arquivo links_biblioteca.json (gerado pelo extrair_biblioteca.py),
baixa cada PDF, extrai o texto, divide em chunks e gera embeddings
via OpenAI para armazenar no Supabase (pgvector).

Uso:
    python scripts/vectorizer.py
    python scripts/vectorizer.py --materia Histología   # filtra por matéria
    python scripts/vectorizer.py --max 10               # limita a 10 recursos

Variáveis de ambiente necessárias:
    SUPABASE_URL
    SUPABASE_SERVICE_KEY  (service_role, não anon key!)
    OPENAI_API_KEY

Requisitos extras:
    pip install pypdf2 supabase openai requests
"""

import argparse
import io
import json
import os
import sys
import time

import requests

try:
    from openai import OpenAI
except ImportError:
    print("❌ openai não instalado. Rode: pip install openai")
    sys.exit(1)

try:
    import pypdf
except ImportError:
    print("❌ pypdf não instalado. Rode: pip install pypdf")
    sys.exit(1)

try:
    from supabase import create_client
except ImportError:
    print("❌ supabase não instalado. Rode: pip install supabase")
    sys.exit(1)

# ─────────────────────────────────────────────
# Configuração
# ─────────────────────────────────────────────
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

LINKS_FILE = os.path.join(os.path.dirname(__file__), "links_biblioteca.json")
MODELO_EMBEDDING = "text-embedding-3-small"
DIMENSOES = 1536
CHUNK_MAX_CHARS = 900          # ~200 tokens — seguro para o modelo
TABELA = "documentos_vector"
SLEEP_ENTRE_PDFS = 1.5        # segundos (evita rate-limit)


def verificar_config():
    erros = []
    if not SUPABASE_URL:
        erros.append("SUPABASE_URL não definida")
    if not SUPABASE_KEY:
        erros.append("SUPABASE_SERVICE_KEY não definida")
    if not OPENAI_API_KEY:
        erros.append("OPENAI_API_KEY não definida")
    if not os.path.exists(LINKS_FILE):
        erros.append(f"Arquivo não encontrado: {LINKS_FILE}. Rode primeiro: python scripts/extrair_biblioteca.py")
    if erros:
        for e in erros:
            print(f"❌ {e}")
        sys.exit(1)


def extrair_texto_pdf(url: str) -> list[tuple[int, str]]:
    """Baixa o PDF em memória e retorna lista de (numero_pagina, texto)."""
    try:
        resp = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code != 200:
            print(f"  ⚠️  HTTP {resp.status_code} para {url[:60]}")
            return []
        reader = pypdf.PdfReader(io.BytesIO(resp.content))
        paginas = []
        for i, pagina in enumerate(reader.pages):
            texto = pagina.extract_text() or ""
            texto = texto.strip()
            if texto:
                paginas.append((i + 1, texto))
        return paginas
    except Exception as e:
        print(f"  ⚠️  Erro ao baixar PDF: {e}")
        return []


def chunk_texto(texto: str, max_chars: int = CHUNK_MAX_CHARS) -> list[str]:
    """Divide o texto em pedaços de no máximo max_chars caracteres."""
    palavras = texto.split()
    chunks, atual, tamanho = [], [], 0
    for palavra in palavras:
        atual.append(palavra)
        tamanho += len(palavra) + 1
        if tamanho >= max_chars:
            chunks.append(" ".join(atual))
            atual, tamanho = [], 0
    if atual:
        chunks.append(" ".join(atual))
    return chunks


def gerar_embedding(client: OpenAI, texto: str) -> list[float]:
    """Gera embedding via OpenAI text-embedding-3-small."""
    resp = client.embeddings.create(model=MODELO_EMBEDDING, input=texto)
    return resp.data[0].embedding


def ja_vetorizado(supabase_client, url: str) -> bool:
    """Verifica se a URL já foi inserida na tabela (evita duplicatas)."""
    res = (
        supabase_client.table(TABELA)
        .select("id")
        .eq("url_origem", url)
        .limit(1)
        .execute()
    )
    return len(res.data) > 0


def processar_biblioteca(filtro_materia: str = None, max_recursos: int = None):
    verificar_config()

    supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    openai_client = OpenAI(api_key=OPENAI_API_KEY)

    with open(LINKS_FILE, "r", encoding="utf-8") as f:
        recursos = json.load(f)

    if filtro_materia:
        recursos = [r for r in recursos if r.get("materia") == filtro_materia]
        print(f"🔍 Filtrando por matéria: {filtro_materia} ({len(recursos)} recursos)")

    if max_recursos:
        recursos = recursos[:max_recursos]

    print(f"\n📚 Total a processar: {len(recursos)} recursos")
    total_chunks = 0

    for idx, recurso in enumerate(recursos, 1):
        titulo = recurso.get("titulo", "Sem título")
        url = recurso.get("url", "")
        materia = recurso.get("materia", "General")

        print(f"\n[{idx}/{len(recursos)}] {titulo[:55]}...")
        print(f"  📎 {url[:70]}")

        if ja_vetorizado(supabase_client, url):
            print("  ✅ Já vetorizado. Pulando.")
            continue

        paginas = extrair_texto_pdf(url)
        if not paginas:
            print("  ⚠️  Nenhum texto extraído. Pulando.")
            continue

        print(f"  📄 {len(paginas)} página(s) extraída(s)")

        for num_pag, texto_pag in paginas:
            chunks = chunk_texto(texto_pag)
            for i, chunk in enumerate(chunks):
                try:
                    embedding = gerar_embedding(openai_client, chunk)
                    supabase_client.table(TABELA).insert({
                        "titulo": f"{titulo} — Pág.{num_pag} pt.{i+1}",
                        "url_origem": url,
                        "materia": materia,
                        "conteudo_chunk": chunk,
                        "embedding": embedding,
                    }).execute()
                    total_chunks += 1
                    print(f"  🧠 Chunk {i+1}/pág.{num_pag} inserido.", end="\r")
                except Exception as e:
                    print(f"\n  ❌ Erro ao inserir chunk: {e}")

        print(f"\n  ✅ {titulo[:40]} — concluído.")
        time.sleep(SLEEP_ENTRE_PDFS)

    print(f"\n🎉 Vetorização concluída! Total de chunks inseridos: {total_chunks}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vetoriza a Biblioteca Conecta FCM no Supabase")
    parser.add_argument("--materia", help="Filtrar por matéria (ex: Histología, Anatomía)")
    parser.add_argument("--max", type=int, help="Número máximo de recursos a processar")
    args = parser.parse_args()

    processar_biblioteca(
        filtro_materia=args.materia,
        max_recursos=args.max
    )
