-- ============================================================
-- INFRAESTRUTURA VETORIAL - ALUMED OS / PROFE JOY IA
-- Execute este arquivo no SQL Editor do Supabase
-- ============================================================

-- 1. Ativar extensão pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Criar tabela de documentos vetorizados
CREATE TABLE IF NOT EXISTS documentos_vector (
    id          UUID    DEFAULT gen_random_uuid() PRIMARY KEY,
    titulo      TEXT    NOT NULL,
    url_origem  TEXT    NOT NULL,
    materia     TEXT    NOT NULL DEFAULT 'General',
    conteudo_chunk TEXT NOT NULL,
    embedding   vector(1536),
    created_at  TIMESTAMPTZ DEFAULT timezone('utc', now()) NOT NULL
);

-- 3. Índice HNSW para busca por cosseno (ultra-rápido em escala)
CREATE INDEX IF NOT EXISTS documentos_vector_embedding_idx
ON documentos_vector
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 4. Índice para filtrar por matéria (acelera queries da Profe Joy)
CREATE INDEX IF NOT EXISTS documentos_vector_materia_idx
ON documentos_vector (materia);

-- ============================================================
-- FUNÇÃO RPC: match_documentos
-- Usada pelo Django para busca semântica (RAG)
-- Exemplo de chamada:
--   supabase.rpc('match_documentos', {
--       'query_embedding': [...],
--       'match_threshold': 0.75,
--       'match_count': 5,
--       'filtro_materia': 'Histología'
--   }).execute()
-- ============================================================
CREATE OR REPLACE FUNCTION match_documentos(
    query_embedding  vector(1536),
    match_threshold  FLOAT     DEFAULT 0.70,
    match_count      INT       DEFAULT 5,
    filtro_materia   TEXT      DEFAULT NULL
)
RETURNS TABLE (
    id              UUID,
    titulo          TEXT,
    url_origem      TEXT,
    materia         TEXT,
    conteudo_chunk  TEXT,
    similarity      FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        dv.id,
        dv.titulo,
        dv.url_origem,
        dv.materia,
        dv.conteudo_chunk,
        1 - (dv.embedding <=> query_embedding) AS similarity
    FROM documentos_vector dv
    WHERE
        -- Filtro opcional por matéria
        (filtro_materia IS NULL OR dv.materia = filtro_materia)
        -- Só retorna resultados acima do threshold de similaridade
        AND 1 - (dv.embedding <=> query_embedding) >= match_threshold
    ORDER BY dv.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- ============================================================
-- SEGURANÇA (Row Level Security)
-- Permite leitura pública (alunos consultam via Django)
-- Escrita apenas com service_role key (scripts de ingestão)
-- ============================================================
ALTER TABLE documentos_vector ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Leitura publica de documentos"
ON documentos_vector FOR SELECT
USING (true);

-- Escrita apenas via service_role (sem policy = bloqueado para anon)
-- Use SUPABASE_SERVICE_KEY nos scripts de ingestão.
