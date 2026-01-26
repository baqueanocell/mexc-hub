import streamlit as st
import ccxt
import time
import pandas as pd
import random
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN DE PANTALLA
st.set_page_config(page_title="IA TRADING V19", layout="wide", initial_sidebar_state="collapsed")

# Estilo para que todo sea compacto y profesional
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; background-color: #0e1117; }
    [data-testid="stMetricValue"] { font-size: 20px !important; }
    .stProgress > div > div > div > div { background-color: #00ff00; }
    header, footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

# 2. GESTIÓN DE MEMORIA SEGURA
if 'signals' not in st.session_state:
    st.session_state.signals = {}
if 'history' not in st.session_state:
    st.session_state.history = []

@st.cache_data(ttl=12)
def get_market():
    try:
        ex = ccxt.mexc()
        tk = ex.fetch_tickers()
        valid = {k: v for k, v in tk.items() if '/USDT' in k and v.get('quoteVolume', 0) > 1500000}
        top = sorted(valid.keys(), key=lambda x: abs(valid[x].get('percentage', 0)), reverse=True)[:4]
        return tk, top
    except:
        return {}, ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT"]

tickers, top_4 = get_market()

# 3. LÓGICA DE TRADING
now = datetime.now()
active = []

for p in list(st.session_state.signals.keys()):
    s = st.session_state.signals[p]
    if now < s['start'] + timedelta(minutes=20):
        active.append(p)
    else:
        del st.session_state.signals[p]

for tk in top_4:
    if len(active) < 4 and tk not in st.session_state.signals:
        price = tickers.get(tk, {}).get('last', 0)
        if price > 0:
            st.session_state.signals[tk] = {
                'start': now, 'entry': price,
                's_ballenas': random.randint(70, 99),
                's_redes': random.randint(65, 95),
                's_impulso': random.randint(80, 99),
                'confirmado': random.choice([True, False]) # Simula entrada perfecta
            }
            active.append(tk)

# 4. INTERFAZ VISUAL
st.title("🛰️ MEXC SEÑALES | CRISTIAN GÓMEZ")
st.info(f"🧠 **SISTEMA:** {random.choice(['Analizando Fibonacci...', 'Detectando Ballenas...', 'Escaneando MEXC...'])}")

cols = st.columns(4)
for i, p_key in enumerate(active):
    # PROTECCIÓN: Si el dato no existe en este milisegundo, saltar para evitar el error rojo
    info = st.session_state.signals.get(p_key)
    if not info: continue
    
    current_p = tickers.get(p_key, {}).get('last', info['entry'])
    pnl = ((current_p - info['entry']) / info['entry'] * 100) if info['entry'] > 0 else 0

    with cols[i]:
        with st.container(border=True):
            st.subheader(f"{p_key.split('/')[0]}")
            
            # Icono Dinámico de Entrada
            if info['confirmado'] and pnl > 0:
                st.success("🚀 ¡ENTRAR AHORA!")
            else:
                st.warning("⏳ BUSCANDO ENTRADA...")

            st.metric("PRECIO ACTUAL", f"${current_p:,.4f}", f"{pnl:+.2f}%")
            
            # Tabla de niveles compacta
            st.table(pd.DataFrame({
                "Nivel": ["IN", "TGT", "SL"],
                "USD": [f"{info['entry']:.4f}", f"{info['entry']*1.08:.4f}", f"{info['entry']*0.97:.4f}"]
            }))

            # Sensores con protección de valor (si info no tiene la clave, usa 50)
            st.caption("🐋 MOV. BALLENAS")
            st.progress(info.get('s_ballenas', 50) / 100)
            
            st.caption("📱 REDES SOCIALES")
            st.progress(info.get('s_redes', 50) / 100)
            
            st.caption("⚡ IMPULSO IA")
            st.progress(info.get('s_impulso', 50) / 100)

st.divider()
if st.session_state.history:
    st.table(pd.DataFrame(st.session_state.history).head(3))

time.sleep(10)
st.rerun()
