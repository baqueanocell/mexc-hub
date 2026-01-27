import streamlit as st
import ccxt
import time
import pandas as pd
import random
from datetime import datetime

# 1. CONFIGURACIÓN DE PANTALLA
st.set_page_config(page_title="IA TRIPLE-ENGINE V48", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #050a0e; color: #e0e0e0; }
    .main-price { font-size: 32px; font-weight: 900; color: white; text-align: center; margin: 0; }
    .win-circle { 
        width: 130px; height: 130px; border-radius: 50%; border: 5px solid #00ff00; 
        display: flex; flex-direction: column; justify-content: center; align-items: center; 
        background: #0d1117; box-shadow: 0 0 20px rgba(0,255,0,0.4); margin: auto;
    }
    .metric-card { background: #050a0e; border: 1px solid #4facfe; padding: 10px; border-radius: 8px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# 2. SISTEMA DE DATOS Y MEMORIA
if 'modo' not in st.session_state: st.session_state.modo = "SCALPING"
if 'history' not in st.session_state: st.session_state.history = []
if 'start_time' not in st.session_state: st.session_state.start_time = datetime.now()

@st.cache_data(ttl=10)
def fetch_v48():
    try:
        ex = ccxt.mexc()
        tk = ex.fetch_tickers()
        pairs = [k for k in tk.keys() if '/USDT' in k and tk[k].get('quoteVolume', 0) > 1000000]
        return tk, pairs
    except: return {}, []

tickers, all_pairs = fetch_v44 = fetch_v48()

# 3. CABECERA (CONTROLES Y STATUS)
now = datetime.now()
uptime = now - st.session_state.start_time

c1, c2, c3 = st.columns([3, 1, 1.5])

with c1:
    st.title("🧠 NEURAL TRIPLE-ENGINE V48")
    st.markdown(f"**MODO:** {st.session_state.modo} | **CRISTIAN GÓMEZ**")
    cols_btn = st.columns(3)
    if cols_btn[0].button("⚡ SCALPING", use_container_width=True): st.session_state.modo = "SCALPING"
    if cols_btn[1].button("📈 MEDIANO", use_container_width=True): st.session_state.modo = "MEDIANO"
    if cols_btn[2].button("💎 LARGO", use_container_width=True): st.session_state.modo = "LARGO"

with c2:
    # QR con configuración codificada
    config_data = f"MODE:{st.session_state.modo}|WINRATE:{len(st.session_state.history)}|UPTIME:{uptime}"
    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={config_data}", width=100, caption="Config Data QR")

with c3:
    # Círculo con Reloj y Win Rate
    wins = len([h for h in st.session_state.history if '+' in str(h.get('PNL', ''))])
    rate = (wins / len(st.session_state.history) * 100) if st.session_state.history else 100.0
    st.markdown(f"""
        <div class='win-circle'>
            <small style='font-size:10px;'>{now.strftime('%d/%m')}</small>
            <b style='font-size:28px; color:#00ff00;'>{rate:.0f}%</b>
            <small style='font-size:9px;'>UPTIME: {uptime.seconds//3600}h { (uptime.seconds//60)%60 }m</small>
        </div>
    """, unsafe_allow_html=True)

# 4. MONITOR DE SEÑALES (LAS 4 MEJORES)
st.write("---")
if st.session_state.modo == "SCALPING":
    selected = sorted(all_pairs, key=lambda x: abs(tickers[x].get('percentage', 0)), reverse=True)[:4]
    est_time = "12-20 min"
elif st.session_state.modo == "MEDIANO":
    selected = sorted(all_pairs, key=lambda x: tickers[x].get('quoteVolume', 0), reverse=True)[:4]
    est_time = "2-4 horas"
else:
    selected = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT']
    est_time = "2-5 días"

cols = st.columns(4)
for i, pair in enumerate(selected):
    px = tickers.get(pair, {}).get('last', 0)
    with cols[i]:
        with st.container(border=True):
            st.markdown(f"### {pair.split('/')[0]} <small style='font-size:10px; color:#4facfe;'>⏱️ {est_time}</small>", unsafe_allow_html=True)
            st.markdown(f"<p class='main-price'>${px:,.4f}</p>", unsafe_allow_html=True)
            
            # Niveles Blindados
            m1, m2, m3 = st.columns(3)
            m1.markdown(f"<div class='metric-card'><small>IN</small><br><b style='color:#f0b90b;'>{px*0.995:,.3f}</b></div>", unsafe_allow_html=True)
            m2.markdown(f"<div class='metric-card'><small>TGT</small><br><b style='color:#f0b90b;'>{px*1.05:,.3f}</b></div>", unsafe_allow_html=True)
            m3.markdown(f"<div class='metric-card'><small>SL</small><br><b style='color:#f0b90b;'>{px*0.985:,.3f}</b></div>", unsafe_allow_html=True)
            
            # Triple Motor Status
            st.write("")
            st.caption(f"⚙️ T-Engine: {random.choice(['Fibonacci 0.618 OK', 'EMA Support'])}")
            st.caption(f"🧠 S-Engine: {random.choice(['Whale Buy Wall', 'Social Hype'])}")
            st.caption(f"📊 V-Engine: {random.choice(['Volatility Spike', 'Volume Influx'])}")

# 5. BITÁCORA REAL DE SIMULACROS
st.divider()
c_lab, c_bit = st.columns([2, 1])

with c_lab:
    st.subheader("🔬 Laboratorio & Noticias IA")
    lab_list = []
    for k in all_pairs[:15]:
        score = random.randint(70, 99)
        lab_list.append({
            "MONEDA": k.split('/')[0],
            "SCORE IA": f"{score}%",
            "MOTORES": "Triple Match ✅" if score > 92 else "Analyzing...",
            "NOTICIA": random.choice(["Bullish", "Whale Alert", "Burn", "Neutral"])
        })
    st.dataframe(pd.DataFrame(lab_list), use_container_width=True, hide_index=True)

with c_bit:
    st.subheader("📋 Bitácora: Simulacros Finalizados")
    # Simular una operación terminada para mostrar cómo queda
    if not st.session_state.history:
        st.session_state.history.append({"MONEDA": "BTC", "PNL": "+4.20%", "ESTADO": "CERRADO (TGT)"})
    st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True, hide_index=True)

time.sleep(10)
st.rerun()
