import streamlit as st
from fpdf import FPDF
import base64

# ==============================================================================
# 0. CONFIGURACIÓN Y ESTILOS
# ==============================================================================
st.set_page_config(
    page_title="AimyWater Master V14",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

def local_css():
    st.markdown("""
    <style>
        .stApp { background-color: #ffffff; color: #000000; }
        
        /* Tarjetas */
        div[data-testid="stMetric"] {
            background-color: #f8f9fa !important;
            border: 1px solid #dee2e6 !important;
            padding: 10px !important;
            border-radius: 8px !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        /* Textos */
        div[data-testid="stMetricLabel"] { color: #6c757d !important; }
        div[data-testid="stMetricValue"] { color: #003366 !important; }
        h1, h2, h3 { color: #004d99 !important; }
        
        /* Botón */
        div.stButton > button:first-child {
            background-color: #004d99 !important;
            color: white !important;
            border-radius: 5px;
            height: 3em;
            font-weight: bold;
            border: none;
        }
        div.stButton > button:first-child:hover {
            background-color: #003366 !important;
        }
    </style>
    """, unsafe_allow_html=True)

local_css()

# ==============================================================================
# 1. BASE DE DATOS (CLASES Y CATÁLOGOS REALES)
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
    def __init__(self, tipo_equipo, nombre, litros_medio, caudal_max_m3h, capacidad_intercambio=0, sal_kg=0, tipo_valvula=""):
        self.tipo_equipo = tipo_equipo 
        self.nombre = nombre
        self.litros_medio = litros_medio 
        self.caudal_max_m3h = caudal_max_m3h
        self.capacidad_intercambio = capacidad_intercambio 
        self.sal_kg = sal_kg 
        self.tipo_valvula = tipo_valvula 

# --- 1. CATÁLOGO ÓSMOSIS ---
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

# --- 2. CATÁLOGO DESCALCIFICADORES (Actualizado con Duplex 300L) ---
catalogo_descal = [
    PreTratamiento("Descalcificador", "BI BLOC 30L IMPRESSION", 30, 1.8, 192, 4.5, "Simplex"),
    PreTratamiento("Descalcificador", "BI BLOC 60L IMPRESSION", 60, 3.6, 384, 9.0, "Simplex"),
    PreTratamiento("Descalcificador", "BI BLOC 100L IMPRESSION", 100, 6.0, 640, 15.0, "Simplex"),
    PreTratamiento("Descalcificador", "TWIN 40L DF IMPRESSION", 40, 2.4, 256, 6.0, "Duplex"),
    PreTratamiento("Descalcificador", "TWIN 100L DF IMPRESSION", 100, 6.0, 640, 15.0, "Duplex"),
    PreTratamiento("Descalcificador", "TWIN 140L DF IMPRESSION", 140, 6.0, 896, 25.0, "Duplex"),
    # NUEVO EQUIPO AÑADIDO DEL PDF
    PreTratamiento("Descalcificador", "DUPLEX 300L IMPRESSION 1.5\"", 300, 6.5, 1800, 45.0, "Duplex"),
]

# --- 3. CATÁLOGO FILTROS CARBÓN (DATOS REALES GRUPAGUA) ---
catalogo_carbon = [
    # Datos extraídos de tus PDFs (Caudal muy restrictivo para decloración efectiva)
    PreTratamiento("Carbon", "DEC 14KG/30L IMPRESSION 1\"", 30, 0.38, 0, 0, "Impression 1\""),
    PreTratamiento("Carbon", "DEC 22KG/45L IMPRESSION 1\"", 45, 0.72, 0, 0, "Impression 1\""),
    PreTratamiento("Carbon", "DEC 28KG/60L IMPRESSION 1\"", 60, 0.80, 0, 0, "Impression 1\""),
    PreTratamiento("Carbon", "DEC 37KG/75L IMPRESSION 1\"", 75, 1.10, 0, 0, "Impression 1\""),
    PreTratamiento("Carbon", "DEC 90KG IMPRESSION 1 1/4\"", 180, 2.68, 0, 0, "Impression 1 1/4\""),
]

# ==============================================================================
# 2. MOTOR DE CÁLCULO
# ==============================================================================

def generar_pdf_tecnico(ro, descal, carbon, flow, blending_pct, consumo, ppm_in, ppm_out, dureza):
    pdf = FPDF()
    pdf.add_page()
    
    # Logo (si existe)
    try:
        pdf.image('logo.png', 10, 8, 33)
        pdf.ln(20)
    except:
        pdf.ln(10)

    # Título
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "INFORME TÉCNICO DE DIMENSIONAMIENTO", 0, 1, 'C')
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, "Generado por AimyWater Engineering AI", 0, 1, 'C')
    pdf.ln(5)

    # Sección 1: Requerimientos
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, "1. DATOS DE PARTIDA", 1, 1, 'L', 1)
    pdf.set_font("Arial", size=10)
    pdf.cell(95, 8, f"Consumo Diario: {consumo} L/dia", 1)
    pdf.cell(95, 8, f"Salinidad Entrada: {ppm_in} ppm", 1, 1)
    pdf.cell(95, 8, f"Dureza: {dureza} Hf", 1)
    pdf.cell(95, 8, f"Salinidad Objetivo: {ppm_out} ppm", 1, 1)
    pdf.ln(5)

    # Sección 2: Solución Propuesta
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, "2. EQUIPOS SELECCIONADOS", 1, 1, 'L', 1)
    
    # RO
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 8, f"A. OSMOSIS INVERSA: {ro.nombre}", 0, 1)
    pdf.set_font("Arial", size=10)
    pdf.cell(10, 8, "", 0, 0)
    pdf.cell(0, 6, f"- Tecnologia: {ro.categoria} ({ro.potencia_kw} kW)", 0, 1)
    pdf.cell(10, 8, "", 0, 0)
    pdf.cell(0, 6, f"- Produccion Nominal: {ro.produccion_nominal} L/dia", 0, 1)
    pdf.cell(10, 8, "", 0, 0)
    pdf.cell(0, 6, f"- Produccion Real Calculada: {int(flow['prod_real_dia'])} L/dia", 0, 1)
    if blending_pct > 0:
        pdf.cell(10, 8, "", 0, 0)
        pdf.cell(0, 6, f"- Sistema Blending (Mezcla): {blending_pct:.1f}% ({int(flow['caudal_bypass_dia'])} L/dia)", 0, 1)

    # Pretratamiento
    pdf.ln(2)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 8, "B. PRE-TRATAMIENTO", 0, 1)
    pdf.set_font("Arial", size=10)
    
    # Carbon
    if carbon:
        pdf.cell(10, 8, "", 0, 0)
        pdf.cell(0, 6, f"- Decloracion: {carbon.nombre}", 0, 1)
        pdf.cell(20, 8, "", 0, 0)
        pdf.cell(0, 6, f"Volumen: {carbon.litros_medio}L | Valvula: {carbon.tipo_valvula}", 0, 1)
    else:
        pdf.cell(10, 8, "", 0, 0)
        pdf.cell(0, 6, "- Decloracion: CONSULTAR (Caudal excesivo para estandar)", 0, 1)

    # Descal
    if descal:
        pdf.cell(10, 8, "", 0, 0)
        pdf.cell(0, 6, f"- Descalcificacion: {descal[0].nombre}", 0, 1)
        pdf.cell(20, 8, "", 0, 0)
        pdf.cell(0, 6, f"Config: {descal[0].tipo_valvula} | Regeneracion estimada: cada {descal[1]:.1f} dias", 0, 1)
    else:
        pdf.cell(10, 8, "", 0, 0)
        pdf.cell(0, 6, "- Descalcificacion: No requerida o no seleccionada", 0, 1)

    pdf.ln(5)
    
    # Sección 3: Balance
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, "3. BALANCE HIDRAULICO", 1, 1, 'L', 1)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 8, f"Caudal Alimentacion Total (Entrada): {int(flow['agua_entrada_total'])} L/dia", 0, 1)
    pdf.cell(0, 8, f"Caudal Rechazo (Desague): {int(flow['rechazo'])} L/dia", 0, 1)
    pdf.cell(0, 8, f"Caudal Producto Final: {int(flow['prod_total_dia'])} L/dia", 0, 1)

    return pdf.output(dest='S').encode('latin-1')

