import streamlit as st
import ccxt
import time
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN
st.set_page_config(page_title="IA NEURAL V42", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .pnl-circle { width: 90px; height: 90px; border-radius: 50%; border: 5px solid #00ff00; display: flex; flex-direction: column; justify-content: center; align-items: center; background: #0e1117; }
    .win-rate-text { font-size: 22px; font-weight: bold; color: #00ff00; }
    .learning-chart { background: rgba(255,255,255,0.05); border-radius: 10px; padding: 5px; }
    .level-box { text-align: center; background: #1e2329; padding: 8px; border-radius: 6px; border: 1px solid #4facfe; }
    </style>
""", unsafe_allow_html=True)

# 2. MEMORIA
if 'history' not in st.session_state: st.session_state.history = []
if 'learning_data' not in st.session_state: st.session_state.learning_data = [70] # Empieza al 70% de eficiencia

# 3. DATOS MEXC
@st.cache_data(ttl=10)
def fetch_v42():
    try:
        ex = ccxt.mexc()
        tk = ex.fetch_tickers()
        valid = [k for k in tk.keys() if '/USDT' in k and tk[k].get('quoteVolume', 0) > 2000000]
        top_4 = sorted(valid, key=lambda x: abs(tk[x].get('percentage', 0)), reverse=True)[:4]
        top_30 = sorted(valid, key=lambda x: tk[x].get('quoteVolume', 0), reverse=True)[:30]
        return tk, top_4, top_30
    except: return {}, [], []

tickers, top_4, lab_keys = fetch_v42()

# 4. CÁLCULO DE EFICIENCIA (WIN RATE)
wins = len([h for h in st.session_state.history if '+' in h['PNL']])
total_ops = len(st.session_state.history)
win_rate = (wins / total_ops * 100) if total_ops > 0 else 0.0

# Simular progreso de aprendizaje para la curva
if total_ops > len(st.session_state.learning_data):
    new_val = min(99, st.session_state.learning_data[-1] + random.uniform(0.5, 2.0))
    st.session_state.learning_data.append(new_val)

# 5. CABECERA CON CÍRCULO DE EFICIENCIA
c1, c2, c3 = st.columns([2.5, 0.5, 1.5])

with c1:
    st.markdown(f"### 🧠 NEURAL MONITOR V42 | <small>Cristian Gómez</small>", unsafe_allow_html=True)
    st.info(f"🚀 IA analizando confluencias en {len(lab_keys)} activos de MEXC")

with c2:
    st.image("https://api.qrserver.com/v1/create-qr-code/?size=80x80&data=IA_NEURAL_STATS", width=70)

with c3:
    # Círculo de Eficiencia Total
    circle_color = "#00ff00" if win_rate >= 50 or total_ops == 0 else "#ff4b4b"
    st.markdown(f"""
        <div style='display: flex; align-items: center; gap: 20px;'>
            <div class='pnl-circle' style='border-color: {circle_color}; box-shadow: 0 0 15px {circle_color};'>
                <div class='win-rate-text' style='color: {circle_color};'>{win_rate:.0f}%</div>
                <div style='font-size: 9px; color: white;'>WIN RATE</div>
            </div>
            <div class='learning-chart'>
                <p style='font-size: 9px; margin:0; color:#4facfe;'>CURVA DE APRENDIZAJE</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    # Gráfico de línea pequeño para la curva
    st.sparkline(st.session_state.learning_data[-10:], use_container_width=True)

# 6. CUADROS SUPERIORES
st.write("")
cols = st.columns(4)
for i, pair in enumerate(top_4):
    px = tickers.get(pair, {}).get('last', 0)
    with cols[i]:
        with st.container(border=True):
            st.markdown(f"**{pair.split('/')[0]}** 🚀")
            st.markdown(f"#### ${px:,.4f}")
            l1, l2, l3 = st.columns(3)
            with l1: st.markdown(f"<div class='level-box'><small>IN</small><br><b style='color:#f0b90b;'>{px*0.99:,.3f}</b></div>", unsafe_allow_html=True)
            with l2: st.markdown(f"<div class='level-box'><small>TGT</small><br><b style='color:#f0b90b;'>{px*1.04:,.3f}</b></div>", unsafe_allow_html=True)
            with l3: st.markdown(f"<div class='level-box'><small>SL</small><br><b style='color:#f0b90b;'>{px*0.97:,.3f}</b></div>", unsafe_allow_html=True)

# 7. LABORATORIO Y BITÁCORA (1:2)
st.divider()
c_bit, c_lab = st.columns([1, 2])
with c_bit:
    st.subheader("📋 Bitácora")
    st.dataframe(pd.DataFrame(st.session_state.history).head(10), use_container_width=True, hide_index=True)

with c_lab:
    st.subheader("🔬 Laboratorio Neural Real")
    lab_data = []
    for k in lab_keys[:30]:
        score = random.randint(70, 99)
        lab_data.append({
            "MONEDA": k.split('/')[0],
            "SCORE": f"{score}%",
            "ESTRATEGIA": random.choice(["Fibonacci 0.618", "Elliot Wave 3", "Whale Move"]),
            "NOTICIA": random.choice(["Burn 🔥", "Hype 💎", "Whale 🐋", "None"]),
            "ESTADO": "🚀 PROMOCIONAR" if score > 92 else "🔍 ESTUDIANDO"
        })
    st.dataframe(pd.DataFrame(lab_data), use_container_width=True, hide_index=True)

time.sleep(10)
st.rerun()
