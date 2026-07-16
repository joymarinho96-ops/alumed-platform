#!/usr/bin/env python3
"""
Fix ALL encoding issues in club.html
Strategy: regex-based replacement of all corrupted Unicode sequences
"""
import sys
import re

def fix_all(path):
    with open(path, 'rb') as f:
        raw = f.read()

    # Remove BOM
    if raw.startswith(b'\xef\xbb\xbf'):
        raw = raw[3:]

    # Decode as UTF-8 (will give us mojibake strings)
    text = raw.decode('utf-8', errors='replace')

    # ══════════════════════════════════════════════════
    # TABLE: corrected chars / corrupted sequences
    # These are double-encoded UTF-8 seen as latin-1 then re-encoded
    # ══════════════════════════════════════════════════
    replacements = [
        # Triple-encoded accents (ÃƒÂx patterns)
        ('Ã\u0192Â©', 'é'),
        ('Ã\u0192Â¨', 'è'),
        ('Ã\u0192Â\xaa', 'ê'),
        ('Ã\u0192Â¯', 'ï'),
        ('Ã\u0192Â­', 'í'),
        ('Ã\u0192Â®', 'î'),
        ('Ã\u0192Â¬', 'ì'),
        ('Ã\u0192Â¡', 'á'),
        ('Ã\u0192Â ', 'à'),
        ('Ã\u0192Â¢', 'â'),
        ('Ã\u0192Â£', 'ã'),
        ('Ã\u0192Â¤', 'ä'),
        ('Ã\u0192Â³', 'ó'),
        ('Ã\u0192Â²', 'ò'),
        ('Ã\u0192Â´', 'ô'),
        ('Ã\u0192Âµ', 'õ'),
        ('Ã\u0192Â¶', 'ö'),
        ('Ã\u0192Âº', 'ú'),
        ('Ã\u0192Â¹', 'ù'),
        ('Ã\u0192Â»', 'û'),
        ('Ã\u0192Â¼', 'ü'),
        ('Ã\u0192Â±', 'ñ'),
        ('Ã\u0192Â§', 'ç'),
        ('Ã\u0192Â°', 'ú'),
        # Uppercase accents (ÃƒÂx)
        ('Ã\u0192\u201a', 'Â'),
        ('Ã\u201aÂ°', '°'),
        ('Ã\u201aÂ·', '·'),
        ('Ã\u201aÂ¿', '¿'),
        ('Ã\u201aÂ¡', '¡'),
        # Double-encoded (Ãx simple)
        ('Ã©', 'é'),
        ('Ã¨', 'è'),
        ('Ã\xaa', 'ê'),
        ('Ã\xab', 'ë'),
        ('Ã­', 'í'),
        ('Ã\xae', 'î'),
        ('Ã¯', 'ï'),
        ('Ã¡', 'á'),
        ('Ã ', 'à'),
        ('Ã¢', 'â'),
        ('Ã£', 'ã'),
        ('Ã¤', 'ä'),
        ('Ã³', 'ó'),
        ('Ã²', 'ò'),
        ('Ã´', 'ô'),
        ('Ãµ', 'õ'),
        ('Ã¶', 'ö'),
        ('Ãº', 'ú'),
        ('Ã¹', 'ù'),
        ('Ã»', 'û'),
        ('Ã¼', 'ü'),
        ('Ã±', 'ñ'),
        ('Ã§', 'ç'),
        ('Ã', 'À'),
        # Smart quotes / dashes
        ('â€™', "'"),
        ('â€œ', '"'),
        ('â€\x9d', '"'),
        ('â€"', '–'),
        ('â€"', '—'),
        ('â€¦', '…'),
        # Degree / symbols
        ('Â°', '°'),
        ('Â·', '·'),
        ('Â¿', '¿'),
        ('Â¡', '¡'),
        ('Â ', '\u00a0'),
        # Corrupted emojis/special chars in comments -> clean replacements
        # These are box-drawing chars used in CSS comments (═══, ♦, etc.)
        # Replace entire corrupted comment decorations with clean ASCII
    ]

    for bad, good in replacements:
        text = text.replace(bad, good)

    # Clean up corrupted emoji/box-drawing in CSS comments
    # Replace lines that are mostly garbage (decorative box chars in comments)
    def clean_comment_line(m):
        # If a comment line is mostly garbled, replace its decoration with clean chars
        content = m.group(0)
        if '\ufffd' in content or 'Ã¢' in content:
            # Replace the garbled box-drawing sequences with simple dashes
            clean = re.sub(r'[\ufffd\xc3\xa2\x82\x9c\xa4\x90\x9d\xe2\x80\x9c\xa2\x84\x94\xc2\x9d\x94\xa0]+', '═', content)
            return clean
        return content

    # Also clean up garbled emoji in HTML (like ðŸ§ -> 🧠)
    emoji_map = {
        'Ã°Å¸â€˜': '🎓',
        'Ã°Å¸â€™': '🎙',
        'Ã°Å¸â€˜¡': '💡',
        'Ã°Å¸': '🔥',
        'ÃŸ': 'ß',
    }
    for bad, good in emoji_map.items():
        text = text.replace(bad, good)

    # Final cleanup: remove remaining replacement chars in comments (they're just decorative)
    # Replace sequences of \ufffd with nothing in CSS comments
    text = re.sub(r'/\*[^\*]*\*/', lambda m: re.sub(r'[\ufffd]+', '', m.group(0)), text)

    # Remove garbled sequences that are leftover noise (Ã and similar in CSS comments)
    # Keep only in HTML content, not in comments
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)

    return text

path = 'templates/core/club.html'
result = fix_all(path)

print("=== VERIFICAÇÃO FINAL ===")
checks = [
    ('Aprendé', True),
    ('Biología', True),
    ('Método', True),
    ('Histología', True),
    ('Embriología', True),
    ('Anatomía', True),
    ('año', True),
    ('acompañamiento', True),
    ('satisfacción', True),
    ('FCM UNLP', True),
]
all_ok = True
for text, should_exist in checks:
    found = text in result
    status = "OK" if found == should_exist else "ERRO"
    if status == "ERRO":
        all_ok = False
    print(f"  {status}: '{text}'")

# Sample
idx = result.find('Aprendé')
if idx > 0:
    print(f"\nTexto hero: {result[idx:idx+50]}")

if all_ok:
    print("\n✓ Todos os textos corrigidos com sucesso!")
else:
    print("\n✗ Ainda há problemas")
