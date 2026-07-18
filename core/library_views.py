from django.shortcuts import render
from core.models import DigitalBook
from core.library_catalog import build_library_payload

def conecta_biblioteca_view(request):
    """
    Vista de la Biblioteca Inteligente integrada en Conecta FCM.
    Carga los libros desde la base de datos y los expone estructurados al frontend.
    """
    books = DigitalBook.objects.all().order_by('subject', 'title')
    library_payload = build_library_payload(books)
    
    return render(
        request,
        'core/biblioteca.html',
        {
            'library_payload': library_payload,
            'library_summary': library_payload['summary'],
        }
    )

def conecta_biblioteca_lector_view(request, book_id):
    """
    Lector de libros y apuntes digitales.
    Si el libro tiene un PDF local/remoto, lo incrusta.
    Si es un recurso indexado (de la migración), ofrece una sala de estudio guiada interactiva.
    """
    from django.shortcuts import get_object_or_404
    book = get_object_or_404(DigitalBook, id=book_id)
    
    pdf_url = ""
    if book.pdf_file:
        pdf_url = book.pdf_file.url
    elif book.pdf_url and "drive.google.com" not in book.pdf_url:
        pdf_url = book.pdf_url

    is_simulated = not bool(pdf_url)
    
    return render(
        request,
        'core/conecta_biblioteca_lector.html',
        {
            'book': book,
            'pdf_url': pdf_url,
            'is_simulated': is_simulated,
        }
    )
