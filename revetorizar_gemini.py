"""
Re-vectorizador Gemini -- ALUMED OS
Usa REST API Gemini v1 com modelo gemini-embedding-001 (dim=3072).
"""
import os
import sys
import time
import requests
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alumed.settings")
from dotenv import load_dotenv
load_dotenv()
django.setup()

from accounts.models import ProfeJoyChunk

GEMINI_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if not GEMINI_KEY:
    print("[ERRO] GEMINI_API_KEY nao encontrada no .env!")
    sys.exit(1)

EMBED_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-embedding-001:embedContent"

def gerar_vetor(texto: str) -> list:
    """Gera embedding via Gemini gemini-embedding-001 (dim=3072)."""
    payload = {
        "model": "models/gemini-embedding-001",
        "content": {"parts": [{"text": texto[:9000]}]},
        "taskType": "RETRIEVAL_DOCUMENT"
    }
    resp = requests.post(EMBED_URL, json=payload, params={"key": GEMINI_KEY}, timeout=30)
    resp.raise_for_status()
    return resp.json()["embedding"]["values"]

def main():
    todos = ProfeJoyChunk.objects.all()
    total = todos.count()
    sem_embed = ProfeJoyChunk.objects.filter(embedding=[]).count()

    print(f"[DB] Total: {total} chunks | Sem embedding: {sem_embed}")
    print("-" * 55)

    if total == 0:
        print("[OK] Sem chunks na DB. Nada a fazer.")
        return

    ok = 0
    erros = 0

    for i, chunk in enumerate(todos, 1):
        if chunk.embedding:  # ja tem vetor, pula
            print(f"[{i}/{total}] OK (ja vetorizado): {(chunk.title or '')[:45]}")
            ok += 1
            continue

        titulo_curto = (chunk.title or "?")[:50]
        print(f"[{i}/{total}] Vetorizando: {titulo_curto}...", end=" ", flush=True)

        try:
            texto = chunk.content or chunk.title or ""
            vetor = gerar_vetor(texto)
            chunk.embedding = vetor
            chunk.save(update_fields=["embedding"])
            ok += 1
            print("OK")
        except Exception as e:
            erros += 1
            print(f"ERRO: {e}")

    print("-" * 55)
    print(f"[FIM] {ok} processados, {erros} erros.")
    com_embed = ProfeJoyChunk.objects.exclude(embedding=[]).count()
    print(f"[DB] {com_embed}/{total} chunks com embedding agora.")

if __name__ == "__main__":
    main()



