import streamlit as st
from fpdf import FPDF
import base64

# ==============================================================================
# 0. CONFIGURACIÓN Y ESTILOS
# ==============================================================================
st.set_page_config(
    page_title="AimyWater V17 Plant",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

def local_css():
    st.markdown("""
    <style>
        .stApp { background-color: #ffffff; color: #000000; }
        
        div[data-testid="stMetric"] {
            background-color: #f8f9fa !important;
            border: 1px solid #dee2e6 !important;
            padding: 10px !important;
            border-radius: 8px !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        div[data-testid="stMetricLabel"] { color: #6c757d !important; }
        div[data-testid="stMetricValue"] { color: #003366 !important; }
        h1, h2, h3 { color: #004d99 !important; }
        
        /* Botón destacado */
        div.stButton > button:first-child {
            background-color: #004d99 !important;
            color: white !important;
            border-radius: 5px;
            height: 3em;
            font-weight: bold;
            border: none;
        }
    </style>
    """, unsafe_allow_html=True)

local_css()

# ==============================================================================
# 1. BASE DE DATOS
# ==============================================================================

class EquipoRO:
    def __init__(self, categoria, nombre, produccion_nominal, max_ppm, eficiencia, potencia_kw):
        self.categoria = categoria
        self.nombre = nombre
        self.produccion_nominal = produccion_nominal
        self.max_ppm = max_ppm
        self.eficiencia = eficiencia
        self.potencia_kw = potencia_kw

class PreTratamiento:
    def __init__(self, tipo_equipo, nombre, medida_botella, caudal_max_m3h, capacidad_intercambio=0, sal_kg=0, tipo_valvula=""):
        self.tipo_equipo = tipo_equipo 
        self.nombre = nombre
        self.medida_botella = medida_botella 
        self.caudal_max_m3h = caudal_max_m3h
        self.capacidad_intercambio = capacidad_intercambio 
        self.sal_kg = sal_kg 
        self.tipo_valvula = tipo_valvula 

# --- CATÁLOGOS ---
catalogo_ro = [
    EquipoRO("Doméstico", "PURHOME PLUS", 300, 3000, 0.50, 0.03),
    EquipoRO("Doméstico", "DF 800 UV-LED", 3000, 1500, 0.71, 0.08),
    EquipoRO("Doméstico", "Direct Flow 1200", 4500, 1500, 0.66, 0.10),
    EquipoRO("Industrial", "ALFA 140", 5000, 2000, 0.50, 0.75),
    EquipoRO("Industrial", "ALFA 240", 10000, 2000, 0.50, 1.1),
    EquipoRO("Industrial", "ALFA 440", 20000, 2000, 0.60, 1.1),
    EquipoRO("Industrial", "ALFA 640", 30000, 2000, 0.60, 2.2),
    EquipoRO("Industrial", "AP-6000 LUXE", 18000, 6000, 0.60, 2.2),
]

catalogo_descal = [
    PreTratamiento("Descalcificador", "BI BLOC 30L IMPRESSION", "10x35", 1.8, 192, 4.5, "Simplex"),
    PreTratamiento("Descalcificador", "BI BLOC 60L IMPRESSION", "12x48", 3.6, 384, 9.0, "Simplex"),
    PreTratamiento("Descalcificador", "BI BLOC 100L IMPRESSION", "14x65", 6.0, 640, 15.0, "Simplex"),
    PreTratamiento("Descalcificador", "TWIN 40L DF IMPRESSION", "10x44", 2.4, 256, 6.0, "Duplex"),
    PreTratamiento("Descalcificador", "TWIN 100L DF IMPRESSION", "14x65", 6.0, 640, 15.0, "Duplex"),
    PreTratamiento("Descalcificador", "TWIN 140L DF IMPRESSION", "16x65", 6.0, 896, 25.0, "Duplex"),
    PreTratamiento("Descalcificador", "DUPLEX 300L IMPRESSION 1.5\"", "24x69", 6.5, 1800, 45.0, "Duplex"),
]

catalogo_carbon = [
    PreTratamiento("Carbon", "DEC 14KG/30L IMPRESSION 1\"", "10x35", 0.38, 0, 0, "Impression 1\""),
    PreTratamiento("Carbon", "DEC 22KG/45L IMPRESSION 1\"", "10x54", 0.72, 0, 0, "Impression 1\""),
    PreTratamiento("Carbon", "DEC 28KG/60L IMPRESSION 1\"", "12x48", 0.80, 0, 0, "Impression 1\""),
    PreTratamiento("Carbon", "DEC 37KG/75L IMPRESSION 1\"", "13x54", 1.10, 0, 0, "Impression 1\""),
    PreTratamiento("Carbon", "DEC 90KG IMPRESSION 1 1/4\"", "18x65", 2.68, 0, 0, "Impression 1 1/4\""),
]

catalogo_silex = [
    PreTratamiento("Silex", "FILTRO SILEX 10x35 IMPRESSION 1\"", "10x35", 0.8, 0, 0, "Impression 1\""),
    PreTratamiento("Silex", "FILTRO SILEX 10x44 IMPRESSION 1\"", "10x44", 0.8, 0, 0, "Impression 1\""),
    PreTratamiento("Silex", "FILTRO SILEX 12x48 IMPRESSION 1\"", "12x48", 1.1, 0, 0, "Impression 1\""),
    PreTratamiento("Silex", "FILTRO SILEX 18x65 IMPRESSION 1.25\"", "18x65", 2.6, 0, 0, "Impression 1 1/4\""),
    PreTratamiento("Silex", "FILTRO SILEX 21x60 IMPRESSION 1.25\"", "21x60", 3.6, 0, 0, "Impression 1 1/4\""),
    PreTratamiento("Silex", "FILTRO SILEX 24x69 IMPRESSION 1.25\"", "24x69", 4.4, 0, 0, "Impression 1 1/4\""),
    PreTratamiento("Silex", "FILTRO SILEX 30x72 IMPRESSION 1.5\"", "30x72", 7.0, 0, 0, "Impression 1 1/2\""),
    PreTratamiento("Silex", "FILTRO SILEX 36x72 IMPRESSION 2\"", "36x72", 10.0, 0, 0, "Impression 2\""),
]

# ==============================================================================
# 2. MOTOR DE CÁLCULO
# ==============================================================================

def generar_pdf_tecnico(ro, descal, carbon, silex, flow, blending_pct, consumo, ppm_in, ppm_out, dureza, usar_buffer, activar_descal, volumen_buffer):
    pdf = FPDF()
    pdf.add_page()
    
    try: pdf.image('logo.png', 10, 8, 33)
    except: pass
    pdf.ln(20)

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "PROYECTO DE PLANTA DE TRATAMIENTO", 0, 1, 'C')
    pdf.ln(5)

    # 1. Datos
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, "1. BASES DE DISEÑO", 1, 1, 'L', 1)
    pdf.set_font("Arial", size=10)
    pdf.cell(95, 8, f"Consumo Objetivo: {consumo} L/dia", 1)
    pdf.cell(95, 8, f"Salinidad Entrada: {ppm_in} ppm", 1, 1)
    
    modo_flujo = "Con Deposito Intermedio (Buffer)" if usar_buffer else "Alimentacion Directa"
    pdf.cell(95, 8, f"Configuracion Hidraulica: {modo_flujo}", 1)
    pdf.cell(95, 8, f"Salinidad Salida: {ppm_out} ppm", 1, 1)
    pdf.ln(5)

    # 2. Equipos
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, "2. TREN DE TRATAMIENTO", 1, 1, 'L', 1)
    
    # Silex
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 8, "A. FILTRACION (SILEX-ANTRACITA)", 0, 1)
    pdf.set_font("Arial", size=10)
    if silex:
        pdf.cell(10, 8, "", 0, 0)
        pdf.cell(0, 6, f"Equipo: {silex.nombre} ({silex.medida_botella})", 0, 1)
    else:
        pdf.cell(10, 8, "", 0, 0)
        pdf.cell(0, 6, "Fuera de rango estandar", 0, 1)

    # Carbon
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 8, "B. DECLORACION (CARBON ACTIVO)", 0, 1)
    pdf.set_font("Arial", size=10)
    if carbon:
        pdf.cell(10, 8, "", 0, 0)
        pdf.cell(0, 6, f"Equipo: {carbon.nombre} ({carbon.medida_botella})", 0, 1)
    else:
        pdf.cell(10, 8, "", 0, 0)
        pdf.cell(0, 6, "Fuera de rango estandar", 0, 1)

    # Buffer (Si aplica)
    if usar_buffer:
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 8, "C. ACUMULACION INTERMEDIA (BUFFER)", 0, 1)
        pdf.set_font("Arial", size=10)
        pdf.cell(10, 8, "", 0, 0)
        pdf.cell(0, 6, f"Deposito Recomendado: {int(volumen_buffer)} Litros", 0, 1)
        pdf.cell(10, 8, "", 0, 0)
        pdf.cell(0, 6, "Funcion: Desacoplar velocidad de filtracion de la osmosis.", 0, 1)

    # Descal / Antiscalant
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 8, "D. ACONDICIONAMIENTO QUIMICO", 0, 1)
    pdf.set_font("Arial", size=10)
    if activar_descal and descal:
        pdf.cell(10, 8, "", 0, 0)
        pdf.cell(0, 6, f"Descalcificador: {descal[0].nombre}", 0, 1)
    elif not activar_descal and dureza > 5:
        pdf.cell(10, 8, "", 0, 0)
        pdf.cell(0, 6, "Metodo: DOSIFICACION DE ANTIINCRUSTANTE (Requerido)", 0, 1)
    else:
        pdf.cell(10, 8, "", 0, 0)
        pdf.cell(0, 6, "No requerido (Agua blanda)", 0, 1)

    # RO
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 8, f"E. OSMOSIS INVERSA: {ro.nombre}", 0, 1)
    pdf.set_font("Arial", size=10)
    pdf.cell(10, 8, "", 0, 0)
    pdf.cell(0, 6, f"Produccion Nominal: {ro.produccion_nominal} L/dia", 0, 1)
    if blending_pct > 0:
        pdf.cell(10, 8, "", 0, 0)
        pdf.cell(0, 6, f"Mezcla (Bypass): {blending_pct:.1f}% ({int(flow['caudal_bypass_dia'])} L/dia)", 0, 1)

    return pdf.output(dest='S').encode('latin-1')

