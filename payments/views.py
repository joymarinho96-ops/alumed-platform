from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import mercadopago
from courses.models import Course, Enrollment, PaymentHistory
from django.contrib.auth import get_user_model
import json

# Importações para o QR Code

import qrcode
from io import BytesIO
import base64

User = get_user_model()

def create_club_payment(request, plan_type):
    messages.info(
        request,
        f"El plan Club {plan_type.capitalize()} todavia no esta disponible."
    )
    return redirect('club')


def check_club_payment_status(request, plan_type):
    return JsonResponse({
        'active': False,
        'available': False,
        'plan_type': plan_type,
    })


def create_payment(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        messages.error(request, "El curso seleccionado no fue encontrado.")
        return redirect('home')

    # Verifica se o usuário já está matriculado e se a matrícula é válida
    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(
            user=request.user,
            course=course,
            expiration_date__gt=timezone.now()
        ).first()

        if enrollment:
            # Se já estiver matriculado, redireciona para o dashboard do curso
            return redirect('courses:course_dashboard', course_id=course.id)

    # --- LÓGICA PARA CURSOS GRATUITOS ---
    if course.is_free:
        if not request.user.is_authenticated:
            # Redireciona para login se não estiver logado
            return redirect(f'/accounts/login/?next={request.path}')
        
        # Cria a matrícula diretamente
        Enrollment.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={'expiration_date': timezone.now() + timezone.timedelta(days=course.duration_days)}
        )
        
        # Redireciona para o dashboard do curso
        messages.success(request, f"¡Te has inscrito exitosamente en {course.title}!")
        return redirect('courses:course_dashboard', course_id=course.id)

    # Garante que o preço seja um float válido
    try:
        price = float(course.price)
        if price <= 0:
            return HttpResponse("Erro: O preço do curso deve ser maior que zero.", status=400)
    except (ValueError, TypeError):
        return HttpResponse("Erro: Preço do curso inválido.", status=400)

    # Inicializa o SDK do Mercado Pago
    access_token = getattr(settings, 'MERCADOPAGO_ACCESS_TOKEN', "APP_USR-6070359759810181-012720-586bdd780f3c02a48fb7e88ddb87a97a-417055483")
    
    if not access_token or access_token.startswith("APP_USR-9e"):
        access_token = "APP_USR-6070359759810181-012720-586bdd780f3c02a48fb7e88ddb87a97a-417055483"
        
    sdk = mercadopago.SDK(access_token)

    # Gera as URLs absolutas explicitamente
    success_url = request.build_absolute_uri(reverse('payments:payment_success')) + f"?course_id={course.id}"
    failure_url = request.build_absolute_uri(reverse('payments:payment_failure'))
    pending_url = request.build_absolute_uri(reverse('payments:payment_pending'))

    # Cria a preferência de pagamento
    preference_data = {
        "items": [
            {
                "title": course.title,
                "quantity": 1,
                "unit_price": price,
                "currency_id": "ARS", # Moeda Argentina
            }
        ],
        "back_urls": {
            "success": success_url,
            "failure": failure_url,
            "pending": pending_url,
        },

        "auto_return": "approved",
        "binary_mode": True,
        "external_reference": json.dumps({'course_id': course.id, 'user_id': request.user.id}), # Passa o ID do curso e do usuário como referência externa
        "notification_url": "https://www.alumedestudiantes.com/pagamento/webhook/",
    }

    try:
        preference_response = sdk.preference().create(preference_data)
        
        if preference_response.get("status") == 201:
            preference = preference_response["response"]
            checkout_url = preference["init_point"]

            # --- GERAÇÃO DO QR CODE ---
            # Cria o QR Code apontando para a URL de checkout
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(checkout_url)
            qr.make(fit=True)

            # Cria a imagem na memória
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            
            # Converte para Base64 para exibir no HTML
            qr_image_base64 = base64.b64encode(buffer.getvalue()).decode()

            # Renderiza a página de pagamento com o QR Code e o Link
            context = {
                'course': course,
                'checkout_url': checkout_url,
                'qr_code': qr_image_base64
            }
            return render(request, 'payments/checkout_options.html', context)
        else:
            # Tenta novamente sem auto_return se falhar
            if "auto_return invalid" in str(preference_response):
                 del preference_data["auto_return"]
                 preference_response = sdk.preference().create(preference_data)
                 if preference_response.get("status") == 201:
                    preference = preference_response["response"]
                    checkout_url = preference["init_point"]
                    
                    # --- GERAÇÃO DO QR CODE ---
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(checkout_url)
                    qr.make(fit=True)
                    img = qr.make_image(fill_color="black", back_color="white")
                    buffer = BytesIO()
                    img.save(buffer, format="PNG")
                    qr_image_base64 = base64.b64encode(buffer.getvalue()).decode()

                    context = {
                        'course': course,
                        'checkout_url': checkout_url,
                        'qr_code': qr_image_base64
                    }
                    return render(request, 'payments/checkout_options.html', context)

            error_message = preference_response.get("response", {}).get("message", "Erro desconhecido.")
            error_detail = preference_response.get("response", {}).get("cause", [])
            return HttpResponse(f"Erro ao criar preferência de pagamento: {error_message} - {error_detail}", status=500)

    except Exception as e:
        print("EXCEPTION:", e)
        return HttpResponse(f"Erro inesperado ao se comunicar com o Mercado Pago: {e}", status=500)

