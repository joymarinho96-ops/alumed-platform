import fitz  # PyMuPDF
import os

def extrair_imagens_pdf(caminho_pdf, pasta_destino="imagens_extraidas"):
  os.makedirs(pasta_destino, exist_ok=True)

  doc = fitz.open(caminho_pdf)
  contador = 0

  for numero_pagina, pagina in enumerate(doc):
    for indice_img, img in enumerate(pagina.get_images()):
      xref = img[0]
      imagem_base = doc.extract_image(xref)
      bytes_imagem = imagem_base["image"]
      extensao = imagem_base["ext"]

      nome_arquivo = f"{pasta_destino}/pagina_{numero_pagina + 1}_img_{indice_img + 1}.{extensao}"

      with open(nome_arquivo, "wb") as f:
        f.write(bytes_imagem)

      contador += 1

  print(
      f"Sucesso! {contador} imagens extraídas e salvas na pasta"
      f" '{pasta_destino}'."
  )

# Ajustamos las rutas para tu entorno:
pdf_path = r"C:\Users\joyce\Downloads\alumesitemdesenvolvimento-main\alumed-platform\static\atlas_histologico\PDFS_APUNTES\Atlas_of_Human_Histology_A_Guide_to_Micr.pdf"
dest_folder = r"C:\Users\joyce\Downloads\alumesitemdesenvolvimento-main\alumed-platform\static\atlas_histologico\MIS_IMAGENES\extracted"

extrair_imagens_pdf(pdf_path, dest_folder)
