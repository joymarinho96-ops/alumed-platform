import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumed.settings')
django.setup()

from courses.models import SimulacroQuestion

questions = [
    {
        "subject": "Anatomía",
        "question_text": "¿Cuál de los siguientes pares craneales emerge de la cara posterior del tronco encefálico (mesencéfalo)?",
        "option_a": "Nervio Oculomotor (III)",
        "option_b": "Nervio Troclear (IV)",
        "option_c": "Nervio Trigémino (V)",
        "option_d": "Nervio Abducens (VI)",
        "correct_option": "B",
        "explanation": "El nervio troclear o patético (IV par craneal) es el único que emerge de la cara posterior del tronco encefálico."
    },
    {
        "subject": "Anatomía",
        "question_text": "En relación a la irrigación del corazón, la arteria descendente anterior es rama terminal de:",
        "option_a": "Arteria Coronaria Derecha",
        "option_b": "Arteria Circunfleja",
        "option_c": "Arteria Coronaria Izquierda",
        "option_d": "Seno Coronario",
        "correct_option": "C",
        "explanation": "La arteria coronaria izquierda se bifurca rápidamente en descendente anterior (interventricular anterior) y circunfleja."
    },
    {
        "subject": "Anatomía",
        "question_text": "¿Qué estructura atraviesa el hiato aórtico del diafragma junto con la arteria aorta?",
        "option_a": "Nervio vago derecho",
        "option_b": "Vena cava inferior",
        "option_c": "Conducto torácico",
        "option_d": "Esófago",
        "correct_option": "C",
        "explanation": "Por el hiato aórtico del diafragma pasan la aorta descendente y el conducto torácico (y a veces la vena ácigos)."
    },
    {
        "subject": "Anatomía",
        "question_text": "El ligamento cruzado anterior de la rodilla se inserta distalmente en:",
        "option_a": "Área intercondílea anterior de la tibia",
        "option_b": "Cóndilo medial del fémur",
        "option_c": "Cabeza del peroné",
        "option_d": "Tuberosidad de la tibia",
        "correct_option": "A",
        "explanation": "El LCA se inserta distalmente en el área intercondílea anterior de la tibia."
    },
    {
        "subject": "Anatomía",
        "question_text": "El lóbulo de la ínsula se encuentra en la profundidad de la cisura de:",
        "option_a": "Rolando (Central)",
        "option_b": "Silvio (Lateral)",
        "option_c": "Calcarina",
        "option_d": "Parieto-occipital",
        "correct_option": "B",
        "explanation": "El lóbulo de la ínsula está oculto en el fondo del surco lateral o cisura de Silvio."
    }
]

for q in questions:
    SimulacroQuestion.objects.get_or_create(
        subject=q['subject'],
        question_text=q['question_text'],
        defaults={
            'option_a': q['option_a'],
            'option_b': q['option_b'],
            'option_c': q['option_c'],
            'option_d': q['option_d'],
            'correct_option': q['correct_option'],
            'explanation': q['explanation']
        }
    )

print(f"Added {len(questions)} 'Choice' questions for Anatomia.")
