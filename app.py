import streamlit as st

# ==============================================================================
# 1. BASE DE DATOS Y CLASES
# ==============================================================================

class EquipoRO:
    def __init__(self, categoria, nombre, produccion_nominal, max_ppm, eficiencia, potencia_kw):
        self.categoria = categoria
        self.nombre = nombre
        self.produccion_nominal = produccion_nominal
        self.max_ppm = max_ppm
        self.eficiencia = eficiencia
        self.potencia_kw = potencia_kw

class Descalcificador:
    def __init__(self, nombre, litros_resina, caudal_max_m3h, capacidad_intercambio, sal_por_regen_kg, tipo):
        self.nombre = nombre
        self.litros_resina = litros_resina
        self.caudal_max_m3h = caudal_max_m3h
        self.capacidad_intercambio = capacidad_intercambio
        self.sal_por_regen_kg = sal_por_regen_kg
        self.tipo = tipo

# Catálogos
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
    Descalcificador("BI BLOC 30L IMPRESSION", 30, 1.8, 192, 4.5, "Simplex"),
    Descalcificador("BI BLOC 60L IMPRESSION", 60, 3.6, 384, 9.0, "Simplex"),
    Descalcificador("BI BLOC 100L IMPRESSION", 100, 6.0, 640, 15.0, "Simplex"),
    Descalcificador("TWIN 40L DF IMPRESSION", 40, 2.4, 256, 6.0, "Duplex"),
    Descalcificador("TWIN 100L DF IMPRESSION", 100, 6.0, 640, 15.0, "Duplex"),
    Descalcificador("TWIN 140L DF IMPRESSION", 140, 6.0, 896, 25.0, "Duplex"),
]

# ==============================================================================
# 2. MOTOR DE CÁLCULO
# ==============================================================================

def calcular_todo(consumo_diario, ppm, dureza, temp, horas_punta, coste_agua_m3, coste_sal_kg, coste_kwh):
    
    # Factor Temp
    tcf = 1.0 if temp >= 25 else max(1.0 - ((25 - temp) * 0.03), 0.1)
    
    # RO
    ro_sel = None
    candidatos = []
    for ro in catalogo_ro:
        if ppm <= ro.max_ppm:
            factor_uso = 1.0 if ro.categoria == "Industrial" else 0.4
            cap_real = ro.produccion_nominal * tcf * factor_uso
            if cap_real >= consumo_diario:
                candidatos.append(ro)
    
    if candidatos:
        if consumo_diario > 600:
            ro_sel = next((x for x in candidatos if x.categoria == "Industrial"), candidatos[-1])
        else:
            ro_sel = next((x for x in candidatos if x.categoria == "Doméstico"), candidatos[0])

    # Descalcificador
    descal_sel = None
    datos_flow = {}
    
    if ro_sel:
        agua_entrada_dia = consumo_diario / ro_sel.eficiencia
        caudal_alim_lh = (ro_sel.produccion_nominal / 24 / ro_sel.eficiencia) * 1.5
        prod_real_dia = ro_sel.produccion_nominal * tcf
        
        datos_flow = {
            "agua_entrada": agua_entrada_dia,
            "rechazo": agua_entrada_dia - consumo_diario,
            "prod_real_dia": prod_real_dia,
            "caudal_produccion_lh": prod_real_dia / 24
        }

        if dureza > 5:
            carga_dia = (agua_entrada_dia / 1000) * dureza
            cands_soft = []
            es_ind = ro_sel.categoria == "Industrial"
            
            for d in catalogo_descal:
                if (d.caudal_max_m3h * 1000) >= caudal_alim_lh:
                    dias = d.capacidad_intercambio / carga_dia if carga_dia > 0 else 99
                    viable = False
                    if es_ind and consumo_diario > 5000:
                        if "Duplex" in d.tipo or dias > 1: viable = True
                    else:
                        if dias >= 0.8: viable = True
                    if viable: cands_soft.append((d, dias))
            
            if cands_soft:
                cands_soft.sort(key=lambda x: (0 if "Duplex" in x[0].tipo and es_ind else 1, x[0].litros_resina))
                descal_sel = cands_soft[0]

    # Económicos
    opex = {}
    if ro_sel:
        coste_agua = (datos_flow['agua_entrada'] / 1000) * 365 * coste_agua_m3
        coste_sal = 0
        kg_sal = 0
        if descal_sel:
            eq, dias = descal_sel
            kg_sal = (365 / dias) * eq.sal_por_regen_kg
            coste_sal = kg_sal * coste_sal_kg
        
        horas_marcha = consumo_diario / datos_flow['caudal_produccion_lh']
        coste_elec = horas_marcha * ro_sel.potencia_kw * 365 * coste_kwh
        
        opex = {
            "total": coste_agua + coste_sal + coste_elec,
            "agua": coste_agua, "sal": coste_sal, "elec": coste_elec, "kg_sal": kg_sal
        }

    # Logística
    logistica = {}
    if ro_sel:
        caudal_demanda = consumo_diario / horas_punta
        if caudal_demanda > datos_flow['caudal_produccion_lh']:
            deficit = caudal_demanda - datos_flow['caudal_produccion_lh']
            logistica["tanque"] = deficit * horas_punta * 1.2
            logistica["msg"] = f"⚠️ La máquina no cubre la punta de consumo ({int(caudal_demanda)} L/h)."
        else:
            logistica["tanque"] = 0
            logistica["msg"] = "✅ Producción directa suficiente."

    return ro_sel, descal_sel, datos_flow, opex, logistica

