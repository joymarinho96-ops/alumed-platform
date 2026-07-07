from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from courses.models import Enrollment
from django.conf import settings

class Command(BaseCommand):
    help = 'Envia un mensaje personalizado a todos los alumnos con matrícula activa, incluyendo la fecha de vencimiento.'

    def add_arguments(self, parser):
        parser.add_argument('subject', type=str, help='Asunto del correo')
        parser.add_argument('message_body', type=str, help='Cuerpo del mensaje principal')

    def handle(self, *args, **options):
        subject_input = options['subject']
        message_body_input = options['message_body']
        
        # Pega todas as matrículas ativas (data de expiração maior ou igual a hoje)
        active_enrollments = Enrollment.objects.filter(expiration_date__gte=timezone.now())
        
        # Para evitar enviar duplicado se o aluno tiver 2 cursos, podemos agrupar por usuário ou enviar um por matrícula.
        # Aqui enviaremos um por matrícula para ser específico sobre o vencimento daquele curso.
        
        self.stdout.write(self.style.SUCCESS(f'Iniciando envío para {active_enrollments.count()} matrículas activas...'))

        count_sent = 0
        for enrollment in active_enrollments:
            user = enrollment.user
            course = enrollment.course
            
            # Calcula dias restantes
            days_remaining = (enrollment.expiration_date.date() - timezone.now().date()).days
            
            # Monta a mensagem personalizada
            full_message = (
                f"Hola, {user.username}!\n\n"
                f"{message_body_input}\n\n"
                f"--------------------------------------------------\n"
                f"ESTADO DE TU CUENTA:\n"
                f"Curso: {course.title}\n"
                f"Vencimiento: {enrollment.expiration_date.strftime('%d/%m/%Y')}\n"
                f"Días restantes: {days_remaining} días\n"
                f"--------------------------------------------------\n\n"
                f"Atentamente,\n"
                f"Equipo ALUMED"
            )

            try:
                send_mail(
                    subject=subject_input,
                    message=full_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                count_sent += 1
                self.stdout.write(f'Enviado a: {user.email} ({course.title})')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error enviando a {user.email}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Envío masivo finalizado. Total enviados: {count_sent}'))
