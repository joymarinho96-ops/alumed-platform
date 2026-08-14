# 🔬 Guía de Integración: Microscopio Virtual con Django

## 📋 Descripción

El archivo `microscopio_virtual.html` es un microscopio educativo completamente funcional que puede ser integrado con cualquier backend. Actualmente contiene datos hardcodeados de 12 láminas histológicas reales de la UFRJ.

## 🔧 Opciones de Integración

### OPCIÓN 1: Sin Cambios (Standalone)
El archivo funciona tal como está sin necesidad de backend.
```
http://localhost:8000/microscopio_virtual.html
```

---

### OPCIÓN 2: Integración con Django (Recomendado)

#### A. Backend Django

**1. Crear API Endpoint:**

```python
# views.py
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def get_laminas(request):
    """Retorna todas las láminas disponibles"""
    laminas = {
        'Embriología': [
            {
                'id': 'lamina02',
                'nombre': 'Cordón Umbilical (Humano)',
                'descripcion': 'Dos arterias y una vena. Gelatina de Wharton visible.',
                'url': 'http://www.histo.ufrj.br/LIB/Lamina%2002_files/0/0_0.jpg'
            },
            # ... más láminas
        ],
        # ... más sistemas
    }
    return JsonResponse(laminas)

@require_http_methods(["GET"])
def get_lamina_detail(request, lamina_id):
    """Retorna detalles de una lámina específica"""
    laminas = get_all_laminas()  # Función auxiliar
    for category, items in laminas.items():
        for lamina in items:
            if lamina['id'] == lamina_id:
                return JsonResponse({'success': True, 'data': lamina})
    return JsonResponse({'success': False, 'error': 'Lámina no encontrada'})

@require_http_methods(["POST"])
def save_annotation(request, lamina_id):
    """Guardar anotaciones del estudiante"""
    import json
    data = json.loads(request.body)
    annotation = {
        'lamina_id': lamina_id,
        'student_id': request.user.id,
        'drawing_data': data.get('drawing'),
        'timestamp': timezone.now(),
        'notes': data.get('notes', '')
    }
    # Guardar en base de datos
    StudentAnnotation.objects.create(**annotation)
    return JsonResponse({'success': True})
```

**2. URLs:**

```python
# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('api/laminas/', views.get_laminas, name='get_laminas'),
    path('api/laminas/<str:lamina_id>/', views.get_lamina_detail, name='get_lamina_detail'),
    path('api/laminas/<str:lamina_id>/save-annotation/', views.save_annotation, name='save_annotation'),
    path('microscopio/', views.microscopio_view, name='microscopio'),
]
```

**3. Vista que renderiza el HTML:**

```python
# views.py
def microscopio_view(request):
    return render(request, 'microscopio_virtual.html', {
        'user': request.user,
        'api_url': '/api/laminas/'
    })
```

#### B. Modificar JavaScript para Django

**Reemplazar la sección de datos con fetch:**

```javascript
// En lugar de const laminasData = { ... }
let laminasData = {};

// Cargar datos del backend al inicializar
async function loadLaminasFromBackend() {
    try {
        const response = await fetch('/api/laminas/');
        laminasData = await response.json();
        console.log('Láminas cargadas desde backend:', laminasData);
    } catch (error) {
        console.error('Error cargando láminas:', error);
        // Fallback a datos locales si el backend no está disponible
        loadLocalData();
    }
}

// Ejecutar antes de init()
document.addEventListener('DOMContentLoaded', async () => {
    await loadLaminasFromBackend();
    init();
});
```

#### C. Guardar Anotaciones

```javascript
// Función para guardar anotaciones
async function saveAnnotation() {
    if (!appState.currentLamina) return;

    const drawingData = appState.canvas.toJSON();
    
    try {
        const response = await fetch(`/api/laminas/${appState.currentLamina.id}/save-annotation/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({
                drawing: drawingData,
                notes: document.getElementById('notes-textarea')?.value || ''
            })
        });

        const result = await response.json();
        if (result.success) {
            alert('✅ Anotaciones guardadas correctamente');
        }
    } catch (error) {
        console.error('Error guardando anotaciones:', error);
    }
}

