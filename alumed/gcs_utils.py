from google.cloud import storage
from django.conf import settings
import datetime
import os
import json
from google.oauth2 import service_account

def get_storage_client():
    """
    Retorna um cliente de armazenamento autenticado.
    """
    credentials = None
    
    if hasattr(settings, 'GS_CREDENTIALS_JSON'):
            info = json.loads(settings.GS_CREDENTIALS_JSON)
            credentials = service_account.Credentials.from_service_account_info(info)
    elif hasattr(settings, 'GS_CREDENTIALS_FILE') and settings.GS_CREDENTIALS_FILE:
            credentials = service_account.Credentials.from_service_account_file(settings.GS_CREDENTIALS_FILE)
    
    if credentials:
        return storage.Client(credentials=credentials)
    else:
        return storage.Client()

def generate_signed_url(blob_name, bucket_name=None):
    """
    Gera uma URL assinada para um objeto no Google Cloud Storage.
    """
    try:
        storage_client = get_storage_client()
        
        target_bucket = bucket_name if bucket_name else settings.GS_BUCKET_NAME
        bucket = storage_client.bucket(target_bucket)
        blob = bucket.blob(blob_name)

        url = blob.generate_signed_url(
            version="v4",
            expiration=datetime.timedelta(hours=1),
            method="GET",
        )
        return url
    except Exception as e:
        print(f"Erro ao gerar URL assinada: {e}")
        return None
