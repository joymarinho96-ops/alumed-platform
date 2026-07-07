import json
import hmac
import hashlib
import logging
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from courses.services import EnrollmentService

logger = logging.getLogger(__name__)

def verify_wix_signature(body_bytes, signature_header):
    """
    Verifica que la firma provista coincida con el hash HMAC-SHA256
    del cuerpo de la solicitud utilizando el secreto compartido.
    """
    secret = getattr(settings, 'ALUMED_WEBHOOK_SECRET', None)
    if not secret:
        # En desarrollo local, si no hay secreto configurado, se permite pasar la firma.
        # En producción DEBE estar configurado.
        logger.warning("ALUMED_WEBHOOK_SECRET no está configurado. Saltándose la validación de firma.")
        return True

    if not signature_header:
        return False

    computed_signature = hmac.new(
        secret.encode('utf-8'),
        body_bytes,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(computed_signature, signature_header)


@csrf_exempt
@require_POST
def wix_webhook_view(request):
    # 1. Validar la firma HMAC para verificar el origen y la integridad de la petición
    signature = request.headers.get('X-Wix-Signature')
    if not verify_wix_signature(request.body, signature):
        logger.warning(f"Intento de Webhook con firma inválida o ausente. Cabecera recibida: {signature}")
        return HttpResponseForbidden("Firma del webhook inválida.")

    # 2. Parsear el cuerpo JSON
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Cuerpo del request no es un JSON válido.")

    # Extraer campos principales
    event = payload.get('event')
    data = payload.get('data', {})

    if not event or not data:
        return HttpResponseBadRequest("Faltan parámetros 'event' o 'data' en el payload.")

    # Extraer campos de datos
    wix_member_id = data.get('wix_member_id')
    email = data.get('email')
    first_name = data.get('first_name', '')
    last_name = data.get('last_name', '')
    product_or_plan_id = data.get('product_or_plan_id')
    amount_paid_val = data.get('amount_paid', 0.00)
    
    # Manejar montos
    try:
        amount_paid = float(amount_paid_val)
    except (ValueError, TypeError):
        amount_paid = 0.00

    # Validar campos mandatorios
    if not email or not product_or_plan_id:
        return HttpResponseBadRequest("Faltan campos obligatorios 'email' o 'product_or_plan_id'.")

    # 3. Validar mapeo de planes/cursos
    plan_mapping = getattr(settings, 'WIX_PLAN_COURSE_MAPPING', {})
    course_ids = plan_mapping.get(product_or_plan_id)

    if not course_ids:
        logger.info(f"Evento ignorado: El plan/producto '{product_or_plan_id}' no está mapeado a ningún curso de Django.")
        return JsonResponse({
            'status': 'ignored',
            'message': f"El identificador '{product_or_plan_id}' no está mapeado en el servidor."
        }, status=200)

    # 4. Determinar tipo de evento (Alta/Acceso vs Baja/Revocación)
    is_revocation_event = any(word in event.lower() for word in ['left', 'cancel', 'removed'])

    if is_revocation_event:
        try:
            from django.contrib.auth.models import User
            from courses.models import Enrollment
            
            # Buscar el usuario local por email
            user = User.objects.filter(email=email.lower().strip()).first()
            if not user:
                logger.info(f"Intento de revocación para {email} ignorado: el usuario no existe en Django.")
                return JsonResponse({
                    'status': 'ignored',
                    'message': f"El usuario {email} no existe localmente."
                }, status=200)
                
            revoked_count = 0
            for course_id in course_ids:
                enrollment = Enrollment.objects.filter(user=user, course_id=course_id, is_active=True).first()
                if enrollment:
                    EnrollmentService.revoke_access(
                        enrollment_id=enrollment.id,
                        revoked_by=None,
                        notes=f"Revocado vía Webhook de Wix. Evento: {event}."
                    )
                    revoked_count += 1
            
            logger.info(f"Revocación exitosa vía Webhook de Wix para {email} en {revoked_count} cursos.")
            return JsonResponse({
                'status': 'success',
                'message': 'Acceso revocado correctamente.',
                'user': user.username,
                'revoked_count': revoked_count
            }, status=200)
            
        except Exception as e:
            logger.error(f"Error procesando la revocación vía Webhook de Wix: {str(e)}", exc_info=True)
            return JsonResponse({
                'status': 'error',
                'message': f"Error interno al procesar revocación: {str(e)}"
            }, status=500)

    # Flujo de Alta / Extensión de Acceso
    # 4. Parsear fechas
    start_date_str = data.get('start_date')
    expiration_date_str = data.get('expiration_date')

    start_date = None
    if start_date_str:
        start_date = parse_datetime(start_date_str)
    if not start_date:
        start_date = timezone.now()

    if not expiration_date_str:
        return HttpResponseBadRequest("Falta el campo obligatorio 'expiration_date'.")

    expiration_date = parse_datetime(expiration_date_str)
    if not expiration_date:
        return HttpResponseBadRequest("El campo 'expiration_date' no tiene un formato de fecha ISO válido.")

    # 5. Ejecutar la sincronización mediante el servicio centralizado
    try:
        user, enrollments = EnrollmentService.grant_access(
            email=email,
            first_name=first_name,
            last_name=last_name,
            course_ids=course_ids,
            access_source='wix',
            start_date=start_date,
            expiration_date=expiration_date,
            amount_paid=amount_paid,
            internal_notes=f"Sincronizado vía Webhook de Wix. Evento: {event}.",
            wix_member_id=wix_member_id
        )
        
        logger.info(f"Sincronización exitosa vía Webhook de Wix para {email} en cursos: {course_ids}")
        return JsonResponse({
            'status': 'success',
            'message': 'Acceso sincronizado correctamente.',
            'user': user.username,
            'enrollments_count': len(enrollments)
        }, status=200)

    except Exception as e:
        logger.error(f"Error procesando el Webhook de Wix: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': f"Error interno del servidor al procesar accesos: {str(e)}"
        }, status=500)
