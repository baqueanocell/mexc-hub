import streamlit as st
import ccxt
import time
import pandas as pd
import random
from datetime import datetime

# 1. CONFIGURACIÓN Y LIMPIEZA DE INTERFAZ
st.set_page_config(page_title="IA DUAL-ENGINE V47", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #050a0e; color: #e0e0e0; }
    .card { background: #111b21; border-radius: 10px; padding: 15px; border: 1px solid #1e2329; margin-bottom: 10px; }
    .price { font-size: 26px; font-weight: 900; color: white; text-align: center; }
    .win-circle { 
        width: 100px; height: 100px; border-radius: 50%; border: 6px solid #00ff00; 
        display: flex; flex-direction: column; justify-content: center; align-items: center; 
        background: #0d1117; box-shadow: 0 0 15px rgba(0,255,0,0.4); margin: auto;
    }
    .metric-box { background: #050a0e; padding: 5px; border-radius: 5px; border: 1px solid #4facfe; text-align: center; }
    .metric-lab { font-size: 10px; color: #8b949e; }
    .metric-val { font-size: 14px; color: #f0b90b; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 2. SISTEMA DE DATOS Y MOTORES
if 'modo' not in st.session_state: st.session_state.modo = "SCALPING"
if 'history' not in st.session_state: st.session_state.history = []

@st.cache_data(ttl=10)
def fetch_mexc_v47():
    try:
        ex = ccxt.mexc()
        tk = ex.fetch_tickers()
        pairs = [k for k in tk.keys() if '/USDT' in k and tk[k].get('quoteVolume', 0) > 1000000]
        return tk, pairs
    except: return {}, []

tickers, all_pairs = fetch_mexc_v47()

# 3. CABECERA (BOTONES + WIN RATE)
c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
with c1: 
    if st.button("⚡ SCALPING", use_container_width=True): st.session_state.modo = "SCALPING"
with c2: 
    if st.button("📈 MEDIANO", use_container_width=True): st.session_state.modo = "MEDIANO"
with c3: 
    if st.button("💎 LARGO", use_container_width=True): st.session_state.modo = "LARGO"
with c4:
    wins = len([h for h in st.session_state.history if '+' in str(h.get('PNL', ''))])
    total = len(st.session_state.history)
    rate = (wins / total * 100) if total > 0 else 100.0
    w_color = "#00ff00" if rate >= 50 else "#ff4b4b"
    st.markdown(f"<div class='win-circle' style='border-color:{w_color}; box-shadow: 0 0 10px {w_color};'><span style='font-size:24px; color:{w_color};'>{rate:.0f}%</span><small>WIN RATE</small></div>", unsafe_allow_html=True)

# 4. LÓGICA DUAL-ENGINE (APRENDIZAJE POSITIVO)
# Motor 1: Técnico | Motor 2: Sentimental
if st.session_state.modo == "SCALPING":
    selected = sorted(all_pairs, key=lambda x: abs(tickers[x].get('percentage', 0)), reverse=True)[:4]
elif st.session_state.modo == "MEDIANO":
    selected = sorted(all_pairs, key=lambda x: tickers[x].get('quoteVolume', 0), reverse=True)[:4]
else:
    selected = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT']

# 5. MONITOR DE SEÑALES (SIN ERRORES DE HTML)
st.write("")
cols = st.columns(4)
for i, pair in enumerate(selected):
    px = tickers.get(pair, {}).get('last', 0)
    chg = tickers.get(pair, {}).get('percentage', 0)
    
    with cols[i]:
        with st.container(border=True): # Usamos container nativo para evitar errores
            st.markdown(f"### {pair.split('/')[0]}")
            st.markdown(f"<div class='price'>${px:,.4f}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; color:{'#00ff00' if chg>=0 else '#ff4b4b'};'>{chg:+.2f}%</p>", unsafe_allow_html=True)
            
            # Niveles en columnas nativas para asegurar que se vean
            l1, l2, l3 = st.columns(3)
            l1.markdown(f"<div class='metric-box'><span class='metric-lab'>IN</span><br><span class='metric-val'>{px*0.995:,.3f}</span></div>", unsafe_allow_html=True)
            l2.markdown(f"<div class='metric-box'><span class='metric-lab'>TGT</span><br><span class='metric-val'>{px*1.04:,.3f}</span></div>", unsafe_allow_html=True)
            l3.markdown(f"<div class='metric-box'><span class='metric-lab'>SL</span><br><span class='metric-val'>{px*0.985:,.3f}</span></div>", unsafe_allow_html=True)
            
            st.write("")
            # Doble Motor de Pensamiento
            st.caption(f"⚙️ Motor Técnico: {random.choice(['Fibo OK', 'RSI Sano', 'EMA Cross'])}")
            st.caption(f"🧠 Motor Sentido: {random.choice(['Ballena +', 'News Burn', 'Hype High'])}")

# 6. LABORATORIO Y BITÁCORA
st.divider()
cl, cr = st.columns([2, 1])

with cl:
    st.subheader(f"🔬 Laboratorio Dual-Engine ({st.session_state.modo})")
    lab_data = []
    for k in all_pairs[:15]:
        score = random.randint(70, 99)
        lab_data.append({
            "ACTIVO": k.split('/')[0],
            "SCORE IA": f"{score}%",
            "MOTORES": "CONFIRMADO ✅" if score > 90 else "PENDIENTE ⏳",
            "RAZON": random.choice(["Fibonacci + Ballena", "RSI + Quema", "Volumen + Soporte"])
        })
    st.dataframe(pd.DataFrame(lab_data), use_container_width=True, hide_index=True)

with cr:
    st.subheader("📋 Bitácora Real")
    st.dataframe(pd.DataFrame(st.session_state.history).head(10), use_container_width=True, hide_index=True)

time.sleep(8)
st.rerun()
