import json
import requests
from PIL import Image
from io import BytesIO
import os

with open('laminas_banco_dados.json', 'r', encoding='utf-8') as f:
    laminas = json.load(f)

if not os.path.exists('imagens_laminas'):
    os.makedirs('imagens_laminas')

headers = {'User-Agent': 'Mozilla/5.0'}

for i, lamina in enumerate(laminas):
    nome_arquivo = f'lamina_{i}.jpg'
    caminho_final = os.path.join('imagens_laminas', nome_arquivo)
    
    url_origem = lamina.get('url', '')
    base_url = url_origem.rsplit('/', 1)[0]
    url_imagem = f'{base_url}/imgs/slide.png'
    
    print(f'Lamina {i+1}: {lamina.get("titulo", "Sem titulo")}')
    print(f'URL: {url_imagem}')
    
    try:
        response = requests.get(url_imagem, headers=headers, timeout=15)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            if img.mode in ('RGBA', 'P', 'LA'):
                bg = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                bg.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = bg
            img.save(caminho_final, 'JPEG', quality=95)
            print(f'OK - Salva em imagens_laminas/{nome_arquivo}\n')
        else:
            print(f'ERRO {response.status_code}\n')
    except Exception as e:
        print(f'ERRO: {e}\n')

print('PRONTO! Laminas baixadas!')
