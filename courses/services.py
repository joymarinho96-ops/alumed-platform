import uuid
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from .models import Course, Enrollment, EnrollmentHistory

class EnrollmentService:

    @staticmethod
    def _get_or_create_user(email, first_name='', last_name='', wix_member_id=None):
        """
        Busca o crea un usuario de Django por su email.
        Asocia el wix_member_id al perfil si se proporciona.
        """
        email = email.lower().strip()
        user = User.objects.filter(email=email).first()
        
        if user:
            # Si el usuario ya existe, nos aseguramos de vincular wix_member_id si no lo tenía
            if wix_member_id:
                profile = user.profile
                if profile.wix_member_id != wix_member_id:
                    profile.wix_member_id = wix_member_id
                    profile.save()
            return user, False

        # Si no existe, generamos un username único
        username_base = email.split('@')[0]
        # Limpieza básica de caracteres especiales
        username_base = ''.join(c for c in username_base if c.isalnum())
        if not username_base:
            username_base = "student"
            
        username = username_base
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{username_base}{counter}"
            counter += 1

        # Crear el usuario
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name or '',
            last_name=last_name or ''
        )
        
        if wix_member_id:
            profile = user.profile
            profile.wix_member_id = wix_member_id
            profile.save()
            
        return user, True

    @classmethod
    @transaction.atomic
    def grant_access(cls, email, first_name, last_name, course_ids, access_source, start_date, expiration_date, amount_paid=0.00, internal_notes='', created_by=None, wix_member_id=None):
        """
        Otorga o extiende el acceso de un estudiante a uno o más cursos.
        Registra la transacción en el historial de auditoría.
        """
        # 1. Obtener o crear el alumno
        user, user_created = cls._get_or_create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            wix_member_id=wix_member_id
        )

        enrollments_processed = []

        # 2. Procesar accesos por cada curso
        for course_id in course_ids:
            try:
                course = Course.objects.get(id=course_id)
            except Course.DoesNotExist:
                # Si el curso no existe localmente, lo saltamos (se registrará en logs si es necesario)
                continue

            # Buscar matrícula existente (activa o inactiva)
            enrollment = Enrollment.objects.filter(user=user, course=course).first()

            if enrollment:
                # Si ya existe la matrícula, decidimos la acción (extensión o reactivación)
                action = 'extend'
                
                # Si estaba desactivada o vencida, es una reactivación
                if not enrollment.is_active or enrollment.expiration_date < timezone.now():
                    action = 'create' # Registramos como nueva creación/reactivación en el historial
                
                # Actualizar los campos
                enrollment.start_date = start_date
                enrollment.expiration_date = expiration_date
                enrollment.access_source = access_source
                enrollment.is_active = True
                
                # Conservar/Concatenar notas internas
                notes_prefix = f"[{timezone.now().strftime('%d/%m/%Y %H:%M')} - {access_source.upper()}] "
                new_notes = notes_prefix + (internal_notes or "Acceso actualizado/extendido.")
                if enrollment.internal_notes:
                    enrollment.internal_notes = f"{enrollment.internal_notes}\n{new_notes}"
                else:
                    enrollment.internal_notes = new_notes
                
                if created_by:
                    enrollment.created_by = created_by
                
                # Limpiar campos de revocación en caso de reactivación
                enrollment.revoked_at = None
                enrollment.revoked_by = None
                
                enrollment.save()
            else:
                # Si no existe, crear una nueva matrícula
                action = 'create'
                notes_prefix = f"[{timezone.now().strftime('%d/%m/%Y %H:%M')} - {access_source.upper()}] "
                formatted_notes = notes_prefix + (internal_notes or "Acceso inicial creado.")
                
                enrollment = Enrollment.objects.create(
                    user=user,
                    course=course,
                    start_date=start_date,
                    expiration_date=expiration_date,
                    access_source=access_source,
                    created_by=created_by,
                    internal_notes=formatted_notes,
                    is_active=True
                )

            # 3. Registrar en el historial de auditoría
            EnrollmentHistory.objects.create(
                enrollment=enrollment,
                user=user,
                course=course,
                action=action,
                access_source=access_source,
                amount_paid=amount_paid,
                performed_by=created_by,
                notes=internal_notes or f"Acceso procesado vía {access_source}."
            )

            enrollments_processed.append(enrollment)

        return user, enrollments_processed

    @classmethod
    @transaction.atomic
    def revoke_access(cls, enrollment_id, revoked_by=None, notes=''):
        """
        Desactiva una matrícula y registra la revocación en el historial.
        """
        enrollment = Enrollment.objects.select_related('user', 'course').get(id=enrollment_id)
        
        if not enrollment.is_active:
            return enrollment # Ya estaba inactiva
            
        enrollment.is_active = False
        enrollment.revoked_at = timezone.now()
        enrollment.revoked_by = revoked_by
        
        revoked_by_username = revoked_by.username if revoked_by else "System/Wix Webhook"
        notes_prefix = f"\n[{timezone.now().strftime('%d/%m/%Y %H:%M')} - REVOCACIÓN] "
        revocation_notes = f"Acceso revocado por {revoked_by_username}. Motivo: {notes or 'No especificado'}."
        enrollment.internal_notes = f"{enrollment.internal_notes}{notes_prefix}{revocation_notes}"
        enrollment.save()

        # Registrar en el historial de auditoría
        EnrollmentHistory.objects.create(
            enrollment=enrollment,
            user=enrollment.user,
            course=enrollment.course,
            action='revoke',
            access_source=enrollment.access_source,
            amount_paid=0.00,
            performed_by=revoked_by,
            notes=notes or "Acceso revocado automáticamente."
        )

        return enrollment
