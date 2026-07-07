from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from courses.models import Enrollment
from django.conf import settings

class Command(BaseCommand):
    help = 'Envia correos de recordatorio de renovación para matrículas que vencen pronto (en Español).'

    def handle(self, *args, **options):
        # Define o período para o lembrete (ex: 7 dias antes de expirar)
        reminder_days = 7
        reminder_date = timezone.now().date() + timedelta(days=reminder_days)

        # Encontra matrículas que expiram exatamente na data do lembrete
        expiring_enrollments = Enrollment.objects.filter(expiration_date__date=reminder_date)

        self.stdout.write(self.style.SUCCESS(f'Encontradas {expiring_enrollments.count()} matrículas venciendo en {reminder_days} días.'))

        for enrollment in expiring_enrollments:
            user = enrollment.user
            course = enrollment.course

            subject = f'Recordatorio: ¡Tu curso {course.title} está por vencer!'
            message = (
                f'Hola, {user.username},\n\n'
                f'Tu inscripción en el curso "{course.title}" vencerá en {reminder_days} días, el día {enrollment.expiration_date.strftime("%d/%m/%Y")}.\n\n'
                f'¡No pierdas el acceso al contenido! Accede a nuestro sitio para renovar tu inscripción.\n\n'
                f'Atentamente,\n'
                f'Equipo ALUMED'
            )
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]

            try:
                send_mail(subject, message, from_email, recipient_list)
                self.stdout.write(self.style.SUCCESS(f'Correo enviado a {user.email}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error al enviar correo a {user.email}: {e}'))

        self.stdout.write(self.style.SUCCESS('Proceso de envío de recordatorios finalizado.'))
