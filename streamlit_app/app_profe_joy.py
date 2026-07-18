import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
import anthropic

# Lazy import de psycopg2 para evitar quebras de binários no Linux do Streamlit Cloud
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_PSYCOPG = True
except ImportError:
    HAS_PSYCOPG = False

# Import do Supabase SDK
try:
    from supabase import create_client, Client
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False

# Carrega as variáveis do arquivo .env ou Secrets automaticamente
load_dotenv()

# 🎨 1. Configuração da Interfaz (ALUMED OS) - Deve ser chamado antes de qualquer elemento Streamlit
st.set_page_config(page_title="Pré-Parcial ALUMED & Profe Joy", page_icon="👩‍🏫", layout="wide")

# ⚙️ 2. Conexões ao Cérebro Central e Configurações de Checkout
url_supabase = os.environ.get("SUPABASE_URL")
key_supabase = os.environ.get("SUPABASE_KEY")
database_url = os.environ.get("DATABASE_URL") or "postgresql://postgres:xaKXWitVrOXmyOVHRppFZPIRMmKTEegS@kodama.proxy.rlwy.net:23469/railway"
openai_key = os.environ.get("OPENAI_API_KEY")
anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

# Checkouts Wix y Videos del Pré-Parcial (lidos de variáveis de ambiente com fallbacks seguros)
checkout_catedra_a = os.environ.get("LINK_CHECKOUT_CATEDRA_A", "https://secretaria478.wixsite.com/conectafcm")
checkout_catedra_b = os.environ.get("LINK_CHECKOUT_CATEDRA_B", "https://secretaria478.wixsite.com/conectafcm")
checkout_catedra_c = os.environ.get("LINK_CHECKOUT_CATEDRA_C", "https://secretaria478.wixsite.com/conectafcm")
checkout_histo = os.environ.get("LINK_CHECKOUT_HISTO", "https://secretaria478.wixsite.com/conectafcm")
checkout_bio = os.environ.get("LINK_CHECKOUT_BIO", "https://secretaria478.wixsite.com/conectafcm")

