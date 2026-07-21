import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumed.settings')
django.setup()

from core.models import DigitalBook

files_data = [
    {"name": "Cuestiones Biología Anual", "id": "1TVrQrlQCN4Ib4hrAstiyXoh9iLi9WyaE", "subject": "bio"},
    {"name": "Cuestiones Histo 1º Cuatrimestre", "id": "1eDdOIM3QMK2G-Zdza0BvyvR5z_CKayD2", "subject": "histo"},
    {"name": "Fecundación - Resumen Objetivo", "id": "1YWuHz7TMQGE4GzqAQ9IAwPyzjTGSjXMb", "subject": "embrio"},
    {"name": "Finales Todos Biología", "id": "1Lgtp9cnklNlRTUyDpsGaKLtbXocMsROj", "subject": "bio"},
    {"name": "Heck HyE Final", "id": "1BnoCoWS7sDtZ5XZ7RvgAH4rOy3ODqCXI", "subject": "histo"},
    {"name": "Histo 30 Parciales Sin Repetir", "id": "1QHRMuCd4QqdrkADyg8l094ssqpT7H8UK", "subject": "histo"},
    {"name": "Histo Todos", "id": "1pVD47zUAz9MVF4F_4HBvXld0QQD02meG", "subject": "histo"},
    {"name": "Parciales Reales Histo y Embrio 2025 Bloque II", "id": "1SAADz2PWCPR3MhisfMGyJ7kqKYuxwIjP", "subject": "histo"},
    {"name": "Preguntas de Pruebas Biología", "id": "1k8IWbE5cQSZ6ExuUR2i8nwD3tZCOahly", "subject": "bio"},
    {"name": "Simulacro HyE Parcial 1", "id": "1vtBx5PyL6XECB8xV1w4QIB_VvD4foFxE", "subject": "histo"},
    {"name": "Unión Anatomía Cátedra C", "id": "1hwg5les6t4cxso_eulX4bcf3gKwn2WBT", "subject": "anato"},
]

for f in files_data:
    pdf_url = f"https://drive.google.com/file/d/{f['id']}/view?usp=sharing"
    obj, created = DigitalBook.objects.get_or_create(
        pdf_url=pdf_url,
        defaults={
            'title': f['name'],
            'description': f"Simulacro oficial de ALUMED para {f['subject'].capitalize()}.",
            'subject': f['subject'],
            'category': 'Simulacros y Exámenes',
            'year': '1º Año',
            'platform': 'Google Drive',
            'status': 'confirmado',
            'tags': 'simulacro, examen, oficial'
        }
    )
    if created:
        print(f"Created: {f['name']}")
    else:
        print(f"Already exists: {f['name']}")

print("DONE!")