# ==============================================================================
# 3. INTERFAZ WEB (STREAMLIT)
# ==============================================================================

st.set_page_config(page_title="GuruWater Genius", page_icon="💧", layout="wide")

st.title("💧 GuruWater: Calculadora de Ingeniería V7.0")
st.markdown("**Versión Genius: Técnica + Económica + Logística**")

with st.sidebar:
    st.header("📋 Datos Técnicos")
    litros = st.number_input("Consumo Diario (Litros)", 100, 30000, 2000, step=100)
    ppm = st.number_input("TDS (ppm)", 50, 7000, 800)
    dureza = st.number_input("Dureza (ºHf)", 0, 100, 35)
    temp = st.slider("Temperatura Agua (ºC)", 5, 35, 15)
    
    st.header("💰 Datos Económicos")
    horas_uso = st.slider("Horas de punta de consumo", 1, 24, 8)
    coste_agua = st.number_input("Coste Agua (€/m3)", 0.0, 10.0, 1.5)
    coste_sal = st.number_input("Coste Sal (€/kg)", 0.0, 5.0, 0.45)
    coste_luz = st.number_input("Coste Luz (€/kWh)", 0.0, 1.0, 0.20)
    
    btn = st.button("CALCULAR PROYECTO 🚀", type="primary")

if btn:
    ro, descal, flow, opex, log = calcular_todo(litros, ppm, dureza, temp, horas_uso, coste_agua, coste_sal, coste_luz)
    
    if not ro:
        st.error("❌ No se encontró solución estándar. Salinidad excesiva o caudal fuera de rango.")
    else:
        # PESTAÑAS
        tab1, tab2, tab3 = st.tabs(["🛠️ Solución Técnica", "💸 Análisis Costes", "📦 Logística"])
        
        with tab1:
            c1, c2 = st.columns(2)
            with c1:
                st.success(f"**ÓSMOSIS: {ro.nombre}**")
                st.write(f"- Producción Real ({temp}ºC): **{int(flow['prod_real_dia'])} L/día**")
                st.write(f"- Eficiencia: {int(ro.eficiencia*100)}%")
            with c2:
                if descal:
                    d, dias = descal
                    st.info(f"**DESCALCIFICADOR: {d.nombre}**")
                    st.write(f"- Configuración: **{d.tipo}**")
                    st.write(f"- Regeneración: Cada {dias:.1f} días")
                else:
                    st.success("✅ No requiere descalcificador")
        
        with tab2:
            st.metric("Coste Operativo Anual (OPEX)", f"{opex['total']:.2f} €", f"{(opex['total']/365):.2f} €/día")
            col_eco1, col_eco2, col_eco3 = st.columns(3)
            col_eco1.metric("Agua", f"{opex['agua']:.0f} €")
            col_eco2.metric("Sal", f"{opex['sal']:.0f} €")
            col_eco3.metric("Luz", f"{opex['elec']:.0f} €")
            st.caption(f"Sal necesaria: {int(opex['kg_sal'])} kg/año")
            
        with tab3:
            if log["tanque"] > 0:
                st.warning(f"Necesitas acumulación: {log['msg']}")
                st.metric("Depósito Recomendado", f"{int(log['tanque'])} Litros")
            else:
                st.success("✅ La máquina cubre la demanda en tiempo real.")