import streamlit as st
import os
from supabase import create_client, Client
from openai import OpenAI
import anthropic

# 🎨 Configuración Global de la Interfaz
st.set_page_config(page_title="ALUMED OS - Profe Joy", page_icon="👩\u200d🏫", layout="wide")

# 🗂️ MENÚ DE NAVEGACIÓN LATERAL (Sidebar)
with st.sidebar:
    st.markdown("### 🧠 ALUMED OS")
    pagina_seleccionada = st.radio(
        "Navegación del Ecosistema",
        ["💬 Chat con Profe Joy", "🚨 Pré-Parcial ALUMED (Zona de Rescate)"]
    )
    st.divider()
    st.markdown("*Tu GPS Universitario para Anatomía, Histología y Embriología en la UNLP.*")

# ==========================================
# 💬 PESTAÑA 1: CHAT CON PROFE JOY (Motor RAG)
# ==========================================
if pagina_seleccionada == "💬 Chat con Profe Joy":
    st.title("✨ IA Profe Joy - Tu Inteligencia Académica 24/7")
    
    # Manejo seguro de las conexiones a las APIs
    try:
        supabase: Client = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))
        client_openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        client_claude = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        apis_activas = True
    except Exception as e:
        apis_activas = False
        st.error("🚨 La IA Profe Joy está descansando. (Falta de créditos o claves API no configuradas).")

    # Memoria del chat
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []

    for msg in st.session_state.mensajes:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    pregunta_alumno = st.chat_input("Escribe tu duda médica aquí...")

    if pregunta_alumno and apis_activas:
        with st.chat_message("user"):
            st.markdown(pregunta_alumno)
        st.session_state.mensajes.append({"role": "user", "content": pregunta_alumno})

        with st.chat_message("assistant"):
            with st.spinner("Analizando la biblioteca ALUMED..."):
                try:
                    # RAG Pipeline (Protegido contra falta de créditos)
                    respuesta_embed = client_openai.embeddings.create(input=pregunta_alumno, model="text-embedding-3-small")
                    vector_pregunta = respuesta_embed.data.embedding

                    resultados_rag = supabase.rpc('match_documentos', {'query_embedding': vector_pregunta, 'match_threshold': 0.75, 'match_count': 3}).execute()
                    
                    contexto_medico = ""
                    enlaces_fuente = []
                    if resultados_rag.data:
                        for doc in resultados_rag.data:
                            contexto_medico += f"Extracto de {doc['titulo']}:\n{doc['conteudo']}\n\n"
                            enlaces_fuente.append(f"- **Fuente Oficial:** [{doc['titulo']}]({doc['url_wix']})")

                    prompt_sistema = f"Asumes el rol de IA Profe Joy de ALUMED OS. Responde ÚNICAMENTE usando este contexto:\n{contexto_medico}"

                    respuesta_claude = client_claude.messages.create(
                        model="claude-3-5-sonnet-20240620", max_tokens=1500, system=prompt_sistema,
                        messages=[{"role": "user", "content": pregunta_alumno}]
                    )
                    
                    respuesta_final = respuesta_claude.content.text
                    if enlaces_fuente:
                        respuesta_final += "\n\n---\n### 📚 Enlaces de Descarga\n" + "\n".join(list(set(enlaces_fuente)))
                        
                    st.markdown(respuesta_final)
                    st.session_state.mensajes.append({"role": "assistant", "content": respuesta_final})
                    
                except Exception as e:
                    st.error(f"⚠️ Hubo un error procesando tu consulta con la IA. Por favor verifica los créditos de las APIs. Detalle: {e}")

# ==========================================
# 🚨 PESTAÑA 2: PRÉ-PARCIAL ALUMED (Conversión)
# ==========================================
elif pagina_seleccionada == "🚨 Pré-Parcial ALUMED (Zona de Rescate)":
    st.markdown("## 🚨 PRÉ-PARCIAL ALUMED: Tu zona de rescate antes del parcial")
    st.markdown("*Primero entendé cómo explicamos. Después decidís hasta dónde querés llegar.*")
    st.divider()

    # 🎬 FASE 1: A Isca de Conteúdo
    st.markdown("### 🎬 Clases de Rescate Gratuitas")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.video(os.environ.get("URL_VIDEO_TEJIDO_NERVIOSO", "https://www.youtube.com/watch?v=dQw4w9WgXcQ")) 
        st.info("**Histología:** Tejido nervioso parte 1 y 2")
        
    with col2:
        st.video(os.environ.get("URL_VIDEO_MEMBRANA", "https://www.youtube.com/watch?v=dQw4w9WgXcQ"))
        st.info("**Biología:** Transporte de Membrana - Parte 1")

    with col3:
        st.video(os.environ.get("URL_VIDEO_EMBRIO", "https://www.youtube.com/watch?v=dQw4w9WgXcQ"))
        st.info("**Embriología:** Repaso Embrio - HYE 1er Parcial")

    st.divider()

    # 🎯 FASE 2: A Segmentação Cirúrgica (Venta Cruzada)
    st.markdown("### ⚡ Seguí preparando este parcial (Intensivos 4ta Fecha)")
    st.markdown("Elegí tu materia o cátedra. Nosotros tenemos el mapa exacto para vos.")

    tab_anato, tab_histo, tab_bio = st.tabs(["🦴 Anatomía", "🧫 Histo y Embrio", "🦠 Biología"])

    with tab_anato:
        st.markdown("#### ¿En qué cátedra cursás?")
        colA, colB, colC = st.columns(3)
        with colA:
            st.success("ANATOMÍA CÁTEDRA A | 2026")
            st.write("**$ 25.800,00**")
            st.link_button("Prepararme para Cátedra A", os.environ.get("LINK_CHECKOUT_CATEDRA_A", "#"), use_container_width=True)
        with colB:
            st.success("ANATOMÍA CÁTEDRA B 🧠")
            st.write("**$ 25.800,00**")
            st.link_button("Prepararme para Cátedra B", os.environ.get("LINK_CHECKOUT_CATEDRA_B", "#"), use_container_width=True)
        with colC:
            st.success("ANATOMÍA CÁTEDRA C")
            st.write("**$ 25.800,00**")
            st.link_button("Prepararme para Cátedra C", os.environ.get("LINK_CHECKOUT_CATEDRA_C", "#"), use_container_width=True)

    with tab_histo:
        st.info("HISTO Y EMBRIO - CURSO ANUAL 2026 🔬 UNLP")
        st.write("**$ 24.300,00**")
        st.link_button("Continuar mi preparación en Histo y Embrio", os.environ.get("LINK_CHECKOUT_HISTO", "#"), use_container_width=True)

    with tab_bio:
        st.info("BIOLOGIA - CURSO ANUAL 2026 🦠 UNLP")
        st.write("**$ 22.800,00**")
        st.link_button("Ver recorrido completo de Biología", os.environ.get("LINK_CHECKOUT_BIO", "#"), use_container_width=True)