def payment_success(request):
    # Tenta pegar o course_id de várias fontes possíveis
    course_id = request.GET.get('course_id')
    
    if not course_id:
        # O Mercado Pago retorna 'external_reference' nos parâmetros da URL de retorno
        external_reference = request.GET.get('external_reference')
        if external_reference:
            try:
                data = json.loads(external_reference)
                course_id = data.get('course_id')
            except json.JSONDecodeError:
                course_id = external_reference # Fallback para caso não seja JSON
        
    # Se ainda não encontrou, tenta pegar do 'collection_id' ou 'preference_id' consultando a API (opcional, mas mais robusto)
    # Por enquanto, vamos confiar que external_reference ou o parâmetro manual funcionem.

    if course_id and request.user.is_authenticated:
        try:
            course = get_object_or_404(Course, id=course_id)

            # Verifica se o usuário já está matriculado
            enrollment = Enrollment.objects.filter(
                user=request.user,
                course=course,
                expiration_date__gt=timezone.now()
            ).first()

            if enrollment:
                 # Se já estiver matriculado, apenas renderiza a página de sucesso sem criar novo histórico
                 return render(request, 'payments/success.html')

            # --- VERIFICAÇÃO DE PAGAMENTO ---
            # Se não estiver matriculado, precisamos verificar se houve um pagamento REAL e RECENTE.
            payment_id = request.GET.get('payment_id') or request.GET.get('collection_id')
            status = request.GET.get('status') or request.GET.get('collection_status')
            
            print(f"DEBUG: Payment Success. ID: {payment_id}, Status: {status}")

            if payment_id and status == 'approved':
                
                # VERIFICAÇÃO DE DUPLICIDADE
                if PaymentHistory.objects.filter(payment_id=str(payment_id)).exists():
                     print(f"DEBUG: Pagamento {payment_id} já existe no histórico.")
                     return HttpResponse("Este pagamento já foi processado anteriormente.", status=400)

                 # Inicializa o SDK do Mercado Pago
                access_token = getattr(settings, 'MERCADOPAGO_ACCESS_TOKEN', "APP_USR-6070359759810181-012720-586bdd780f3c02a48fb7e88ddb87a97a-417055483")
                if not access_token or access_token.startswith("APP_USR-9e"):
                    access_token = "APP_USR-6070359759810181-012720-586bdd780f3c02a48fb7e88ddb87a97a-417055483"
                
                sdk = mercadopago.SDK(access_token)
                print(f"DEBUG: Verificando na API MP...")
                payment_info = sdk.payment().get(payment_id)

                if payment_info["status"] == 200:
                    payment = payment_info["response"]
                    if payment["status"] == "approved":
                        # Verifica data
                        payment_date_created = payment.get("date_created")
                        if payment_date_created:
                            payment_date = parse_datetime(payment_date_created)
                            if timezone.is_naive(payment_date):
                                payment_date = timezone.make_aware(payment_date)
                            
                            print(f"DEBUG: Data do pagamento: {payment_date}")
                            # Se o pagamento for antigo (> 30 minutos), não processa matrícula
                            if payment_date < timezone.now() - timezone.timedelta(minutes=30):
                                print("DEBUG: Pagamento antigo.")
                                return HttpResponse("O link de pagamento expirou ou já foi processado.", status=400)

                        print("DEBUG: Criando histórico e renovando...")
                        # --- REGISTRO NO HISTÓRICO DE PAGAMENTOS ---
                        PaymentHistory.objects.create(
                            user=request.user,
                            course=course,
                            amount_paid=course.price,
                            days_added=course.duration_days,
                            payment_id=str(payment_id)
                        )
                        
                        # Cria a matrícula
                        Enrollment.objects.create(
                            user=request.user,
                            course=course,
                            expiration_date=timezone.now() + timezone.timedelta(days=course.duration_days)
                        )
                            
                        # Renderiza a página de sucesso
                        return render(request, 'payments/success.html')

            # Se chegou aqui, não houve pagamento válido confirmado na URL e o usuário não está matriculado
            print("DEBUG: Falha na verificação ou pagamento não encontrado na URL.")
            return redirect('courses:course_detail', course_id=course.id)

        except Exception as e:
             print(f"DEBUG EXCEPTION: {e}")
             return HttpResponse(f"Erro ao processar a matrícula: {e}. Course ID recebido: {course_id}", status=500)
    
    # Se chegou aqui, faltou course_id ou usuário não logado
    debug_info = f"User: {request.user}, Course ID: {course_id}, GET Params: {request.GET}"
    return HttpResponse(f"Pagamento aprovado, mas houve um erro ao identificar o curso ou usuário. Entre em contato com o suporte com esta mensagem: {debug_info}")

