# Arquitectura de Integración: ALUMED Híbrido (Wix + Django)

Este documento detalla la arquitectura de integración para el ecosistema **ALUMED**, donde **Wix** actúa como el núcleo operativo/negocio y **Django** funciona como la **Capa de Experiencia (Experience Layer)** encargada de las herramientas avanzadas e interactivas.

---

## 1. Arquitectura Completa de la Integración (Modelo de Espejo)

El sistema opera bajo un modelo donde **Wix es la autoridad absoluta de accesos y matrículas**. Django no crea accesos por sí mismo, sino que **sincroniza y espeta** (refleja) los permisos definidos en Wix en tiempo real.

```mermaid
graph TD
    subgraph Ecosistema Wix (Núcleo Operativo y Autoridad de Accesos)
        WixAuth[Wix Members & Auth]
        WixPrograms[Wix Online Programs / Planes]
        WixStore[Wix Stores / Pasarela / Transferencias]
    end

    subgraph Capa de Experiencia Django (Espejo y Herramientas UX)
        DjWebhook[Endpoint Webhook Django /webhook-wix/]
        DjDB_Users[(Modelo Django: User & Profile)]
        DjDB_Perms[(Modelo Django: Enrollment Cache)]
        DjViews[Vistas Interactivas / Player / 3D / IA]
    end

    %% Flujos de datos y liberación
    User -->|1a. Compra Online| WixStore
    AdminStaff -->|1b. Pago Manual por Transferencia: Liberar en Wix| WixPrograms
    
    WixPrograms -->|2. Webhook: Participant Joined| DjWebhook
    DjWebhook -->|3. Crea/Actualiza Usuario| DjDB_Users
    DjWebhook -->|4. Sincroniza / Actualiza Permiso| DjDB_Perms
    
    DjDB_Perms -->|5. Renderiza según accesos| DjViews
```

---

## 2. Qué Partes Permanecen en Wix (Autoridad de la Verdad)

Wix es la única fuente de verdad operativa. Ningún acceso o matrícula se origina de manera oficial en Django:
1. **Autenticación Base:** Registro e inicio de sesión de miembros en Wix.
2. **Ciclo de Ventas:** Checkout, catálogo público de cursos y cobro mediante Mercado Pago.
3. **Liberación de Accesos por Compra:** Al comprar un curso en Wix, el sistema de Wix le otorga el acceso al programa correspondiente.
4. **Liberación de Accesos Manuales (Transferencias o Cortesías):** Si un estudiante paga por transferencia bancaria, el staff de administración lo agrega **manualmente en Wix** a través del panel:
   * `Programas online` ➔ `Programa` ➔ `Invitar/agregar participantes`.
5. **CRM y Gestión de Miembros:** Seguimiento de alumnos, envío de emails automáticos y facturación.

---

## 3. Qué Partes se Desarrollan en Django (Capa de Experiencia)

Django consume y espeta las decisiones tomadas en Wix para brindar la interfaz interactiva de aprendizaje:
1. **El Dashboard del Estudiante (Student Dashboard):** Progreso gamificado, accesos a cursos activos reflejados desde Wix y próximos eventos.
2. **El Reproductor de Cursos (Interactive Player):** Menú lateral estructurado y visor de lecciones y videos.
3. **Herramientas Especializadas:**
   * **Microscopio Virtual:** Visor de láminas de alta resolución.
   * **Anatomía 3D:** Modelos interactivos.
   * **IA Profe Joy:** Chat inteligente de tutoría médica.
   * **Flashcards:** Creación de mazos y repaso con repetición espaciada.
4. **Soportes:** Biblioteca Digital (Google Cloud Storage), Cartelera FCM (scraping en tiempo real), etc.

---

## 4. Cómo Compartir Autenticación (SSO)

Para que el alumno no tenga fricciones:
* Al loguearse en Wix e ir a las secciones de Django, Wix genera un **JWT** firmado con una clave secreta.
* El JWT contiene los datos del alumno (`email`, `first_name`, `last_name`, `wix_member_id`) y expira en pocos segundos.
* Django recibe el JWT en `/auth/callback/`, valida la firma, e inicia sesión localmente (`login(request, user)`) del estudiante.

---

## 5. Cómo Compartir Sesión

* **Subdominios Compartidos:** Wix operará en el dominio raíz (ej. `alumedestudiantes.com`) y Django en un subdominio (ej. `app.alumedestudiantes.com`), compartiendo cookies de sesión para la navegación fluida.

---

## 6. Cómo Compartir Identidad Visual

* **Navigation Mirroring:** Django clona la estructura y estilos CSS (morados oscuros y amarillos de alto contraste) del Header y Footer oficiales de Wix, logrando que el usuario no sienta que sale de la plataforma al usar las herramientas de Django.

---

## 7. Cómo Compartir Permisos y Accesos (Sincronización Hacia Django)

La sincronización es **unidireccional** (Wix ➔ Django) mediante webhooks de eventos de Wix:
* **Evento de Alta/Unión:** Cuando un estudiante compra un curso o es agregado manualmente a un programa en Wix, Wix dispara el Webhook `OnlinePrograms_ParticipantJoined` (o `PaidPlans_PlanPurchased`). Django procesa el evento, crea el usuario si no existe, y guarda una matrícula local (`Enrollment`).
* **Evento de Baja/Salida:** Si expira el tiempo del curso o se remueve al estudiante en Wix, Wix dispara `OnlinePrograms_ParticipantLeft` (o `PaidPlans_PlanCancelled`). Django actualiza la matrícula local a `is_active = False` y registra la fecha de finalización.

---

## 8. Cómo Integrar Futuras Funcionalidades sin Alterar Wix

* Las nuevas herramientas interactivas se crean como Django Apps modulares independientes. Wix simplemente enlazará a estas herramientas mediante URLs dinámicas que validan la sesión.

---

## 9. Cómo Mantener Escalabilidad para Nuevos Módulos

* **Assets Desacoplados:** Almacenamiento de archivos pesados en Google Cloud Storage (GCS), manteniendo la base de datos local SQLite/Postgres ligera y enfocada únicamente en la lógica de estados de accesos de estudiantes.

---

## 10. Roadmap Completo de la Arquitectura

1. **Fase 1: Sincronización Core (Wix Webhooks ➔ Django Enrollment Cache).**
2. **Fase 2: Autenticación Unificada (SSO por JWT).**
3. **Fase 3: Unificación Visual e Interfaces.**
4. **Fase 4: Despliegue de Herramientas Interactivas y Módulos Avanzados (Microscopio, Flashcards, IA).**