def calcular_logica(consumo, ppm_in, ppm_out, dureza, temp, horas, coste_agua, coste_sal, coste_luz, usar_buffer, activar_descal):
    tcf = 1.0 if temp >= 25 else max(1.0 - ((25 - temp) * 0.03), 0.1)
    
    # 1. BLENDING & RO
    ppm_ro = ppm_in * 0.05
    if ppm_out < ppm_ro: ppm_out = ppm_ro
    
    pct_ro = 1.0 if ppm_in == ppm_ro else (ppm_in - ppm_out) / (ppm_in - ppm_ro)
    pct_ro = max(0.0, min(1.0, pct_ro))
    
    litros_ro = consumo * pct_ro
    litros_bypass = consumo - litros_ro

    # Selección RO
    ro_sel = None
    candidatos = []
    for ro in catalogo_ro:
        if ppm_in <= ro.max_ppm:
            factor = 1.0 if ro.categoria == "Industrial" else 0.4
            if (ro.produccion_nominal * tcf * factor) >= litros_ro:
                candidatos.append(ro)
    
    if candidatos:
        ro_sel = next((x for x in candidatos if x.categoria == "Industrial"), candidatos[-1]) if litros_ro > 600 else next((x for x in candidatos if x.categoria == "Doméstico"), candidatos[0])

    descal_sel = None
    carbon_sel = None
    silex_sel = None
    flow = {}
    opex = {}
    volumen_buffer = 0
    alerta_autonomia = None
    
    if ro_sel:
        # --- CÁLCULO DE CAUDALES (LA CLAVE DE LA V17) ---
        
        agua_entrada_ro_dia = litros_ro / ro_sel.eficiencia
        agua_alimentacion_total_dia = agua_entrada_ro_dia + litros_bypass
        
        # Caudal instantáneo que chupa la bomba de RO (L/h)
        caudal_bomba_ro_lh = (ro_sel.produccion_nominal / 24 / ro_sel.eficiencia) * 1.5 
        
        if usar_buffer:
            # LÓGICA BUFFER:
            # Los filtros trabajan suaves 20h al día para llenar el depósito.
            # La RO chupa del depósito a su velocidad máxima.
            caudal_calculo_filtros = agua_alimentacion_total_dia / 20 # Dejamos 4h para lavados
            
            # Dimensionado del depósito (Buffer)
            # Debe aguantar al menos 2 horas de operación a tope de la RO para no ciclar
            volumen_buffer = caudal_bomba_ro_lh * 2 
        else:
            # LÓGICA DIRECTA:
            # Los filtros deben dar el caudal instantáneo que pide la bomba de RO
            caudal_calculo_filtros = caudal_bomba_ro_lh + (litros_bypass / horas)
            volumen_buffer = 0

        flow = {
            "agua_entrada_total": agua_alimentacion_total_dia,
            "prod_ro_dia": litros_ro,
            "caudal_bypass_dia": litros_bypass,
            "prod_total_dia": consumo,
            "rechazo": agua_entrada_ro_dia - litros_ro,
            "prod_real_dia": ro_sel.produccion_nominal * tcf,
            "blending_pct": (litros_bypass / consumo) * 100,
            "caudal_diseno_filtros": caudal_calculo_filtros # Dato clave para debug
        }

        # 3. SELECCIÓN FILTROS (Usando el caudal calculado según modo)
        
        # Silex
        cands_silex = [s for s in catalogo_silex if (s.caudal_max_m3h * 1000) >= caudal_calculo_filtros]
        if cands_silex:
            cands_silex.sort(key=lambda x: x.caudal_max_m3h)
            silex_sel = cands_silex[0]

        # Carbon
        cands_carbon = [c for c in catalogo_carbon if (c.caudal_max_m3h * 1000) >= caudal_calculo_filtros]
        if cands_carbon:
            cands_carbon.sort(key=lambda x: x.caudal_max_m3h)
            carbon_sel = cands_carbon[0]

        # 4. DESCALCIFICADOR (Solo si está activado)
        if activar_descal and dureza > 5:
            carga = (agua_alimentacion_total_dia / 1000) * dureza
            
            cands_validos = []   
            cands_fallback = []  
            es_ind = ro_sel.categoria == "Industrial"
            
            for d in catalogo_descal:
                if (d.caudal_max_m3h * 1000) >= caudal_calculo_filtros:
                    dias = d.capacidad_intercambio / carga if carga > 0 else 99
                    if dias >= 5.0: cands_validos.append((d, dias))
                    else: cands_fallback.append((d, dias))
            
            if cands_validos:
                cands_validos.sort(key=lambda x: (0 if "Duplex" in x[0].tipo_valvula and es_ind else 1, x[0].medida_botella))
                descal_sel = cands_validos[0]
            elif cands_fallback:
                cands_fallback.sort(key=lambda x: x[0].caudal_max_m3h, reverse=True)
                descal_sel = cands_fallback[0]
                alerta_autonomia = f"⚠️ Autonomía: {descal_sel[1]:.1f} días"

        # OPEX
        c_agua = (agua_alimentacion_total_dia / 1000) * 365 * coste_agua
        c_sal, kg_sal = 0, 0
        if descal_sel:
            kg_sal = (365 / descal_sel[1]) * descal_sel[0].sal_kg
            c_sal = kg_sal * coste_sal
        
        horas_marcha = litros_ro / ((ro_sel.produccion_nominal * tcf)/24)
        c_elec = horas_marcha * ro_sel.potencia_kw * 365 * coste_luz
        
        opex = {"total": c_agua + c_sal + c_elec, "agua": c_agua, "sal": c_sal, "elec": c_elec, "kg_sal": kg_sal}

    return ro_sel, descal_sel, carbon_sel, silex_sel, flow, opex, alerta_autonomia, volumen_buffer

