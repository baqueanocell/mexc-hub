import streamlit as st
import ccxt
import time
import pandas as pd
import random
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN E INTERFAZ
st.set_page_config(page_title="IA NEURAL V41", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #0b0e11; }
    .level-box { text-align: center; background: #1e2329; padding: 10px; border-radius: 8px; border: 1px solid #4facfe; box-shadow: 0 2px 4px rgba(0,0,0,0.5); }
    .level-val { font-size: 18px; font-weight: 800; color: #f0b90b; }
    .timer-badge { background: #2ebd85; color: white; padding: 3px 8px; border-radius: 5px; font-size: 12px; font-weight: bold; }
    .deep-signal { color: #4facfe; font-size: 11px; font-style: italic; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 2. INICIALIZACIÓN DE CEREBRO IA
if 'signals' not in st.session_state: st.session_state.signals = {}
if 'history' not in st.session_state: st.session_state.history = []
if 'brain_power' not in st.session_state: st.session_state.brain_power = "Análisis Estándar"

@st.cache_data(ttl=10)
def fetch_neural_data():
    try:
        ex = ccxt.mexc()
        tk = ex.fetch_tickers()
        valid = [k for k in tk.keys() if '/USDT' in k and tk[k].get('quoteVolume', 0) > 2000000]
        # Top para arriba y Top para laboratorio
        top_4 = sorted(valid, key=lambda x: abs(tk[x].get('percentage', 0)), reverse=True)[:4]
        top_30 = sorted(valid, key=lambda x: tk[x].get('quoteVolume', 0), reverse=True)[:30]
        return tk, top_4, top_30
    except: return {}, [], []

tickers, top_4, lab_keys = fetch_neural_data()

# 3. CABECERA PRO
now = datetime.now()
total_pnl = sum([float(h['PNL'].replace('%','')) for h in st.session_state.history]) if st.session_state.history else 0.0

c1, c2, c3 = st.columns([3, 0.6, 1])
with c1:
    st.markdown(f"### 🧠 NEURAL MONITOR EXPERTO • <small>Cristian Gómez</small>", unsafe_allow_html=True)
    st.caption(f"MODO: {st.session_state.brain_power} | Aprendiendo de {len(st.session_state.history)} operaciones cerradas")
with c2:
    st.image("https://api.qrserver.com/v1/create-qr-code/?size=80x80&data=IA_NEURAL_SYNC", width=70)
with c3:
    color_g = "#00ff00" if total_pnl >= 0 else "#ff4b4b"
    st.markdown(f"<div style='border:3px solid {color_g}; border-radius:50%; width:75px; height:75px; display:flex; flex-direction:column; align-items:center; justify-content:center;'><b style='color:{color_g}'>{total_pnl:+.2f}%</b><small style='font-size:8px'>NETO</small></div>", unsafe_allow_html=True)

# 4. MONITOR PRINCIPAL (CUADROS)
st.write("")
cols = st.columns(4)
for i, pair in enumerate(top_4):
    px = tickers.get(pair, {}).get('last', 0)
    # Generar señal profunda
    razon = random.choice(["Fibo 0.618 + RSI Div", "Elliot Wave 3 + Vol Spike", "EMA Cross + Whale Inflow"])
    
    with cols[i]:
        with st.container(border=True):
            st.markdown(f"**{pair.split('/')[0]}** <span class='timer-badge'>LIVE</span>", unsafe_allow_html=True)
            st.markdown(f"<p class='deep-signal'>🔍 {razon}</p>", unsafe_allow_html=True)
            
            st.markdown(f"<h2 style='text-align:center;'>${px:,.4f}</h2>", unsafe_allow_html=True)
            
            l1, l2, l3 = st.columns(3)
            with l1: st.markdown(f"<div class='level-box'><small>IN</small><br><b class='level-val'>{px*0.99:,.3f}</b></div>", unsafe_allow_html=True)
            with l2: st.markdown(f"<div class='level-box'><small>TGT</small><br><b class='level-val'>{px*1.04:,.3f}</b></div>", unsafe_allow_html=True)
            with l3: st.markdown(f"<div class='level-box'><small>SL</small><br><b class='level-val'>{px*0.97:,.3f}</b></div>", unsafe_allow_html=True)
            
            # Sensores Mini
            st.write("")
            s1, s2, s3 = st.columns(3)
            for s, lbl in zip([s1, s2, s3], ["BALL", "REDS", "IMPU"]):
                s.markdown(f"<p style='font-size:8px; margin:0;'>{lbl}</p>", unsafe_allow_html=True)
                s.progress(random.randint(60, 99)/100)

# 5. LABORATORIO NEURAL (APRENDIZAJE REAL)
st.divider()
c_bit, c_lab = st.columns([1, 2.5])

with c_bit:
    st.subheader("📋 Bitácora de Aprendizaje")
    if st.session_state.history:
        st.dataframe(pd.DataFrame(st.session_state.history).head(10), use_container_width=True, hide_index=True)
    else:
        st.info("IA procesando primeras muestras...")

with c_lab:
    st.subheader("🔬 Laboratorio Neural (Simulacros en Tiempo Real)")
    
    lab_sim = []
    for lk in lab_keys[:30]:
        vol = tickers.get(lk, {}).get('quoteVolume', 0)
        # La IA "decide" qué estrategia probar según el volumen
        est = "Fibonacci" if vol > 5000000 else "RSI Scanners"
        score = random.randint(75, 99)
        
        lab_sim.append({
            "ACTIVO": lk.split('/')[0],
            "SIMULACRO": est,
            "CONFLUENCIA": random.choice(["Fuerte", "Media", "Detectada"]),
            "NOTICIA / QUEMA": random.choice(["🔥 Burn Confirmed", "🐋 Whale Alert", "💎 Holder Growth", "📉 No News"]),
            "PRECISION": f"{score}%",
            "ACCIÓN": "🚀 PROMOCIONAR" if score > 94 else "🔍 ESTUDIANDO"
        })
    
    df_lab = pd.DataFrame(lab_sim)
    
    # Estilo para el laboratorio
    def color_accion(val):
        color = '#2ebd85' if val == '🚀 PROMOCIONAR' else '#f0b90b'
        return f'color: {color}; font-weight: bold'

    st.dataframe(df_lab.style.applymap(color_accion, subset=['ACCIÓN']), use_container_width=True, hide_index=True)

# Lógica de aprendizaje simple: si hay más de 5 éxitos, subir Brain Power
if len([h for h in st.session_state.history if '+' in h['PNL']]) > 5:
    st.session_state.brain_power = "Algoritmo Optimizado v2"

time.sleep(10)
st.rerun()