video_nervioso = os.environ.get("URL_VIDEO_TEJIDO_NERVIOSO", "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
video_membrana = os.environ.get("URL_VIDEO_MEMBRANA", "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
video_embrio = os.environ.get("URL_VIDEO_EMBRIO", "https://www.youtube.com/watch?v=dQw4w9WgXcQ")

# 🍔 Sidebar de Navegação Superior-Lateral
st.sidebar.markdown("<div style='text-align: center; padding-bottom: 10px;'>", unsafe_allow_html=True)

# Tentativa de carregar a imagem do avatar de forma local
avatar_path = "static/img/profe_joy_avatar.jpg"
if os.path.exists(avatar_path):
    st.sidebar.image(avatar_path, width=120)
else:
    st.sidebar.markdown("<h1 style='font-size: 5rem; margin: 0;'>👩‍🏫</h1>", unsafe_allow_html=True)

st.sidebar.markdown("### **ALUMED OS**</div>", unsafe_allow_html=True)
st.sidebar.divider()

# Navegação entre abas
pagina = st.sidebar.radio(
    "Navegación del Estudiante:",
    ["💬 Chat con Profe Joy", "🚨 Pré-Parcial (Zona de Rescate)"]
)

st.sidebar.divider()
st.sidebar.info("💡 **Tip ALUMED:** Podés cambiar de pestaña en cualquier momento para estudiar gratis o blindar tu preparación para el parcial.")

# ==========================================
# 💬 PÁGINA A: CHAT CON PROFE JOY (RAG)
# ==========================================
if pagina == "💬 Chat con Profe Joy":
    # Restrições de chaves mínimas necessárias
    if not openai_key or not anthropic_key:
        st.error("🚨 **Error de Configuración:** Por favor, asegúrate de configurar `OPENAI_API_KEY` y `ANTHROPIC_API_KEY` en tus Secrets (Streamlit Cloud) o en tu arquivo `.env` local.")
        st.info("💡 **Tip:** Abre los Secrets de Streamlit Cloud y añade las variables de entorno.")
        st.stop()

    # Inicializa clientes de APIs
    client_openai = OpenAI(api_key=openai_key)
    client_claude = anthropic.Anthropic(api_key=anthropic_key)

    # Determina o modo de conexão ao banco de dados RAG de forma ultra-resiliente
    db_mode = None
    supabase_client = None

    if url_supabase and key_supabase and HAS_SUPABASE:
        try:
            supabase_client = create_client(url_supabase, key_supabase)
            db_mode = "supabase"
        except Exception as e:
            st.warning(f"⚠️ Erro ao inicializar Supabase SDK, tentando Postgres: {e}")

    if not db_mode and HAS_PSYCOPG:
        db_mode = "postgres"

    if not db_mode:
        st.error("🚨 **Error de Conectores:** No se pudo inicializar ningún conector de base de dados. "
                 "Instala `psycopg2-binary` para modo local o define `SUPABASE_URL` y `SUPABASE_KEY` para modo HTTP nube.")
        st.stop()

    def buscar_documentos(vector_pregunta, match_threshold=0.3, match_count=3):
        """Busca fragmentos relevantes de forma híbrida no Supabase (HTTP) ou Postgres (SQL)."""
        if db_mode == "supabase":
            try:
                resposta = supabase_client.rpc('match_documentos', {
                    'query_embedding': vector_pregunta,
                    'match_threshold': match_threshold,
                    'match_count': match_count
                }).execute()
                return resposta.data
            except Exception as e:
                st.error(f"🚨 **Error en consulta RAG Supabase:** {e}")
                return []
        elif db_mode == "postgres":
            try:
                conn = psycopg2.connect(database_url)
                cur = conn.cursor(cursor_factory=RealDictCursor)
                cur.execute("""
                    SELECT id, titulo, conteudo, materia, url_wix, similarity
                    FROM match_documentos(%s::vector, %s, %s);
                """, (vector_pregunta, match_threshold, match_count))
                rows = cur.fetchall()
                cur.close()
                conn.close()
                return rows
            except Exception as e:
                st.error(f"🚨 **Error en consulta RAG Postgres:** {e}")
                return []
        return []

    st.title("✨ IA Profe Joy - Tu Inteligencia Académica 24/7")
    st.markdown("Tu GPS Universitario para Anatomía, Histología y Embriología en la UNLP.")

    # Memoria del chat en Streamlit
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []

    # Renderiza histórico de chat
    for msg in st.session_state.mensajes:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 💬 Interceptando la pregunta del estudante
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

                    # 🔎 Fase B: Búsqueda Semántica Híbrida
                    resultados_rag = buscar_documentos(
                        vector_pregunta, 
                        match_threshold=0.3, 
                        match_count=3
                    )

                    contexto_medico = ""
                    enlaces_fuente = []
                    
                    if resultados_rag:
                        for doc in resultados_rag:
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
                    
                    REGLA CRÍTICA: Responde ÚNICAMENTE utilizando el contexto de la biblioteca. 
                    Si la resposta no se encuentra en el contexto, responde exactamente: "Corazón, todavía no tengo PDFs cargados sobre este tema 😢, pero podemos trabajarlo juntos con lo que sé. Mientras tanto, pedile al administrador que suba el material para darte una explicación más completa."
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
                        
                        # Efecto Ecosistema: Venta cruzada
                        respuesta_final += "\n\n💡 *Tip ALUMED: ¿Quieres consolidar este tema? Te recomiendo practicar la visualización interactiva en el Microscopio Virtual o blindar tu preparación en la pestaña PRÉ-PARCIAL ALUMED.*"
                    else:
                        if "todavía no tengo PDFs cargados" not in respuesta_final:
                            respuesta_final += "\n\n💡 *Tip ALUMED: Te recomiendo practicar la visualización interactiva en el Microscopio Virtual o repasar los atlas de anatomía 3D en la plataforma.*"

                    # Renderizar en la UI
                    st.markdown(respuesta_final)
                    st.session_state.mensajes.append({"role": "assistant", "content": respuesta_final})
                    
                except Exception as e:
                    st.error(f"🚨 **Error durante el procesamiento:** {e}")

# ==========================================
# 🚨 PÁGINA B: PRÉ-PARCIAL ALUMED
# ==========================================
elif pagina == "🚨 Pré-Parcial (Zona de Rescate)":
    # 🛡️ CABEÇALHO: O Porto Seguro
    st.markdown("<div style='background-color: #3b1111; padding: 20px; border-radius: 12px; border-left: 6px solid #ef4444; margin-bottom: 20px;'>", unsafe_allow_html=True)
    st.markdown("## 🚨 PRÉ-PARCIAL ALUMED: Tu zona de rescate antes del parcial")
    st.markdown("*Primero entendé cómo explicamos. Después decidís hasta dónde querés llegar.*")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.divider()

    # 🎣 FASE 1: A Isca de Conteúdo (Aulas Gratuitas)
    st.markdown("### 🎬 Clases de Rescate Gratuitas")
    st.markdown("Probá la calidad. Sentí la diferencia.")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.video(video_nervioso)
        st.info("**Histología:** Tejido nervioso parte 1 y 2")
        
    with col2:
        st.video(video_membrana)
        st.info("**Biología:** Transporte de Membrana - Parte 1")

    with col3:
        st.video(video_embrio)
        st.info("**Embriología:** Repaso Embrio - HYE 1er Parcial")

    st.divider()

    # 🎯 FASE 2: A Segmentação Cirúrgica (O Xeque-Mate da Venda)
    st.markdown("### ⚡ Seguí preparando este parcial (Intensivos 4ta Fecha)")
    st.markdown("Elegí tu materia o cátedra. Nosotros tenemos el mapa exacto para vos.")

    # Usando abas para organizar por matéria
    tab_anato, tab_histo, tab_bio = st.tabs(["🦴 Anatomía", "🧫 Histo y Embrio", "🦠 Biología"])

    with tab_anato:
        st.markdown("#### ¿En qué cátedra cursás?")
        colA, colB, colC = st.columns(3)
        
        with colA:
            st.markdown("<div style='background-color: #1e113b; padding: 15px; border-radius: 10px; border: 1px solid #7c3aed; text-align: center;'>", unsafe_allow_html=True)
            st.success("ANATOMÍA CÁTEDRA A | 2026")
            st.write("Curso anual + repasos + simulacros específicos")
            st.write("**$ 25.800,00**")
            st.markdown(f"<a href='{checkout_catedra_a}' target='_blank'><button style='width:100%; padding:10px; background-color:#eab308; color:black; border:none; border-radius:6px; font-weight:bold; cursor:pointer;'>Prepararme para Cátedra A</button></a>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
                
        with colB:
            st.markdown("<div style='background-color: #1e113b; padding: 15px; border-radius: 10px; border: 1px solid #7c3aed; text-align: center;'>", unsafe_allow_html=True)
            st.success("ANATOMÍA CÁTEDRA B 🧠 CURSO ANUAL 2026")
            st.write("Curso anual + repasos + simulacros específicos")
            st.write("**$ 25.800,00**")
            st.markdown(f"<a href='{checkout_catedra_b}' target='_blank'><button style='width:100%; padding:10px; background-color:#eab308; color:black; border:none; border-radius:6px; font-weight:bold; cursor:pointer;'>Prepararme para Cátedra B</button></a>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
                
        with colC:
            st.markdown("<div style='background-color: #1e113b; padding: 15px; border-radius: 10px; border: 1px solid #7c3aed; text-align: center;'>", unsafe_allow_html=True)
            st.success("ANATOMÍA CÁTEDRA C")
            st.write("Curso anual + repasos + simulacros específicos")
            st.write("**$ 25.800,00**")
            st.markdown(f"<a href='{checkout_catedra_c}' target='_blank'><button style='width:100%; padding:10px; background-color:#eab308; color:black; border:none; border-radius:6px; font-weight:bold; cursor:pointer;'>Prepararme para Cátedra C</button></a>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    with tab_histo:
        st.markdown("<div style='background-color: #1e113b; padding: 25px; border-radius: 12px; border: 1px solid #7c3aed;'>", unsafe_allow_html=True)
        st.info("HISTO Y EMBRIO - CURSO ANUAL 2026 🔬 UNLP | 1ER PARCIAL")
        st.write("Acceso de emergencia por 100 días con clases teóricas, repasos y simulacros.")
        st.write("**$ 24.300,00**")
        st.markdown(f"<a href='{checkout_histo}' target='_blank'><button style='width:100%; padding:12px; background-color:#eab308; color:black; border:none; border-radius:6px; font-weight:bold; cursor:pointer;'>Continuar mi preparación en Histo y Embrio</button></a>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_bio:
        st.markdown("<div style='background-color: #1e113b; padding: 25px; border-radius: 12px; border: 1px solid #7c3aed;'>", unsafe_allow_html=True)
        st.info("BIOLOGIA - CURSO ANUAL 2026 🦠 UNLP | 1ER PARCIAL")
        st.write("Clases teóricas, repasos y simulacros.")
        st.write("**$ 22.800,00**")
        st.markdown(f"<a href='{checkout_bio}' target='_blank'><button style='width:100%; padding:12px; background-color:#eab308; color:black; border:none; border-radius:6px; font-weight:bold; cursor:pointer;'>Ver recorrido completo de Biología</button></a>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