// Agregar botón para guardar
document.getElementById('btn-save-annotation')?.addEventListener('click', saveAnnotation);
```

---

### OPCIÓN 3: Flask

```python
# app.py
from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route('/api/laminas')
def get_laminas():
    return jsonify(laminas_data)

@app.route('/microscopio')
def microscopio():
    return render_template('microscopio_virtual.html')
```

---

## 📊 Modelo de Base de Datos (Django)

```python
from django.db import models
from django.contrib.auth.models import User

class Lamina(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    nombre = models.CharField(max_length=255)
    sistema = models.CharField(max_length=100)
    descripcion = models.TextField()
    url = models.URLField()
    imagen_preview = models.ImageField(upload_to='previews/', null=True, blank=True)
    
    class Meta:
        db_table = 'laminas'

class StudentAnnotation(models.Model):
    estudiante = models.ForeignKey(User, on_delete=models.CASCADE)
    lamina = models.ForeignKey(Lamina, on_delete=models.CASCADE)
    dibujo_json = models.JSONField()
    notas = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_annotations'
        unique_together = ('estudiante', 'lamina')
```

---

## 🚀 Deployment

### Local (Desarrollo)
```bash
cd /path/to/HHISTOLOGY
python -m http.server 8000
# Acceder a: http://localhost:8000/microscopio_virtual.html
```

### Django Development
```bash
cd /path/to/django_project
python manage.py runserver
# Acceder a: http://localhost:8000/microscopio/
```

### Production (Gunicorn + Nginx)
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

---

## 📝 Estructura de Archivos

```
HHISTOLOGY/
├── microscopio_virtual.html        # Interfaz principal
├── laminas_ufrj_datos.json         # Datos de láminas (referencia)
├── imagens_laminas/
│   └── Lamina15.dzi                # Imágenes DZI
└── (OPCIONAL) django_app/
    ├── views.py
    ├── urls.py
    ├── models.py
    └── templates/
        └── microscopio_virtual.html
```

---

## 🔌 API Reference

### GET /api/laminas/
Retorna todas las láminas organizadas por categoría

**Respuesta:**
```json
{
  "Sistema Digestivo": [
    {
      "id": "lamina06",
      "nombre": "Intestino Delgado",
      "descripcion": "Vellosidades intestinales...",
      "url": "http://..."
    }
  ]
}
```

### GET /api/laminas/{lamina_id}/
Retorna detalles de una lámina específica

### POST /api/laminas/{lamina_id}/save-annotation/
Guarda anotaciones del estudiante

**Payload:**
```json
{
  "drawing": {...fabricjs_data...},
  "notes": "Mis observaciones..."
}
```

---

## 🎨 Personalización

### Cambiar Datos
Reemplaza `laminasData` en el JavaScript con tu propio JSON

### Cambiar Colores
Modifica las variables de Tailwind en CSS

### Agregar Herramientas
Agrega botones en el toolbar y conecta con Fabric.js

---

## ✅ Checklist de Implementación

- [ ] Crear app Django
- [ ] Definir modelos (Lamina, StudentAnnotation)
- [ ] Crear views/serializers
- [ ] Configurar URLs
- [ ] Copiar microscopio_virtual.html
- [ ] Agregar fetch() para cargar datos
- [ ] Implementar guardado de anotaciones
- [ ] Agregar autenticación (usuario)
- [ ] Testear en desarrollo
- [ ] Deployer a producción

---

## 🐛 Troubleshooting

**Q: Las imágenes no cargan**
A: Verifica que las URLs de UFRJ sean correctas y que el servidor de imágenes esté disponible

**Q: Los dibujos no se guardan**
A: Asegúrate que:
- El usuario esté autenticado
- El CSRF token esté presente
- El endpoint POST esté configurado

**Q: Error CORS**
A: Agrega a Django:
```python
INSTALLED_APPS = [
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
]
```

---

**Última actualización:** 7 de enero de 2026
**Versión:** 1.0.0
**Autor:** Sistema de Microscopía Virtual Educativa
