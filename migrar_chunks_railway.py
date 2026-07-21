"""Migra os chunks da Profe Joy do SQLite local para o PostgreSQL do Railway.

Uso seguro:
    set RAILWAY_DATABASE_URL=postgresql://...
    python migrar_chunks_railway.py                 # apenas mostra o plano
    python migrar_chunks_railway.py --apply          # adiciona os chunks
    python migrar_chunks_railway.py --apply --replace # substitui os chunks remotos
"""
import argparse
import json
import os

from dotenv import load_dotenv


def get_local_chunks():
    """Lê o SQLite mesmo quando DATABASE_URL estiver definido no ambiente."""
    os.environ["DJANGO_SETTINGS_MODULE"] = "alumed.settings"
    load_dotenv()
    os.environ.pop("DATABASE_URL", None)

    import django

    django.setup()
    from accounts.models import ProfeJoyChunk

    return [
        {
            "title": chunk.title or "",
            "content": chunk.content or "",
            "subject": chunk.subject or "",
            "source_type": chunk.source_type or "",
            "source_url": chunk.source_url or "",
            "chunk_index": chunk.chunk_index or 0,
            "year": chunk.year or "",
            "embedding": chunk.embedding or [],
        }
        for chunk in ProfeJoyChunk.objects.all()
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="confirma a escrita no Railway")
    parser.add_argument(
        "--replace",
        action="store_true",
        help="remove os chunks remotos antes de inserir; requer --apply",
    )
    args = parser.parse_args()

    if args.replace and not args.apply:
        parser.error("--replace requer --apply")

    chunks = get_local_chunks()
    print(f"[LOCAL] {len(chunks)} chunks encontrados no SQLite.")

    if not args.apply:
        print("[SIMULACAO] Nenhum dado remoto foi alterado. Use --apply para executar.")
        return

    railway_url = os.environ.get("RAILWAY_DATABASE_URL")
    if not railway_url:
        parser.error("Defina RAILWAY_DATABASE_URL antes de usar --apply.")

    import psycopg2

    with psycopg2.connect(railway_url) as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM accounts_profejoychunk")
        remote_count = cur.fetchone()[0]
        print(f"[RAILWAY] {remote_count} chunks existentes.")

        if args.replace:
            cur.execute("DELETE FROM accounts_profejoychunk")
            print("[RAILWAY] Chunks existentes removidos dentro da transacao.")

        for index, chunk in enumerate(chunks, 1):
            cur.execute(
                """
                INSERT INTO accounts_profejoychunk
                    (title, content, subject, source_type, source_url,
                     chunk_index, year, embedding, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """,
                (
                    chunk["title"], chunk["content"], chunk["subject"],
                    chunk["source_type"], chunk["source_url"],
                    chunk["chunk_index"], chunk["year"],
                    json.dumps(chunk["embedding"]),
                ),
            )
            if index % 10 == 0 or index == len(chunks):
                print(f"  [{index}/{len(chunks)}] preparado")

    print(f"[OK] {len(chunks)} chunks enviados ao Railway.")


if __name__ == "__main__":
    main()
