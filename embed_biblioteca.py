import os
import re

print("Applying Biblioteca Embed...")

def patch_file(filepath, replacements):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    for old, new in replacements:
        content = content.replace(old, new)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Patched {filepath}")

# 1. Update static/atlas_histologico/index.html
index_html = r'C:\Users\joyce\Downloads\alumesitemdesenvolvimento-main\alumed-platform\static\atlas_histologico\index.html'

# Update sidebar link
old_sidebar_link_static = """<a class="nav-btn" id="nav-biblioteca" href="https://secretaria478.wixsite.com/conectafcm/biblioteca-virtual" target="_blank" style="text-decoration: none; display: flex; align-items: center; gap: 10px;">
          <i class="fa-solid fa-book-open" style="color: var(--cyan-neon);"></i>
          <span>Biblioteca Virtual</span>
        </a>"""
new_sidebar_link_static = """<button class="nav-btn" id="nav-biblioteca" onclick="mostrarBiblioteca(this)">
          <i class="fa-solid fa-book-open" style="color: var(--cyan-neon);"></i>
          <span>Biblioteca Virtual</span>
        </button>"""

# Add tab content
tab_html = """
      <!-- TAB: BIBLIOTECA VIRTUAL -->
      <section id="tab-biblioteca" class="tab-content" style="padding:0; margin:0; overflow:hidden;">
        <div class="biblioteca-embed-wrapper">
          <iframe 
            id="iframe-biblioteca"
            src="https://secretaria478.wixsite.com/conectafcm/biblioteca-virtual" 
            frameborder="0" 
            scrolling="no"
            allowfullscreen>
          </iframe>
        </div>
      </section>
"""

patch_file(index_html, [
    (old_sidebar_link_static, new_sidebar_link_static),
])
with open(index_html, 'r', encoding='utf-8') as f:
    if 'id="tab-biblioteca"' not in f.read():
        patch_file(index_html, [("</main>", tab_html + "\n      </main>")])

# 2. Update templates/core/atlas_histologico.html
django_html = r'C:\Users\joyce\Downloads\alumesitemdesenvolvimento-main\alumed-platform\templates\core\atlas_histologico.html'

old_sidebar_link_django = """<a class="nav-btn" id="nav-biblioteca" href="/biblioteca/" style="text-decoration: none; display: flex; align-items: center; gap: 10px;">
          <i class="fa-solid fa-book-open" style="color: var(--cyan-neon);"></i>
          <span>Biblioteca Virtual</span>
        </a>"""
new_sidebar_link_django = """<button class="nav-btn" id="nav-biblioteca" onclick="mostrarBiblioteca(this)">
          <i class="fa-solid fa-book-open" style="color: var(--cyan-neon);"></i>
          <span>Biblioteca Virtual</span>
        </button>"""

# Also fix the top nav in django template
old_topnav_link_django = """<a href="/biblioteca/" style="color: #cbd5e1; text-decoration: none; font-weight: 600; font-size: 0.88rem;">Biblioteca</a>"""
new_topnav_link_django = """<a href="#" onclick="mostrarBiblioteca(document.getElementById('nav-biblioteca')); return false;" style="color: #cbd5e1; text-decoration: none; font-weight: 600; font-size: 0.88rem;">Biblioteca</a>"""

patch_file(django_html, [
    (old_sidebar_link_django, new_sidebar_link_django),
    (old_topnav_link_django, new_topnav_link_django)
])
with open(django_html, 'r', encoding='utf-8') as f:
    if 'id="tab-biblioteca"' not in f.read():
        patch_file(django_html, [("</main>", tab_html + "\n      </main>")])

# 3. Update style.css
css_file = r'C:\Users\joyce\Downloads\alumesitemdesenvolvimento-main\alumed-platform\static\atlas_histologico\style.css'
css_append = """
/* BIBLIOTECA VIRTUAL EMBED */
#tab-biblioteca {
  height: calc(100vh - 60px); /* Ajustar según topbar */
  width: 100%;
  display: none;
}
#tab-biblioteca.active {
  display: block;
}
.biblioteca-embed-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
}
/* Ocultar barra superior y márgenes del Wix empujando el iframe hacia arriba y ampliando la altura */
#iframe-biblioteca {
  position: absolute;
  top: -100px; /* Esconde banner superior de Wix */
  left: 0;
  width: 100%;
  height: calc(100% + 150px); /* Compensa el top negativo para evitar espacio blanco abajo */
  border: none;
  overflow: hidden;
}
"""
with open(css_file, 'r', encoding='utf-8') as f:
    if '.biblioteca-embed-wrapper' not in f.read():
        with open(css_file, 'a', encoding='utf-8') as fa:
            fa.write(css_append)
        print("Patched style.css")

# 4. Update app.js
app_js = r'C:\Users\joyce\Downloads\alumesitemdesenvolvimento-main\alumed-platform\static\atlas_histologico\app.js'
js_append = """
// --- BIBLIOTECA VIRTUAL LOGIC ---
window.mostrarBiblioteca = function(btnEl) {
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
  
  const sec = document.getElementById('tab-biblioteca');
  if (sec) sec.classList.add('active');
  if (btnEl) btnEl.classList.add('active');
};
"""
with open(app_js, 'r', encoding='utf-8') as f:
    if 'mostrarBiblioteca' not in f.read():
        with open(app_js, 'a', encoding='utf-8') as fa:
            fa.write(js_append)
        print("Patched app.js")

print("Done embedding Biblioteca.")
