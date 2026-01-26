import streamlit as st
import pandas as pd

# Configuración visual
st.set_page_config(page_title="MEXC Intelligence Hub", layout="wide")

# Estilo Dark Mode Personalizado
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stProgress > div > div > div > div { background-color: #00ffcc; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ MEXC INTELLIGENCE HUB")

# Sidebar para control
st.sidebar.header("Configuración")
modo = st.sidebar.radio("Modo de Red:", ["Prueba (Costo 0)", "Real (MEXC API)"])

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Top 10 Monedas - Triple Confluencia")
    # Datos de prueba con los porcentajes que pediste
    monedas = [
        {"name": "VEREM", "social": 85, "whales": 92, "impulse": 88},
        {"name": "BTC", "social": 45, "whales": 60, "impulse": 40},
        {"name": "ETH", "social": 70, "whales": 55, "impulse": 65},
    ]
    
    for m in monedas:
        with st.container():
            st.write(f"### {m['name']}")
            st.write(f"📊 Social: **{m['social']}%** | 🐋 Ballenas: **{m['whales']}%** | ⚡ Impulso: **{m['impulse']}%**")
            st.progress(m['social']/100)
            st.progress(m['whales']/100)
            st.progress(m['impulse']/100)
            st.divider()

with col2:
    st.success("### 🎯 ALERTA DE PRIORIDAD")
    if monedas[0]['social'] > 80:
        st.write(f"**¡CONFLUENCIA EN {monedas[0]['name']}!**")
        st.write("Nivel Fibonacci: **0.618 Oro**")
        st.write("Precio Entrada: **$90.50**")
    
    st.info("### 📈 Mini Gráfico Fib")
    st.line_chart([10, 15, 12, 18, 14, 20])
