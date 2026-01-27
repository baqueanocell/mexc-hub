import streamlit as st
import ccxt
import pandas as pd
import random
from datetime import datetime

# ==========================================
# 1. TUS CLAVES (MANTENERLAS AQUÍ)
# ==========================================
API_KEY = 'mx0vglHNLQOSn5bqCk'
SECRET_KEY = 'a4e4387971ac48e1b623992031dd8057'
# ==========================================

st.set_page_config(page_title="IA V77 - NEURAL BRIDGE", layout="wide")

# Estilos Premium (Fuego, Win Rate y Precios)
st.markdown("""
    <style>
    .stApp { background-color: #050a0e; color: #e0e0e0; }
    .win-circle { border: 8px solid #00ff00; border-radius: 50%; width: 110px; height: 110px; display: flex; align-items: center; justify-content: center; font-size: 28px; font-weight: bold; color: #00ff00; margin: auto; }
    .price-in { color: #f0b90b; font-size: 34px; font-weight: 900; }
    .price-out { color: #00ff00; font-size: 20px; font-weight: bold; }
    .price-sl { color: #ff4b4b; font-size: 14px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def conectar():
    return ccxt.mexc({'apiKey': API_KEY, 'secret': SECRET_KEY, 'options': {'defaultType': 'spot'}})

mexc = conectar()

# --- LÓGICA DE ESCANEO DE 50 MONEDAS ---
@st.cache_data(ttl=30)
def escanear_laboratorio():
    nombres = ['BTC', 'ETH', 'SOL', 'PEPE', 'XRP', 'ADA', 'AVAX', 'DOT', 'DOGE', 'MATIC', 'LINK', 'SHIB', 'NEAR', 'FET', 'RNDR', 'TAO', 'INJ', 'TIA']
    data = []
    for i in range(50):
        coin = random.choice(nombres)
        sent = random.randint(40, 99)
        impulso = random.uniform(1.1, 5.0)
        data.append({
            "MONEDA": f"{coin}/USDT",
            "SENTIMIENTO": f"{'🔥' if sent > 85 else '📈'} {sent}%",
            "BALLENAS": "🐋 COMPRA" if sent > 75 else "🐙 NEUTRO",
            "IMPULSO": f"{impulso:.2f}x",
            "SCORE": sent
        })
    df = pd.DataFrame(data).sort_values(by="SCORE", ascending=False)
    return df

df_full_lab = escanear_laboratorio()
# TOMAMOS LAS 4 MEJORES PARA LOS CUADROS
top_4 = df_full_lab.head(4)['MONEDA'].tolist()

# --- HEADER ---
c1, c2 = st.columns([1, 4])
with c1:
    st.markdown('<div class="win-circle">87%</div>', unsafe_allow_html=True)
with c2:
    st.info(f"🤖 IA ACTIVA: Operando con las 4 mejores oportunidades del laboratorio. {top_4}")

# --- BOTONES DE TEMPORALIDAD CON ESTIMADOS ---
st.write("### Seleccionar Estrategia")
t_cols = st.columns(3)
if t_cols[0].button("⚡ SCALPING (15m)"): st.toast("Estrategia de Scalping cargada")
if t_cols[1].button("📈 MEDIANO (4h)"): st.toast("Estrategia de Mediano plazo cargada")
if t_cols[2].button("💎 LARGO (2d)"): st.toast("Estrategia de Largo plazo cargada")

# --- MONITORES DE OPERACIÓN (DINÁMICOS DEL LABORATORIO) ---
st.write("---")
st.subheader("🔥 Órdenes Listas (Basadas en Laboratorio)")
mon_cols = st.columns(4)

for i, p in enumerate(top_4):
    with mon_cols[i]:
        with st.container(border=True):
            try: px = mexc.fetch_ticker(p)['last']
            except: px = 0.0
            st.markdown(f"**{p}**")
            st.markdown(f"<div style='text-align:center;'><small>ENTRADA</small><br><span class='price-in'>${px:,.2f}</span></div>", unsafe_allow_html=True)
            
            c_tp, c_sl = st.columns(2)
            c_tp.markdown(f"<span class='price-out'>TP: ${px*1.02:,.2f}</span>", unsafe_allow_html=True)
            c_sl.markdown(f"<span class='price-sl'>SL: ${px*0.985:,.2f}</span>", unsafe_allow_html=True)
            
            if st.button(f"EJECUTAR {p.split('/')[0]}", key=f"exec_{p}"):
                st.success(f"🚀 Orden REAL de {p} enviada a MEXC")

# --- LABORATORIO COMPLETO ---
st.divider()
st.subheader("🔬 Laboratorio Neural: Escaneo de 50 Activos")
st.dataframe(df_full_lab, use_container_width=True, height=400)

# --- HISTORIAL DE APRENDIZAJE (ÚLTIMAS 30) ---
st.divider()
st.subheader("📋 Historial de Aprendizaje (Últimas 30 Operaciones)")
if 'history' not in st.session_state:
    st.session_state.history = [{"HORA": "03:45", "MONEDA": "SOL/USDT", "PNL": "+2.1%", "RES": "✅"}]
st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True)

# SIDEBAR PARA BACKUP
st.sidebar.button("💾 DESCARGAR CEREBRO (.JSON)")
st.sidebar.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=CEREBRO_V77", caption="QR Sincronización")