def calcular_arquitecto(consumo, ppm_in, ppm_out, dureza, temp, horas, coste_agua, coste_sal, coste_luz):
    tcf = 1.0 if temp >= 25 else max(1.0 - ((25 - temp) * 0.03), 0.1)
    
    # 1. BLENDING
    ppm_ro = ppm_in * 0.05
    if ppm_out < ppm_ro: ppm_out = ppm_ro
    
    if ppm_in == ppm_ro:
        pct_ro = 1.0
    else:
        pct_ro = (ppm_in - ppm_out) / (ppm_in - ppm_ro)
        pct_ro = max(0.0, min(1.0, pct_ro))
    
    litros_ro_necesarios = consumo * pct_ro
    litros_bypass = consumo - litros_ro_necesarios

    # 2. SELECCIÓN RO
    ro_sel = None
    candidatos = []
    for ro in catalogo_ro:
        if ppm_in <= ro.max_ppm:
            factor_uso = 1.0 if ro.categoria == "Industrial" else 0.4
            cap_real = ro.produccion_nominal * tcf * factor_uso
            if cap_real >= litros_ro_necesarios:
                candidatos.append(ro)
    
    if candidatos:
        ro_sel = next((x for x in candidatos if x.categoria == "Industrial"), candidatos[-1]) if litros_ro_necesarios > 600 else next((x for x in candidatos if x.categoria == "Doméstico"), candidatos[0])

    descal_sel = None
    carbon_sel = None
    flow = {}
    opex = {}
    
    if ro_sel:
        # Balance Hidráulico
        agua_entrada_ro = litros_ro_necesarios / ro_sel.eficiencia
        # Caudal punta que traga la RO (L/h)
        caudal_alim_ro_lh = (ro_sel.produccion_nominal / 24 / ro_sel.eficiencia) * 1.5 
        # El caudal punta total incluye el bypass si este pasa por el pretratamiento
        # Asumimos peor caso: Todo el agua pasa por pretratamiento
        caudal_bypass_lh = litros_bypass / horas
        caudal_punta_tratamiento_lh = caudal_alim_ro_lh + caudal_bypass_lh
        
        agua_entrada_total = agua_entrada_ro + litros_bypass

        flow = {
            "agua_entrada_total": agua_entrada_total,
            "prod_ro_dia": litros_ro_necesarios,
            "caudal_bypass_dia": litros_bypass,
            "prod_total_dia": consumo,
            "rechazo": agua_entrada_ro - litros_ro_necesarios,
            "prod_real_dia": ro_sel.produccion_nominal * tcf,
            "blending_pct": (litros_bypass / consumo) * 100
        }

        # 3. SELECCIÓN CARBÓN (MÁS ESTRICTO AHORA)
        cands_carbon = []
        for c in catalogo_carbon:
            if (c.caudal_max_m3h * 1000) >= caudal_punta_tratamiento_lh:
                cands_carbon.append(c)
        if cands_carbon:
            # Ordenar por tamaño (menor a mayor)
            cands_carbon.sort(key=lambda x: x.litros_medio)
            carbon_sel = cands_carbon[0]

        # 4. SELECCIÓN DESCALCIFICADOR
        if dureza > 5:
            carga = (agua_entrada_total / 1000) * dureza
            cands_soft = []
            es_ind = ro_sel.categoria == "Industrial"
            
            for d in catalogo_descal:
                if (d.caudal_max_m3h * 1000) >= caudal_punta_tratamiento_lh:
                    dias = d.capacidad_intercambio / carga if carga > 0 else 99
                    viable = False
                    if es_ind and consumo > 5000:
                        if "Duplex" in d.tipo_valvula or dias > 1: viable = True
                    else:
                        if dias >= 0.8: viable = True
                    if viable: cands_soft.append((d, dias))
            
            if cands_soft:
                # Priorizar Duplex si es industrial, luego tamaño
                cands_soft.sort(key=lambda x: (0 if "Duplex" in x[0].tipo_valvula and es_ind else 1, x[0].litros_medio))
                descal_sel = cands_soft[0]

        # OPEX
        c_agua = (agua_entrada_total / 1000) * 365 * coste_agua
        c_sal = 0
        kg_sal = 0
        if descal_sel:
            eq, dias = descal_sel
            kg_sal = (365 / dias) * eq.sal_kg
            c_sal = kg_sal * coste_sal
        
        # Horas de la bomba RO (solo el agua que pasa por RO)
        horas_marcha_ro = litros_ro_necesarios / ((ro_sel.produccion_nominal * tcf)/24)
        c_elec = horas_marcha_ro * ro_sel.potencia_kw * 365 * coste_luz
        
        opex = {"total": c_agua + c_sal + c_elec, "agua": c_agua, "sal": c_sal, "elec": c_elec, "kg_sal": kg_sal}

    return ro_sel, descal_sel, carbon_sel, flow, opex

