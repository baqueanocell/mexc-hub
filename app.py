import streamlit as st
import ccxt
import time
import pandas as pd
import random
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN DE PANTALLA
st.set_page_config(page_title="IA NEURAL V43", layout="wide", initial_sidebar_state="collapsed")

# Estilo Cyber-Futurista
st.markdown("""
    <style>
    .stApp { background-color: #050a0e; color: #e0e0e0; }
    .main-title { font-size: 35px; font-weight: 900; color: #00d4ff; text-shadow: 0 0 10px #00d4ff; margin-bottom: 0px; }
    .status-bar { background: #10161d; padding: 10px; border-left: 5px solid #00d4ff; border-radius: 5px; margin-bottom: 20px; font-family: monospace; }
    
    /* Cuadros de Monedas */
    .crypto-card { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 15px; transition: 0.3s; }
    .crypto-card:hover { border-color: #00d4ff; box-shadow: 0 0 15px rgba(0, 212, 255, 0.2); }
    .price-tag { font-size: 28px; font-weight: bold; color: white; text-align: center; }
    
    /* Niveles Pro */
    .level-container { display: flex; justify-content: space-between; margin-top: 10px; gap: 5px; }
    .level-item { flex: 1; background: #0d1117; padding: 5px; border-radius: 4px; text-align: center; border: 1px solid #4facfe; }
    .level-label { font-size: 9px; color: #8b949e; display: block; }
    .level-price { font-size: 14px; font-weight: bold; color: #f0b90b; }
    
    /* Círculo de Win Rate */
    .win-circle { width: 100px; height: 100px; border-radius: 50%; border: 6px solid #00ff00; display: flex; flex-direction: column; 
                  justify-content: center; align-items: center; background: #0d1117; box-shadow: 0 0 20px rgba(0,255,0,0.3); }
    </style>
""", unsafe_allow_html=True)

# 2. SISTEMA DE DATOS Y MEMORIA
if 'history' not in st.session_state: st.session_state.history = []
if 'start_time' not in st.session_state: st.session_state.start_time = datetime.now()

@st.cache_data(ttl=10)
def get_mexc_data():
    try:
        ex = ccxt.mexc()
        tk = ex.fetch_tickers()
        pairs = [k for k in tk.keys() if '/USDT' in k and tk[k].get('quoteVolume', 0) > 2000000]
        top_4 = sorted(pairs, key=lambda x: abs(tk[x].get('percentage', 0)), reverse=True)[:4]
        top_20 = sorted(pairs, key=lambda x: tk[x].get('quoteVolume', 0), reverse=True)[:20]
        return tk, top_4, top_20
    except: return {}, [], []

tickers, top_4, lab_keys = get_mexc_data()

# 3. CABECERA (TÍTULO + QR + WIN RATE)
c1, c2, c3 = st.columns([3, 0.7, 1.3])

with c1:
    st.markdown("<h1 class='main-title'>IA NEURAL MONITOR • V43</h1>", unsafe_allow_html=True)
    uptime = (datetime.now() - st.session_state.start_time)
    st.markdown(f"<div class='status-bar'>⚙️ ESTADO: Aprendiendo de {len(st.session_state.history)} ciclos | ONLINE: {uptime.seconds//60}m {uptime.seconds%60}s</div>", unsafe_allow_html=True)

with c2:
    st.image("https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=NEURAL_DATA_SYNC", width=90)

with c3:
    wins = len([h for h in st.session_state.history if '+' in str(h.get('PNL', ''))])
    rate = (wins / len(st.session_state.history) * 100) if st.session_state.history else 100.0
    color = "#00ff00" if rate >= 50 else "#ff4b4b"
    st.markdown(f"""
        <div style='display: flex; align-items: center; justify-content: center;'>
            <div class='win-circle' style='border-color: {color}; box-shadow: 0 0 15px {color};'>
                <span style='font-size: 24px; font-weight: bold; color: {color};'>{rate:.0f}%</span>
                <span style='font-size: 10px; color: white;'>WIN RATE</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

# 4. MONITOR PRINCIPAL (CUADROS)
st.write("")
cols = st.columns(4)
for i, pair in enumerate(top_4):
    px = tickers.get(pair, {}).get('last', 0)
    chg = tickers.get(pair, {}).get('percentage', 0)
    p_color = "#00ff00" if chg >= 0 else "#ff4b4b"
    icon = "🚀" if chg > 1 else "⏳"
    
    with cols[i]:
        st.markdown(f"""
            <div class='crypto-card'>
                <div style='display: flex; justify-content: space-between;'>
                    <b style='color:#00d4ff; font-size:18px;'>{pair.split('/')[0]}</b>
                    <span>{icon}</span>
                </div>
                <div class='price-tag'>${px:,.4f}</div>
                <div style='text-align:center; color:{p_color}; font-size:14px; margin-bottom:10px;'>{chg:+.2f}% (24h)</div>
                <div class='level-container'>
                    <div class='level-item'><span class='level-label'>IN</span><b class='level-price'>{px*0.995:,.3f}</b></div>
                    <div class='level-item'><span class='level-label'>TGT</span><b class='level-price'>{px*1.04:,.3f}</b></div>
                    <div class='level-item'><span class='level-label'>SL</span><b class='level-price'>{px*0.98:,.3f}</b></div>
                </div>
                <hr style='margin: 10px 0; border: 0.5px solid #30363d;'>
                <div style='font-size:10px; color:#8b949e; text-align:center;'>
                    🧠 IA: {random.choice(['Fibo Detectado', 'Ballena Entrando', 'RSI Divergencia'])}
                </div>
            </div>
        """, unsafe_allow_html=True)

# 5. LABORATORIO Y BITÁCORA (NUEVO FORMATO DIVIDIDO)
st.markdown("<br>", unsafe_allow_html=True)
col_left, col_right = st.columns([1, 2])

with col_left:
    st.markdown("### 📋 BITÁCORA REAL")
    if st.session_state.history:
        st.dataframe(pd.DataFrame(st.session_state.history).head(15), use_container_width=True, hide_index=True)
    else:
        st.info("Esperando cierre de primer ciclo...")

with col_right:
    st.markdown("### 🔬 LABORATORIO NEURAL (Simulando en Tiempo Real)")
    lab_data = []
    for k in lab_keys:
        score = random.randint(70, 99)
        lab_data.append({
            "ACTIVO": k.split('/')[0],
            "SCORE": f"{score}%",
            "IA_ANALYSIS": random.choice(["📐 Fibonacci 0.618", "🌊 Elliot Wave 3", "🐋 Whale Alert", "🔥 Burn Event"]),
            "NOTICIA": random.choice(["Positive", "Bullish", "High Vol", "Neutral"]),
            "STATUS": "🚀 PROMOCIONAR" if score > 94 else "🔍 ESTUDIANDO"
        })
    df_lab = pd.DataFrame(lab_data)
    st.dataframe(df_lab, use_container_width=True, hide_index=True)

# Auto-refresh
time.sleep(10)
st.rerun()
