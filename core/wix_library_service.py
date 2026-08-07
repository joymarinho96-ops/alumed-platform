import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class WixLibraryService:
    """
    Servicio para consumir la colección de Biblioteca Virtual 
    desde el CMS Headless de Wix (@wix/data).
    """
    def __init__(self):
        self.client_id = getattr(settings, 'WIX_HEADLESS_CLIENT_ID', '')
        self.site_id = getattr(settings, 'WIX_SITE_ID', '')
        self.api_key = getattr(settings, 'WIX_API_KEY', '')
        self.collection_id = getattr(settings, 'WIX_LIBRARY_COLLECTION_ID', 'BibliotecaVirtual')
        
        # URL base teórica para consultar items de una colección en Wix Data REST API
        # Documentación de Wix: https://dev.wix.com/api/rest/wix-data/wix-data/items/query
        self.query_url = "https://www.wixapis.com/wix-data/v2/items/query"
        
        self.headers = {
            'Authorization': self.api_key,
            'wix-site-id': self.site_id, # Algunos endpoints piden el site-id o account-id
            'Content-Type': 'application/json'
        }

    def get_library_items(self, search_query=None, materia_code=None, page=1, limit=12):
        """
        Consulta los registros de la colección filtrando por nombre o materia.
        Si la API de Wix requiere un payload GraphQL o un Query object, lo adaptamos aquí.
        """
        # Estructura del payload según estándar de Wix Data Query
        payload = {
            "dataCollectionId": self.collection_id,
            "query": {
                "filter": {},
                "paging": {
                    "limit": limit,
                    "offset": (page - 1) * limit
                }
            }
        }
        
        # Filtros dinámicos
        if search_query or materia_code:
            payload["query"]["filter"] = {"$and": []}
            
            if search_query:
                payload["query"]["filter"]["$and"].append({
                    "title": {"$contains": search_query}
                })
            if materia_code:
                payload["query"]["filter"]["$and"].append({
                    "materia_code": {"$eq": materia_code}
                })

        try:
            response = requests.post(self.query_url, headers=self.headers, json=payload, timeout=10)
            
            if response.status_code == 401 or response.status_code == 403:
                logger.warning("Wix API no autorizada. Usando Mock Data de Biblioteca.")
                return self._get_mock_items(search_query, materia_code)
                
            response.raise_for_status()
            data = response.json()
            return [self.parse_shared_file_item(item) for item in data.get('items', [])]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Wix Library Items: {e}")
            # Fallback a Mock data en desarrollo si falla la conexión
            return self._get_mock_items(search_query, materia_code)

    def get_item_download_url(self, item_id, user):
        """
        Valida el item y retorna la URL segura del CDN.
        (En producción, aquí podríamos generar un enlace firmado si Wix lo soporta, 
        o simplemente devolver el campo 'fileUrl' del item consultado).
        """
        if not user or not user.is_authenticated:
            raise PermissionError("Debes iniciar sesión para descargar.")
            
        # Hacemos fetch del item específico
        payload = {
            "dataCollectionId": self.collection_id,
            "query": {
                "filter": {"_id": {"$eq": item_id}}
            }
        }
        
        try:
            response = requests.post(self.query_url, headers=self.headers, json=payload, timeout=10)
            if response.status_code == 200:
                items = response.json().get('items', [])
                if items:
                    # Supongamos que el campo del archivo PDF en Wix se llama 'archivoPdf'
                    # o que el item ya trae la URL.
                    parsed = self.parse_shared_file_item(items[0])
                    return parsed['download_url'] or '#'
        except:
            pass
            
        # Si estamos usando mocks o falló
        return f"https://cdn.alumed.com/downloads/mock_{item_id}.pdf"

    def parse_shared_file_item(self, item):
        """
        Normaliza los campos nativos de la colección SharedFiles de Wix.
        """
        data = item.get('data', {})
        
        # Extraer URL del PDF
        file_url = data.get('fileUrl') or data.get('document') or data.get('url', '')
        
        # Si viene con el protocolo de Wix Media (wix:document://), lo convertimos a HTTPS
        if file_url.startswith('wix:document://'):
            # Normalización básica de CDN de Wix si aplica
            doc_id = file_url.split('/')[-1]
            file_url = f"https://docs.wixstatic.com/ugd/{doc_id}"

        return {
            'id': item.get('_id', data.get('_id')),
            'title': data.get('fileName') or data.get('title') or 'Material de Estudio',
            'description': data.get('description', ''),
            'download_url': file_url,
            'thumbnail': data.get('thumbnailUrl') or data.get('image', ''),
            'materia': data.get('category') or data.get('folder', 'General')
        }

    def _get_mock_items(self, search_query=None, materia_code=None):
        """Datos falsos de respaldo en caso de que la API de Wix no esté configurada aún."""
        mocks = [
            {'id': '1', 'title': 'Netter - Atlas de Anatomía', 'materia': 'Anatomía', 'materia_code': 'ANA', 'thumbnail': 'https://m.media-amazon.com/images/I/51wX5s6uHhL.jpg', 'description': 'El mejor atlas.', 'download_url': '#'},
            {'id': '2', 'title': 'Ross - Histología', 'materia': 'Histología', 'materia_code': 'HIS', 'thumbnail': 'https://m.media-amazon.com/images/I/51M3v0v1YKL.jpg', 'description': 'Texto y atlas.', 'download_url': '#'},
            {'id': '3', 'title': 'Guyton - Fisiología Médica', 'materia': 'Fisiología', 'materia_code': 'FIS', 'thumbnail': 'https://m.media-amazon.com/images/I/41Kxk7O5H7L.jpg', 'description': 'Fisiología fundamental.', 'download_url': '#'}
        ]
        
        if search_query:
            mocks = [m for m in mocks if search_query.lower() in m['title'].lower()]
        if materia_code:
            # En el mock pusimos materia_code, pero en el normal es folder/category
            mocks = [m for m in mocks if m.get('materia_code') == materia_code]
            
        return mocks
