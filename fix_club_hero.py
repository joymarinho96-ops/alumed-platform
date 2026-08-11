import re

file_path = r'C:\Users\joyce\Downloads\alumesitemdesenvolvimento-main\alumed-platform\templates\core\club.html'
with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

pattern = r'<div class="hero-visual" style="flex:0 0 400px;height:480px;position:relative;">.*?<!-- Cards flotantes con info -->'
replacement = r'''<div class="hero-visual" style="flex:0 0 400px;height:480px;position:relative;">

        <!-- Blob glow -->
        <div style="position:absolute;inset:0;background:radial-gradient(circle at 50% 50%,rgba(124,58,237,.25),transparent 70%);border-radius:50%;"></div>

        <!-- Central circle con imagen Profe Joy -->
        <div style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:280px;height:280px;border-radius:50%;background:rgba(255,255,255,.03);border:1px solid rgba(124,58,237,.3);display:flex;align-items:center;justify-content:center;overflow:hidden;box-shadow:0 0 40px rgba(124,58,237,.2);">
          <img src="{% static 'core/img/profe_joy_nobg.png' %}" alt="Profe Joy" style="width:100%;height:100%;object-fit:cover;transform:scale(1.1) translateY(10px);">
        </div>

        <!-- ECG ring -->
        <svg style="position:absolute;inset:0;width:100%;height:100%;" viewBox="0 0 400 480">
          <circle cx="200" cy="240" r="155" fill="none" stroke="rgba(124,58,237,.2)" stroke-width="1.5" stroke-dasharray="6,8"/>
          <circle cx="200" cy="240" r="110" fill="none" stroke="rgba(255,230,0,.12)" stroke-width="1" stroke-dasharray="4,10"/>
        </svg>

        <!-- Cards flotantes con info -->'''

new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Fix the word ANATOMÍA
new_content = re.sub(r'<div[^>]*>ANATOM.*?A</div>', r'<div style="font-size:10px;color:#FFE600;font-weight:800;font-family:\'Orbitron\',sans-serif;letter-spacing:1px;">ANATOMÍA</div>', new_content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)
print('Patched hero-visual in club.html')