# ==============================================================================
# 3. INTERFAZ
# ==============================================================================

col_logo, col_header = st.columns([1, 5])
with col_logo:
    try: st.image("logo.png", width=150)
    except: st.warning("Logo?")
with col_header:
    st.title("AimyWater Architect V17")
    st.markdown("**Plataforma de Dimensionamiento con Depósito Intermedio**")

st.markdown("---")

with st.sidebar:
    st.header("⚙️ Configuración")
    
    with st.expander("1. Hidráulica & Proceso", expanded=True):
        consumo = st.number_input("Caudal Diario (L)", 100, 100000, 5000, step=500)
        horas = st.slider("Horas Trabajo Planta", 1, 24, 12)
        # NUEVOS CONTROLES
        usar_buffer = st.checkbox("Usar Depósito Intermedio (Buffer)", value=True, help="Permite dimensionar filtros más pequeños trabajando 20h/día")
        activar_descal = st.checkbox("Incluir Descalcificador", value=True, help="Desmarcar para usar Antiincrustante")

    with st.expander("2. Calidad Agua", expanded=True):
        ppm_in = st.number_input("TDS Entrada", 50, 8000, 800)
        ppm_out = st.slider("TDS Objetivo", 0, 1000, 50)
        dureza = st.number_input("Dureza (ºHf)", 0, 100, 35)
        temp = st.slider("Temp (ºC)", 5, 35, 15)
        
    with st.expander("3. Costes"):
        coste_agua = st.number_input("Agua €/m3", 0.0, 10.0, 1.5)
        coste_sal = st.number_input("Sal €/kg", 0.0, 5.0, 0.45)
        coste_luz = st.number_input("Luz €/kWh", 0.0, 1.0, 0.20)
    
    st.markdown("---")
    btn_calc = st.button("CALCULAR PLANTA", type="primary")

