import streamlit as st
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env automaticamente
load_dotenv()

from supabase import create_client, Client
from openai import OpenAI
import anthropic

# 🎨 1. Configuração da Interfaz (ALUMED OS) - Deve ser chamado antes de qualquer elemento Streamlit
st.set_page_config(page_title="IA Profe Joy - ALUMED OS", page_icon="👩‍🏫", layout="centered")

# ⚙️ 2. Conexões ao Cérebro Central (Supabase, OpenAI y Claude)
url_supabase = os.environ.get("SUPABASE_URL")
key_supabase = os.environ.get("SUPABASE_KEY")
openai_key = os.environ.get("OPENAI_API_KEY")
anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

# Verifica chaves de segurança de forma elegante
if not url_supabase or not key_supabase or not openai_key or not anthropic_key:
    st.error("🚨 **Error de Configuración:** Por favor, asegúrate de configurar las variables de entorno `SUPABASE_URL`, `SUPABASE_KEY`, `OPENAI_API_KEY` y `ANTHROPIC_API_KEY` antes de ejecutar la aplicación.")
    st.info("💡 **Tip:** Puedes configurar estas variables en el panel de control de Railway/Vercel o localmente en tu terminal.")
    st.stop()

# Inicializa clientes de forma segura
supabase: Client = create_client(url_supabase, key_supabase)
client_openai = OpenAI(api_key=openai_key)
client_claude = anthropic.Anthropic(api_key=anthropic_key)

st.title("✨ IA Profe Joy - Tu Inteligencia Académica 24/7")
st.markdown("Tu GPS Universitario para Anatomía, Histología y Embriología en la UNLP.")

# Memoria del chat en Streamlit
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# Renderiza histórico de chat
for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 💬 3. Interceptando la pregunta del estudiante
pregunta_alumno = st.chat_input("Escribe tu duda médica aquí...")

if pregunta_alumno:
    # Mostrar la pregunta en pantalla
    with st.chat_message("user"):
        st.markdown(pregunta_alumno)
    st.session_state.mensajes.append({"role": "user", "content": pregunta_alumno})

    with st.chat_message("assistant"):
        with st.spinner("Analizando la biblioteca ALUMED..."):
            try:
                # 🧠 Fase A: Transformar la pregunta en vetor
                resposta_embed = client_openai.embeddings.create(
                    input=pregunta_alumno,
                    model="text-embedding-3-small"
                )
                vector_pregunta = resposta_embed.data.embedding

                # 🔎 Fase B: Búsqueda Semántica en Supabase (usando la función 'match_documentos' de pgvector)
                # O RPC de pgvector cruza a semântica e traz os trechos de manuais mais próximos
                resultados_rag = supabase.rpc(
                    'match_documentos', 
                    {'query_embedding': vector_pregunta, 'match_threshold': 0.3, 'match_count': 3}
                ).execute()

                contexto_medico = ""
                enlaces_fuente = []
                
                if resultados_rag.data:
                    for doc in resultados_rag.data:
                        contexto_medico += f"Extracto de {doc['titulo']} (Materia: {doc.get('materia', 'Medicina')}):\n{doc['conteudo']}\n\n"
                        if doc.get('url_wix'):
                            enlaces_fuente.append(f"- **Fuente Oficial:** [{doc['titulo']}]({doc['url_wix']})")

                # 🛡️ Fase C: Aislamiento de Contexto (Blindaje anti-alucinación)
                prompt_sistema = f"""
                Asumes el rol de IA Profe Joy, el motor definitivo de ALUMED OS.
                Sua missão não é apenas responder perguntas: você acompanha, ensina e ajuda estudantes do primeiro ano de Medicina da UNLP a compreender de verdade as matérias.
                
                PERSONALIDAD:
                - Habla en español, adaptado a la Facultad de Ciencias Médicas de la UNLP (español argentino).
                - Tu tono debe ser sumamente afectuoso, empático, motivador y lúdico ("GPS Universitario").
                - Puedes llamar al alumno: "corazón", "mis amores", "doc".
                - A veces finaliza frases con: "allright", "¿entendiste, sí o no?", "¿pudiste?", "estoy eh".
                
                REGLA CRÍTICA: Responde ÚNICAMENTE utilizando el siguiente contexto extraído de los libros de la biblioteca. 
                Si la respuesta no se encuentra en el contexto, responde: "Corazón, todavía no tengo PDFs cargados sobre este tema 😢, pero podemos trabajarlo juntos con lo que sé. Mientras tanto, pedile al administrador que suba el material para darte una explicación más completa."
                Luego, puedes complementar brevemente la explicación utilizando conocimiento científico general.
                
                CONTEXTO DE LA BIBLIOTECA ALUMED:
                {contexto_medico}
                """

                # ⚡ Fase D: Claude procesa y redacta
                respuesta_claude = client_claude.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=1500,
                    system=prompt_sistema,
                    messages=[{"role": "user", "content": pregunta_alumno}]
                )

                respuesta_final = respuesta_claude.content[0].text

                # 🔗 Fase E: Inyección cruzada y links de descarga
                if enlaces_fuente:
                    respuesta_final += "\n\n---\n### 📚 Enlaces de Descarga Directa\n"
                    respuesta_final += "\n".join(list(set(enlaces_fuente)))
                    
                    # Efecto Ecosistema: Venta cruzada o redirección al Microscopio/Anatomía 3D
                    respuesta_final += "\n\n💡 *Tip ALUMED: ¿Quieres consolidar este tema? Te recomiendo practicar la visualización interactiva en el Microscopio Virtual o blindar tu preparación en la pestaña PRÉ-PARCIAL ALUMED.*"
                else:
                    # Se não vieram links RAG, adiciona o aviso afetuoso e sugestões do ecossistema
                    if "todavía no tengo PDFs cargados" not in respuesta_final:
                        respuesta_final += "\n\n💡 *Tip ALUMED: Te recomiendo practicar la visualización interactiva en el Microscopio Virtual o repasar los atlas de anatomía 3D en la plataforma.*"

                # Renderizar en la UI
                st.markdown(respuesta_final)
                st.session_state.mensajes.append({"role": "assistant", "content": respuesta_final})
                
            except Exception as e:
                st.error(f"🚨 **Error durante el procesamiento:** {e}")
