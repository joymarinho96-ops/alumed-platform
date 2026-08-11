import fitz  # PyMuPDF
from deep_translator import GoogleTranslator
import os

pdf_path = r"C:\Users\joyce\Downloads\alumesitemdesenvolvimento-main\alumed-platform\static\atlas_histologico\PDFS_APUNTES\Atlas_of_Human_Histology_A_Guide_to_Micr.pdf"
output_dir = r"C:\Users\joyce\Downloads\alumesitemdesenvolvimento-main\alumed-platform\static\atlas_histologico\MIS_IMAGENES\extracted"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def test_extraction(page_num=10):
    print(f"--- Procesando página {page_num} ---")
    doc = fitz.open(pdf_path)
    
    if page_num >= len(doc):
        print("Página fuera de rango.")
        return
        
    page = doc.load_page(page_num)
    
    # 1. Extraer texto original
    text = page.get_text("text").strip()
    if not text:
        print("No se encontró texto en esta página.")
    else:
        print("\n[TEXTO ORIGINAL INGLÉS] (Primeros 300 caracteres):")
        print(text[:300] + "...")
        
        # 2. Traducir al español
        try:
            translator = GoogleTranslator(source='en', target='es')
            translated = translator.translate(text[:500]) # Traducimos una muestra
            print("\n[TRADUCCIÓN ESPAÑOL] (Muestra):")
            print(translated)
        except Exception as e:
            print(f"Error al traducir: {e}")

    # 3. Extraer imágenes
    image_list = page.get_images(full=True)
    if image_list:
        print(f"\n[IMÁGENES] Se encontraron {len(image_list)} imágenes en esta página.")
        for image_index, img in enumerate(image_list, start=1):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_name = f"page_{page_num}_img_{image_index}.{image_ext}"
            image_path = os.path.join(output_dir, image_name)
            
            with open(image_path, "wb") as image_file:
                image_file.write(image_bytes)
            print(f" - Imagen guardada: {image_name}")
    else:
        print("\n[IMÁGENES] No se encontraron imágenes en esta página.")

if __name__ == '__main__':
    # Vamos a probar con la página 15 como muestra (suele haber contenido)
    test_extraction(15)