if btn_calc:
    ro, descal, carbon, silex, flow, opex, alerta, v_buffer = calcular_logica(consumo, ppm_in, ppm_out, dureza, temp, horas, coste_agua, coste_sal, coste_luz, usar_buffer, activar_descal)
    
    if not ro:
        st.error("❌ Sin solución viable.")
    else:
        # --- RESUMEN ---
        st.subheader("✅ Diseño de Planta")
        
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Ósmosis Inversa", ro.nombre)
        
        modo_txt = "Con Depósito" if usar_buffer else "Directo"
        k2.metric("Modo Operación", modo_txt)
        
        k3.metric("Caudal Filtración", f"{int(flow['caudal_diseno_filtros'])} L/h", "Velocidad de paso")
        
        if not activar_descal and dureza > 5:
            k4.metric("Acondicionamiento", "Antiincrustante", "Químico", delta_color="off")
        elif descal:
            k4.metric("Descalcificador", descal[0].nombre)
        else:
            k4.metric("Descalcificador", "No requerido")

        st.markdown("---")
        
        # --- DETALLE EQUIPOS ---
        c1, c2 = st.columns(2)
        
        with c1:
            st.info("💧 LÍNEA DE FILTRACIÓN (PRE-TRATAMIENTO)")
            
            # Silex
            if silex: st.write(f"**1. Silex:** {silex.nombre} ({silex.medida_botella})")
            else: st.error("1. Silex: Caudal excesivo")
                
            # Carbon
            if carbon: st.write(f"**2. Carbón:** {carbon.nombre} ({carbon.medida_botella})")
            else: st.error("2. Carbón: Caudal excesivo (Usar Bisulfito)")
            
            # Buffer
            if usar_buffer:
                st.success(f"🛢️ **Depósito Intermedio:** {int(v_buffer)} Litros")
                st.caption("Acumulación necesaria antes de la ósmosis.")
                
            # Descal / Antiincrustante
            if activar_descal and descal:
                st.write(f"**3. Descal:** {descal[0].nombre}")
                if alerta: st.warning(alerta)
            elif not activar_descal and dureza > 5:
                st.write("**3. Acond:** Dosificación de Antiincrustante")

        with c2:
            st.info("⚡ LÍNEA DE PRODUCCIÓN (OSMOSIS)")
            st.write(f"**Equipo:** {ro.nombre}")
            st.write(f"Producción Pura: {int(flow['prod_ro_dia'])} L/d")
            st.write(f"Bypass (Mezcla): {int(flow['caudal_bypass_dia'])} L/d")
            st.write(f"Consumo Total: {int(flow['prod_total_dia'])} L/d")

        st.markdown("---")
        
        # --- PDF ---
        col_pdf, _ = st.columns([1, 4])
        with col_pdf:
            try:
                pdf_bytes = generar_pdf_tecnico(ro, descal, carbon, silex, flow, flow['blending_pct'], consumo, ppm_in, ppm_out, dureza, alerta)
                b64 = base64.b64encode(pdf_bytes).decode()
                href = f'<a href="data:application/octet-stream;base64,{b64}" download="informe_planta_aimywater.pdf" style="text-decoration:none;"><button style="background-color:#cc0000;color:white;padding:10px;border-radius:5px;border:none;cursor:pointer;width:100%;">📄 Descargar PDF Planta</button></a>'
                st.markdown(href, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error PDF: {e}")

else:
    st.info("👈 Pulsa Calcular.")
