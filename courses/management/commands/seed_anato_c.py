from django.core.management.base import BaseCommand
from courses.models import Course, Module, Lesson, SimulacroQuestion

class Command(BaseCommand):
    help = 'Sembra contenido completo y banco de preguntas de examen para Anatomía Cátedra C (FCM-UNLP).'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("[ROBOT] Iniciando robot extractor para Anatomia Catedra C..."))

        # 1. Obter ou criar o curso de Anatomia Cátedra C (ID 5)
        course, created = Course.objects.get_or_create(
            id=5,
            defaults={
                'title': 'ANATOMÍA CÁTEDRA C - FCM UNLP',
                'description': 'Curso completo de Anatomía Cátedra C (FCM UNLP). Contenido teórico, imágenes señaladas, guía de trabajos prácticos y simulacros de parcial.',
                'price': 15000.00,
                'duration_days': 365
            }
        )
        if not created:
            course.title = 'ANATOMÍA CÁTEDRA C - FCM UNLP'
            course.save()

        self.stdout.write(self.style.SUCCESS(f"Curso de Anatomía Cátedra C pronto: [{course.id}] {course.title}"))

        # 2. Criar Módulos temáticos de Anatomia Cat C
        modulos_data = [
            ("Módulo 1: Locomotor (Osteología, Artrología y Miología)", 1, [
                ("1.1 Huesos del Miembro Superior e Inferior", "video", "https://youtube.com/embed/example1", 1),
                ("1.2 Articulaciones Clave de Parcial (Cátedra C)", "video", "https://youtube.com/embed/example2", 2),
                ("1.3 Plexo Braquial y Plexo Lumboacro", "html", "", 3),
            ]),
            ("Módulo 2: Esplacnología (Tórax, Abdomen y Pelvis)", 2, [
                ("2.1 Corazón, Grandes Vasos y Mediastino", "video", "https://youtube.com/embed/example3", 1),
                ("2.2 Aparato Digestivo y Vías Biliares", "html", "", 2),
                ("2.3 Sistema Urogenital y Retroperitoneo", "video", "https://youtube.com/embed/example4", 3),
            ]),
            ("Módulo 3: Neuroanatomía Central y Periférica", 3, [
                ("3.1 Configuración Externa e Interna del Encéfalo", "video", "https://youtube.com/embed/example5", 1),
                ("3.2 Pares Craneales y Vías de Conducción", "html", "", 2),
                ("3.3 Vía Piramidal y Sistema Ventricular", "simulacro", "", 3),
            ]),
            ("Módulo 4: Trampas de Examen y Simulacros de Parcial", 4, [
                ("4.1 Guía de Preguntas Tomadas en Parciales Cátedra C", "simulacro", "", 1),
                ("4.2 Integración Topográfica y Cortes Transversales", "html", "", 2),
            ]),
        ]

        for mod_title, mod_order, lessons in modulos_data:
            module, _ = Module.objects.get_or_create(
                course=course,
                title=mod_title,
                defaults={'order': mod_order}
            )
            for les_title, les_type, video_url, les_order in lessons:
                Lesson.objects.get_or_create(
                    module=module,
                    title=les_title,
                    defaults={
                        'lesson_type': les_type,
                        'video_url': video_url,
                        'order': les_order
                    }
                )

        self.stdout.write(self.style.SUCCESS("Módulos e aulas de Anatomía Cátedra C semeados com sucesso!"))

        # 3. Banco de Preguntas Cátedra C FCM-UNLP
        preguntas_c = [
            {
                "subject": "Anatomía",
                "question_text": "¿Qué nervio atraviesa el canal torsión del húmero junto a la arteria braquial profunda?",
                "option_a": "Nervio mediano",
                "option_b": "Nervio radial",
                "option_c": "Nervio cubital",
                "option_d": "Nervio axilar",
                "correct_option": "B",
                "explanation": "El nervio radial transcurre por el canal de torsión (surco del nervio radial) del húmero acompañado por la arteria braquial profunda."
            },
            {
                "subject": "Anatomía",
                "question_text": "¿Cuál es el contenido del triángulo femoral (de Scarpa) de medial a lateral?",
                "option_a": "Nervio, Arteria, Vena, Linfáticos",
                "option_b": "Vena, Arteria, Nervio",
                "option_c": "Linfáticos (VAN-L de med a lat: Vena, Arteria, Nervio)",
                "option_d": "Arteria, Vena, Nervio",
                "correct_option": "C",
                "explanation": "De medial a lateral en el triángulo femoral se disponen: Ganglio de Cloquet/Linfáticos, Vena femoral, Arteria femoral y Nervio femoral (V-A-N)."
            },
            {
                "subject": "Anatomía",
                "question_text": "¿Qué músculo forma el límite medial del triángulo del codo?",
                "option_a": "Músculo pronador redondo",
                "option_b": "Músculo braquiorradial",
                "option_c": "Músculo bíceps braquial",
                "option_d": "Músculo braquial anterior",
                "correct_option": "A",
                "explanation": "El límite medial de la fosa del codo es el músculo pronador redondo (pronator teres) y el límite lateral es el braquiorradial."
            },
            {
                "subject": "Anatomía",
                "question_text": "¿En qué meato nasal desemboca el conducto nasolagrimal?",
                "option_a": "Meato superior",
                "option_b": "Meato medio",
                "option_c": "Meato inferior",
                "option_d": "Receso esfenoetmoidal",
                "correct_option": "C",
                "explanation": "El conducto nasolagrimal drena lágrimas directamente en el meato nasal inferior."
            },
            {
                "subject": "Anatomía",
                "question_text": "¿Qué arteria da origen a la arteria interventricular anterior (descendente anterior)?",
                "option_a": "Arteria coronaria derecha",
                "option_b": "Arteria coronaria izquierda",
                "option_c": "Arteria circunfleja",
                "option_d": "Arteria marginal derecha",
                "correct_option": "B",
                "explanation": "La arteria coronaria izquierda se divide en la rama interventricular anterior y la rama circunfleja."
            },
            {
                "subject": "Anatomía",
                "question_text": "¿A qué nivel vertebral finaliza la médula espinal en el adulto?",
                "option_a": "T12 - L1",
                "option_b": "L1 - L2",
                "option_c": "L4 - L5",
                "option_d": "S1 - S2",
                "correct_option": "B",
                "explanation": "En el adulto, el cono medular de la médula espinal finaliza a nivel del disco intervertebral L1-L2."
            },
            {
                "subject": "Anatomía",
                "question_text": "¿Qué estructura atraviesa el foramen ciático mayor por encima del músculo piriforme?",
                "option_a": "Nervio ciático",
                "option_b": "Arteria y nervio glúteo superior",
                "option_c": "Arteria y nervio glúteo inferior",
                "option_d": "Nervio pudendo",
                "correct_option": "B",
                "explanation": "Por el espacio suprapiriforme del foramen ciático mayor emergen la arteria, vena y nervio glúteos superiores."
            },
            {
                "subject": "Anatomía",
                "question_text": "¿Cuál es la arteria principal que irriga el área de Broca (área motora del lenguaje)?",
                "option_a": "Arteria cerebral anterior",
                "option_b": "Arteria cerebral media",
                "option_c": "Arteria cerebral posterior",
                "option_d": "Arteria basilar",
                "correct_option": "B",
                "explanation": "La arteria cerebral media irriga la cara dorsolateral del hemisferio cerebral, incluyendo el área de Broca en el giro frontal inferior."
            },
            {
                "subject": "Anatomía",
                "question_text": "¿Qué par craneal inerva motoramente al músculo oblicuo superior del ojo?",
                "option_a": "III par (Oculomotor)",
                "option_b": "IV par (Troclear / Patético)",
                "option_c": "VI par (Abducens)",
                "option_d": "V1 par (Oftálmico)",
                "correct_option": "B",
                "explanation": "Mnemotecnia clásica: SO4 (Superior Oblique - Troclear IV), LR6 (Lateral Rectus - Abducens VI), el resto por el III."
            },
            {
                "subject": "Anatomía",
                "question_text": "¿Dónde desemboca la vena zígos principal?",
                "option_a": "Vena cava inferior",
                "option_b": "Vena cava superior",
                "option_c": "Vena braquiocefálica izquierda",
                "option_d": "Aurícula derecha",
                "correct_option": "B",
                "explanation": "El arco de la vena zígos pasa por encima del pedículo pulmonar derecho y desemboca en la cara posterior de la vena cava superior."
            }
        ]

        creadas = 0
        for p in preguntas_c:
            _, created = SimulacroQuestion.objects.get_or_create(
                question_text=p["question_text"],
                defaults=p
            )
            if created:
                creadas += 1

        self.stdout.write(self.style.SUCCESS("[SUCCESS] EXTRACCION COMPLETA: Nuevas preguntas agregadas al Banco de Anatomia Catedra C!"))
