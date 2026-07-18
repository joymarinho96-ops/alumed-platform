import os
import json
import requests
from pypdf import PdfReader  # Versão recomendada e moderna de PyPDF2 usada no ALUMED OS
from supabase import create_client, Client
from openai import OpenAI

# ⚙️ 1. Configurações do Cérebro Central (Supabase e Embeddings)
url_supabase: str = os.environ.get("SUPABASE_URL")
key_supabase: str = os.environ.get("SUPABASE_KEY")
openai_key: str = os.environ.get("OPENAI_API_KEY")

# Inicializa conexões se as chaves estiverem presentes
supabase: Client = None
if url_supabase and key_supabase:
    supabase = create_client(url_supabase, key_supabase)

client_ai = None
if openai_key:
    client_ai = OpenAI(api_key=openai_key)

def baixar_e_extrair_texto(url_pdf):
    """Baixa o PDF do Wix/Drive temporariamente e extrai todo o texto com pypdf."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    }
    resposta = requests.get(url_pdf, headers=headers, timeout=30)
    resposta.raise_for_status()
    
    caminho_temp = "temp_alumed.pdf"
    with open(caminho_temp, 'wb') as f:
        f.write(resposta.content)
        
    texto_extraido = ""
    try:
        leitor = PdfReader(caminho_temp)
        # Extrai o texto página por página
        for pagina in leitor.pages:
            texto_pagina = pagina.extract_text()
            if texto_pagina:
                texto_extraido += texto_pagina + "\n"
    finally:
        if os.path.exists(caminho_temp):
            os.remove(caminho_temp) # Limpa o rastro físico
            
    return texto_extraido

def gerar_vetor(texto):
    """Converte o texto médico em coordenadas matemáticas (Embedding) usando OpenAI."""
    if not client_ai:
        raise ValueError("OPENAI_API_KEY não configurada no ambiente.")
    resposta = client_ai.embeddings.create(
        input=texto[:8000],  # Limita tamanho para evitar estouro de tokens em chamadas simples
        model="text-embedding-3-small"
    )
    return list(resposta.data.embedding)

def injeção_de_conhecimento(caminho_json):
    print("🚀 [ALUMED OS] Iniciando a Vetorização RAG da Biblioteca...")
    
    if not supabase or not client_ai:
        print("🚨 Erro: SUPABASE_URL, SUPABASE_KEY ou OPENAI_API_KEY não configurados no ambiente.")
        return
        
    if not os.path.exists(caminho_json):
        print(f"🛑 Arquivo de links '{caminho_json}' não encontrado.")
        return
        
    # Lê a lista de livros extraída pelo seu robô Playwright
    with open(caminho_json, 'r', encoding='utf-8') as arquivo:
        livros = json.load(arquivo)
        
    print(f"📚 Encontrados {len(livros)} livros para processar.")
    
    for livro in livros:
        titulo = livro.get('titulo') or livro.get('title')
        link = livro.get('link') or livro.get('url_pdf') or livro.get('pdf_url')
        materia = livro.get('materia') or livro.get('subject') or 'Medicina Geral'
        
        if not titulo or not link:
            continue
            
        print(f"📥 Processando e vetorizando: '{titulo}'...")
        
        try:
            # 1. Download e Leitura
            conteudo_completo = baixar_e_extrair_texto(link)
            
            # Se o PDF for de imagem escaneada e retornar texto vazio,
            # usamos um fallback de metadados para que ele ainda seja indexável e recomendável
            if not conteudo_completo.strip():
                print(f"   ⚠️ [ESCANEADO] PDF de imagem sem texto extraível. Gerando metadados de fallback.")
                conteudo_completo = f"Material de estudio de medicina titulado: {titulo}. Categoría/Materia: {materia}. Disponible para descarga completa en el enlace de la biblioteca."
            
            # 2. Conversão Vetorial
            vetor_matematico = gerar_vetor(conteudo_completo)
            
            # 3. Upload para a tabela biblioteca_documentos no Supabase
            dados_rag = {
                "titulo": titulo,
                "conteudo": conteudo_completo,
                "embedding": vetor_matematico,
                "materia": materia,
                "url_wix": link
            }
            
            # Insere os dados na tabela do Supabase
            supabase.table('biblioteca_documentos').insert(dados_rag).execute()
            print(f"   ✅ SUCESSO! {titulo} armazenado no córtex da IA Profe Joy!")
            
        except Exception as erro:
            print(f"   🚨 Falha ao processar '{titulo}': {erro}")

if __name__ == "__main__":
    # Gatilho de Execução local
    # Executa passando o arquivo JSON de links como argumento
    import sys
    arquivo_links = "links_biblioteca.json"
    if len(sys.argv) > 1:
        arquivo_links = sys.argv[1]
    
    injeção_de_conhecimento(arquivo_links)
