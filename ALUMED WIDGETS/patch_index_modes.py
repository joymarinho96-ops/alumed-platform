import re
import os

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Replace each nav-btn with a group containing the two new buttons.
# Biología
bio_replacement = """<div class="nav-item-group">
        <button class="nav-btn" id="nav-bio" onclick="toggleSubMenu('bio-submenu', this)">
          <i class="fa-solid fa-list-check"></i>
          <span>Biología</span>
        </button>
        <div class="sub-menu" id="bio-submenu" style="display:none; flex-direction: column; padding-left: 20px; gap: 4px; margin-top: 4px;">
           <button class="nav-btn sub-btn" style="font-size: 0.8rem; padding: 6px 12px;" onclick="iniciarSimulacroParcialReal('biologia')">⏱️ Simulacro Parcial Real</button>
           <button class="nav-btn sub-btn" style="font-size: 0.8rem; padding: 6px 12px;" onclick="iniciarEntrenamientoPorTema('biologia', 'Todos')">💪 Treinar por Temas (TPs)</button>
        </div>
      </div>"""
html = re.sub(r'<button class="nav-btn" id="nav-bio"[^>]*>.*?<span>Biologa</span>\s*</button>', bio_replacement, html, flags=re.DOTALL)

# Histología
hye_replacement = """<div class="nav-item-group">
        <button class="nav-btn" id="nav-hye" onclick="toggleSubMenu('hye-submenu', this)">
          <i class="fa-solid fa-microscope"></i>
          <span>Histología y Embriología</span>
        </button>
        <div class="sub-menu" id="hye-submenu" style="display:none; flex-direction: column; padding-left: 20px; gap: 4px; margin-top: 4px;">
           <button class="nav-btn sub-btn" style="font-size: 0.8rem; padding: 6px 12px;" onclick="iniciarSimulacroParcialReal('histo_embrio')">⏱️ Simulacro Parcial Real</button>
           <button class="nav-btn sub-btn" style="font-size: 0.8rem; padding: 6px 12px;" onclick="iniciarEntrenamientoPorTema('histo_embrio', 'Todos')">💪 Treinar por Temas (TPs)</button>
        </div>
      </div>"""
html = re.sub(r'<button class="nav-btn" id="nav-hye"[^>]*>.*?<span>Histologa y Embriologa</span>\s*</button>', hye_replacement, html, flags=re.DOTALL)

# Anatomía A
anatoa_replacement = """<div class="nav-item-group">
        <button class="nav-btn active" id="nav-anatoa" onclick="toggleSubMenu('anatoa-submenu', this)">
          <i class="fa-solid fa-comments"></i>
          <span>Anatomía A</span>
        </button>
        <div class="sub-menu" id="anatoa-submenu" style="display:none; flex-direction: column; padding-left: 20px; gap: 4px; margin-top: 4px;">
           <button class="nav-btn sub-btn" style="font-size: 0.8rem; padding: 6px 12px;" onclick="iniciarSimulacroParcialReal('anato_a')">⏱️ Simulacro Parcial Real</button>
           <button class="nav-btn sub-btn" style="font-size: 0.8rem; padding: 6px 12px;" onclick="iniciarEntrenamientoPorTema('anato_a', 'Todos')">💪 Treinar por Temas (TPs)</button>
        </div>
      </div>"""
html = re.sub(r'<button class="nav-btn active" id="nav-anatoa"[^>]*>.*?<span>Anatoma A</span>\s*</button>', anatoa_replacement, html, flags=re.DOTALL)

# Anatomía B
anatob_replacement = """<div class="nav-item-group">
        <button class="nav-btn" id="nav-anatob" onclick="toggleSubMenu('anatob-submenu', this)">
          <i class="fa-solid fa-crosshairs"></i>
          <span>Anatomía B</span>
        </button>
        <div class="sub-menu" id="anatob-submenu" style="display:none; flex-direction: column; padding-left: 20px; gap: 4px; margin-top: 4px;">
           <button class="nav-btn sub-btn" style="font-size: 0.8rem; padding: 6px 12px;" onclick="iniciarSimulacroParcialReal('anato_b')">⏱️ Simulacro Parcial Real (Pinches)</button>
           <button class="nav-btn sub-btn" style="font-size: 0.8rem; padding: 6px 12px;" onclick="iniciarEntrenamientoPorTema('anato_b', 'Todos')">💪 Treinar por Temas (TPs)</button>
        </div>
      </div>"""
html = re.sub(r'<button class="nav-btn" id="nav-anatob"[^>]*>.*?<span>Anatoma B</span>\s*</button>', anatob_replacement, html, flags=re.DOTALL)

# Anatomía C
anatoc_replacement = """<div class="nav-item-group">
        <button class="nav-btn" id="nav-anatoc" onclick="toggleSubMenu('anatoc-submenu', this)">
          <i class="fa-solid fa-comments"></i>
          <span>Anatomía C</span>
        </button>
        <div class="sub-menu" id="anatoc-submenu" style="display:none; flex-direction: column; padding-left: 20px; gap: 4px; margin-top: 4px;">
           <button class="nav-btn sub-btn" style="font-size: 0.8rem; padding: 6px 12px;" onclick="iniciarSimulacroParcialReal('anato_c')">⏱️ Simulacro Parcial Real</button>
           <button class="nav-btn sub-btn" style="font-size: 0.8rem; padding: 6px 12px;" onclick="iniciarEntrenamientoPorTema('anato_c', 'Todos')">💪 Treinar por Temas (TPs)</button>
        </div>
      </div>"""
html = re.sub(r'<button class="nav-btn" id="nav-anatoc"[^>]*>.*?<span>Anatoma C</span>\s*</button>', anatoc_replacement, html, flags=re.DOTALL)


# Add the timer header to index.html
timer_html = """
    <!--  ? ? ? ? ? ? ? ? ? ? ? ? ? ? CONTENIDO PRINCIPAL  ? ? ? ? ? ? ? ? ? ? ? ? ? ? -->
    <main class="content">
      <div id="examen-header" style="display: none; background: var(--bg-card); padding: 10px 20px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; border-radius: 8px; margin-bottom: 20px;">
        <h2 id="examen-titulo" style="margin: 0; font-size: 1.2rem; color: var(--fg-default);">Examen</h2>
        <div id="examen-timer" style="font-family: monospace; font-size: 1.5rem; font-weight: bold; color: var(--danger);">00:00</div>
        <button class="btn-primary" onclick="entregarParcialManualmente()">Entregar Examen</button>
      </div>
"""
html = html.replace('<!--  ? ? ? ? ? ? ? ? ? ? ? ? ? ? CONTENIDO PRINCIPAL  ? ? ? ? ? ? ? ? ? ? ? ? ? ? -->\n    <main class="content">', timer_html)

# Add Results Modal to index.html
results_modal = """
  <div id="resultados-modal" class="modal-overlay" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 10000; align-items: center; justify-content: center;">
    <div style="background: var(--bg-card); padding: 30px; border-radius: 12px; max-width: 500px; width: 90%; text-align: center; border: 1px solid var(--border);">
      <h2 style="margin-top: 0;">Resultados del Parcial</h2>
      <div id="resultado-estado" style="font-size: 1.8rem; font-weight: 800; margin: 20px 0;"></div>
      <p id="resultado-mensaje" style="font-size: 1.1rem; color: var(--muted);"></p>
      <div style="margin-top: 30px; display: flex; gap: 10px; justify-content: center;">
        <button class="btn-secondary" onclick="cerrarResultados()">Volver al Inicio</button>
      </div>
    </div>
  </div>
</body>
"""
html = html.replace('</body>', results_modal)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
