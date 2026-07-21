import os
import sys
from dotenv import load_dotenv

# Try importing required LangChain packages
try:
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_openai import OpenAIEmbeddings
    from langchain_community.vectorstores import FAISS
except ImportError as e:
    print(f"Error importing LangChain modules: {e}")
    print("Ensure you have installed: pip install langchain langchain-community langchain-openai pypdf faiss-cpu")
    sys.exit(1)

# Load env variables (for OPENAI_API_KEY)
load_dotenv()

def main():
    pdfs = [
        r"C:\Users\joyce\Downloads\Estatuto-de-la-UNLP (1).pdf",
        r"C:\Users\joyce\Downloads\ANEXO I.pdf",
        r"C:\Users\joyce\Downloads\RESOLUCIÓN Nº465 - 2018 - REGIMEN DE ENSEÑANZA Y PROMOCION (1).pdf"
    ]
    
    all_docs = []
    
    print("1. Cargando los documentos legales...")
    for pdf_path in pdfs:
        if not os.path.exists(pdf_path):
            print(f"Advertencia: No se encontró el archivo PDF en la ruta: {pdf_path}")
            continue
        print(f"   Cargando: {os.path.basename(pdf_path)}...")
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        all_docs.extend(docs)
        
    if not all_docs:
        print("Error: No se pudo cargar ningún documento.")
        sys.exit(1)
        
    print(f"   Se cargaron {len(all_docs)} páginas en total.")

    print("2. Dividiendo el texto en fragmentos (chunks)...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = text_splitter.split_documents(all_docs)
    print(f"   Se generaron {len(chunks)} fragmentos.")

    print("3. Generando Embeddings y guardando en FAISS (Vector DB)...")
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    vectorstore = FAISS.from_documents(chunks, embeddings)
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    save_path = os.path.join(current_dir, "vector_store", "estatuto_index")
    
    os.makedirs(os.path.join(current_dir, "vector_store"), exist_ok=True)
    
    vectorstore.save_local(save_path)
    print(f"¡Éxito! El índice vectorial unificado se guardó en: {save_path}")

if __name__ == "__main__":
    main()
