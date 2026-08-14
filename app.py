import streamlit as st
from datetime import date
import urllib.request
import xml.etree.ElementTree as ET
import html as html_lib

st.set_page_config(
    page_title="CONECTA FCM — Portal Dourado",
    page_icon="⚜️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── RSS SCRAPER ─────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_rss():
    try:
        req = urllib.request.Request(
            "https://www.med.unlp.edu.ar/index.php?format=feed&type=rss",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=8) as r:
            raw = r.read()
        root = ET.fromstring(raw)
        out = []
        for it in root.findall(".//item"):
            title = it.findtext("title","").strip()
            link  = it.findtext("link","").strip()
            desc  = html_lib.unescape(it.findtext("description","").strip())
            desc  = ET.fromstring(f"<x>{desc}</x>").text or desc if "<" in desc else desc
            pub   = it.findtext("pubDate","")[:16].strip()
            out.append({"t":title,"l":link,"d":desc,"f":pub})
        return out, True
    except:
        return [], False

NEWS_LIVE, LIVE_OK = fetch_rss()
NEWS_FALLBACK = [
    {"t":"La Facultad fue sede de una jornada regional sobre procuración y trasplante","l":"https://www.med.unlp.edu.ar","d":"Profesionales de CABA y Buenos Aires participaron de la Jornada del INCUCAI en nuestra Facultad.","f":"17 Jul 2026"},
    {"t":"El Taller de Parkinson abre convocatoria a nuevos participantes","l":"https://www.med.unlp.edu.ar","d":"Espacio gratuito de educación física para personas con Parkinson y profesionales de la salud.","f":"16 Jul 2026"},
    {"t":"Curso de Soporte Vital Avanzado para estudiantes de los últimos años","l":"https://www.med.unlp.edu.ar","d":"Inscripción abierta al curso impulsado por el Hospital de Simulación Clínica (HoSiC).","f":"Jul 2026"},
    {"t":"33° Jornadas Jóvenes Investigadores AUGM — Porto Alegre, Brasil","l":"https://www.med.unlp.edu.ar","d":"Convocatoria abierta para participar en la UFRGS los días 20, 21 y 22 de octubre de 2026.","f":"Jul 2026"},
    {"t":"Prórroga documentación secundaria — vence 31 de agosto","l":"https://www.med.unlp.edu.ar","d":"Nuevo plazo para presentar certificados de no adeudar materias del nivel secundario.","f":"01 Ago 2026"},
]
NEWS = NEWS_LIVE if LIVE_OK else NEWS_FALLBACK

# ── MEGA CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;900&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800;900&display=swap');

*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html,body,[class*="css"]{font-family:'Plus Jakarta Sans',sans-serif!important;}

/* ── FUNDO PREMIUM ── */
.stApp{
  background:
    radial-gradient(ellipse 90% 60% at 10% 0%, rgba(0,60,110,0.55) 0%, transparent 55%),
    radial-gradient(ellipse 70% 50% at 90% 30%, rgba(0,90,70,0.35) 0%, transparent 50%),
    radial-gradient(ellipse 60% 80% at 50% 100%, rgba(0,40,90,0.4) 0%, transparent 60%),
    linear-gradient(160deg, #040d1a 0%, #060f16 50%, #030c18 100%)!important;
  min-height:100vh;
}
.main .block-container{padding:0!important;max-width:100%!important;}

/* ── SIDEBAR ── */
[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#040e1c 0%,#050d18 100%)!important;
  border-right:1px solid rgba(249,168,37,0.2)!important;
}
[data-testid="stSidebar"]>div:first-child{padding-top:0!important;}
[data-testid="stSidebar"] *{color:#cbd5e1!important;}
[data-testid="stSidebar"] .stRadio label{
  padding:10px 16px!important;border-radius:10px!important;
  font-size:0.87rem!important;font-weight:600!important;
  color:rgba(203,213,225,0.8)!important;cursor:pointer!important;
  transition:all 0.2s!important;border:1px solid transparent!important;
  display:flex!important;align-items:center!important;
}
[data-testid="stSidebar"] .stRadio label:hover{
  background:rgba(249,168,37,0.1)!important;
  color:#f9a825!important;border-color:rgba(249,168,37,0.2)!important;
}

/* ── TICKER ── */
.ticker-wrap{
  background:linear-gradient(90deg,#0d47a1,#01579b);
  border-bottom:2px solid #f9a825;
  overflow:hidden;
  display:flex;align-items:center;
}
.ticker-label{
  background:#f9a825;color:#040d1a;
  font-size:0.63rem;font-weight:900;padding:9px 14px;
  text-transform:uppercase;letter-spacing:0.1em;
  white-space:nowrap;flex-shrink:0;
}
.ticker-track{overflow:hidden;flex:1;}
.ticker-inner{
  display:inline-block;white-space:nowrap;
  animation:ticker 65s linear infinite;
  padding:9px 0;
}
.ticker-inner:hover{animation-play-state:paused;}
@keyframes ticker{from{transform:translateX(100vw);}to{transform:translateX(-100%);}}
.t-item{display:inline-block;margin-right:70px;font-size:0.79rem;color:#90caf9;}
.t-item strong{color:#e3f2fd;font-weight:700;margin-right:7px;}
.t-dot{color:#f9a825;margin-right:70px;}

/* ── HEADER ── */
.hdr{
  background:linear-gradient(135deg,rgba(4,16,40,0.97),rgba(6,20,50,0.95));
  border-bottom:1px solid rgba(249,168,37,0.25);
  backdrop-filter:blur(20px);
}
.hdr-inner{display:flex;align-items:center;justify-content:space-between;padding:14px 28px;}

.logo-orb{
  width:52px;height:52px;
  background:linear-gradient(135deg,rgba(249,168,37,0.18),rgba(21,101,192,0.25));
  border:1.5px solid rgba(249,168,37,0.35);
  border-radius:14px;
  display:flex;align-items:center;justify-content:center;
  font-size:1.55rem;flex-shrink:0;
}

.hdr-name{font-size:0.85rem;font-weight:800;color:#e3f2fd;text-transform:uppercase;letter-spacing:0.07em;line-height:1.2;}
.hdr-sub{font-size:0.63rem;color:rgba(179,229,252,0.55);margin-top:3px;letter-spacing:0.04em;}

.hdr-sep{width:1px;height:46px;background:rgba(249,168,37,0.2);margin:0 18px;}

.badge-conecta{
  background:linear-gradient(135deg,#f9a825,#f57f17);
  color:#040d1a;font-family:'Cinzel',serif;
  font-size:0.85rem;font-weight:800;
  padding:9px 22px;border-radius:10px;
  letter-spacing:0.08em;
  box-shadow:0 0 24px rgba(249,168,37,0.35),0 4px 14px rgba(0,0,0,0.4);
}

/* ── NAVBAR ── */
.nav{
  background:rgba(5,15,35,0.92);
  border-bottom:2px solid rgba(249,168,37,0.25);
  padding:0 28px;
  display:flex;gap:2px;overflow-x:auto;
  backdrop-filter:blur(10px);
}
.nav-i{
  padding:11px 16px;font-size:0.78rem;font-weight:700;
  color:rgba(179,229,252,0.65);white-space:nowrap;
  border-bottom:2px solid transparent;margin-bottom:-2px;
  transition:all 0.18s;letter-spacing:0.02em;cursor:default;
}
.nav-i:hover{color:#f9a825;border-bottom-color:#f9a825;background:rgba(249,168,37,0.06);}

/* ── GLASS CARDS ── */
.glass{
  background:rgba(255,255,255,0.04);
  border:1px solid rgba(255,255,255,0.09);
  border-radius:16px;
  backdrop-filter:blur(16px);
  padding:20px 22px;
  margin-bottom:14px;
  transition:all 0.25s;
  box-shadow:0 4px 20px rgba(0,0,0,0.35);
  position:relative;overflow:hidden;
}
.glass::before{
  content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(249,168,37,0.3),transparent);
}
.glass:hover{
  background:rgba(255,255,255,0.07);
  border-color:rgba(249,168,37,0.22);
  transform:translateY(-2px);
  box-shadow:0 8px 32px rgba(0,0,0,0.45);
}

.glass-blue{
  background:rgba(21,101,192,0.12);
  border:1px solid rgba(21,101,192,0.25);
  border-radius:16px;
  padding:20px 22px;margin-bottom:14px;
  box-shadow:0 4px 20px rgba(0,0,0,0.3);
  position:relative;overflow:hidden;
}
.glass-blue::before{content:'';position:absolute;top:0;left:0;width:4px;height:100%;background:linear-gradient(to bottom,#1565c0,#42a5f5);}

.glass-gold{
  background:rgba(249,168,37,0.08);
  border:1px solid rgba(249,168,37,0.22);
  border-radius:16px;
  padding:20px 22px;margin-bottom:14px;
  box-shadow:0 4px 20px rgba(0,0,0,0.3);
  position:relative;overflow:hidden;
}
.glass-gold::before{content:'';position:absolute;top:0;left:0;width:4px;height:100%;background:linear-gradient(to bottom,#f9a825,#f57f17);}

.glass-red{
  background:rgba(198,40,40,0.1);
  border:1px solid rgba(198,40,40,0.25);
  border-radius:16px;
  padding:20px 22px;margin-bottom:14px;
  box-shadow:0 4px 20px rgba(0,0,0,0.3);
  position:relative;overflow:hidden;
}
.glass-red::before{content:'';position:absolute;top:0;left:0;width:4px;height:100%;background:linear-gradient(to bottom,#c62828,#ef5350);}

/* ── BADGES ── */
.bd{display:inline-block;padding:3px 9px;border-radius:5px;font-size:0.62rem;font-weight:800;text-transform:uppercase;letter-spacing:0.07em;margin-right:5px;margin-bottom:4px;}
.bd-b{background:rgba(21,101,192,0.25);color:#90caf9;border:1px solid rgba(21,101,192,0.4);}
.bd-g{background:rgba(249,168,37,0.18);color:#ffd54f;border:1px solid rgba(249,168,37,0.35);}
.bd-r{background:rgba(198,40,40,0.2);color:#ef9a9a;border:1px solid rgba(198,40,40,0.35);}
.bd-gr{background:rgba(46,125,50,0.2);color:#a5d6a7;border:1px solid rgba(46,125,50,0.35);}
.bd-t{background:rgba(0,137,123,0.2);color:#80cbc4;border:1px solid rgba(0,137,123,0.35);}

/* ── SEC HEADER ── */
.sec{border-left:3px solid #f9a825;padding-left:16px;margin-bottom:22px;}
.sec .ey{font-size:0.65rem;font-weight:800;text-transform:uppercase;letter-spacing:0.2em;color:#f9a825;}
.sec h2{font-size:1.5rem;font-weight:800;color:#e3f2fd;margin:3px 0 4px;line-height:1.2;}
.sec p{font-size:0.83rem;color:rgba(179,229,252,0.55);margin:0;}

/* ── STATS ── */
.stat{
  background:rgba(255,255,255,0.04);
  border:1px solid rgba(255,255,255,0.08);
  border-radius:14px;padding:18px;text-align:center;
  backdrop-filter:blur(10px);transition:all 0.2s;
}
.stat:hover{background:rgba(255,255,255,0.07);transform:translateY(-2px);}
.stat.b{border-top:2px solid #1565c0;}
.stat.g{border-top:2px solid #f9a825;}
.stat-n{font-family:'Cinzel',serif;font-size:1.9rem;font-weight:900;color:#90caf9;line-height:1;}
.stat-n.g{color:#ffd54f;}
.stat-l{font-size:0.68rem;color:rgba(179,229,252,0.5);font-weight:700;text-transform:uppercase;letter-spacing:0.06em;margin-top:5px;}

/* ── TABLE ── */
.tbl{width:100%;border-collapse:collapse;border-radius:14px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.4);}
.tbl th{background:rgba(21,101,192,0.6);color:#e3f2fd;padding:12px 14px;font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.07em;text-align:left;}
.tbl td{padding:11px 14px;font-size:0.84rem;color:#cbd5e1;border-bottom:1px solid rgba(255,255,255,0.06);background:rgba(255,255,255,0.03);}
.tbl tr:hover td{background:rgba(21,101,192,0.1);}

/* ── LINK CARD ── */
.lk{
  display:flex;align-items:center;gap:14px;
  background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
  border-radius:14px;padding:14px 18px;margin-bottom:10px;
  text-decoration:none!important;transition:all 0.2s;
  backdrop-filter:blur(10px);
}
.lk:hover{background:rgba(21,101,192,0.15);border-color:rgba(21,101,192,0.4);transform:translateX(4px);}
.lk-ico{width:44px;height:44px;background:rgba(21,101,192,0.2);border:1px solid rgba(21,101,192,0.35);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.3rem;flex-shrink:0;}

/* ── CHAT ── */
.c-bot{background:rgba(21,101,192,0.15);border:1px solid rgba(21,101,192,0.3);border-radius:14px 14px 14px 4px;padding:13px 17px;margin:7px 0;font-size:0.87rem;color:#e3f2fd;line-height:1.6;max-width:80%;}
.c-usr{background:linear-gradient(135deg,#1565c0,#0d47a1);border-radius:14px 14px 4px 14px;padding:11px 17px;margin:7px 0 7px auto;font-size:0.87rem;color:#fff;font-weight:500;max-width:70%;text-align:right;}

/* ── HERO ── */
.hero{
  background:linear-gradient(135deg,rgba(13,71,161,0.7) 0%,rgba(1,87,155,0.5) 50%,rgba(0,105,92,0.3) 100%);
  border:1px solid rgba(249,168,37,0.18);
  border-radius:18px;padding:38px 34px;margin-bottom:26px;
  position:relative;overflow:hidden;
  backdrop-filter:blur(14px);
  box-shadow:0 8px 40px rgba(0,0,0,0.5),0 0 60px rgba(13,71,161,0.15);
}
.hero::before{
  content:'';position:absolute;top:-80px;right:-80px;
  width:300px;height:300px;border-radius:50%;
  background:radial-gradient(circle,rgba(249,168,37,0.08) 0%,transparent 70%);
}
.hero::after{
  content:'🏛️';position:absolute;right:36px;top:50%;
  transform:translateY(-50%);font-size:8rem;opacity:0.05;
}

/* ── AUTH ROW ── */
.ar{display:flex;align-items:center;padding:13px 18px;background:rgba(255,255,255,0.03);border-bottom:1px solid rgba(255,255,255,0.05);transition:background 0.15s;}
.ar:hover{background:rgba(21,101,192,0.12);}
.ar:first-child{border-radius:14px 14px 0 0;}
.ar:last-child{border-radius:0 0 14px 14px;border-bottom:none;}

/* ── MAT ROW ── */
.mr{display:flex;align-items:center;justify-content:space-between;padding:11px 16px;background:rgba(255,255,255,0.02);border-bottom:1px solid rgba(255,255,255,0.05);font-size:0.85rem;}
.mr:hover{background:rgba(21,101,192,0.1);}

/* ── INPUTS ── */
.stTextInput>div>div>input{background:rgba(255,255,255,0.06)!important;border:1.5px solid rgba(255,255,255,0.12)!important;border-radius:10px!important;color:#e2e8f0!important;font-size:0.9rem!important;}
.stTextInput>div>div>input:focus{border-color:rgba(249,168,37,0.5)!important;box-shadow:0 0 0 3px rgba(249,168,37,0.1)!important;}
.stSelectbox>div>div{background:rgba(255,255,255,0.06)!important;border:1.5px solid rgba(255,255,255,0.12)!important;border-radius:10px!important;color:#e2e8f0!important;}

/* ── BUTTONS ── */
.stButton>button{background:linear-gradient(135deg,#1565c0,#0d47a1)!important;color:white!important;border:none!important;border-radius:10px!important;font-weight:700!important;font-family:'Plus Jakarta Sans',sans-serif!important;padding:9px 22px!important;transition:all 0.2s!important;box-shadow:0 4px 14px rgba(13,71,161,0.35)!important;}
.stButton>button:hover{background:linear-gradient(135deg,#1976d2,#1565c0)!important;transform:translateY(-2px)!important;box-shadow:0 6px 20px rgba(13,71,161,0.5)!important;}

.stProgress>div>div>div{background:linear-gradient(90deg,#1565c0,#f9a825)!important;}
[data-testid="metric-container"]{background:rgba(255,255,255,0.04)!important;border:1px solid rgba(255,255,255,0.1)!important;border-top:2px solid #1565c0!important;border-radius:12px!important;padding:14px!important;}
[data-testid="metric-container"] label{color:rgba(179,229,252,0.6)!important;font-size:0.73rem!important;}
[data-testid="metric-container"] [data-testid="stMetricValue"]{color:#90caf9!important;font-weight:800!important;}

#MainMenu,header[data-testid="stHeader"],footer{visibility:hidden;}
::-webkit-scrollbar{width:5px;}
::-webkit-scrollbar-track{background:rgba(255,255,255,0.03);}
::-webkit-scrollbar-thumb{background:rgba(21,101,192,0.5);border-radius:3px;}
</style>
""", unsafe_allow_html=True)

# ── TICKER ──────────────────────────────────────────────────
ticker_html = " <span class='t-dot'>◆</span> ".join([
    f"<span class='t-item'><strong>{n['t']}</strong></span>" for n in NEWS
])
live_label = "🟢 EN VIVO · med.unlp.edu.ar" if LIVE_OK else "🟡 CONECTA FCM"

st.markdown(f"""
<div class="ticker-wrap">
  <div class="ticker-label">{live_label}</div>
  <div class="ticker-track">
    <div class="ticker-inner">{ticker_html}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── HEADER ──────────────────────────────────────────────────
st.markdown("""
<div class="hdr">
  <div class="hdr-inner">
    <div style="display:flex;align-items:center;gap:0;">
      <div style="display:flex;align-items:center;gap:13px;padding-right:18px;border-right:1px solid rgba(249,168,37,0.18);">
        <div class="logo-orb">🏛️</div>
        <div>
          <div class="hdr-name">Facultad de Ciencias Médicas</div>
          <div class="hdr-sub">Universidad Nacional de La Plata · Desde 1897</div>
        </div>
      </div>
      <div style="display:flex;align-items:center;gap:11px;padding-left:18px;">
        <div class="logo-orb" style="font-size:1.3rem;">🎓</div>
        <div>
          <div style="font-size:0.75rem;font-weight:800;color:#e3f2fd;text-transform:uppercase;letter-spacing:0.1em;">UNLP</div>
          <div style="font-size:0.58rem;color:rgba(179,229,252,0.4);">La Plata · Argentina</div>
        </div>
      </div>
    </div>
    <div class="badge-conecta">⚜️ CONECTA FCM</div>
  </div>
</div>
<div class="nav">
  <span class="nav-i">🏠 Inicio</span>
  <span class="nav-i">📢 Cartelera</span>
  <span class="nav-i">📚 Biblioteca</span>
  <span class="nav-i">📅 Exámenes</span>
  <span class="nav-i">🎓 Plan de Estudios</span>
  <span class="nav-i">🏛️ Carreras</span>
  <span class="nav-i">🔗 Links</span>
  <span class="nav-i">🤖 IA Médico</span>
  <span class="nav-i">👥 Autoridades</span>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="background:linear-gradient(135deg,rgba(13,71,161,0.5),rgba(0,60,50,0.3));
         padding:22px 16px 16px;text-align:center;margin:-1rem -1rem 0;
         border-bottom:1px solid rgba(249,168,37,0.2);">
      <div style="font-size:2.4rem;margin-bottom:6px;filter:drop-shadow(0 0 12px rgba(249,168,37,0.4));">⚜️</div>
      <div style="font-family:'Cinzel',serif;font-size:1.05rem;font-weight:800;
           background:linear-gradient(135deg,#fff,#f9a825);
           -webkit-background-clip:text;-webkit-text-fill-color:transparent;
           letter-spacing:0.08em;">CONECTA FCM</div>
      <div style="font-size:0.58rem;color:rgba(179,229,252,0.4);letter-spacing:0.18em;text-transform:uppercase;margin-top:3px;">Edición Dourado · 2026</div>
    </div>
    <div style="height:1px;background:linear-gradient(90deg,transparent,rgba(249,168,37,0.3),transparent);margin:0 0 14px;"></div>
    <div style="font-size:0.58rem;font-weight:800;letter-spacing:0.2em;text-transform:uppercase;color:rgba(179,229,252,0.35);padding:0 6px 8px;">NAVEGACIÓN</div>
    """, unsafe_allow_html=True)

    nav = st.radio("nav",[
        "🏠  Inicio","📢  Cartelera","📚  Biblioteca","📅  Exámenes",
        "🎓  Plan de Estudios","🏛️  Carreras","🔗  Links Oficiales",
        "👥  Autoridades","🤖  Asistente IA","📊  Calculadora","🗺️  Mapa FCM"
    ], label_visibility="collapsed")

    st.markdown(f"""
    <div style="margin:18px -1rem 0;padding:12px 14px;background:rgba(0,0,0,0.25);
         font-size:0.66rem;color:rgba(179,229,252,0.4);line-height:1.9;
         border-top:1px solid rgba(249,168,37,0.1);">
      📍 Calle 60 y 120, La Plata<br>
      ☎ (0221) 424-1596<br>
      {'<span style="color:#4ade80;">🟢 RSS conectado</span>' if LIVE_OK else '<span style="color:#fbbf24;">🟡 Modo caché</span>'}
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ── DATOS ───────────────────────────────────────────────────
PLAN={"1° Año":[{"m":"Anatomía Humana","t":"Anual","hs":300},{"m":"Biología","t":"Anual","hs":180},{"m":"Citología, Histología y Embriología","t":"Anual","hs":200},{"m":"Ciencias Sociales y Medicina","t":"Cuatrimestral","hs":80},{"m":"Informática Básica","t":"Bimestral","hs":40}],"2° Año":[{"m":"Bioquímica y Biología Molecular","t":"Anual","hs":240},{"m":"Fisiología y Física Biológica","t":"Anual","hs":280},{"m":"Psicología Médica","t":"Bimestral","hs":60},{"m":"Epidemiología","t":"Bimestral","hs":60}],"3° Año":[{"m":"Patología","t":"Anual","hs":220},{"m":"Semiología","t":"Anual","hs":300},{"m":"Microbiología y Parasitología","t":"Anual","hs":180},{"m":"Farmacología Básica","t":"Anual","hs":180},{"m":"Inglés Médico","t":"Anual","hs":80},{"m":"Salud y Medicina Comunitaria","t":"Cuatrimestral","hs":100}],"4° Año":[{"m":"Medicina Interna I","t":"Anual","hs":350},{"m":"Cirugía I","t":"Bimestral","hs":120},{"m":"Farmacología Aplicada","t":"Cuatrimestral","hs":120},{"m":"Infectología","t":"Bimestral","hs":80},{"m":"Neurología, Psiquiatría, Dermatología","t":"Rotativos","hs":200}],"5°–6° Año":[{"m":"Medicina Interna II","t":"Anual","hs":400},{"m":"Cirugía II","t":"Anual","hs":300},{"m":"Pediatría y Neonatología","t":"Anual","hs":280},{"m":"Ginecología y Obstetricia","t":"Anual","hs":260},{"m":"Toxicología y Bioética","t":"Cuatrimestral","hs":120}],"PFO":[{"m":"Práctica Final Obligatoria","t":"Rotatorio Hospitalario","hs":1600}]}
CARRERAS=[{"n":"Medicina","i":"🩺","d":"6 años + PFO","h":"+5.600 hs","desc":"Formación integral del médico. Incluye 1.600 hs de PFO en hospitales universitarios. Acreditada por CONEAU."},{"n":"Enfermería Universitaria","i":"💉","d":"4 años","h":"~3.000 hs","desc":"Formación universitaria en enfermería con enfoque comunitario y hospitalario."},{"n":"Lic. en Nutrición","i":"🥗","d":"4 años","h":"~2.800 hs","desc":"Nutrición clínica, comunitaria y deportiva con práctica hospitalaria integrada."},{"n":"Lic. en Obstetricia","i":"👶","d":"4 años","h":"~3.200 hs","desc":"Salud materna e infantil con prácticas en hospitales públicos universitarios."},{"n":"Tec. Prácticas Cardiológicas","i":"🫀","d":"3 años","h":"~1.800 hs","desc":"ECG, Holter, ergometría y monitores cardiológicos de última generación."}]
AUTORIDADES=[{"c":"Decano","n":"Prof. Dr. Gustavo Horacio Marín","nota":"Electo 30/03/2026 · Primer decano peronista en la historia de la FCM"},{"c":"Vicedecana","n":"Prof. Dra. Irene Lucía Ennis","nota":""},{"c":"Secretario General","n":"Matías Ezequiel Rojo","nota":""},{"c":"Sec. Asuntos Académicos","n":"Dra. Elsa Margarita Chiappa","nota":""},{"c":"Sec. Ciencia y Técnica","n":"Prof. Dr. Martín Vila Petroff","nota":""},{"c":"Sec. Extensión Universitaria","n":"Lic. Pablo Vetere","nota":""},{"c":"Sec. Asuntos Estudiantiles","n":"Srita. Martina Novoa","nota":""},{"c":"Sec. Sup. Administrativa","n":"Sr. Danilo Alberto Rodríguez","nota":""}]
LINKS=[{"n":"Sitio Oficial FCM UNLP","u":"https://www.med.unlp.edu.ar","i":"🌐","d":"Portal principal de la Facultad"},{"n":"SIU Guaraní — Autogestión","u":"https://autogestion.guarani.unlp.edu.ar","i":"🎓","d":"Inscripciones, finales, historial académico"},{"n":"Cartelera Virtual de Cátedras","u":"http://cartelera.med.unlp.edu.ar/","i":"📢","d":"Avisos oficiales en tiempo real"},{"n":"Entorno Educativo — Alumnos","u":"http://entorno.med.unlp.edu.ar/","i":"📚","d":"Material bibliográfico y guías"},{"n":"Aulas Web UNLP","u":"https://aulasweb.unlp.edu.ar/","i":"💻","d":"Plataforma virtual de cursadas"},{"n":"Entorno Docente","u":"http://educativa.med.unlp.edu.ar/login/index.php","i":"👨‍🏫","d":"Gestión docente y comunicación"}]
BIB=[{"id":"b1","t":"Anatomía — Rouvière & Delmas","cat":"Anatomía","a":"1° Año","p":2450,"d":"Descriptiva, topográfica y funcional. Esencial para el Anfiteatro FCM.","ia":"3 tomos: Cabeza-Cuello, Tronco, Miembros. Clave para parciales prácticos."},{"id":"b2","t":"Histología — Ross & Pawlina","cat":"Histología","a":"1° Año","p":1040,"d":"Fotomicrografías HD con correlación histopatológica.","ia":"Epitelios, especializaciones apicales, glándulas. Atlas digital incluido."},{"id":"b3","t":"Fisiología — Guyton & Hall","cat":"Fisiología","a":"2° Año","p":1150,"d":"Estándar mundial de mecanismos fisiológicos humanos.","ia":"Renal (Asa de Henle), cardiovascular, respiratoria, SNC completo."},{"id":"b4","t":"Bioquímica de Harper","cat":"Bioquímica","a":"2° Año","p":820,"d":"Metabolismo, enzimología y biología molecular clínica.","ia":"Krebs, glucólisis, β-oxidación, errores innatos del metabolismo."},{"id":"b5","t":"Patología — Robbins & Cotran","cat":"Patología","a":"3° Año","p":1400,"d":"Patología general y especial con bases fisiopatológicas.","ia":"Inflamación, neoplasias, aterosclerosis, nefropatías, hepatopatías."},{"id":"b6","t":"Farmacología — Goodman & Gilman","cat":"Farmacología","a":"3° Año","p":1420,"d":"Farmacodinámica, farmacocinética y terapéutica médica.","ia":"Antibióticos, analgésicos, psicofármacos y sus mecanismos de acción."}]
EXAMENES=[{"m":"Anatomía Humana — 1° Año","t":"1er Parcial Práctico","f":date(2026,8,10),"h":"08:00 hs","a":"Anfiteatro Central"},{"m":"PFO — Examen Sumativo","t":"Práctica Final Obligatoria","f":date(2026,8,7),"h":"08:00 hs","a":"Sede Hospital FCM"},{"m":"Histología — 1° Año","t":"2do Parcial Teórico","f":date(2026,8,18),"h":"10:30 hs","a":"Aula Magna 1"},{"m":"Fisiología — 2° Año","t":"Final Turno Agosto","f":date(2026,8,25),"h":"14:00 hs","a":"Aula 5 · Edif. Central"},{"m":"Bioquímica — 2° Año","t":"Recuperatorio 1° Módulo","f":date(2026,9,2),"h":"09:00 hs","a":"Laboratorios Subsuelo"}]
MATERIAS=[{"n":"Anatomía Humana","a":"1° Año"},{"n":"Biología","a":"1° Año"},{"n":"Citología, Histología y Embriología","a":"1° Año"},{"n":"Bioquímica y Biología Molecular","a":"2° Año"},{"n":"Fisiología y Física Biológica","a":"2° Año"},{"n":"Epidemiología","a":"2° Año"},{"n":"Patología","a":"3° Año"},{"n":"Semiología","a":"3° Año"},{"n":"Farmacología Básica","a":"3° Año"},{"n":"Microbiología y Parasitología","a":"3° Año"},{"n":"Medicina Interna I","a":"4° Año"},{"n":"Cirugía I","a":"4° Año"}]
IA={"henle":"**🫀 Asa de Henle — Contracorriente**\n\n**Rama Descendente:** Permeable al H₂O · Impermeable a Na⁺/Cl⁻\n\n**Rama Ascendente Gruesa:** Impermeable H₂O · Transporta Na⁺/K⁺/2Cl⁻ (NKCC2) → gradiente osmótico medular (hasta 1200 mOsm/kg)\n\n💊 *Furosemida inhibe NKCC2 → diuresis potente*","histología":"**🔬 Final Histología FCM**\n\n**4 Tejidos:** Epitelial · Conectivo · Muscular · Nervioso\n\n**Epitelial:** Simple/Estratificado/Pseudoestratificado × Plano/Cúbico/Cilíndrico\n\n**Especializaciones:** Microvellosidades (absorción) · Cilias (movilización) · Estereocilias (sensorial)","shock":"**🚨 Shock Anafiláctico**\n\n**Mecanismo:** Antígeno → IgE mastocitos → Degranulación → Histamina/Leucotrienos/Triptasa\n\n**Tto 1ª línea:** 💉 Adrenalina IM 0.3–0.5mg vasto lateral\n\n*Luego:* Fluidos IV · H1/H2 · Corticoides · O₂","krebs":"**🔄 Ciclo de Krebs**\n\nSede: Matriz mitocondrial · Entrada: Acetil-CoA + Oxalacetato\n\n**Por vuelta:** 3 NADH · 1 FADH₂ · 1 GTP · 2 CO₂\n\n**Regulado por:** Citrato sintasa · Isocitrato deshidrogenasa","epitelio":"**🧱 Epitelio — Clasificación FCM**\n\n**Capas:** Simple · Estratificado · Pseudoestratificado\n**Forma:** Plano · Cúbico · Cilíndrico\n\n**Especializaciones apicales:**\n- Microvellosidades → absorción (intestino delgado)\n- Cilias → movilización (tráquea, trompas)\n- Estereocilias → sensorial (cóclea)"}

# ═══════════════════════════════════════════════════════════
#  PÁGINAS
# ═══════════════════════════════════════════════════════════

if nav == "🏠  Inicio":
    st.markdown(f"""
    <div class="hero">
      <div style="position:relative;z-index:1;">
        <div style="font-size:0.65rem;font-weight:800;text-transform:uppercase;letter-spacing:0.22em;color:rgba(249,168,37,0.8);margin-bottom:10px;">⚜️ Portal Estudiantil · FCM · UNLP · La Plata</div>
        <h1 style="font-family:'Plus Jakarta Sans',sans-serif;font-size:2.1rem;font-weight:900;color:#e3f2fd;margin:0 0 12px;line-height:1.15;">
          Facultad de Ciencias Médicas,<br>
          <span style="background:linear-gradient(135deg,#f9a825,#ffcc02);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">toda en tu mano.</span>
        </h1>
        <p style="color:rgba(179,229,252,0.75);font-size:0.92rem;margin:0;max-width:540px;line-height:1.65;">
          Noticias <strong>{'en vivo' if LIVE_OK else 'en caché'}</strong> de med.unlp.edu.ar · Biblioteca médica digital · Plan de estudios oficial · Asistente IA clínico
        </p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    with c1: st.markdown('<div class="stat b"><div class="stat-n">1897</div><div class="stat-l">Fundación FCM</div></div>',unsafe_allow_html=True)
    with c2: st.markdown('<div class="stat g"><div class="stat-n g">5</div><div class="stat-l">Carreras de Grado</div></div>',unsafe_allow_html=True)
    with c3: st.markdown('<div class="stat b"><div class="stat-n">+5.600</div><div class="stat-l">Horas — Medicina</div></div>',unsafe_allow_html=True)
    with c4: st.markdown('<div class="stat g"><div class="stat-n g">24/7</div><div class="stat-l">Portal Activo</div></div>',unsafe_allow_html=True)

    st.markdown("<div style='height:22px'></div>",unsafe_allow_html=True)
    ca,cb = st.columns([3,2])

    with ca:
        src = "🟢 En vivo — med.unlp.edu.ar" if LIVE_OK else "🟡 Noticias en caché"
        st.markdown(f'<div class="sec"><div class="ey">📢 {src}</div><h2>Últimas Noticias FCM</h2></div>',unsafe_allow_html=True)
        for n in NEWS[:4]:
            st.markdown(f"""
            <div class="glass-blue">
              <span class="bd bd-b">🌐 FCM · UNLP</span>
              <div style="font-weight:700;font-size:0.9rem;color:#e3f2fd;margin:8px 0 5px;">{n['t']}</div>
              <div style="font-size:0.79rem;color:rgba(179,229,252,0.65);line-height:1.5;margin-bottom:10px;">{n['d'][:160]}{'…' if len(n['d'])>160 else ''}</div>
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="font-size:0.67rem;color:rgba(179,229,252,0.4);">📅 {n['f']}</span>
                <a href="{n['l']}" target="_blank" style="font-size:0.72rem;color:#90caf9;font-weight:700;text-decoration:none;">Ver nota →</a>
              </div>
            </div>
            """,unsafe_allow_html=True)

    with cb:
        st.markdown('<div class="sec"><div class="ey">⚡ Accesos Rápidos</div><h2>Links Oficiales</h2></div>',unsafe_allow_html=True)
        for l in LINKS:
            st.markdown(f"""
            <a href="{l['u']}" target="_blank" class="lk">
              <div class="lk-ico">{l['i']}</div>
              <div style="flex:1;">
                <div style="font-weight:700;font-size:0.84rem;color:#e3f2fd;">{l['n']}</div>
                <div style="font-size:0.71rem;color:rgba(179,229,252,0.5);margin-top:1px;">{l['d']}</div>
              </div>
              <span style="color:#90caf9;font-size:0.9rem;">→</span>
            </a>
            """,unsafe_allow_html=True)

elif nav == "📢  Cartelera":
    st.markdown(f'<div class="sec"><div class="ey">📢 {"🟢 Datos en vivo" if LIVE_OK else "🟡 Caché local"} — med.unlp.edu.ar</div><h2>Cartelera de Noticias FCM</h2><p>Noticias y comunicados oficiales de la Facultad</p></div>',unsafe_allow_html=True)
    busca = st.text_input("🔍","",placeholder="Buscar noticias...",label_visibility="collapsed")
    nf = [n for n in NEWS if not busca or busca.lower() in n['t'].lower() or busca.lower() in n['d'].lower()]
    st.markdown(f"<p style='font-size:0.75rem;color:rgba(179,229,252,0.4);margin-bottom:12px;'>{len(nf)} noticia(s) — Actualización cada 5 min</p>",unsafe_allow_html=True)
    for i,n in enumerate(nf):
        with st.expander(f"🌐  {n['t']}", expanded=(i==0)):
            st.markdown(f"""
            <div class="glass-blue" style="margin:0;">
              <span class="bd bd-b">🌐 Oficial FCM · UNLP</span>
              <p style="font-size:0.9rem;color:#e3f2fd;line-height:1.65;margin:10px 0;">{n['d']}</p>
              <div style="display:flex;justify-content:space-between;align-items:center;border-top:1px solid rgba(21,101,192,0.25);padding-top:8px;margin-top:8px;">
                <span style="font-size:0.68rem;color:rgba(179,229,252,0.4);">📅 {n['f']}</span>
                <a href="{n['l']}" target="_blank" style="color:#90caf9;font-weight:700;font-size:0.8rem;text-decoration:none;">med.unlp.edu.ar →</a>
              </div>
            </div>
            """,unsafe_allow_html=True)
    if st.button("🔄 Actualizar noticias"):
        st.cache_data.clear(); st.rerun()

elif nav == "📚  Biblioteca":
    st.markdown('<div class="sec"><div class="ey">📚 Acervo Digital</div><h2>Biblioteca Médica FCM</h2><p>Bibliografía oficial con resúmenes por IA</p></div>',unsafe_allow_html=True)
    filtro = st.selectbox("",["Todo","Anatomía","Histología","Fisiología","Bioquímica","Patología","Farmacología","1° Año","2° Año","3° Año"],label_visibility="collapsed")
    lb=[b for b in BIB if filtro=="Todo" or filtro in b["cat"] or filtro in b["a"]]
    c1,c2=st.columns(2)
    for i,b in enumerate(lb):
        col=c1 if i%2==0 else c2
        col.markdown(f"""
        <div class="glass">
          <div style="display:flex;justify-content:space-between;margin-bottom:9px;">
            <span class="bd bd-b">{b['cat']}</span>
            <span class="bd bd-g">{b['a']}</span>
          </div>
          <div style="font-weight:700;font-size:0.92rem;color:#e3f2fd;margin-bottom:5px;">{b['t']}</div>
          <div style="font-size:0.79rem;color:rgba(179,229,252,0.55);line-height:1.5;margin-bottom:10px;">{b['d']}</div>
          <div style="font-size:0.69rem;color:#90caf9;font-weight:600;">📄 {b['p']} páginas</div>
        </div>
        """,unsafe_allow_html=True)
        cb1,cb2=col.columns(2)
        with cb1:
            if st.button("📖 Ver PDF",key=f"v{b['id']}"): st.info(f"**{b['t']}** — Visor PDF activado.")
        with cb2:
            if st.button("🤖 Resumen IA",key=f"i{b['id']}"): st.success(b["ia"])

elif nav == "📅  Exámenes":
    st.markdown('<div class="sec"><div class="ey">⏳ Calendario 2026</div><h2>Exámenes y Fechas FCM</h2><p>Parciales, recuperatorios y finales en tiempo real</p></div>',unsafe_allow_html=True)
    hoy=date.today()
    st.markdown('<table class="tbl"><thead><tr><th>Materia</th><th>Tipo</th><th>Fecha</th><th>Hora</th><th>Aula</th><th>Días</th></tr></thead><tbody>',unsafe_allow_html=True)
    for e in sorted(EXAMENES,key=lambda x:x["f"]):
        dias=(e["f"]-hoy).days
        if dias>0: c="#90caf9";t=f"Faltan {dias}d"
        elif dias==0: c="#ef9a9a";t="¡HOY!"
        else: c="rgba(179,229,252,0.3)";t="Pasado"
        bdg=f'<span class="bd bd-r">{e["t"]}</span>' if dias<=7 and dias>=0 else f'<span class="bd bd-b">{e["t"]}</span>'
        st.markdown(f"<tr><td style='font-weight:600;color:#e3f2fd;'>{e['m']}</td><td>{bdg}</td><td style='color:#cbd5e1;'>{e['f'].strftime('%d/%m/%Y')}</td><td style='color:#cbd5e1;'>{e['h']}</td><td style='font-size:0.79rem;color:rgba(179,229,252,0.55);'>{e['a']}</td><td style='font-weight:800;color:{c};'>{t}</td></tr>",unsafe_allow_html=True)
    st.markdown("</tbody></table>",unsafe_allow_html=True)

elif nav == "🎓  Plan de Estudios":
    st.markdown('<div class="sec"><div class="ey">🎓 Medicina FCM UNLP</div><h2>Plan de Estudios Oficial</h2><p>6 años + PFO · +5.600 hs · Acreditado CONEAU</p></div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    c1.metric("Total Horas","+5.600","Obligatorias"); c2.metric("Duración","6 Años + PFO"); c3.metric("PFO","1.600 hs","Hospitalario")
    st.markdown("<div style='height:14px'></div>",unsafe_allow_html=True)
    for anio,mats in PLAN.items():
        is_pfo=anio=="PFO"
        hdr_c="rgba(249,168,37,0.6)" if is_pfo else "rgba(21,101,192,0.6)"
        brd="rgba(249,168,37,0.3)" if is_pfo else "rgba(21,101,192,0.3)"
        st.markdown(f'<div style="background:rgba(255,255,255,0.03);border:1px solid {brd};border-radius:14px;overflow:hidden;margin-bottom:14px;"><div style="background:{hdr_c};padding:11px 18px;font-weight:700;font-size:0.86rem;color:#e3f2fd;letter-spacing:0.03em;">{anio}</div>',unsafe_allow_html=True)
        for m in mats:
            st.markdown(f'<div class="mr"><span style="font-weight:600;color:#e3f2fd;">{m["m"]}</span><div style="display:flex;gap:8px;align-items:center;"><span class="bd bd-b">{m["t"]}</span><span style="font-size:0.79rem;color:rgba(179,229,252,0.55);font-weight:600;min-width:52px;text-align:right;">{m["hs"]} hs</span></div></div>',unsafe_allow_html=True)
        st.markdown("</div>",unsafe_allow_html=True)

elif nav == "🏛️  Carreras":
    st.markdown('<div class="sec"><div class="ey">🏛️ Oferta Académica</div><h2>Carreras de Grado — FCM UNLP</h2><p>5 carreras universitarias acreditadas</p></div>',unsafe_allow_html=True)
    c1,c2=st.columns(2)
    for i,c in enumerate(CARRERAS):
        col=c1 if i%2==0 else c2
        col.markdown(f'<div class="glass"><div style="font-size:2.2rem;margin-bottom:10px;filter:drop-shadow(0 0 8px rgba(249,168,37,0.3));">{c["i"]}</div><div style="font-weight:800;font-size:0.96rem;color:#e3f2fd;margin-bottom:7px;">{c["n"]}</div><div style="font-size:0.8rem;color:rgba(179,229,252,0.55);line-height:1.55;margin-bottom:14px;">{c["desc"]}</div><div style="display:flex;gap:8px;"><span class="bd bd-b">⏱ {c["d"]}</span><span class="bd bd-g">📚 {c["h"]}</span></div></div>',unsafe_allow_html=True)

elif nav == "🔗  Links Oficiales":
    st.markdown('<div class="sec"><div class="ey">🔗 Sistemas Académicos</div><h2>Links y Portales Oficiales FCM</h2><p>Todos los portales de gestión académica</p></div>',unsafe_allow_html=True)
    for l in LINKS:
        st.markdown(f'<a href="{l["u"]}" target="_blank" class="lk"><div class="lk-ico">{l["i"]}</div><div style="flex:1;"><div style="font-weight:700;font-size:0.9rem;color:#e3f2fd;">{l["n"]}</div><div style="font-size:0.74rem;color:rgba(179,229,252,0.5);margin-top:2px;">{l["d"]}</div><div style="font-size:0.67rem;color:#90caf9;margin-top:3px;">{l["u"]}</div></div><div style="color:#90caf9;font-size:1.1rem;margin:auto 0;">→</div></a>',unsafe_allow_html=True)
    st.markdown('<div class="glass-gold"><div style="font-weight:800;color:#ffd54f;margin-bottom:8px;">📧 Correos Oficiales</div><div style="font-size:0.85rem;color:rgba(255,213,79,0.8);line-height:2.2;">Alumnado: <strong>alumnado@med.unlp.edu.ar</strong> &nbsp;|&nbsp; SAE: <strong>sestudiantil@med.unlp.edu.ar</strong><br>Concursos: <strong>concursos@med.unlp.edu.ar</strong> &nbsp;|&nbsp; Posgrado: <strong>postgrado@med.unlp.edu.ar</strong></div></div>',unsafe_allow_html=True)

elif nav == "👥  Autoridades":
    st.markdown('<div class="sec"><div class="ey">👥 Gestión 2026–2030</div><h2>Autoridades FCM UNLP</h2><p>Asumidas el 8 de mayo de 2026 en el Aula Magna Dr. Bernardo Houssay</p></div>',unsafe_allow_html=True)
    st.markdown('<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(21,101,192,0.25);border-radius:14px;overflow:hidden;">',unsafe_allow_html=True)
    for i,a in enumerate(AUTORIDADES):
        is_d=i==0
        bar="#f9a825" if is_d else "#1565c0"
        bg="rgba(249,168,37,0.07)" if is_d else "transparent"
        fw = "800" if is_d else "600"
        nota_html = f'<div style="font-size:0.7rem;color:#90caf9;margin-top:2px;">{a["nota"]}</div>' if a.get("nota") else ""
        icon_html = "<span style='font-size:1.3rem;'>🏛️</span>" if is_d else ""
        st.markdown(f'<div class="ar" style="background:{bg};"><div style="width:4px;height:40px;background:{bar};border-radius:2px;margin-right:16px;flex-shrink:0;"></div><div style="flex:1;"><div style="font-size:0.67rem;font-weight:800;text-transform:uppercase;letter-spacing:0.08em;color:rgba(179,229,252,0.45);">{a["c"]}</div><div style="font-size:0.94rem;font-weight:{fw};color:#e3f2fd;">{a["n"]}</div>{nota_html}</div>{icon_html}</div>',unsafe_allow_html=True)
    st.markdown("</div>",unsafe_allow_html=True)

elif nav == "🤖  Asistente IA":
    st.markdown('<div class="sec"><div class="ey">🧠 Tutor Clínico</div><h2>Asistente IA Médico FCM</h2><p>Especializado en el programa de la Facultad de Ciencias Médicas UNLP</p></div>',unsafe_allow_html=True)
    cc,ca=st.columns([3,1])
    with ca:
        st.markdown('<p style="font-size:0.65rem;font-weight:800;text-transform:uppercase;letter-spacing:0.14em;color:rgba(179,229,252,0.4);margin-bottom:10px;">⚡ ATAJOS</p>',unsafe_allow_html=True)
        if "atk" not in st.session_state: st.session_state.atk=None
        for lbl,k in [("🫀 Asa de Henle","henle"),("🔬 Histología","histología"),("🚨 Shock Anafiláctico","shock"),("🔄 Ciclo de Krebs","krebs"),("🧱 Epitelios","epitelio")]:
            if st.button(lbl,use_container_width=True,key=f"a_{k}"): st.session_state.atk=k
    with cc:
        if "msgs" not in st.session_state:
            st.session_state.msgs=[{"r":"bot","t":"¡Hola! 🎓 Soy el **Asistente IA de la FCM UNLP**. Puedo explicarte mecanismos, prepararte para parciales y resumir la bibliografía oficial. ¿Empezamos?"}]
        chat_html="".join([f'<div class="c-bot">{m["t"]}</div>' if m["r"]=="bot" else f'<div class="c-usr">{m["t"]}</div>' for m in st.session_state.msgs])
        st.markdown(f'<div style="max-height:380px;overflow-y:auto;padding:4px;background:rgba(0,0,0,0.15);border-radius:14px;border:1px solid rgba(255,255,255,0.06);">{chat_html}</div>',unsafe_allow_html=True)
        if st.session_state.atk:
            st.session_state.msgs.append({"r":"bot","t":IA.get(st.session_state.atk,"Consultando base de datos...")})
            st.session_state.atk=None; st.rerun()
        with st.form("cf",clear_on_submit=True):
            ci,cb=st.columns([5,1])
            with ci: ui=st.text_input("","",placeholder="Preguntá sobre Anatomía, Fisiología, Farmacología...",label_visibility="collapsed")
            with cb: env=st.form_submit_button("→")
        if env and ui.strip():
            st.session_state.msgs.append({"r":"user","t":ui})
            q=ui.lower()
            resp=next((IA[k] for k in IA if k in q),f"Revisé tu consulta sobre **\"{ui}\"**. ¿Querés que busque en la biblioteca FCM o te armo un plan de estudio?")
            st.session_state.msgs.append({"r":"bot","t":resp}); st.rerun()

elif nav == "📊  Calculadora":
    st.markdown('<div class="sec"><div class="ey">📊 Rendimiento</div><h2>Calculadora de Promedio FCM</h2><p>Ingresá tus notas para calcular tu promedio general</p></div>',unsafe_allow_html=True)
    cf,cr=st.columns([3,2])
    notas=[]
    with cf:
        st.markdown('<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(21,101,192,0.25);border-radius:14px;overflow:hidden;"><div style="background:rgba(21,101,192,0.5);padding:11px 18px;font-weight:700;font-size:0.84rem;color:#e3f2fd;">Materias — Medicina FCM UNLP</div>',unsafe_allow_html=True)
        for m in MATERIAS:
            cn,cn2=st.columns([4,1])
            with cn: st.markdown(f'<div style="padding:11px 18px 3px;font-size:0.86rem;font-weight:600;color:#e3f2fd;">{m["n"]} <span style="color:rgba(179,229,252,0.4);font-weight:400;font-size:0.73rem;">({m["a"]})</span></div>',unsafe_allow_html=True)
            with cn2:
                nota=st.selectbox("",[ "-","4","5","6","7","8","9","10"],label_visibility="collapsed",key=f"n_{m['n']}")
                if nota!="-": notas.append(int(nota))
        st.markdown("</div>",unsafe_allow_html=True)
    with cr:
        ap=len(notas);tot=len(MATERIAS);prom=sum(notas)/ap if ap>0 else 0;prog=ap/tot
        color="#90caf9" if prom>=7 else ("#ffd54f" if prom>=6 else "#ef9a9a")
        st.markdown(f'<div class="glass" style="text-align:center;padding:28px;"><div style="font-size:0.65rem;font-weight:800;text-transform:uppercase;letter-spacing:0.16em;color:rgba(179,229,252,0.4);margin-bottom:6px;">PROMEDIO GENERAL</div><div style="font-family:Cinzel,serif;font-size:4rem;font-weight:900;color:{color};line-height:1;margin-bottom:8px;filter:drop-shadow(0 0 16px {color}66);">{prom:.2f}</div><div style="font-size:0.8rem;color:rgba(179,229,252,0.45);">{ap} de {tot} materias</div><div style="background:rgba(0,0,0,0.3);border-radius:8px;overflow:hidden;height:7px;margin:16px 0 6px;"><div style="height:100%;width:{int(prog*100)}%;background:linear-gradient(90deg,#1565c0,#f9a825);border-radius:8px;"></div></div><div style="font-size:0.68rem;color:rgba(179,229,252,0.35);">{int(prog*100)}% de avance curricular</div></div>',unsafe_allow_html=True)
        if prom>=9: st.success("🏆 ¡Promedio Dourado! Excelencia absoluta.")
        elif prom>=7: st.info("⭐ Muy buen promedio.")
        elif prom>=6: st.warning("📈 Aprobado, hay margen de mejora.")
        elif prom>0: st.error("📚 Reforzá con el Asistente IA.")

elif nav == "🗺️  Mapa FCM":
    st.markdown('<div class="sec"><div class="ey">🗺️ Edificio FCM</div><h2>Mapa de la Facultad</h2><p>Calle 60 y 120, La Plata · Buenos Aires</p></div>',unsafe_allow_html=True)
    UBIC=[{"n":"Anfiteatro de Anatomía","i":"💀","p":"PB — Pabellón Central","d":"Disección y piezas anatómicas. Guardapolvo blanco obligatorio."},{"n":"Biblioteca Central FCM","i":"📚","p":"1er Piso — Sector Oeste","d":"Libros físicos, computadoras y WiFi. Lunes a Viernes."},{"n":"Laboratorios de Histología","i":"🔬","p":"2do Piso — Edificio Anexo","d":"Microscopios ópticos y cámaras de proyección para láminas."},{"n":"Aula Magna Dr. B. Houssay","i":"🏛️","p":"PB — Hall Central","d":"Capacidad 500 personas. Simposios y actos académicos."},{"n":"Secretaría Académica (SAE)","i":"📋","p":"PB — Ala Berisso","d":"Libretas, analíticos, equivalencias. sestudiantil@med.unlp.edu.ar"},{"n":"Hospital de Simulación (HoSiC)","i":"🏥","p":"Edificio Sur","d":"Simuladores hápticos y rotatorios clínicos."},{"n":"Departamento de Alumnado","i":"🎓","p":"Av. 60 y 120 — PB","d":"Inscripciones. alumnado@med.unlp.edu.ar"}]
    sel=st.radio("",[u["n"] for u in UBIC],label_visibility="collapsed")
    sd=next(u for u in UBIC if u["n"]==sel)
    c1,c2=st.columns([2,3])
    with c1:
        st.markdown(f'<div class="glass-gold" style="text-align:center;padding:26px;"><div style="font-size:3rem;margin-bottom:10px;filter:drop-shadow(0 0 10px rgba(249,168,37,0.4));">{sd["i"]}</div><div style="font-weight:800;font-size:1rem;color:#ffd54f;margin-bottom:8px;">{sd["n"]}</div><div style="font-size:0.82rem;color:rgba(255,213,79,0.7);line-height:1.6;margin-bottom:14px;">{sd["d"]}</div><div style="background:rgba(249,168,37,0.1);border:1px solid rgba(249,168,37,0.25);border-radius:8px;padding:9px 12px;font-size:0.75rem;color:rgba(255,213,79,0.8);">📍 {sd["p"]}</div></div>',unsafe_allow_html=True)
    with c2:
        st.markdown('<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:14px;overflow:hidden;"><div style="background:rgba(21,101,192,0.5);color:#e3f2fd;padding:10px 16px;font-size:0.76rem;font-weight:700;text-transform:uppercase;letter-spacing:0.07em;">Planta FCM — Calle 60 y 120</div>',unsafe_allow_html=True)
        for u in UBIC:
            act=u["n"]==sel
            st.markdown(f'<div style="display:flex;align-items:center;gap:12px;padding:12px 16px;background:{"rgba(21,101,192,0.15)" if act else "transparent"};border-bottom:1px solid rgba(255,255,255,0.05);border-left:{"3px solid #90caf9" if act else "3px solid transparent"};"><span style="font-size:1.2rem;">{u["i"]}</span><div><div style="font-size:0.83rem;font-weight:{"700" if act else "500"};color:{"#90caf9" if act else "#cbd5e1"};">{u["n"]}</div><div style="font-size:0.68rem;color:rgba(179,229,252,0.4);">{u["p"]}</div></div>{"<span style=\'margin-left:auto;color:#90caf9;font-weight:800;\'>●</span>" if act else ""}</div>',unsafe_allow_html=True)
        st.markdown("</div>",unsafe_allow_html=True)