# ==============================================================================
# 3. INTERFAZ GRÁFICA
# ==============================================================================

col_logo, col_header = st.columns([1, 5])
with col_logo:
    try: st.image("logo.png", width=150)
    except: st.warning("Subir logo.png")
with col_header:
    st.title("AimyWater Architect V14")
    st.markdown("**Plataforma de Dimensionamiento con Catálogo Real Grupagua**")

st.markdown("---")

with st.sidebar:
    st.header("⚙️ Datos de Entrada")
    
    with st.expander("1. Demanda y Calidad", expanded=True):
        consumo = st.number_input("Caudal Diario (L/día)", 100, 100000, 2000, step=100)
        horas = st.slider("Horas de Trabajo Disponibles", 1, 24, 8)
        ppm_in = st.number_input("TDS Entrada (ppm)", 50, 8000, 800)
        ppm_out = st.slider("TDS Salida Objetivo (Mezcla)", 0, 1000, 50)
        dureza = st.number_input("Dureza (ºHf)", 0, 100, 35)
        temp = st.slider("Temperatura (ºC)", 5, 35, 15)
        
    with st.expander("2. Costes (€)"):
        coste_agua = st.number_input("Agua (€/m3)", 0.0, 10.0, 1.5)
        coste_sal = st.number_input("Sal (€/kg)", 0.0, 5.0, 0.45)
        coste_luz = st.number_input("Luz (€/kWh)", 0.0, 1.0, 0.20)
    
    st.markdown("---")
    btn_calc = st.button("CALCULAR SISTEMA COMPLETO", type="primary")

