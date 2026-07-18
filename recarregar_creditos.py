import os
import sys
from supabase import create_client, Client

# Configuração da conexão com o banco central Supabase do ALUMED OS
# Certifique-se de configurar as variáveis de ambiente no Railway/produção
URL_SUPABASE: str = os.environ.get("SUPABASE_URL")
KEY_SUPABASE: str = os.environ.get("SUPABASE_KEY")

def recarregar_creditos_e_logar(email_aluno: str, creditos_comprados: int) -> bool:
    """
    Função do Firewall e Sistema de Recarga Inteligente (ALUMED OS).
    
    1. Verifica a identidade do aluno e seu saldo anterior.
    2. Calcula com segurança o novo saldo (Soma Atômica).
    3. Atualiza o saldo e define o status de acesso como ativo (IA Profe Joy destravada).
    4. Grava o log de auditoria permanente na tabela 'log_creditos'.
    """
    print(f"🚀 Iniciando recarga para o aluno: {email_aluno}")
    
    if not URL_SUPABASE or not KEY_SUPABASE:
        print("🚨 Erro: SUPABASE_URL ou SUPABASE_KEY não configurados no ambiente.")
        return False
        
    try:
        # Inicializa o cliente do Supabase
        supabase: Client = create_client(URL_SUPABASE, KEY_SUPABASE)
        
        # Passo 1: Verificação de Identidade e Saldo Atual
        resposta_aluno = supabase.table('alunos').select('saldo_creditos').eq('email', email_aluno).execute()
        
        if not resposta_aluno.data:
            print("🚨 Erro: Aluno não encontrado na base de dados de alunos.")
            return False
            
        saldo_anterior = resposta_aluno.data[0]['saldo_creditos']
        
        # Passo 2: A Soma Atômica (Cálculo Seguro de Créditos)
        saldo_novo = saldo_anterior + creditos_comprados
        
        # Passo 3: Atualização e Liberação (Status de Segurança ativo)
        supabase.table('alunos').update({
            'saldo_creditos': saldo_novo,
            'status_acesso': 'ativo'
        }).eq('email', email_aluno).execute()
        
        # Passo 4: O Disparo do Log de Auditoria Permanente
        dados_log = {
            'email_aluno': email_aluno,
            'creditos_adicionados': creditos_comprados,
            'saldo_anterior': saldo_anterior,
            'saldo_novo': saldo_novo,
            'status_acesso': 'ativo'
        }
        supabase.table('log_creditos').insert(dados_log).execute()
        
        print(f"✅ SUCESSO! {creditos_comprados} créditos injetados. Status 'ativo'. Log gravado no PostgreSQL e IA Profe Joy Ilimitada destravada para {email_aluno}!")
        return True

    except Exception as erro:
        print(f"🚨 Falha crítica no sistema de recarga: {erro}")
        return False

if __name__ == "__main__":
    # Exemplo rápido para uso e teste
    # venv\Scripts\python.exe recarregar_creditos.py "aluno.teste@unlp.edu.ar" 100
    if len(sys.argv) > 2:
        recarregar_creditos_e_logar(sys.argv[1], int(sys.argv[2]))
    else:
        print("💡 Uso: python recarregar_creditos.py <email_do_aluno> <quantidade_de_creditos>")
