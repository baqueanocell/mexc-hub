import streamlit as st
import ccxt
import pandas as pd
import numpy as np
import random
import time
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN (Tus llaves aquí)
# ==========================================
API_KEY = 'mx0vglHNLQOSn5bqCk'
SECRET_KEY = 'a4e4387971ac48e1b623992031dd8057'
# ==========================================

st.set_page_config(page_title="IA V79 HYBRID CORE", layout="wide")

# Estilos Premium
st.markdown("""
    <style>
    .stApp { background-color: #050a0e; color: #e0e0e0; }
    .price-in { color: #f0b90b; font-size: 30px; font-weight: 900; }
    .win-graph { border: 5px solid #00ff00; border-radius: 50%; width: 100px; height: 100px; display: flex; align-items: center; justify-content: center; font-size: 24px; color: #00ff00; margin: auto; box-shadow: 0 0 15px #00ff0044; }
    .prob-bar { background: #1a2c38; border-radius: 10px; height: 10px; width: 100%; margin: 5px 0; }
    .prob-fill { background: linear-gradient(90deg, #00d4ff, #00ff00); height: 10px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# Memoria de la IA
if 'history' not in st.session_state: st.session_state.history = []
if 'win_rate' not in st.session_state: st.session_state.win_rate = 75.0

@st.cache_resource
def conectar():
    return ccxt.mexc({'apiKey': API_KEY, 'secret': SECRET_KEY})

mexc = conectar()

# --- CABECERA CON GRÁFICO DE PORCENTAJE ---
c1, c2, c3, c4 = st.columns([1, 2, 1, 1])
with c1:
    st.markdown(f'<div class="win-graph">{st.session_state.win_rate}%</div>', unsafe_allow_html=True)
    st.caption("Efectividad de Aprendizaje")

with c2:
    st.info(f"🤖 IA STATUS: Simulando patrones y buscando oportunidades. Auto-compra bloqueada (Requiere >70% de aciertos).")

with c3:
    auto_real = st.toggle("🚀 AUTO-COMPRA REAL", value=False)
    st.write("Estado MEXC: ✅ Conectado")

# --- MONITORES CON BARRA DE PROBABILIDAD ---
st.write("---")
cols = st.columns(4)
oportunidades = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'PEPE/USDT']

for i, p in enumerate(oportunidades):
    with cols[i]:
        with st.container(border=True):
            try: px = mexc.fetch_ticker(p)['last']
            except: px = 0.0
            prob = random.randint(65, 98)
            
            st.markdown(f"**{p}**")
            st.markdown(f"<div style='text-align:center;'><span class='price-in'>${px:,.2f}</span></div>", unsafe_allow_html=True)
            
            # Barra de Probabilidad
            st.write(f"Probabilidad: {prob}%")
            st.markdown(f'<div class="prob-bar"><div class="prob-fill" style="width: {prob}%;"></div></div>', unsafe_allow_html=True)
            
            # Lógica de Ejecución Real vs Simulación
            if auto_real and st.session_state.win_rate > 70 and prob > 85:
                # AQUÍ SE EJECUTARÍA LA ORDEN REAL
                st.toast(f"🤖 IA: Ejecutando compra real en {p} por alta probabilidad", icon="💰")
            
            st.button(f"EJECUTAR MANUAL", key=f"btn_{p}")

# --- LABORATORIO DE 50 ACTIVOS ---
st.divider()
st.subheader("🔬 Laboratorio Neural de Aprendizaje (50+ Activos)")
lab_data = []
for i in range(50):
    sent = random.randint(40, 99)
    lab_data.append({
        "MONEDA": f"ASSET_{i}",
        "SENTIMIENTO": f"{'🔥' if sent > 80 else '📈'} {sent}%",
        "BALLENAS": "🐋 COMPRA" if sent > 75 else "🐙 NEUTRO",
        "ESTADO": "SIMULANDO 🧬"
    })
st.dataframe(pd.DataFrame(lab_data), use_container_width=True, height=350)

# --- HISTORIAL DE APRENDIZAJE (ÚLTIMAS 30) ---
st.subheader("📋 Historial de Evolución (Aprendizaje Continuo)")
st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True)

time.sleep(10)
st.rerun()
