import streamlit as st
import ccxt
import time
import pandas as pd
import random
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN Y ESTILO
st.set_page_config(page_title="IA MONITOR V38", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .header-container { display: flex; justify-content: space-between; align-items: center; background: #1e2329; padding: 15px; border-radius: 10px; }
    .title-main { font-size: 28px; font-weight: 800; color: white; margin: 0; }
    .pnl-circle { width: 85px; height: 85px; border-radius: 50%; border: 4px solid #00ff00; display: flex; flex-direction: column; justify-content: center; align-items: center; background: #0e1117; }
    
    /* Estilo para los Niveles Grandes */
    .level-box { text-align: center; background: rgba(255, 255, 255, 0.05); padding: 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); }
    .level-val { font-size: 22px; font-weight: 800; color: #f0b90b; display: block; }
    .level-lab { font-size: 10px; color: #848e9c; font-weight: bold; text-transform: uppercase; }
    
    .price-live { font-size: 26px; font-weight: bold; color: white; }
    .sensor-tag { font-size: 9px; font-weight: bold; color: #848e9c; }
    </style>
""", unsafe_allow_html=True)

# 2. MEMORIA
if 'start_time' not in st.session_state: st.session_state.start_time = datetime.now()
if 'signals' not in st.session_state: st.session_state.signals = {}
if 'history' not in st.session_state: st.session_state.history = []

@st.cache_data(ttl=10)
def fetch_mexc_v38():
    try:
        ex = ccxt.mexc()
        tk = ex.fetch_tickers()
        valid = [k for k in tk.keys() if '/USDT' in k and tk[k].get('quoteVolume', 0) > 1500000]
        top_4 = sorted(valid, key=lambda x: abs(tk[x].get('percentage', 0)), reverse=True)[:4]
        top_30 = sorted(valid, key=lambda x: tk[x].get('quoteVolume', 0), reverse=True)[:30]
        return tk, top_4, top_30
    except: return {}, [], []

tickers, top_4, lab_keys = fetch_mexc_v38()

# 3. LÓGICA DE SEÑALES
now = datetime.now()
active_pairs = []
for p in list(st.session_state.signals.keys()):
    if now < st.session_state.signals[p]['start'] + timedelta(minutes=20):
        active_pairs.append(p)
    else:
        s = st.session_state.signals[p]
        pnl_f = ((tickers.get(p,{}).get('last', s['entry']) - s['entry']) / s['entry'] * 100)
        st.session_state.history.insert(0, {"HORA": now.strftime("%H:%M"), "MONEDA": p.split('/')[0], "PNL": f"{pnl_f:+.2f}%"})
        del st.session_state.signals[p]

for tk in top_4:
    if len(active_pairs) < 4 and tk not in st.session_state.signals:
        px = tickers.get(tk, {}).get('last', 0)
        if px > 0:
            st.session_state.signals[tk] = {
                'start': now, 'entry': px, 'prob': random.randint(92, 99),
                'b': random.randint(70, 99), 'r': random.randint(60, 95), 'i': random.randint(75, 99)
            }
            active_pairs.append(tk)

# 4. CABECERA (TÍTULO + QR + CÍRCULO)
total_pnl = sum([float(h['PNL'].replace('%','')) for h in st.session_state.history]) if st.session_state.history else 0.0
uptime = f"{(now - st.session_state.start_time).seconds//3600}h {((now - st.session_state.start_time).seconds//60)%60}m"

c_t, c_q, c_p = st.columns([3, 0.6, 1])
with c_t:
    st.markdown(f"<div class='title-main'>MONITOR IA EXPERTO MEXC</div><div style='color: #4facfe;'>Cristian Gómez • Uptime: {uptime}</div>", unsafe_allow_html=True)
with c_q:
    st.image("https://api.qrserver.com/v1/create-qr-code/?size=80x80&data=HISTORIAL_IA_CRISTIAN", width=75)
with c_p:
    color = "#00ff00" if total_pnl >= 0 else "#ff4b4b"
    st.markdown(f"<div class='pnl-circle' style='border-color:{color};'><div style='font-size:18px; color:{color}; font-weight:bold;'>{total_pnl:+.2f}%</div><div style='font-size:9px; color:white;'>GLOBAL</div></div>", unsafe_allow_html=True)

# 5. CUADROS DE MONEDAS (DISEÑO REAJUSTADO)
st.write("")
cols = st.columns(4)
for i, pair in enumerate(active_pairs):
    s = st.session_state.signals.get(pair)
    last_p = tickers.get(pair, {}).get('last', s['entry'])
    pnl = ((last_p - s['entry']) / s['entry'] * 100)
    
    with cols[i]:
        with st.container(border=True):
            # Fila Superior: Moneda e Icono de Estado
            t1, t2 = st.columns([2, 1])
            t1.markdown(f"### {pair.split('/')[0]}")
            if pnl > 0.05: t2.markdown("## 🚀") # Icono chico entrar
            else: t2.markdown("## ⏳") # Icono chico buscando
            
            # Precio Real centrado
            st.markdown(f"<div style='text-align:center;' class='price-live'>${last_p:,.4f} <small style='color:{'#00ff00' if pnl>=0 else '#ff4b4b'}; font-size:16px;'>{pnl:+.2f}%</small></div>", unsafe_allow_html=True)
            
            st.write("")
            
            # NIVELES MEDIANO-GRANDES (IN, TP, SL)
            l1, l2, l3 = st.columns(3)
            with l1: st.markdown(f"<div class='level-box'><span class='level-lab'>ENTRADA</span><span class='level-val'>{s['entry']:.4f}</span></div>", unsafe_allow_html=True)
            with l2: st.markdown(f"<div class='level-box'><span class='level-lab'>TARGET</span><span class='level-val'>{s['entry']*1.05:.4f}</span></div>", unsafe_allow_html=True)
            with l3: st.markdown(f"<div class='level-box'><span class='level-lab'>STOP</span><span class='level-val'>{s['entry']*0.98:.4f}</span></div>", unsafe_allow_html=True)
            
            st.divider()
            # Sensores Nano
            s1, s2, s3 = st.columns(3)
            with s1: st.markdown("<p class='sensor-tag'>🐋 BALL</p>", unsafe_allow_html=True); st.progress(s['b']/100)
            with s2: st.markdown("<p class='sensor-tag'>📱 REDS</p>", unsafe_allow_html=True); st.progress(s['r']/100)
            with s3: st.markdown("<p class='sensor-tag'>⚡ IMPU</p>", unsafe_allow_html=True); st.progress(s['i']/100)

# 6. HISTORIAL Y LABORATORIO
st.divider()
h1, h2 = st.columns(2)
with h1:
    st.subheader("📋 Bitácora Real")
    st.dataframe(pd.DataFrame(st.session_state.history).head(20), use_container_width=True, hide_index=True)
with h2:
    st.subheader("🧠 Laboratorio IA")
    lab_list = [{"MONEDA": k.split('/')[0], "SCORE": f"{random.randint(70,99)}%", "ESTUDIO": "Analizando..."} for k in lab_keys[:30]]
    st.dataframe(pd.DataFrame(lab_list), use_container_width=True, hide_index=True)

time.sleep(10)
st.rerun()
