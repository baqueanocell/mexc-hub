import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Configuración de página y Estilo "Slim & Neon"
st.set_page_config(page_title="MEXC Intelligence Hub", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b0e14; }
    .stProgress > div > div > div > div { height: 8px !important; border-radius: 10px; }
    div[data-testid="stMetricValue"] { font-size: 18px; color: #00ffcc; }
    .reportview-container .main .block-container { padding-top: 2rem; }
    h3 { font-size: 1.2rem !important; margin-bottom: 0px; }
    </style>
    """, unsafe_allow_html=True)

# Encabezado
st.title("🛡️ MEXC INTELLIGENCE HUB")
st.caption(f"Actualizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

col_main, col_side = st.columns([2, 1])

with col_main:
    st.subheader("📊 Top 10 Monedas - Triple Confluencia")
    
    # Datos simulados con porcentajes
    monedas = [
        {"name": "VEREM", "social": 98, "whales": 90, "impulse": 95},
        {"name": "BTC", "social": 45, "whales": 50, "impulse": 30},
        {"name": "ETH", "social": 60, "whales": 75, "impulse": 55},
        {"name": "SOL", "social": 80, "whales": 40, "impulse": 70},
    ]

    for m in monedas:
        with st.container():
            st.write(f"**{m['name']}**")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.caption(f"Sentimiento: {m['social']}%")
                st.progress(m['social']/100)
            with c2:
                st.caption(f"Ballenas: {m['whales']}%")
                st.progress(m['whales']/100)
            with c3:
                st.caption(f"Impulso: {m['impulse']}%")
                st.progress(m['impulse']/100)
            st.write("---")

with col_side:
    # Sección Alerta
    st.success("### 🎯 ALERTA DE PRIORIDAD")
    st.metric(label="Oportunidad Detectada", value="VEREM / USDT")
    st.write("**Nivel Fib:** 0.618 Oro ($90.50)")
    
    st.divider()
    
    # NUEVO: Historial de Operaciones
    st.subheader("📜 Historial de Operaciones")
    historial = pd.DataFrame([
        {"Hora": "12:15", "Moneda": "BTC", "Acción": "COMPRA", "Resultado": "+2.1%"},
        {"Hora": "11:40", "Moneda": "SOL", "Acción": "VENTA", "Resultado": "-0.5%"},
        {"Hora": "09:20", "Moneda": "VEREM", "Acción": "COMPRA", "Resultado": "+8.4%"},
    ])
    st.table(historial)

    st.info("💡 *El historial registra las señales confirmadas por la IA.*")
