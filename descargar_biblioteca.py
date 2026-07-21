import os
import zipfile
import subprocess
import sys

# Install gdown if not present
try:
    import gdown
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "gdown"])
    import gdown

FILE_ID = '10vHqHw3PbgQulON87sLXaWzh4qIgzVr5'
URL = f'https://drive.google.com/uc?id={FILE_ID}'
OUTPUT_ZIP = 'biblioteca.zip'
EXTRACT_DIR = 'biblioteca_alumed'

def main():
    print("Iniciando descarga desde Google Drive...")
    gdown.download(URL, OUTPUT_ZIP, quiet=False)
    
    print(f"\nDescarga completada. Descomprimiendo en '{EXTRACT_DIR}'...")
    os.makedirs(EXTRACT_DIR, exist_ok=True)
    
    try:
        with zipfile.ZipFile(OUTPUT_ZIP, 'r') as zip_ref:
            zip_ref.extractall(EXTRACT_DIR)
        print("¡Descompresión exitosa!")
        
        # Limpiar el zip
        os.remove(OUTPUT_ZIP)
        print("Archivo .zip eliminado para ahorrar espacio.")
    except Exception as e:
        print(f"Error al descomprimir: {e}")

if __name__ == '__main__':
    main()