if btn_calc:
    ro, descal, carbon, flow, opex = calcular_arquitecto(consumo, ppm_in, ppm_out, dureza, temp, horas, coste_agua, coste_sal, coste_luz)
    
    if not ro:
        st.error("❌ No se encontró solución viable. Revisa caudales o salinidad.")
    else:
        # --- ENCABEZADO ---
        st.subheader("✅ Configuración Recomendada")
        
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Equipo RO", ro.nombre)
        k2.metric("Producción RO", f"{int(flow['prod_ro_dia'])} L/d")
        k3.metric("Bypass (Mezcla)", f"{flow['blending_pct']:.1f}%")
        k4.metric("Consumo Total", f"{int(flow['prod_total_dia'])} L/d")

        st.markdown("---")
        
        # --- DETALLE ---
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.info("🔵 1. ÓSMOSIS INVERSA")
            st.write(f"**Modelo:** {ro.nombre}")
            st.write(f"Eficiencia: {int(ro.eficiencia*100)}%")
            st.write(f"Agua necesaria: {int(flow['agua_entrada_total'])} L/día")
        
        with c2:
            st.success("⚫ 2. DECLORACIÓN")
            if carbon:
                st.write(f"**Modelo:** {carbon.nombre}")
                st.write(f"Volumen Carbón: **{carbon.litros_medio} Kg/L**")
                st.write(f"Caudal Máx: {carbon.caudal_max_m3h} m³/h")
                st.caption("Vital para proteger la membrana del cloro.")
            else:
                st.error("Caudal excesivo para filtros de carbón estándar. Usar dosificación Bisulfito.")

        with c3:
            st.warning("🟠 3. DESCALCIFICACIÓN")
            if descal:
                d, dias = descal
                st.write(f"**Modelo:** {d.nombre}")
                st.write(f"Config: **{d.tipo_valvula}**")
                st.write(f"Regeneración: Cada **{dias:.1f} días**")
            else:
                st.write("No requerida o caudal excesivo.")

        st.markdown("---")
        
        # --- DESCARGAS ---
        col_pdf, col_space = st.columns([1, 4])
        with col_pdf:
            try:
                pdf_bytes = generar_pdf_tecnico(ro, descal, carbon, flow, flow['blending_pct'], consumo, ppm_in, ppm_out, dureza)
                b64 = base64.b64encode(pdf_bytes).decode()
                href = f'<a href="data:application/octet-stream;base64,{b64}" download="informe_aimywater.pdf" style="text-decoration:none;"><button style="background-color:#cc0000;color:white;padding:10px;border-radius:5px;border:none;cursor:pointer;width:100%;">📄 Descargar PDF Técnico</button></a>'
                st.markdown(href, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error PDF: {e}")

else:
    st.info("👈 Pulsa Calcular para ver la magia.")
