import sys
content = open('netlify_build/cronograma_tps.html', encoding='utf-8').read()
lines = content.splitlines()
for i, l in enumerate(lines):
    if 'tps-container' in l:
        start = max(0, i - 10)
        end = min(len(lines), i + 10)
        out = '\n'.join(f'{idx+1}: {lines[idx]}' for idx in range(start, end))
        sys.stdout.buffer.write(out.encode('utf-8'))
        break
