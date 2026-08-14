"""
recarregar_creditos.py
----------------------
Script de gestão e sincronização atômica do saldo de créditos de IA para estudantes.
Atualiza o Supabase (tabela estudantes), libera o status_acesso para 'ativo',
salva cache em creditos_ia/config_creditos.json e gera logs em creditos_ia/logs_transacoes/.

Uso:
    python scripts/recarregar_creditos.py --email estudante@gmail.com --creditos 150 --plano "Club ALUMED"

Variáveis de Ambiente:
    SUPABASE_URL
    SUPABASE_SERVICE_KEY
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Diretórios base
BASE_DIR = Path(__file__).resolve().parent.parent
PASTA_CREDITOS = BASE_DIR / "creditos_ia"
PASTA_LOGS = PASTA_CREDITOS / "logs_transacoes"
CONFIG_FILE = PASTA_CREDITOS / "config_creditos.json"

# Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")


def get_supabase_client():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ SUPABASE_URL e SUPABASE_SERVICE_KEY são obrigatórios.")
        return None
    try:
        from supabase import create_client
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except ImportError:
        print("❌ Pacote supabase não instalado. Rode: pip install supabase")
        return None


def enviar_notificacao_whatsapp(telefone: str, nome: str, creditos_adquiridos: int, novo_saldo: int):
    """Envia mensagem de confirmação via WhatsApp se configurado."""
    try:
        # Tenta usar o serviço WhatsApp nativo do projeto
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alumed.settings")
        import django
        django.setup()
        from core.whatsapp_service import WhatsAppService

        wa = WhatsAppService()
        msg = (
            f"¡Hola {nome}! 🎉\n\n"
            f"⚡ *¡Recarga Confirmada en ESTATUTO / ALUMED OS!*\n"
            f"• Créditos sumados: *+{creditos_adquiridos}*\n"
            f"• Tu saldo actual: *{novo_saldo} créditos*\n"
            f"• Estado de tu cuenta: *ACTIVA*\n\n"
            f"¡Ya podés seguir consultando a la Profe Joy IA sin límites! 🟣"
        )
        wa.send_text_message(telefone, msg)
        print(f"📱 Notificação enviada para o WhatsApp: {telefone}")
    except Exception as e:
        print(f"⚠️  Notificação WhatsApp ignorada ({e}). A recarga foi concluída com sucesso.")


def recarregar_creditos_aluno(email_estudante: str, creditos_adquiridos: int, plano: str = "Club ALUMED") -> int:
    """
    Atualiza o saldo do aluno no Supabase, libera o status de acesso
    e registra arquivos de log e cache local.
    """
    print(f"[*] Sincronizando recarga de {creditos_adquiridos} créditos para: {email_estudante}")

    # 1. Garantir que as pastas de segurança existam
    PASTA_LOGS.mkdir(parents=True, exist_ok=True)

    supabase = get_supabase_client()
    if not supabase:
        return None

    try:
        # 2. Buscar o registro do aluno usando o e-mail cadastrado
        aluno_query = (
            supabase.table("estudantes")
            .select("*")
            .eq("email", email_estudante)
            .execute()
        )

        if not aluno_query.data:
            raise ValueError(f"Estudante {email_estudante} não encontrado na base de dados.")

        aluno = aluno_query.data[0]
        id_aluno = aluno.get("id")
        nome_aluno = aluno.get("nombre") or aluno.get("username") or email_estudante
        telefone_aluno = aluno.get("telefono") or aluno.get("whatsapp")
        creditos_anteriores = aluno.get("creditos_ia", 0) or 0
        novo_saldo = creditos_anteriores + creditos_adquiridos

        # 3. Atualizar Supabase: injeta saldo, muda plano e força 'status_acesso' para 'ativo'
        supabase.table("estudantes").update({
            "creditos_ia": novo_saldo,
            "status_acesso": "ativo",
            "plano_estudo": plano,
        }).eq("id", id_aluno).execute()

        # 4. Gravar cache local (config_creditos.json)
        config_data = {
            "ultimo_update": datetime.utcnow().isoformat(),
            "aluno_id": id_aluno,
            "email": email_estudante,
            "saldo_creditos": novo_saldo,
            "status": "ativo",
            "plano": plano,
        }

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)

        # 5. Gerar arquivo de Log Físico
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = PASTA_LOGS / f"recarga_{id_aluno}_{timestamp_str}.log"
        with open(log_filename, "w", encoding="utf-8") as log_f:
            log_f.write("--- LOG DE TRANSAÇÃO ALUMED OS ---\n")
            log_f.write(f"Data: {datetime.now().isoformat()}\n")
            log_f.write(f"Aluno ID: {id_aluno}\n")
            log_f.write(f"Email: {email_estudante}\n")
            log_f.write(f"Créditos Anteriores: {creditos_anteriores}\n")
            log_f.write(f"Créditos Adicionados: {creditos_adquiridos}\n")
            log_f.write(f"Novo Saldo de IA: {novo_saldo}\n")
            log_f.write("Status de Acesso: ATIVO\n")
            log_f.write(f"Plano Sincronizado: {plano}\n")
            log_f.write("Sincronização de Servidor: SUCESSO\n")
            log_f.write("----------------------------------\n")

        print(f"[+] Sucesso! {creditos_adquiridos} créditos liberados e conta destravada para {email_estudante}.")

        # 6. Notificar no WhatsApp se houver telefone cadastrado
        if telefone_aluno:
            enviar_notificacao_whatsapp(telefone_aluno, nome_aluno, creditos_adquiridos, novo_saldo)

        return novo_saldo

    except Exception as e:
        print(f"[-] Falha na engrenagem de créditos: {e}")
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recarrega créditos de IA para um estudante no Supabase")
    parser.add_argument("--email", required=True, help="E-mail do estudante")
    parser.add_argument("--creditos", type=int, default=150, help="Quantidade de créditos a adicionar")
    parser.add_argument("--plano", default="Club ALUMED", help="Nome do plano")
    args = parser.parse_args()

    recarregar_creditos_aluno(args.email, args.creditos, args.plano)
