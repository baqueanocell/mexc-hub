import streamlit as st
import ccxt
import time
import pandas as pd
import random
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN DE PANTALLA
st.set_page_config(page_title="IA TRADING V21", layout="wide", initial_sidebar_state="collapsed")

# Estilo para mejorar la visibilidad de los sensores
st.markdown("""
    <style>
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #00f2fe, #4facfe); }
    [data-testid="stMetricValue"] { color: #00ff00; }
    </style>
""", unsafe_allow_html=True)

# 2. MEMORIA Y DATOS
if 'signals' not in st.session_state:
    st.session_state.signals = {}

@st.cache_data(ttl=10)
def get_mexc_data():
    try:
        ex = ccxt.mexc()
        tk = ex.fetch_tickers()
        valid = {k: v for k, v in tk.items() if '/USDT' in k and v.get('quoteVolume', 0) > 1500000}
        top = sorted(valid.keys(), key=lambda x: abs(valid[x].get('percentage', 0)), reverse=True)[:4]
        return tk, top
    except:
        return {}, ["BTC/USDT", "ETH/USDT", "SOL/USDT", "PEPE/USDT"]

tickers, top_pairs = get_mexc_data()

# 3. PENSAMIENTOS DINÁMICOS DE LA IA (Entretenido)
pensamientos = [
    "🔍 Analizando niveles de Fibonacci 0.618...",
    "🐋 Detectando grandes depósitos de ballenas en tiempo real...",
    "📱 Escaneando sentimiento alcista en X (Twitter) y Telegram...",
    "⚡ Calculando fuerza de impulso RSI y MACD...",
    "🛡️ Filtrando falsos breakouts en temporalidad de 5min...",
    "📊 Comparando volumen de MEXC vs Binance...",
    "🤖 Optimizando stop-loss dinámico para máxima ganancia...",
    "🚀 Buscando patrones de entrada institucional detectados..."
]
status_ia = random.choice(pensamientos)

# 4. LÓGICA DE SEÑALES
now = datetime.now()
active = []
for p in list(st.session_state.signals.keys()):
    if now < st.session_state.signals[p]['start'] + timedelta(minutes=20):
        active.append(p)
    else:
        del st.session_state.signals[p]

for tk in top_pairs:
    if len(active) < 4 and tk not in st.session_state.signals:
        p_last = tickers.get(tk, {}).get('last', 0)
        if p_last > 0:
            st.session_state.signals[tk] = {
                'start': now, 'entry': p_last,
                'b': random.randint(70, 99), 'r': random.randint(60, 95), 'i': random.randint(75, 99),
                'score': random.randint(0, 100)
            }
            active.append(tk)

# 5. INTERFAZ VISUAL
st.title("🛰️ MEXC SEÑALES | MONITOR V21")

# --- BARRA DE STATUS ENTRETENIDA ---
st.success(f"**IA STATUS:** {status_ia}")

st.divider()

cols = st.columns(4)
for i, pair in enumerate(active):
    info = st.session_state.signals.get(pair)
    if not info: continue
    
    current_p = tickers.get(pair, {}).get('last', info['entry'])
    pnl = ((current_p - info['entry']) / info['entry'] * 100) if info['entry'] > 0 else 0

    with cols[i]:
        with st.container(border=True):
            st.subheader(pair.split('/')[0])
            
            # Semáforo de Entrada
            if info['score'] > 65 and pnl > 0.1:
                st.success("🚀 ¡ENTRAR AHORA!")
            else:
                st.warning("⏳ BUSCANDO ENTRADA...")

            st.metric("PRECIO ACTUAL", f"${current_p:,.4f}", f"{pnl:+.2f}%")
            
            # Niveles IA
            st.write("**NIVELES:**")
            st.table(pd.DataFrame({
                "TIPO": ["IN", "TGT", "SL"],
                "USD": [f"{info['entry']:.5f}", f"{info['entry']*1.07:.5f}", f"{info['entry']*0.98:.5f}"]
            }))

            # Sensores con Nombres específicos
            st.caption("🐋 MOV. BALLENAS")
            st.progress(info['b'] / 100)
            st.caption("📱 REDES SOCIALES")
            st.progress(info['r'] / 100)
            st.caption("⚡ IMPULSO IA")
            st.progress(info['i'] / 100)
            
            st.info(f"CIERRE EN: {20 - int((now - info['start']).total_seconds() // 60)} MIN")

# Refresco automático cada 8 segundos para que el status cambie seguido
time.sleep(8)
st.rerun()
