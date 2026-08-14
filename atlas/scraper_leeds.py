import requests
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urljoin
import time

# Create folder for images if it doesn't exist
os.makedirs('imagens_laminas', exist_ok=True)

base_url = "https://www.histology.leeds.ac.uk"

# TODAS as páginas com slides detalhadas
pages_to_scrape = [
    # DIGESTIVO
    ("/digestive/stomach.php", "Estômago"),
    ("/digestive/cardiac_pyloric.php", "Cardíaco/Pilórico"),
    ("/digestive/small_intestine.php", "Intestino Delgado"),
    ("/digestive/small_intestine_detail.php", "Int. Delgado Detalhe"),
    ("/digestive/large_intestine.php", "Intestino Grosso"),
    ("/digestive/liver.php", "Fígado"),
    ("/digestive/liver_hepatocyte.php", "Hepatócitos"),
    ("/digestive/pancreas.php", "Pâncreas"),
    ("/digestive/gallbladder.php", "Vesícula Biliar"),
    ("/digestive/appendix.php", "Apêndice"),
    
    # SANGUE
    ("/blood/index.php", "Sangue"),
    ("/blood/erythrocytes.php", "Eritrócitos"),
    ("/blood/white_cells.php", "Células Brancas"),
    ("/blood/platelets.php", "Plaquetas"),
    
    # PELE
    ("/skin/index.php", "Pele"),
    ("/skin/epidermis.php", "Epiderme"),
    ("/skin/dermis.php", "Derme"),
    ("/skin/hair.php", "Cabelo"),
    ("/skin/sweat_glands.php", "Glândulas Sudoríparas"),
    
    # OSSO
    ("/bone/index.php", "Osso"),
    ("/bone/compact_bone.php", "Osso Compacto"),
    ("/bone/spongy_bone.php", "Osso Esponjoso"),
    
    # CIRCULATÓRIO
    ("/circulatory/index.php", "Sistema Circulatório"),
    ("/circulatory/arteries.php", "Artérias"),
    ("/circulatory/veins.php", "Veias"),
    ("/circulatory/capillaries.php", "Capilares"),
    
    # RESPIRATORY
    ("/respiratory/index.php", "Sistema Respiratório"),
    ("/respiratory/trachea.php", "Traqueia"),
    ("/respiratory/lungs.php", "Pulmões"),
    
    # REPRODUTOR
    ("/female/index.php", "Sistema Reprodutor Feminino"),
    ("/male/index.php", "Sistema Reprodutor Masculino"),
]

laminas_data = []
image_count = 0

def download_image(img_url, title, topic_name):
    """Download and save a single image"""
    global image_count
    try:
        img_response = requests.get(img_url, timeout=15)
        
        if img_response.status_code == 200 and len(img_response.content) > 3000:  # At least 3KB
            image_count += 1
            
            # Determine file extension
            if '.jpg' in img_url.lower():
                file_extension = '.jpg'
            elif '.jpeg' in img_url.lower():
                file_extension = '.jpg'
            elif '.png' in img_url.lower():
                file_extension = '.png'
            elif '.gif' in img_url.lower():
                file_extension = '.png'
            else:
                file_extension = '.jpg'
            
            filename = f"lamina_leeds_{image_count:03d}{file_extension}"
            filepath = os.path.join('imagens_laminas', filename)
            
            with open(filepath, 'wb') as f:
                f.write(img_response.content)
            
            print(f"    ✅ {filename} ({len(img_response.content)//1024}KB) - {title[:40]}")
            
            laminas_data.append({
                "id": image_count,
                "titulo": title[:100],
                "topico": topic_name,
                "url_original": img_url,
                "arquivo_local": filename,
                "tamanho_bytes": len(img_response.content)
            })
            return True
    except Exception as e:
        pass
    return False

def scrape_page(page_path, topic_name):
    """Scrape a specific Leeds histology page"""
    url = base_url + page_path
    try:
        response = requests.get(url, timeout=15)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all img tags
        images = soup.find_all('img', src=True)
        
        found_count = 0
        for img in images:
            img_src = img.get('src')
            img_alt = img.get('alt', 'Sem descrição')
            
            # Skip navigation/decoration images
            if any(skip in img_src.lower() for skip in ['logo', 'icon', 'button', 'nav', 'bullet', 'pdf']):
                continue
            
            # Look for actual image files
            if any(ext in img_src.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                img_url = urljoin(base_url, img_src)
                if download_image(img_url, img_alt, topic_name):
                    found_count += 1
        
        if found_count > 0:
            print(f"  🔍 {topic_name:30} → {found_count} imagens baixadas")
        else:
            print(f"  ⚠️  {topic_name:30} → nenhuma imagem encontrada")
        
        time.sleep(0.5)  # Gentle rate limiting
        
    except requests.exceptions.ConnectionError:
        print(f"  ❌ {topic_name:30} → Erro de conexão")
    except Exception as e:
        print(f"  ❌ {topic_name:30} → {str(e)[:30]}")

# Main scraping
print("\n" + "=" * 80)
print("🔬 SCRAPER UNIVERSITY OF LEEDS HISTOLOGY - SUPER MODO")
print("=" * 80)
print(f"\n📍 Raspando {len(pages_to_scrape)} páginas do site...\n")

for page_path, topic_name in pages_to_scrape:
    scrape_page(page_path, topic_name)

# Save metadata
with open('laminas_leeds_banco.json', 'w', encoding='utf-8') as f:
    json.dump(laminas_data, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 80)
print(f"✅ SCRAPING CONCLUÍDO!")
print(f"📊 Total de lâminas baixadas: {image_count}")
print(f"💾 Dados salvos em: laminas_leeds_banco.json")
print(f"📁 Imagens em: imagens_laminas/")
print("=" * 80 + "\n")