def payment_failure(request):
    return render(request, 'payments/failure.html')

def payment_pending(request):
    return render(request, 'payments/pending.html')

def check_payment_status(request, course_id):
    if not request.user.is_authenticated:
        return JsonResponse({'enrolled': False})
    
    # 1. Verifica no banco de dados local primeiro
    is_enrolled = Enrollment.objects.filter(
        user=request.user,
        course_id=course_id,
        expiration_date__gt=timezone.now()
    ).exists()
    
    if is_enrolled:
        return JsonResponse({'enrolled': True})

    # 2. Se não estiver matriculado localmente, verifica na API do Mercado Pago
    # Isso serve como fallback para localhost onde o Webhook não chega
    try:
        access_token = getattr(settings, 'MERCADOPAGO_ACCESS_TOKEN', "APP_USR-6070359759810181-012720-586bdd780f3c02a48fb7e88ddb87a97a-417055483")
        if not access_token or access_token.startswith("APP_USR-9e"):
            access_token = "APP_USR-6070359759810181-012720-586bdd780f3c02a48fb7e88ddb87a97a-417055483"
        
        sdk = mercadopago.SDK(access_token)
        
        # Reconstrói a referência externa exatamente como foi criada
        external_ref = json.dumps({'course_id': int(course_id), 'user_id': request.user.id})
        
        filters = {
            "status": "approved",
            "external_reference": external_ref
        }
        
        print(f"DEBUG: Buscando pagamento para course_id={course_id} user={request.user.id}")
        search_result = sdk.payment().search(filters)
        
        if search_result["status"] == 200 and search_result["response"]["results"]:
            results = search_result["response"]["results"]
            # Ordena por data de criação (mais recente primeiro)
            results.sort(key=lambda x: x.get("date_created", ""), reverse=True)
            
            found_new_payment = False
            
            for payment in results:
                payment_id_mp = str(payment["id"])
                print(f"DEBUG: Analisando pagamento ID: {payment_id_mp}, Status: {payment['status']}")

                # VERIFICAÇÃO DE DUPLICIDADE
                if PaymentHistory.objects.filter(payment_id=payment_id_mp).exists():
                    print(f"DEBUG: Pagamento {payment_id_mp} JÁ EXISTE no histórico. Verificando próximo...")
                    continue

                # Verifica se o pagamento é recente
                payment_date_created = payment.get("date_created")
                print(f"DEBUG: Data do pagamento: {payment_date_created}")
                
                if payment_date_created:
                    payment_date = parse_datetime(payment_date_created)
                    if payment_date:
                        if timezone.is_naive(payment_date):
                            payment_date = timezone.make_aware(payment_date)
                        
                        # Se o pagamento for mais antigo que 30 minutos, ignoramos
                        if payment_date < timezone.now() - timezone.timedelta(minutes=30):
                             print("DEBUG: Pagamento muito antigo. Ignorando.")
                             continue

                course = Course.objects.get(id=course_id)

                print(f"DEBUG: Pagamento VÁLIDO encontrado: {payment_id_mp}. Processando renovação...")
                # Cria Histórico de Pagamento
                PaymentHistory.objects.create(
                    user=request.user,
                    course=course,
                    amount_paid=course.price,
                    days_added=course.duration_days,
                    payment_id=payment_id_mp
                )

                # Cria ou Atualiza Matrícula
                enrollment, created = Enrollment.objects.get_or_create(
                    user=request.user,
                    course=course,
                    defaults={'expiration_date': timezone.now() + timezone.timedelta(days=course.duration_days)}
                )

                if not created:
                    if enrollment.expiration_date > timezone.now():
                        enrollment.expiration_date = enrollment.expiration_date + timezone.timedelta(days=course.duration_days)
                    else:
                        enrollment.expiration_date = timezone.now() + timezone.timedelta(days=course.duration_days)
                    enrollment.save()
                
                found_new_payment = True
                return JsonResponse({'enrolled': True})
            
            if not found_new_payment:
                print("DEBUG: Nenhum pagamento novo e válido encontrado na lista.")
                return JsonResponse({'enrolled': False})
            
    except Exception as e:
        print(f"Check Status Error: {e}")
        
    return JsonResponse({'enrolled': False})

