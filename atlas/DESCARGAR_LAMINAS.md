# 📥 Guía: Descargar Láminas UFRJ Localmente

## ¿Por qué descargar?

El servidor UFRJ tiene restricciones **CORS** (Cross-Origin Resource Sharing) que impiden cargar imágenes directamente desde el navegador. Descargar las imágenes localmente:

✅ **Elimina errores de CORS**
✅ **Carga más rápido** (localhost vs servidor UFRJ)
✅ **Funciona sin internet** (después de descargar)
✅ **Mejor experiencia educativa** (sin lag)

---

## 🚀 Paso 1: Ejecutar el Descargador

```bash
cd c:\Users\joyce\OneDrive\Desktop\HHISTOLOGY
python baixar_laminas_ufrj.py
```

### Qué hace:
- 📥 Descarga cada lámina de UFRJ en múltiples niveles de zoom
- 💾 Organiza en carpetas: `imagens_laminas/lamina_{id}/`
- 🔄 Reintentos automáticos si algo falla
- ⏱️ Respecta tiempos de espera para no sobrecargar servidor
- 📝 Actualiza `laminas_ufrj_dados.json` con URLs locales

### Tiempo estimado:
- **~10-15 minutos** (depende de tu conexión)
- **Tamaño total:** ~200-300 MB

---

## 🔄 Paso 2: Cómo Funciona el Fallback

El `microscopio_virtual.html` ahora tiene lógica inteligente:

```javascript
// 1️⃣ Intenta cargar desde URL LOCAL primero
if (existe "/imagens_laminas/lamina_02/nivel_0_0.jpg") {
    cargar desde local  ✅ Sin CORS
}

// 2️⃣ Si no existe, intenta UFRJ directamente
si no {
    cargar desde UFRJ + CORS headers
}

// 3️⃣ Si ambas fallan, mostrar placeholder
si falla UFRJ {
    mostrar mensaje de error
}
```

---

## 📂 Estructura de Carpetas Después

```
HHISTOLOGY/
├── microscopio_virtual.html      ← Abre esto
├── baixar_laminas_ufrj.py        ← Ejecuta esto primero
├── laminas_ufrj_dados.json       ← Se actualiza automáticamente
└── imagens_laminas/
    ├── lamina_02/
    │   ├── nivel_12_0_0.jpg      (zoom muy pequeño)
    │   ├── nivel_11_0_0.jpg
    │   ├── nivel_10_0_0.jpg      (thumbnail)
    │   └── ... (más niveles)
    ├── lamina_03/
    │   ├── nivel_12_0_0.jpg
    │   └── ...
    └── ... (más láminas)
```

---

## 🖥️ Paso 3: Iniciar el Servidor

```bash
cd c:\Users\joyce\OneDrive\Desktop\HHISTOLOGY
python -m http.server 8000
```

**Acceder a:**
```
http://localhost:8000/microscopio_virtual.html
```

---

## ✅ Verificar que Funcionó

1. Abre el navegador en `http://localhost:8000/microscopio_virtual.html`
2. Selecciona una lámina del sidebar
3. Abre DevTools (`F12` → Console)
4. Debes ver: `✅ Cargando lamina_02 desde: /imagens_laminas/lamina_02/nivel_0_0.jpg`

Si ves eso, ¡está funcionando sin CORS! 🎉

---

## 🔧 Troubleshooting

### Q: "Error: Timed out"
```
R: El servidor UFRJ está lento. El script reintenta 3 veces automáticamente.
   Espera más o intenta más tarde.
```

### Q: "404 Not Found" en nivel_12
```
R: Algunos niveles de zoom pueden no existir en UFRJ.
   El script intenta alternativas automáticamente.
```

### Q: Imagenes no cargan en el navegador
```
R: Verifica que el servidor está corriendo:
   netstat -ano | findstr :8000
   
   O reinicia:
   python -m http.server 8000
```

### Q: Quiero descargar solo algunas láminas
```
R: Edita baixar_laminas_ufrj.py y filtra en ejecutar():

   for categoria, laminas in laminas_data.items():
       for lamina in laminas:
           if lamina['id'] in ['lamina_02', 'lamina_03']:  # ← Solo estas
               self.descargar_piramide_lamina(...)
```

### Q: Quiero actualizar una lámina
```
R: Elimina su carpeta y ejecuta el descargador de nuevo:
   Remove-Item imagens_laminas\lamina_02 -Recurse
   python baixar_laminas_ufrj.py
```

---

## 🌐 Alternativa: Sin Descargar (Usar UFRJ Directo)

Si prefieres no descargar:

1. El fallback del código intenta UFRJ directo
2. **PERO** puede fallar por CORS en algunos navegadores
3. Para evitar CORS, usa un proxy:

```javascript
// En microscopio_virtual.html, cambia:
url: 'https://cors-anywhere.herokuapp.com/' + lamina.url

// O usa un proxy propio (Django)
```

---

## 📊 Estadísticas

**Láminas descargadas:** 12
**Niveles por lámina:** 13 (zoom levels 0-12)
**Formato:** JPEG de múltiples resoluciones
**Tamaño estimado:** 15-25 MB por lámina
**Total:** 180-300 MB

---

## 💡 Tips

✅ **Descarga en background:** Abre PowerShell otra y deja corriendo mientras trabajas

✅ **Monitorea progreso:** El script muestra ✅/❌ en tiempo real

✅ **Fallback automático:** Si falla local, intenta UFRJ. Si falla UFRJ, muestra error

✅ **Caché del navegador:** Las imágenes se cachean en `localhost`, super rápido en reload

---

## 🎓 Integración con Backend

Cuando hagas el Django backend:

```python
# views.py
from pathlib import Path

@api_view(['GET'])
def get_lamina_image(request, lamina_id, nivel):
    # Servir imagen local directamente
    ruta = Path(f'imagens_laminas/lamina_{lamina_id}/nivel_{nivel}_0_0.jpg')
    with open(ruta, 'rb') as f:
        return FileResponse(f, content_type='image/jpeg')
```

---

**Estado:** ✅ Listo para usar
**Última actualización:** 7 de enero, 2026
