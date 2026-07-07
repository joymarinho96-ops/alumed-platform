import os.path
import base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings

# Escopos necessários para enviar e-mail
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

class GmailApiEmailBackend(BaseEmailBackend):
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently)
        self.service = None

    def open(self):
        """
        Cria a conexão com a API do Gmail.
        """
        if self.service:
            return True

        creds = None
        token_path = os.path.join(settings.BASE_DIR, 'token.json')
        creds_path = os.path.join(settings.BASE_DIR, 'credentials.json')

        # O arquivo token.json armazena os tokens de acesso e atualização do usuário.
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)

        # Se não houver credenciais (válidas) disponíveis, deixe o usuário fazer login.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Erro ao atualizar token: {e}")
                    # Se falhar a atualização, força novo login
                    creds = None
            
            if not creds:
                if not os.path.exists(creds_path):
                    print("Arquivo 'credentials.json' não encontrado. Por favor, baixe-o do Google Cloud Console.")
                    return False
                
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                # Força o uso da porta 8080 para corresponder ao cadastro no Google Cloud
                creds = flow.run_local_server(port=8080)
            
            # Salva as credenciais para a próxima execução
            with open(token_path, 'w') as token:
                token.write(creds.to_json())

        try:
            self.service = build('gmail', 'v1', credentials=creds)
            return True
        except HttpError as error:
            print(f'Ocorreu um erro ao conectar com a API do Gmail: {error}')
            if not self.fail_silently:
                raise error
            return False

    def close(self):
        """
        Fecha a conexão.
        """
        self.service = None

    def send_messages(self, email_messages):
        """
        Envia uma ou mais mensagens de e-mail.
        """
        if not email_messages:
            return 0

        if not self.open():
            return 0

        num_sent = 0
        for message in email_messages:
            if self._send(message):
                num_sent += 1
        
        return num_sent

    def _send(self, email_message):
        """
        Envia uma única mensagem usando a API do Gmail.
        """
        try:
            message = MIMEText(email_message.body)
            message['to'] = ', '.join(email_message.to)
            message['from'] = email_message.from_email
            message['subject'] = email_message.subject

            # Codifica a mensagem para base64url
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            body = {'raw': raw_message}

            self.service.users().messages().send(userId='me', body=body).execute()
            return True
        except HttpError as error:
            print(f'Ocorreu um erro ao enviar e-mail: {error}')
            if not self.fail_silently:
                raise error
            return False
        except Exception as e:
            print(f'Erro inesperado ao enviar e-mail: {e}')
            if not self.fail_silently:
                raise e
            return False