@csrf_exempt
def webhook(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("WEBHOOK: Notificação recebida do Mercado Pago:", data)
            
            topic = data.get('type') or data.get('topic')
            resource_id = data.get('data', {}).get('id') or data.get('resource')

            if topic == 'payment':
                 # Inicializa o SDK do Mercado Pago
                access_token = getattr(settings, 'MERCADOPAGO_ACCESS_TOKEN', "APP_USR-6070359759810181-012720-586bdd780f3c02a48fb7e88ddb87a97a-417055483")
                if not access_token or access_token.startswith("APP_USR-9e"):
                    access_token = "APP_USR-6070359759810181-012720-586bdd780f3c02a48fb7e88ddb87a97a-417055483"
                
                sdk = mercadopago.SDK(access_token)
                payment_info = sdk.payment().get(resource_id)
                
                if payment_info["status"] == 200:
                    payment = payment_info["response"]
                    status = payment.get("status")
                    external_reference = payment.get("external_reference")
                    payment_id_mp = str(payment["id"])
                    
                    # VERIFICAÇÃO DE DUPLICIDADE
                    if PaymentHistory.objects.filter(payment_id=payment_id_mp).exists():
                        print(f"WEBHOOK: Pagamento {payment_id_mp} já processado.")
                        return HttpResponse(status=200)

                    if status == 'approved' and external_reference:
                        try:
                            ref_data = json.loads(external_reference)
                            course_id = ref_data.get('course_id')
                            user_id = ref_data.get('user_id')
                            
                            if course_id and user_id:
                                user = User.objects.get(id=user_id)
                                course = Course.objects.get(id=course_id)

                                # Verifica se o usuário já está matriculado
                                enrollment = Enrollment.objects.filter(
                                    user=user,
                                    course=course,
                                    expiration_date__gt=timezone.now()
                                ).first()

                                if enrollment:
                                    print(f"WEBHOOK: Usuário {user.username} já matriculado no curso {course.title}. Ignorando pagamento duplicado.")
                                    return HttpResponse(status=200)

                                # --- REGISTRO NO HISTÓRICO DE PAGAMENTOS ---
                                PaymentHistory.objects.create(
                                    user=user,
                                    course=course,
                                    amount_paid=course.price,
                                    days_added=course.duration_days,
                                    payment_id=payment_id_mp
                                )

                                # Cria a matrícula
                                Enrollment.objects.create(
                                    user=user,
                                    course=course,
                                    expiration_date=timezone.now() + timezone.timedelta(days=course.duration_days)
                                )

                                print(f"WEBHOOK: Nova matrícula criada para usuário {user.username} no curso {course.title}")
                                    
                        except (json.JSONDecodeError, User.DoesNotExist, Course.DoesNotExist) as e:
                            print(f"WEBHOOK ERROR: Falha ao processar external_reference ou encontrar objetos: {e}")

            return HttpResponse(status=200)
        except Exception as e:
            print(f"WEBHOOK ERROR: {e}")
            return HttpResponse(status=500)

    return HttpResponse(status=400)
