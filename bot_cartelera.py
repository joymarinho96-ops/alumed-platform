import os
import sys
from bs4 import BeautifulSoup
import requests
from supabase import create_client, Client

# Configura encoding do console
sys.stdout.reconfigure(encoding='utf-8')

# ⚙️ Conexão com o Supabase (ALUMED OS)
URL_SUPABASE: str = os.environ.get("SUPABASE_URL")
KEY_SUPABASE: str = os.environ.get("SUPABASE_KEY")
TOKEN_TELEGRAM: str = os.environ.get("TELEGRAM_BOT_TOKEN")

def enviar_notificacao_telegram(chat_id: str, mensagem: str):
    """Envia uma mensagem via bot de Telegram para o estudante."""
    if not TOKEN_TELEGRAM:
        print("⚠️ TELEGRAM_BOT_TOKEN não configurado. Ignorando disparo.")
        return
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": mensagem,
        "parse_mode": "HTML"
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code == 200:
            print(f"   📬 Mensagem enviada para o chat_id: {chat_id}")
        else:
            print(f"   ⚠️ Falha ao disparar telegram ({r.status_code}): {r.text}")
    except Exception as e:
        print(f"   🚨 Erro no disparo Telegram: {e}")

def verificar_e_disparar_cartelera():
    print("🚀 [CONECTA RADAR] Iniciando varredura ativa da Cartelera...")
    
    if not URL_SUPABASE or not KEY_SUPABASE:
        print("🚨 Erro: SUPABASE_URL ou SUPABASE_KEY não configurados no ambiente.")
        return

    # Inicializa o cliente do Supabase
    supabase: Client = create_client(URL_SUPABASE, KEY_SUPABASE)

    # 1. Leitura Pública (Web Scraping de Nível 3 da Cartelera)
    url_cartelera = "https://www.med.unlp.edu.ar/index.php/cartelera" # Exemplo de URL oficial da Cátedra
    print(f"🔗 Acessando Cartelera: {url_cartelera}")
    
    try:
        res = requests.get(url_cartelera, timeout=15)
        if res.status_code != 200:
            print(f"❌ Não foi possível ler a Cartelera (Status: {res.status_code})")
            return
            
        soup = BeautifulSoup(res.content, 'html.parser')
        
        # Encontra as caixas verdes com a classe card-outline-success (conforme arquitetura Conecta)
        avisos_encontrados = soup.find_all(class_='card-outline-success')
        print(f"🔍 Encontrados {len(avisos_encontrados)} avisos na Cartelera.")
        
        for aviso in avisos_encontrados:
            # Extrai os dados limpos (data, título, subtítulo e setor)
            # Adapte as seleções conforme a estrutura HTML exata se necessário
            titulo_elemento = aviso.find(class_='card-title') or aviso.find('h4') or aviso.find('h5')
            titulo_texto = titulo_elemento.get_text().strip() if titulo_elemento else None
            
            corpo_elemento = aviso.find(class_='card-text') or aviso.find('p')
            corpo_texto = corpo_elemento.get_text().strip() if corpo_elemento else ""
            
            if not titulo_texto:
                continue
                
            print(f"📌 Processando aviso: '{titulo_texto[:50]}...'")
            
            # 2. Conexão com Banco (Evita duplicações consultando cartelera_avisos)
            busca = supabase.table('cartelera_avisos').select('id').eq('titulo', titulo_texto).execute()
            
            if busca.data:
                print("   ℹ️ Aviso já enviado anteriormente. Ignorando.")
                continue
                
            print("   🚨 Novo aviso detectado! Registrando no Supabase...")
            
            # 3. Grava o aviso na tabela de memória do Supabase
            supabase.table('cartelera_avisos').insert({
                'titulo': titulo_texto,
                'conteudo': corpo_texto
            }).execute()
            
            # 4. Mapeia o público alvo segmentado por ano
            # Determina o ano associado à notícia com base em palavras-chave no texto
            ano_alvo = "1er Año"
            if "2do" in titulo_texto.lower() or "2°" in titulo_texto.lower():
                ano_alvo = "2do Año"
            elif "3er" in titulo_texto.lower() or "3°" in titulo_texto.lower():
                ano_alvo = "3er Año"
            elif "4to" in titulo_texto.lower() or "4°" in titulo_texto.lower():
                ano_alvo = "4to Año"
            elif "5to" in titulo_texto.lower() or "5°" in titulo_texto.lower():
                ano_alvo = "5to Año"
                
            print(f"   🎯 Segmentando alunos do público-alvo: {ano_alvo}")
            
            # 5. Puxa os alunos segmentados do Supabase
            resposta_alunos = supabase.table('alunos').select('telegram_id').eq('ano_estudo', ano_alvo).execute()
            
            if not resposta_alunos.data:
                print(f"   ℹ️ Nenhum aluno com a tag {ano_alvo} para disparar.")
                continue
                
            # Dispara as mensagens via Telegram
            mensagem_disparo = f"📢 <b>Novo Aviso da Cartelera - {ano_alvo}</b>\n\n<b>{titulo_texto}</b>\n\n{corpo_texto}"
            
            for aluno in resposta_alunos.data:
                telegram_id = aluno.get('telegram_id')
                if telegram_id:
                    enviar_notificacao_telegram(telegram_id, mensagem_disparo)

    except Exception as e:
        print(f"🚨 Erro no fluxo do bot_cartelera: {e}")

if __name__ == "__main__":
    verificar_e_disparar_cartelera()
