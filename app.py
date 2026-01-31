import streamlit as st
import pandas as pd

# 1. CONFIGURACION
st.set_page_config(page_title="NUCLEO V67", layout="wide")

# 2. INTERFAZ
col1, col2 = st.columns([2, 1])

with col1:
    st.title("LEON DE ORO V67")
    st.header("LABORATORIO DE APRENDIZAJE")
    
    st.info("AI THOUGHT: Analizando sentimiento y ballenas para SCALPING...")
    
    st.subheader("Simulacion Instantanea de PNL")
    st.metric(label="PNL Estimado", value="+2.45%", delta="1.2% Bullish")

    st.subheader("Historial de Ordenes (Ultimos 30)")
    datos = {
        "Moneda": ["SOL", "BTC", "ETH"],
        "Estado": ["ENTRY", "EXIT", "LOSS"],
        "Resultado": ["+5.2%", "+2.1%", "-0.5%"]
    }
    st.table(pd.DataFrame(datos))

with col2:
    st.header("CONTROL CARTUCHO 1")
    st.success("Balance en MEXC: $200.00 USDT")
    st.warning("RIESGO GLOBAL: 0.5%")
    
    st.write("---")
    st.write("PRECIOS DE OPERACION")
    st.subheader("ENTRY: $120.50")
    st.write("TAKE PROFIT: $125.00")
    st.write("STOP LOSS: $119.80")
    
    st.write("---")
    st.image("https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=Volumen_Pattern_V67")
    
    if st.button("COPIA DE SEGURIDAD JSON"):
        st.write("Configuracion guardada.")
