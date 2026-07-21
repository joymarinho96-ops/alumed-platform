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
    pasta_livros = 'biblioteca_alumed'
    
    if not os.path.exists(pasta_livros):
        print(f"Error: No se encontró la carpeta {pasta_livros}. Espera a que termine la descarga y extracción.")
        sys.exit(1)
        
    print("🧠 Iniciando la lectura y vectorización de la Biblioteca ALUMED (FAISS)...")
    
    all_docs = []
    
    archivos = [f for f in os.listdir(pasta_livros) if f.endswith('.pdf')]
    print(f"Encontrados {len(archivos)} libros PDF en la carpeta.")
    
    for nome_arquivo in archivos:
        pdf_path = os.path.join(pasta_livros, nome_arquivo)
        print(f"📖 Leyendo el libro: {nome_arquivo}...")
        try:
            loader = PyPDFLoader(pdf_path)
            docs = loader.load()
            all_docs.extend(docs)
        except Exception as e:
            print(f"🚨 Error al leer {nome_arquivo}: {e}")
            
    if not all_docs:
        print("Error: No se pudo cargar ningún texto de los libros.")
        sys.exit(1)
        
    print(f"   Se cargaron {len(all_docs)} páginas en total.")

    print("2. Dividiendo el texto en fragmentos (chunks)...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=300,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = text_splitter.split_documents(all_docs)
    print(f"   Se generaron {len(chunks)} fragmentos de conocimiento médico.")

    print("3. Generando Embeddings y guardando en FAISS (Vector DB Local)...")
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # Podría demorar dependiendo de la cantidad de libros
    vectorstore = FAISS.from_documents(chunks, embeddings)
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    save_path = os.path.join(current_dir, "streamlit_app", "vector_store", "biblioteca_index")
    
    os.makedirs(os.path.join(current_dir, "streamlit_app", "vector_store"), exist_ok=True)
    
    vectorstore.save_local(save_path)
    print(f"🎉 ¡Proceso completado! La Profe Joy ya sabe toda la carrera. El cerebro se guardó en: {save_path}")

if __name__ == "__main__":
    main()
