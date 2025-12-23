import streamlit as st
from fpdf import FPDF
import base64
import plotly.express as px
import pandas as pd
import math

# ==============================================================================
# 0. CONFIGURACIÓN VISUAL (DARK TECH MASTER)
# ==============================================================================
st.set_page_config(
    page_title="AimyWater Master V42",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inyección CSS para forzar Modo Oscuro Tecnológico
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    /* RESET GLOBAL A MODO OSCURO */
    html, body, [class*="css"], [data-testid="stAppViewContainer"] {
        font-family: 'Outfit', sans-serif !important;
        background-color: #0e1117 !important;
        color: #e2e8f0 !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 1px solid #30363d;
    }

    /* INPUTS */
    input, .stNumberInput input, .stSelectbox, .stSlider {
        color: #ffffff !important;
        background-color: #0d1117 !important;
    }
    label {
        color: #00e5ff !important; /* Azul Neón */
        font-weight: 600 !important;
    }

    /* TARJETAS MÉTRICAS */
    div[data-testid="stMetric"] {
        background-color: #1f2937 !important;
        border: 1px solid #374151 !important;
        border-radius: 10px !important;
        padding: 15px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important;
    }
    div[data-testid="stMetricLabel"] { color: #9ca3af !important; }
    div[data-testid="stMetricValue"] { color: #ffffff !important; }

    /* BOTONES */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #00c6ff 0%, #0072ff 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        box-shadow: 0 0 15px rgba(0, 114, 255, 0.3) !important;
    }

    /* CARDS PERSONALIZADAS */
    .tech-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-left: 4px solid #00e5ff;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .tech-title { color: #00e5ff; font-size: 0.8rem; text-transform: uppercase; font-weight: 700; }
    .tech-value { color: white; font-size: 1.5rem; font-weight: 700; }
    .tech-sub { color: #8b949e; font-size: 0.8rem; }
    
    /* AVISOS */
    .alert-box {
        padding: 10px;
        border-radius: 5px;
        margin-top: 10px;
        font-size: 0.9rem;
    }
    .alert-red { background-color: #450a0a; border: 1px solid #991b1b; color: #fecaca; }
    .alert-yellow { background-color: #422006; border: 1px solid #a16207; color: #fde047; }

</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 1. SEGURIDAD (LOGIN DIRECTO)
# ==============================================================================
def check_auth():
    if "auth" not in st.session_state: st.session_state["auth"] = False
    if st.session_state["auth"]: return True
    
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        st.markdown("### 🔐 AimyWater Engineering")
        user = st.text_input("Usuario")
        pwd = st.text_input("Access Key", type="password")
        if st.button("LOGIN", type="primary"):
            # Credenciales: admin / aimywater2025
            if user == "admin" and pwd == "aimywater2025":
                st.session_state["auth"] = True
                st.rerun()
            else:
                st.error("Acceso denegado")
    return False

if not check_auth(): st.stop()

# ==============================================================================
# 2. MOTORES DE CÁLCULO (INGENIERÍA AVANZADA)
# ==============================================================================

class EquipoRO:
    def __init__(self, n, prod, ppm, ef, kw):
        self.nombre = n
        self.produccion_nominal = prod
        self.max_ppm = ppm
        self.eficiencia = ef
        self.potencia_kw = kw

class Descal:
    def __init__(self, n, bot, caud, cap, sal, wash):
        self.nombre = n
        self.medida_botella = bot
        self.caudal_max = caud
        self.capacidad = cap
        self.sal_kg = sal
        self.caudal_wash = wash # Caudal necesario para contralavado

# BD SIMPLIFICADA
ro_db = [
    EquipoRO("PURHOME PLUS", 300, 3000, 0.5, 0.03),
    EquipoRO("DF 800 UV-LED", 3000, 1500, 0.71, 0.08),
    EquipoRO("Direct Flow 1200", 4500, 1500, 0.66, 0.10),
    EquipoRO("ALFA 140", 5000, 2000, 0.5, 0.75),
    EquipoRO("ALFA 240", 10000, 2000, 0.5, 1.1),
    EquipoRO("ALFA 440", 20000, 2000, 0.6, 1.1),
    EquipoRO("AP-6000 LUXE", 18000, 6000, 0.6, 2.2),
]

descal_db = [
    Descal("BI BLOC 30L", "10x35", 1.8, 192, 4.5, 2.0),
    Descal("BI BLOC 60L", "12x48", 3.6, 384, 9.0, 3.5),
    Descal("TWIN 40L", "10x44", 2.4, 256, 6.0, 2.5),
    Descal("TWIN 100L", "14x65", 6.0, 640, 15.0, 5.0),
    Descal("DUPLEX 300L", "24x69", 6.5, 1800, 45.0, 9.0),
]

def calcular_tuberia(caudal_lh):
    # Velocidad recomendada 1.5 m/s
    if caudal_lh < 1500: return '3/4"'
    elif caudal_lh < 3000: return '1"'
    elif caudal_lh < 5000: return '1 1/4"'
    elif caudal_lh < 9000: return '1 1/2"'
    elif caudal_lh < 15000: return '2"'
    else: return '2 1/2"'

def calcular(origen, modo, consumo, ppm, dureza, temp, horas, costes, buffer_on, descal_on, man_fin, man_buf):
    res = {}
    msgs = []
    
    # 1. Ajuste por Origen (Pozo = Factor Seguridad)
    factor_seguridad_filtros = 1.2 if origen == "Pozo" else 1.0
    
    # 2. Limitador de Recuperación por Salinidad (Ingeniería Avanzada)
    factor_recuperacion = 1.0
    if ppm > 2500:
        factor_recuperacion = 0.8 # Bajamos eficiencia un 20% por seguridad
        msgs.append(f"⚠️ Alta Salinidad ({ppm} ppm): Se ha reducido la eficiencia calculada para proteger las membranas.")

    # 3. Depósitos
    res['v_final'] = man_fin if man_fin > 0 else consumo * 0.75
    
    # 4. Cálculo
    if modo == "Solo Descalcificación":
        q_target = (consumo / horas) * factor_seguridad_filtros
        cands = [d for d in descal_db if (d.caudal_max * 1000) >= q_target]
        if cands:
            carga = (consumo/1000)*dureza
            validos = [d for d in cands if (d.capacidad/carga if carga>0 else 99) >= 5]
            res['descal'] = validos[0] if validos else cands[-1]
            res['dias'] = res['descal'].capacidad / carga if carga > 0 else 99
            res['sal_anual'] = (365/res['dias']) * res['descal'].sal_kg
            res['opex'] = res['sal_anual'] * costes['sal']
            res['caudal_punta'] = q_target
            res['wash'] = res['descal'].caudal_wash * 1000
        else:
            res['descal'] = None
            
    else: # RO
        tcf = 1.0 if temp >= 25 else max(1.0 - ((25 - temp) * 0.03), 0.1)
        q_target = consumo
        
        ro_cands = [r for r in ro_db if ppm <= r.max_ppm and ((r.produccion_nominal * tcf / 24) * horas) >= q_target]
        
        if ro_cands:
            ro_best = next((r for r in ro_cands if "ALFA" in r.nombre or "AP" in r.nombre), ro_cands[-1]) if q_target > 600 else ro_cands[0]
            res['ro'] = ro_best
            
            # Eficiencia Real ajustada
            efi_real = ro_best.eficiencia * factor_recuperacion
            res['efi_real'] = efi_real
            
            agua_in = consumo / efi_real
            q_bomba = (ro_best.produccion_nominal / 24 / ro_best.eficiencia) * 1.5 # Caudal instantáneo bomba
            
            if buffer_on:
                q_filtros = (agua_in / 20) * factor_seguridad_filtros
                res['v_buffer'] = man_buf if man_buf > 0 else q_bomba * 2
            else:
                q_filtros = q_bomba * factor_seguridad_filtros
                res['v_buffer'] = 0
            
            res['q_filtros'] = q_filtros
            
            # Selección Descal
            if descal_on and dureza > 5:
                carga = (agua_in/1000)*dureza
                ds = [d for d in descal_db if (d.caudal_max*1000) >= q_filtros]
                if ds:
                    v = [d for d in ds if (d.capacidad/carga if carga>0 else 99) >= 5]
                    res['descal'] = v[0] if v else ds[-1]
                    res['dias'] = res['descal'].capacidad / carga if carga > 0 else 99
                    res['sal_anual'] = (365/res['dias']) * res['descal'].sal_kg
                    res['wash'] = res['descal'].caudal_wash * 1000
                else: res['descal'] = None
            
            # Opex
            kwh = (consumo / ((ro_best.produccion_nominal * tcf)/24)) * ro_best.potencia_kw * 365
            sal = res.get('sal_anual', 0)
            m3 = (agua_in/1000)*365
            res['opex'] = (kwh*costes['luz']) + (sal*costes['sal']) + (m3*costes['agua'])
            res['breakdown'] = {'Agua': m3*costes['agua'], 'Sal': sal*costes['sal'], 'Luz': kwh*costes['luz']}
            
        else: res['ro'] = None

    # Tubería recomendada
    max_flow = max(res.get('q_filtros', 0), res.get('caudal_punta', 0), res.get('wash', 0))
    res['tuberia'] = calcular_tuberia(max_flow)
    res['msgs'] = msgs
    
    return res

# ==============================================================================
# 3. INTERFAZ
# ==============================================================================

# Header con Logo
c_logo, c_title = st.columns([1,5])
with c_logo:
    try: st.image("logo.png", width=120)
    except: st.warning("Logo?")
with c_title:
    st.markdown("# AimyWater Master")
    st.markdown("**Plataforma de Ingeniería de Tratamiento de Aguas**")

st.divider()

# Sidebar
with st.sidebar:
    st.header("1. Configuración de Proyecto")
    
    origen = st.selectbox("Origen del Agua", ["Red Pública", "Pozo / Río"])
    modo = st.selectbox("Modo de Diseño", ["Planta Completa (RO)", "Solo Descalcificación"])
    
    with st.expander("Hidráulica", expanded=True):
        consumo = st.number_input("Consumo Diario (L)", value=2000)
        horas = st.number_input("Horas Producción", value=20)
        
        if modo == "Planta Completa (RO)":
            buffer = st.checkbox("Buffer Intermedio", value=True)
            descal = st.checkbox("Incluir Descalcificador", value=True)
        else:
            buffer, descal = False, True

    with st.expander("Calidad Agua"):
        dureza = st.number_input("Dureza (ºHf)", value=35)
        ppm = st.number_input("TDS (ppm)", value=800) if "RO" in modo else 0
        temp = st.number_input("Temp (ºC)", value=15) if "RO" in modo else 25

    with st.expander("Costes Unitarios"):
        ca = st.number_input("Agua €/m3", value=1.5)
        cs = st.number_input("Sal €/kg", value=0.45)
        cl = st.number_input("Luz €/kWh", value=0.20)
        costes = {'agua': ca, 'sal': cs, 'luz': cl}
        
    with st.expander("Manual (Opcional)"):
        mf = st.number_input("Depósito Final (L)", value=0)
        mb = st.number_input("Buffer (L)", value=0)

    if st.button("CALCULAR SISTEMA", type="primary", use_container_width=True):
        st.session_state['run'] = True

# Dashboard
if st.session_state.get('run'):
    res = calcular(origen, modo, consumo, ppm, dureza, temp, horas, costes, buffer, descal, mf, mb)
    
    if res.get('ro') or res.get('descal'):
        
        # AVISOS DE INGENIERÍA
        if origen == "Pozo":
            st.markdown("<div class='alert-box alert-yellow'>⚠️ <b>ALERTA DE POZO:</b> Se ha aplicado un factor de seguridad del 20% en filtros. Se requiere pre-filtración de Silex/Turbidex obligatoria (Ver PDF).</div>", unsafe_allow_html=True)
        
        for msg in res['msgs']:
            st.markdown(f"<div class='alert-box alert-red'>{msg}</div>", unsafe_allow_html=True)

        # DIAGRAMA DE FLUJO (VISUAL)
        st.markdown("### 🏭 Tren de Tratamiento")
        c1, c2, c3, c4 = st.columns(4)
        
        with c1:
            if res.get('q_filtros'):
                st.markdown(f"""<div class='tech-card'>
                    <div class='tech-title'>⚡ FILTRACIÓN</div>
                    <div class='tech-value'>{int(res['q_filtros'])} L/h</div>
                    <div class='tech-sub'>Caudal Servicio</div>
                </div>""", unsafe_allow_html=True)
                
        with c2:
            if res.get('descal'):
                st.markdown(f"""<div class='tech-card'>
                    <div class='tech-title'>🧂 ABLANDAMIENTO</div>
                    <div class='tech-value'>{res['descal'].nombre}</div>
                    <div class='tech-sub'>Regen: {res['dias']:.1f} días</div>
                </div>""", unsafe_allow_html=True)
                
        with c3:
            if res.get('ro'):
                st.markdown(f"""<div class='tech-card'>
                    <div class='tech-title'>💧 ÓSMOSIS</div>
                    <div class='tech-value'>{res['ro'].nombre}</div>
                    <div class='tech-sub'>Efic: {int(res['efi_real']*100)}%</div>
                </div>""", unsafe_allow_html=True)
                
        with c4:
            st.markdown(f"""<div class='tech-card'>
                <div class='tech-title'>📏 TUBERÍA REC.</div>
                <div class='tech-value'>{res['tuberia']}</div>
                <div class='tech-sub'>Acometida Mínima</div>
            </div>""", unsafe_allow_html=True)

        # DEPÓSITOS
        st.markdown("### 🛢️ Acumulación")
        dt1, dt2 = st.columns(2)
        if res.get('v_buffer', 0) > 0:
            dt1.metric("🛡️ Buffer Intermedio", f"{int(res['v_buffer'])} L", "Pre-RO")
        dt2.metric("📦 Depósito Final", f"{int(res['v_final'])} L", "Agua Producto")

        # ANÁLISIS ECONÓMICO (SOLO RO)
        if modo == "Planta Completa (RO)":
            st.markdown("### 💸 Análisis OPEX")
            gf1, gf2 = st.columns([2,1])
            with gf1:
                df = pd.DataFrame(list(res['breakdown'].items()), columns=['Concepto', 'Coste'])
                fig = px.pie(df, values='Coste', names='Concepto', hole=0.6, color_discrete_sequence=px.colors.sequential.Cyan)
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white")
                st.plotly_chart(fig, use_container_width=True)
            with gf2:
                st.metric("Coste Diario Total", f"{(res['opex']/365):.2f} €")
                st.metric("Consumo Sal", f"{int(res.get('sal_anual',0))} Kg/año")

        # CHECKLIST INSTALACIÓN
        st.markdown("### ✅ Checklist de Instalación")
        col_check1, col_check2 = st.columns(2)
        col_check1.info(f"**Caudal Punta Lavado:** {int(res.get('wash', 0))} L/h (La bomba de alimentación debe dar esto a 2.5 bar).")
        col_check2.info(f"**Tubería Colectora:** Mínimo {res['tuberia']} para evitar pérdidas de carga.")

    else:
        st.error("No se encontró solución estándar para estos parámetros.")

else:
    st.info("👈 Configura el proyecto en el menú lateral.")
