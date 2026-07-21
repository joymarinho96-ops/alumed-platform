import os
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()
os.environ["DATABASE_URL"] = "postgresql://postgres:xaKXWitVrOXmyOVHRppFZPIRMmKTEegS@kodama.proxy.rlwy.net:23469/railway"

import vetorizador_alumed

if __name__ == "__main__":
    print("Iniciando script RAG ALUMED...")
    vetorizador_alumed.injeção_de_conhecimento("apuntes_alumed.json")
    print("Processo finalizado!")
