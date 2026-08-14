import json
import requests

with open('laminas_banco_dados.json') as f:
    laminas = json.load(f)

for i in range(1, 3):
    url = laminas[i]['url']
    base = url.rsplit('/', 1)[0]
    img_url = f'{base}/imgs/slide.png'
    
    r = requests.get(img_url, headers={'User-Agent': 'Mozilla/5.0'})
    print(f'Lamina {i}:')
    print(f'  Status: {r.status_code}')
    print(f'  Type: {r.headers.get("content-type")}')
    print(f'  Size: {len(r.content)}')
    print(f'  URL: {img_url}')
    print()
