# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from core.grilla_cleaner import limpiar_grilla_estudiantes
import json

class Command(BaseCommand):
    help = 'Limpia grillas de notas desordenadas con ruido de OCR/PDF para ALUMED / Conecta FCM.'

    def add_arguments(self, parser):
        parser.add_argument('--archivo', type=str, help='Ruta al archivo TXT con el texto de la grilla.')

    def handle(self, *args, **options):
        archivo = options.get('archivo')
        if archivo:
            with open(archivo, 'r', encoding='utf-8', errors='ignore') as f:
                texto = f.read()
        else:
            self.stdout.write(self.style.NOTICE("Procesando muestra de grilla de prueba..."))
            texto = """
            anatomia 8  1061194 47312118 Ferreyra  aprobado
            anatomia 8  1119069 FK884282 GAR  Promocion
            anatomia 8  1109166 Bc417823 Iquinas Parra  Promocion
            anatomia 8  1098577 48303248 Lapitzondo Algañaras  aprobado
            anatomia 8  969759 95682565 Larrauri Acuña  aprobado
            anatomia 8  1117460 96282519 LIBERATO DE SOUZA  Promocion
            anatomia 8  1071063 GK570118 MESSIAS DE SOUZA FONS  Promocion
            anatomia 8  1088710 225928469 Mael Neves Cardim  aprobado
            anatomia 8  1100953 48430299 Nahon  Promocion
            anatomia 8 1027608 46829842 Navarro  aprobado
            0 larouca  Promocion
            868044 ojeda, martina  aprobado
            864347  Promocion
            888532 alves de andrade  Promocion
            938321 santos casteda, maria  aprobado
            837162 ayala,valentina  aprobado
            0 aguirre, rosa  Promocion
            0 hernandez, lautaro  Promocion
            0 kuster, liandra  Promocion
            0 fernandez pastore, noren  aprobado
            """

        registros = limpiar_grilla_estudiantes(texto)
        self.stdout.write(self.style.SUCCESS(f"[SUCCESS] Se limpiaron {len(registros)} registros con exito!"))
        for r in registros[:5]:
            self.stdout.write(f" -> {r['Legajo']} | {r['DNI']} | {r['Apellido_Nombre']} | {r['Estado']}")
