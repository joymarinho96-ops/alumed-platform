# Guía de Configuración e Integración: Wix Velo ➔ Django

Esta guía práctica contiene el procedimiento y las plantillas de código para configurar **Wix Velo** para enviar eventos de accesos y matrículas a la Capa de Experiencia de **Django**.

---

## 1. Eventos de Wix que Debemos Escuchar

Para sincronizar correctamente el estado de las inscripciones, escucharemos los eventos de la aplicación **Programas Online de Wix (Online Programs)**. 

| Evento de Wix | Evento Velo (`events.js`) | Acción en Django |
| :--- | :--- | :--- |
| **Alumno se une / es invitado a curso** | `wixOnlinePrograms_onParticipantJoined` | Crea el usuario en Django (si no existe) y activa/extiende su matrícula (`Enrollment`). |
| **Alumno abandona / es removido** | `wixOnlinePrograms_onParticipantLeft` | Desactiva temporal o definitivamente la matrícula del alumno en Django (`is_active = False`). |

*(Nota: Opcionalmente, si utilizas los planes de precios de Wix, puedes escuchar `wixPaidPlans_onPlanPurchased` y `wixPaidPlans_onPlanCanceled`).*

---

## 2. Dónde Configurar esto en Wix (Velo Backend)

1. Abre el editor de tu sitio en **Wix**.
2. Activa el **Modo Dev** en la barra superior.
3. En la barra lateral izquierda de código, navega hasta la carpeta **Código Público y del Backend** ➔ **Backend**.
4. Haz clic en **Agregar Archivo** y nómbralo exactamente como **`events.js`** (si ya existe un archivo de eventos, edítalo para integrar este código).
5. Crea un secreto seguro en el administrador de secretos de tu panel de Wix (`Opciones del Sitio ➔ Administrador de Secretos`) con el nombre exacto de **`WIX_WEBHOOK_SECRET`**.

---

## 3. Código Velo Backend para `events.js`

Pega el siguiente código en el archivo `events.js` de Wix:

```javascript
import { getSecret } from 'wix-secrets-backend';
import { fetch } from 'wix-fetch';
import crypto from 'crypto';

// URL del servidor de Django. Reemplazar por tu ngrok para pruebas locales
// o por el dominio oficial en producción (ej. https://app.alumedestudiantes.com/pagamento/webhook-wix/)
const DJANGO_WEBHOOK_URL = "https://TU_SUBDOMINIO_NGROK.ngrok-free.app/pagamento/webhook-wix/";

async function sendToDjango(event, data) {
    try {
        const secret = await getSecret("WIX_WEBHOOK_SECRET");
        const payload = {
            event: event,
            timestamp: Date.now(),
            data: data
        };
        const bodyStr = JSON.stringify(payload);
        
        // 1. Generar la firma HMAC-SHA256
        const signature = crypto
            .createHmac('sha256', secret)
            .update(bodyStr)
            .digest('hex');
            
        // 2. Enviar el HTTP POST request de forma asíncrona
        const response = await fetch(DJANGO_WEBHOOK_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Wix-Signature': signature
            },
            body: bodyStr
        });
        
        if (response.ok) {
            console.log(`[ALUMED Webhook] Enviado con éxito: ${event}`);
        } else {
            const errText = await response.text();
            console.error(`[ALUMED Webhook Error] Falló el evento ${event}: ${response.status} - ${errText}`);
        }
    } catch (err) {
        console.error("[ALUMED Webhook Error] Error interno en sendToDjango:", err);
    }
}

/**
 * Evento cuando un alumno se inscribe o el staff lo invita manualmente a un programa en Wix.
 */
export function wixOnlinePrograms_onParticipantJoined(event) {
    const participant = event.participant;
    
    // Calcular fecha de expiración (si no viene en el evento, definimos 365 días por defecto)
    const start = event.joinedDate || new Date();
    const expiry = event.expiryDate || new Date(start.getTime() + 365 * 24 * 60 * 60 * 1000);

    const data = {
        wix_member_id: participant.memberId,
        email: participant.email,
        first_name: participant.firstName || "",
        last_name: participant.lastName || "",
        product_or_plan_id: event.programId, // Mapeado en settings.py de Django
        // Detectar si fue por compra (checkout) o invitación manual (transferencia)
        access_source: event.joinSource === 'INVITED' ? 'transferencia' : 'wix',
        amount_paid: 0.00, // Puede asociarse a variables según el tipo de programa
        start_date: start.toISOString(),
        expiration_date: expiry.toISOString()
    };

    return sendToDjango("OnlinePrograms_ParticipantJoined", data);
}

/**
 * Evento cuando la matrícula expira, es cancelada o el alumno es removido en Wix.
 */
export function wixOnlinePrograms_onParticipantLeft(event) {
    const participant = event.participant;
    const data = {
        wix_member_id: participant.memberId,
        email: participant.email,
        product_or_plan_id: event.programId,
        expiration_date: new Date().toISOString() // Cancela el acceso inmediatamente
    };

    return sendToDjango("OnlinePrograms_ParticipantLeft", data);
}
```

---

## 4. Pruebas Locales Seguras con `ngrok`

Para redirigir los webhooks reales de tu editor Wix a tu servidor local de Django:

1. **Descarga ngrok** en tu computadora e inicia sesión en su sitio oficial.
2. Abre una terminal local y levanta el túnel apuntando al puerto de tu servidor local (`8000`):
   ```bash
   ngrok http 8000
   ```
3. Copia la URL HTTPS que ngrok te proporcione (ej: `https://abcd-12-34.ngrok-free.app`).
4. Reemplaza temporalmente la constante `DJANGO_WEBHOOK_URL` en tu archivo `events.js` de Wix con tu URL de ngrok:
   ```javascript
   const DJANGO_WEBHOOK_URL = "https://abcd-12-34.ngrok-free.app/pagamento/webhook-wix/";
   ```
5. Publica los cambios de tu sitio Wix (los eventos del Backend solo corren en el sitio publicado).

---

## 5. Confirmación de Sincronización en Django

Para corroborar que los eventos de Wix se procesaron correctamente:

1. Abre el panel de administración de Django (`/admin`) con una cuenta superusuario.
2. Ingresa a la sección **Enrollments** (Matrículas).
3. Busca al estudiante y verifica que:
   * Se haya creado su registro en Django con el `wix_member_id` correcto.
   * La matrícula esté activa y configurada con el origen correcto (`wix` o `transferencia`).
4. Ingresa a la sección **Historiales de Matrículas** (`EnrollmentHistory`) para revisar el log inmutable del evento procesado.
5. Si ocurrió algún error, revisa el archivo de registro (logs) de Django para identificar fallas en la validación de la firma o el parseo de datos.

---

## 6. Checklist antes del Despliegue en Producción

- [ ] Asegurarse de crear la variable de entorno `WIX_WEBHOOK_SECRET` con la misma clave en Wix Secrets Manager y en el archivo de producción `.env` de Django.
- [ ] Actualizar la constante `DJANGO_WEBHOOK_URL` en Wix con el dominio oficial de producción (ej. `https://app.alumedestudiantes.com/pagamento/webhook-wix/`).
- [ ] Validar que todos los IDs de programas en Wix coincidan exactamente con las claves declaradas en el diccionario `WIX_PLAN_COURSE_MAPPING` de Django.
- [ ] Asegurarse de que el servidor web de Django tenga los puertos abiertos para recibir solicitudes HTTPS externas desde los servidores de Wix.
