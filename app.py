import streamlit as st
from fpdf import FPDF
import base64
import plotly.express as px
import pandas as pd
from supabase import create_client, Client

# ==============================================================================
# 0. CONFIGURACIÓN
# ==============================================================================
st.set_page_config(page_title="HYDROLOGIC", page_icon="🌊", layout="wide", initial_sidebar_state="expanded")

# --- CONEXIÓN SUPABASE ---
@st.cache_resource
def init_connection():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_connection()

# --- ESTILOS ---
def local_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=Inter:wght@300;400;600&display=swap');
        html, body, [class*="css"], [data-testid="stAppViewContainer"] {
            font-family: 'Inter', sans-serif !important; background-color: #0f172a !important; color: #e2e8f0 !important;
        }
        .brand-logo { font-family: 'Rajdhani', sans-serif; font-size: 2.5rem; font-weight: 700; background: -webkit-linear-gradient(0deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin:0;}
        .brand-sub { font-family: 'Inter', sans-serif; font-size: 0.8rem; color: #94a3b8; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 20px;}
        [data-testid="stSidebar"] { background-color: #1e293b !important; border-right: 1px solid #334155; }
        input, .stNumberInput input, .stSelectbox, .stSlider { color: #ffffff !important; background-color: #0f172a !important; border: 1px solid #334155 !important; }
        label { color: #38bdf8 !important; font-weight: 600 !important; }
        div[data-testid="stMetric"] { background-color: #1e293b !important; border: 1px solid #334155 !important; border-radius: 8px !important; }
        div[data-testid="stMetricLabel"] { color: #94a3b8 !important; }
        div[data-testid="stMetricValue"] { color: #ffffff !important; font-family: 'Rajdhani', sans-serif !important; }
        div.stButton > button:first-child { background: linear-gradient(90deg, #0ea5e9 0%, #3b82f6 100%) !important; color: white !important; border: none !important; font-weight: bold !important; border-radius: 6px; }
        .tech-card { background-color: #1e293b; border: 1px solid #334155; border-left: 4px solid #38bdf8; padding: 15px; border-radius: 6px; margin-bottom: 10px; }
        .tech-title { color: #38bdf8; font-size: 0.75rem; text-transform: uppercase; font-weight: 700; letter-spacing: 1px; }
        .tech-value { color: white; font-size: 1.3rem; font-weight: 700; font-family: 'Rajdhani', sans-serif; }
        .tech-sub { color: #94a3b8; font-size: 0.8rem; }
        .alert-box { padding: 12px; border-radius: 6px; margin-top: 10px; font-size: 0.9rem; background-color: #422006; border: 1px solid #a16207; color: #fde047; }
        .admin-panel { background-color: #312e81; padding: 15px; border-radius: 8px; border: 1px solid #6366f1; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)
local_css()

# ==============================================================================
# 1. LOGIN
# ==============================================================================
def check_auth():
    if "auth" not in st.session_state: st.session_state["auth"] = False
    if st.session_state["auth"]: return True
    
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.markdown('<p class="brand-logo">HYDROLOGIC</p>', unsafe_allow_html=True)
        st.markdown('<p class="brand-sub">ENGINEERING ACCESS</p>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        user = st.text_input("User ID")
        pwd = st.text_input("Password", type="password")
        
        if st.button("LOGIN", type="primary", use_container_width=True):
            try:
                response = supabase.table("usuarios").select("*").eq("username", user).eq("password", pwd).execute()
                if len(response.data) > 0:
                    usuario_data = response.data[0]
                    if usuario_data["activo"]:
                        st.session_state["auth"] = True
                        st.session_state["user_info"] = usuario_data
                        st.toast(f"Bienvenido, {usuario_data['empresa']}", icon="✅")
                        st.rerun()
                    else: st.error("Licencia expirada.")
                else: st.error("Credenciales incorrectas.")
            except Exception as e: st.error(f"Error conexión: {e}")
    return False

if not check_auth(): st.stop()

# ==============================================================================
# 2. LÓGICA TÉCNICA (V50)
# ==============================================================================
class EquipoRO:
    def __init__(self, n, prod, ppm, ef, kw):
        self.nombre = n; self.produccion_nominal = prod; self.max_ppm = ppm; self.eficiencia = ef; self.potencia_kw = kw
class Filtro:
    def __init__(self, tipo, n, bot, caud, wash, sal=0, cap=0):
        self.tipo = tipo; self.nombre = n; self.medida_botella = bot; self.caudal_max = caud; self.caudal_wash = wash; self.sal_kg = sal; self.capacidad = cap

ro_db = [
    EquipoRO("PURHOME PLUS", 300, 3000, 0.5, 0.03), EquipoRO("DF 800 UV-LED", 3000, 1500, 0.71, 0.08),
    EquipoRO("Direct Flow 1200", 4500, 1500, 0.66, 0.10), EquipoRO("ALFA 140", 5000, 2000, 0.5, 0.75),
    EquipoRO("ALFA 240", 10000, 2000, 0.5, 1.1), EquipoRO("ALFA 440", 20000, 2000, 0.6, 1.1),
    EquipoRO("AP-6000 LUXE", 18000, 6000, 0.6, 2.2),
]
silex_db = [Filtro("Silex", "SIL 10x35", "10x35", 0.8, 2.0), Filtro("Silex", "SIL 10x44", "10x44", 0.8, 2.0), Filtro("Silex", "SIL 12x48", "12x48", 1.1, 3.0), Filtro("Silex", "SIL 18x65", "18x65", 2.6, 6.0), Filtro("Silex", "SIL 21x60", "21x60", 3.6, 9.0), Filtro("Silex", "SIL 24x69", "24x69", 4.4, 12.0), Filtro("Silex", "SIL 30x72", "30x72", 7.0, 18.0), Filtro("Silex", "SIL 36x72", "36x72", 10.0, 25.0)]
carbon_db = [Filtro("Carbon", "DEC 30L", "10x35", 0.38, 1.5), Filtro("Carbon", "DEC 45L", "10x54", 0.72, 2.0), Filtro("Carbon", "DEC 60L", "12x48", 0.80, 2.5), Filtro("Carbon", "DEC 75L", "13x54", 1.10, 3.5), Filtro("Carbon", "DEC 90KG", "18x65", 2.68, 6.0)]
descal_db = [Filtro("Descal", "BI BLOC 30L", "10x35", 1.8, 2.0, 4.5, 192), Filtro("Descal", "BI BLOC 60L", "12x48", 3.6, 3.5, 9.0, 384), Filtro("Descal", "TWIN 40L", "10x44", 2.4, 2.5, 6.0, 256), Filtro("Descal", "TWIN 100L", "14x65", 6.0, 5.0, 15.0, 640), Filtro("Descal", "DUPLEX 300L", "24x69", 6.5, 9.0, 45.0, 1800)]

def calcular_tuberia(caudal_lh):
    if caudal_lh < 1500: return '3/4"'
    elif caudal_lh < 3000: return '1"'
    elif caudal_lh < 5000: return '1 1/4"'
    elif caudal_lh < 9000: return '1 1/2"'
    else: return '2"'

def calcular(origen, modo, consumo, caudal_punta, ppm, dureza, temp, horas, costes, buffer_on, descal_on, man_fin, man_buf):
    res = {}
    msgs = []
    fs = 1.2 if origen == "Pozo" else 1.0
    res['v_final'] = man_fin if man_fin > 0 else max(consumo * 0.75, caudal_punta * 60)
    
    if modo == "Solo Descalcificación":
        q_target = (consumo / horas) * fs
        cands = [d for d in descal_db if (d.caudal_max * 1000) >= q_target]
        if cands:
            carga = (consumo/1000)*dureza
            validos = [d for d in cands if (d.capacidad/carga if carga>0 else 99) >= 5]
            res['descal'] = validos[0] if validos else cands[-1]
            res['dias'] = res['descal'].capacidad / carga if carga > 0 else 99
            res['sal_anual'] = (365/res['dias']) * res['descal'].sal_kg
            res['opex'] = res['sal_anual'] * costes['sal']
            res['wash'] = res['descal'].caudal_wash * 1000
            res['q_filtros'] = q_target
        else: res['descal'] = None
    else: 
        tcf = 1.0 if temp >= 25 else max(1.0 - ((25 - temp) * 0.03), 0.1)
        factor_recuperacion = 0.8 if ppm > 2500 else 1.0
        q_target = consumo
        ro_cands = [r for r in ro_db if ppm <= r.max_ppm and ((r.produccion_nominal * tcf / 24) * horas) >= q_target]
        
        if ro_cands:
            res['ro'] = next((r for r in ro_cands if "ALFA" in r.nombre or "AP" in r.nombre), ro_cands[-1]) if q_target > 600 else ro_cands[0]
            res['efi_real'] = res['ro'].eficiencia * factor_recuperacion
            res['q_prod_hora'] = (res['ro'].produccion_nominal * tcf) / 24
            agua_in = consumo / res['efi_real']
            q_bomba = (res['ro'].produccion_nominal / 24 / res['ro'].eficiencia) * 1.5
            
            if buffer_on:
                q_filtros = (agua_in / 20) * fs 
                res['v_buffer'] = man_buf if man_buf > 0 else q_bomba * 2
            else:
                q_filtros = q_bomba * fs 
                res['v_buffer'] = 0
            res['q_filtros'] = q_filtros
            
            sx_cands = [s for s in silex_db if (s.caudal_max * 1000) >= q_filtros]
            res['silex'] = sx_cands[0] if sx_cands else None
            cb_cands = [c for c in carbon_db if (c.caudal_max * 1000) >= q_filtros]
            res['carbon'] = cb_cands[0] if cb_cands else None

            if descal_on and dureza > 5:
                ds = [d for d in descal_db if (d.caudal_max*1000) >= q_filtros]
                if ds:
                    carga = (agua_in/1000)*dureza
                    v = [d for d in ds if (d.capacidad/carga if carga>0 else 99) >= 5]
                    res['descal'] = v[0] if v else ds[-1]
                    res['dias'] = res['descal'].capacidad / carga if carga > 0 else 99
                    res['sal_anual'] = (365/res['dias']) * res['descal'].sal_kg
                    res['wash'] = res['descal'].caudal_wash * 1000
                else: res['descal'] = None
            
            kwh = (consumo / res['q_prod_hora']) * res['ro'].potencia_kw * 365
            sal = res.get('sal_anual', 0)
            m3 = (agua_in/1000)*365
            res['opex'] = (kwh*costes['luz']) + (sal*costes['sal']) + (m3*costes['agua'])
            res['breakdown'] = {'Agua': m3*costes['agua'], 'Sal': sal*costes['sal'], 'Luz': kwh*costes['luz']}
            res['wash'] = max((res['silex'].caudal_wash if res.get('silex') else 0), (res['carbon'].caudal_wash if res.get('carbon') else 0), (res['descal'].caudal_wash if res.get('descal') else 0)) * 1000
        else: res['ro'] = None

    max_flow = max(res.get('q_filtros', 0), res.get('wash', 0))
    res['tuberia'] = calcular_tuberia(max_flow)
    res['msgs'] = msgs
    return res

def create_pdf(res, inputs, modo, empresa_cliente):
    pdf = FPDF()
    pdf.add_page()
    try: pdf.image('logo.png', 10, 8, 33)
    except: pass
    pdf.ln(20)
    def clean(text): return str(text).encode('latin-1', 'replace').decode('latin-1') if text else "N/A"
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, clean(f"INFORME TÉCNICO - {empresa_cliente.upper()}"), 0, 1, 'C')
    pdf.ln(10)
    
    # PARAMETROS
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, clean("1. PARAMETROS"), 0, 1)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 8, clean(f"Consumo: {inputs['consumo']} L/dia"), 0, 1)
    if modo == "Planta Completa (RO)":
        pdf.cell(0, 8, clean(f"TDS Entrada: {inputs['ppm']} ppm | Dureza: {inputs['dureza']} Hf"), 0, 1)
    pdf.ln(5)
    
    # EQUIPOS
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, clean("2. EQUIPOS SELECCIONADOS"), 0, 1)
    pdf.set_font("Arial", '', 10)
    
    if modo == "Solo Descalcificación":
        if res.get('descal'):
            pdf.cell(0, 8, clean(f"DESCAL: {res['descal'].nombre} ({res['descal'].medida_botella})"), 0, 1)
            pdf.cell(0, 8, clean(f"  Regeneracion: Cada {res['dias']:.1f} dias"), 0, 1)
    else: 
        if res.get('silex'): pdf.cell(0, 8, clean(f"A. SILEX: {res['silex'].nombre} ({res['silex'].medida_botella})"), 0, 1)
        if res.get('carbon'): pdf.cell(0, 8, clean(f"B. CARBON: {res['carbon'].nombre} ({res['carbon'].medida_botella})"), 0, 1)
        if res.get('v_buffer', 0) > 0: pdf.cell(0, 8, clean(f"C. BUFFER INTERMEDIO: {int(res['v_buffer'])} Litros"), 0, 1)
        if res.get('descal'): pdf.cell(0, 8, clean(f"D. DESCAL: {res['descal'].nombre} ({res['descal'].medida_botella})"), 0, 1)
        if res.get('ro'): pdf.cell(0, 8, clean(f"E. OSMOSIS: {res['ro'].nombre} ({res['ro'].produccion_nominal} L/dia)"), 0, 1)
    
    # INSTALACION
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, clean("3. REQUISITOS"), 0, 1)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 8, clean(f"DEPOSITO FINAL: {int(res['v_final'])} Litros"), 0, 1)
    pdf.set_text_color(200, 0, 0)
    pdf.cell(0, 8, clean(f"ACOMETIDA REQUERIDA: {int(res.get('wash', 0))} L/h a 2.5 bar"), 0, 1)
    pdf.set_text_color(0,0,0)
    
    return pdf.output(dest='S').encode('latin-1')

# ==============================================================================
# 3. INTERFAZ Y PANEL DE ADMINISTRACIÓN
# ==============================================================================
c_head1, c_head2 = st.columns([1, 5])
with c_head1:
    try: st.image("logo.png", width=120)
    except: st.warning("Logo?")
with c_head2:
    empresa = st.session_state.get("user_info", {}).get("empresa", "HYDROLOGIC")
    st.markdown('<p class="brand-logo">HYDROLOGIC</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="brand-sub">LICENCIA: {empresa}</p>', unsafe_allow_html=True)

st.divider()

col_sb, col_main = st.columns([1, 2.5])

with col_sb:
    # --- PANEL ADMIN (SOLO VISIBLE PARA ADMIN) ---
    rol = st.session_state.get("user_info", {}).get("rol", "cliente")
    
    if rol == "admin":
        st.markdown("""<div class="admin-panel">👑 <b>PANEL GESTIÓN CLIENTES</b></div>""", unsafe_allow_html=True)
        with st.expander("Crear Nuevo Usuario"):
            new_user = st.text_input("Usuario (Login)")
            new_pass = st.text_input("Contraseña")
            new_company = st.text_input("Nombre Empresa")
            if st.button("➕ Crear Cliente"):
                try:
                    supabase.table("usuarios").insert({
                        "username": new_user,
                        "password": new_pass,
                        "empresa": new_company,
                        "rol": "cliente",
                        "activo": True
                    }).execute()
                    st.success(f"Usuario {new_user} creado!")
                except Exception as e:
                    st.error(f"Error: {e}")
        st.markdown("---")

    if st.button("Cerrar Sesión"):
        st.session_state["auth"] = False
        st.rerun()
    st.subheader("Configuración")
    origen = st.selectbox("Origen", ["Red Pública", "Pozo"])
    modo = st.selectbox("Modo", ["Planta Completa (RO)", "Solo Descalcificación"])
    consumo = st.number_input("Consumo Diario (L)", value=2000, step=100)
    caudal_punta = st.number_input("Caudal Punta (L/min)", value=40)
    horas = st.number_input("Horas Prod", value=20)
    buffer = st.checkbox("Buffer Intermedio", value=True) if "RO" in modo else False
    descal = st.checkbox("Descalcificador", value=True) if "RO" in modo else True
    ppm = st.number_input("TDS (ppm)", value=800) if "RO" in modo else 0
    dureza = st.number_input("Dureza (Hf)", value=35)
    temp = st.number_input("Temp (C)", value=15) if "RO" in modo else 25
    with st.expander("Costes / Manual"):
        ca = st.number_input("Agua €", value=1.5); cs = st.number_input("Sal €", value=0.45); cl = st.number_input("Luz €", value=0.20)
        mf = st.number_input("Dep Final (L)", value=0); mb = st.number_input("Buffer (L)", value=0)
    costes = {'agua': ca, 'sal': cs, 'luz': cl}
    if st.button("CALCULAR", type="primary", use_container_width=True): st.session_state['run'] = True

if st.session_state.get('run'):
    res = calcular(origen, modo, consumo, caudal_punta, ppm, dureza, temp, horas, costes, buffer, descal, mf, mb)
    if res.get('ro') or res.get('descal'):
        # ... (VISUALIZACIÓN DASHBOARD IGUAL QUE V50) ...
        # ... (Solo cambia la llamada al PDF para pasar 'empresa') ...
        try:
            inputs_pdf = {'consumo': consumo, 'horas': horas, 'origen': origen, 'ppm': ppm, 'dureza': dureza, 'punta': caudal_punta}
            pdf_data = create_pdf(res, inputs_pdf, modo, empresa)
            b64 = base64.b64encode(pdf_data).decode()
            col_main.markdown(f'<a href="data:application/octet-stream;base64,{b64}" download="informe_{empresa}.pdf"><button style="background:#00e5ff;color:black;width:100%;padding:15px;border:none;border-radius:10px;font-weight:bold;">📥 DESCARGAR INFORME {empresa.upper()}</button></a>', unsafe_allow_html=True)
        except Exception as e:
            col_main.error(f"Error PDF: {e}")
            
        # [AQUÍ IRÍA EL RESTO DE TU CÓDIGO DE VISUALIZACIÓN DE GRÁFICOS Y TARJETAS V50]
        # (He resumido para no repetir, usa el bloque de visualización de V50 pero con este cambio en el PDF)
    else:
        col_main.error("Sin solución estándar.")
else:
    col_main.info("Sistema listo. Introduce parámetros.")
