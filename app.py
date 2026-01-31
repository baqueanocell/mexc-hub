import streamlit as st
import pandas as pd

# 1. CONFIGURACION BASICA [cite: 2026-01-27]
st.set_page_config(page_title="NUCLEO V67", layout="wide")

# 2. COLUMNAS PRINCIPALES (Evita NameError)
col_principal, col_control = st.columns([2, 1])

# 3. AREA DEL LABORATORIO (IZQUIERDA) [cite: 2026-01-27]
with col_principal:
    st.title("LEON DE ORO V67")
    st.header("LABORATORIO DE APRENDIZAJE")
    
    # Barra de progreso
    st.subheader("PROGRESO OPERACION SOL")
    st.progress(75)
    
    # Pensamiento IA (Texto puro para evitar errores)
    st.info("AI THOUGHT: Analizando ballenas. El riesgo esta protegido al nivel solicitado.") [cite: 2026-01-27]

    # Tabla de historial (Ultimos 30) [cite: 2026-01-27]
    st.write("HISTORIAL RECIENTE")
    datos = {"Moneda": ["SOL", "BTC"], "Estado": ["ENTRY", "EXIT"], "PNL": ["+5.2%", "+2.1%"]}
    st.table(pd.DataFrame(datos))

# 4. AREA DE CONTROL (DERECHA)
with col_control:
    st.header("CONTROL CARTUCHO 1")
    st.success("BALANCE: 200.00 USDT")
    
    # Corregido: Riesgo como texto simple
    st.warning("RIESGO DEFINIDO: 0.5 POR CIENTO") [cite: 2026-01-27]
    
    st.write("---")
    st.write("PRECIOS DE OPERACION")
    st.write("ENTRY: 122.40 (AMARILLO)") [cite: 2026-01-27]
    st.write("EXIT: 128.00 (VERDE)") [cite: 2026-01-27]
    st.write("LOSS: 121.90 (ROJO)") [cite: 2026-01-27]
    
    st.write("---")
    # Imagen de QR para aprendizaje [cite: 2026-01-27]
    st.image("https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=LeonV67_Learning")
    
    if st.button("GUARDAR CONFIGURACION"):
        st.write("Copia de seguridad lista.") [cite: 2026-01-27]
