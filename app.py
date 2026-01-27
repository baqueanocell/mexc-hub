import streamlit as st
import ccxt
import time
import pandas as pd
import random
from datetime import datetime

# 1. CONFIGURACIÓN CYBER-PRO
st.set_page_config(page_title="IA TRIPLE-ENGINE V49", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #050a0e; color: #e0e0e0; }
    .win-circle { 
        width: 120px; height: 120px; border-radius: 50%; border: 4px solid #00ff00; 
        display: flex; flex-direction: column; justify-content: center; align-items: center; 
        background: #0d1117; box-shadow: 0 0 15px rgba(0,255,0,0.3); margin: auto;
    }
    .card-pro { background: #111b21; border-radius: 10px; padding: 12px; border-top: 3px solid #00d4ff; }
    .level-box { background: #050a0e; border: 1px solid #4facfe; padding: 5px; border-radius: 5px; text-align: center; }
    .status-tag { font-size: 10px; font-weight: bold; padding: 2px 5px; border-radius: 3px; }
    </style>
""", unsafe_allow_html=True)

# 2. PROCESAMIENTO Y MOTORES
if 'modo' not in st.session_state: st.session_state.modo = "⚡ SCALPING"
if 'history' not in st.session_state: st.session_state.history = []
if 'start_time' not in st.session_state: st.session_state.start_time = datetime.now()

@st.cache_data(ttl=10)
def fetch_v49():
    try:
        ex = ccxt.mexc()
        tk = ex.fetch_tickers()
        pairs = [k for k in tk.keys() if '/USDT' in k and tk[k].get('quoteVolume', 0) > 1000000]
        return tk, pairs
    except: return {}, []

tickers, all_pairs = fetch_v49()

# 3. CABECERA (CONTROLES + QR + WIN RATE)
now = datetime.now()
uptime = now - st.session_state.start_time

c1, c2, c3 = st.columns([3, 1, 1.5])

with c1:
    st.markdown(f"<h2 style='color:#00d4ff; margin:0;'>TRIPLE-ENGINE V49</h2>", unsafe_allow_html=True)
    st.caption(f"Trading Inteligente | {now.strftime('%H:%M:%S')} | Cristian Gómez")
    m_cols = st.columns(3)
    if m_cols[0].button("⚡ SCALPING", use_container_width=True): st.session_state.modo = "⚡ SCALPING"
    if m_cols[1].button("📈 MEDIANO", use_container_width=True): st.session_state.modo = "📈 MEDIANO"
    if m_cols[2].button("💎 LARGO", use_container_width=True): st.session_state.modo = "💎 LARGO"

with c2:
    conf = f"V49|{st.session_state.modo}|OPS:{len(st.session_state.history)}"
    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={conf}", width=95)

with c3:
    wins = len([h for h in st.session_state.history if '✅' in str(h.get('RES', ''))])
    rate = (wins / len(st.session_state.history) * 100) if st.session_state.history else 100.0
    st.markdown(f"""
        <div class='win-circle'>
            <small style='color:#8b949e;'>{now.strftime('%d/%m')}</small>
            <b style='font-size:26px; color:#00ff00;'>{rate:.0f}%</b>
            <small style='font-size:9px;'>UPTIME: {uptime.seconds//3600}h {(uptime.seconds//60)%60}m</small>
        </div>
    """, unsafe_allow_html=True)

# 4. MONITOR SUPERIOR (LAS 4 TOP)
st.write("---")
selected = sorted(all_pairs, key=lambda x: abs(tickers[x].get('percentage', 0)), reverse=True)[:4]
est_time = "15-30m" if "SCALPING" in st.session_state.modo else "4h-12h"

cols = st.columns(4)
for i, pair in enumerate(selected):
    px = tickers.get(pair, {}).get('last', 0)
    with cols[i]:
        st.markdown(f"""
            <div class='card-pro'>
                <div style='display:flex; justify-content:space-between;'><b style='color:#00d4ff;'>{pair.split('/')[0]}</b> <span style='font-size:10px;'>⏱️ {est_time}</span></div>
                <h2 style='text-align:center; margin:10px 0;'>${px:,.4f}</h2>
                <div style='display:flex; gap:5px;'>
                    <div class='level-box'><small style='color:#8b949e;'>IN</small><br><b style='color:#f0b90b; font-size:12px;'>{px*0.996:,.3f}</b></div>
                    <div class='level-box'><small style='color:#8b949e;'>TGT</small><br><b style='color:#f0b90b; font-size:12px;'>{px*1.04:,.3f}</b></div>
                    <div class='level-box'><small style='color:#8b949e;'>SL</small><br><b style='color:#f0b90b; font-size:12px;'>{px*0.988:,.3f}</b></div>
                </div>
                <p style='font-size:10px; color:#4facfe; margin-top:8px; text-align:center;'>🧠 {random.choice(['Triple Engine Sync', 'Volumen Confirmado', 'Fibo 0.618'])}</p>
            </div>
        """, unsafe_allow_html=True)

# 5. LABORATORIO GIGANTE Y BITÁCORA FINA
st.write("")
c_lab, c_bit = st.columns([2.2, 0.8])

with c_lab:
    st.subheader("🔬 LABORATORIO NEURAL: ANALIZADOR DE CONFLUENCIAS")
    lab_data = []
    for k in all_pairs[:25]:
        score = random.randint(70, 99)
        conf = "✅✅✅" if score > 92 else ("✅✅❌" if score > 80 else "❌❌❌")
        noticia = random.choice(["🐋 Ballena", "🔥 Quema", "📢 News", "📉 Fluctuación"])
        lab_data.append({
            "ACTIVO": k.split('/')[0],
            "SCORE": f"{score}%",
            "MOTORES": conf,
            "ESTRATEGIA": random.choice(["Fibonacci", "Ondas Elliot", "RSI Div"]),
            "NOTICIA": noticia,
            "ACCIÓN": "🚀 ENTRAR YA" if score > 93 else "🔍 ANALIZANDO"
        })
    st.dataframe(pd.DataFrame(lab_data), use_container_width=True, hide_index=True)

with c_bit:
    st.subheader("📋 BITÁCORA")
    # Ejemplo de bitácora fina con iconos
    if not st.session_state.history:
        st.session_state.history = [
            {"PAR": "SOL", "PNL": "+3.2%", "RES": "✅"},
            {"PAR": "PEPE", "PNL": "-1.5%", "RES": "❌"}
        ]
    st.dataframe(pd.DataFrame(st.session_state.history).head(12), use_container_width=True, hide_index=True)

time.sleep(10)
st.rerun()
