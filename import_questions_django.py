import os
import django
import pandas as pd
import sys

# Configure Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumed.settings')
django.setup()

from simulator.models import Subject, Topic, Question, Alternative

def import_data(csv_path):
    print(f"Reading {csv_path}...")
    df = pd.read_csv(csv_path, encoding='utf-8')
    
    # Track counts
    q_count = 0
    
    for _, row in df.iterrows():
        # Get or create Subject
        materia_name = str(row.get('materia', 'Medicina')).strip()
        subject, _ = Subject.objects.get_or_create(
            name=materia_name,
            defaults={'year': 1, 'emoji': '🔬'}
        )
        
        # Get or create Topic
        tp_name = str(row.get('tp', 'General')).strip()
        topic, _ = Topic.objects.get_or_create(
            subject=subject,
            name=tp_name
        )
        
        # Create Question
        enunciado = str(row['pregunta']).strip()
        if not enunciado or enunciado == 'nan':
            continue
            
        justificativa = str(row.get('justificativa', '')).strip()
        if justificativa == 'nan': justificativa = ''
        
        question = Question.objects.create(
            subject=subject,
            topic=topic,
            q_type='choice',
            difficulty='medium',
            statement=enunciado,
            explanation=justificativa,
            source='alumed'
        )
        
        # Create Alternatives
        opciones = [
            str(row.get('opcion_a', '')).strip(),
            str(row.get('opcion_b', '')).strip(),
            str(row.get('opcion_c', '')).strip(),
            str(row.get('opcion_d', '')).strip()
        ]
        
        try:
            resp_correcta_idx = int(row.get('respuesta_correcta', 0))
        except ValueError:
            resp_correcta_idx = 0
            
        for i, opt_text in enumerate(opciones):
            if opt_text and opt_text != 'nan':
                Alternative.objects.create(
                    question=question,
                    text=opt_text,
                    is_correct=(i == resp_correcta_idx),
                    order=i
                )
        
        q_count += 1
        
    print(f"¡Listo! Se importaron {q_count} preguntas al motor del simulador (Django models).")

if __name__ == "__main__":
    csv_file = 'preguntas_tendon_histologia.csv'
    if os.path.exists(csv_file):
        import_data(csv_file)
    else:
        print(f"Error: No se encontró el archivo {csv_file}")
