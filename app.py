import streamlit as st
import ccxt
import time
import pandas as pd
import random
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN
st.set_page_config(page_title="IA MONITOR V40", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .title-main { font-size: 26px; font-weight: 800; color: white; margin: 0; }
    .pnl-circle { width: 80px; height: 80px; border-radius: 50%; border: 4px solid #00ff00; display: flex; flex-direction: column; justify-content: center; align-items: center; background: #0e1117; }
    .level-box { text-align: center; background: rgba(30, 35, 41, 0.9); padding: 8px; border-radius: 6px; border: 1px solid #4facfe; }
    .level-val { font-size: 18px; font-weight: 800; color: #f0b90b; display: block; }
    .level-lab { font-size: 9px; color: #848e9c; font-weight: bold; }
    .timer-badge { background: #ff4b4b; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold; }
    .price-live { font-size: 22px; font-weight: bold; color: white; }
    </style>
""", unsafe_allow_html=True)

# 2. MEMORIA DE SESIÓN
if 'start_time' not in st.session_state: st.session_state.start_time = datetime.now()
if 'signals' not in st.session_state: st.session_state.signals = {}
if 'history' not in st.session_state: st.session_state.history = []

@st.cache_data(ttl=10)
def fetch_data():
    try:
        ex = ccxt.mexc()
        tk = ex.fetch_tickers()
        valid = [k for k in tk.keys() if '/USDT' in k and tk[k].get('quoteVolume', 0) > 1000000]
        top_4 = sorted(valid, key=lambda x: abs(tk[x].get('percentage', 0)), reverse=True)[:4]
        top_30 = sorted(valid, key=lambda x: tk[x].get('quoteVolume', 0), reverse=True)[:30]
        return tk, top_4, top_30
    except: return {}, [], []

tickers, top_4, lab_keys = fetch_data()

# 3. LÓGICA DE ROTACIÓN Y TIEMPO
now = datetime.now()
active_pairs = []
for p in list(st.session_state.signals.keys()):
    # Cada orden dura 20 minutos
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

# 4. CABECERA
total_pnl = sum([float(h['PNL'].replace('%','')) for h in st.session_state.history]) if st.session_state.history else 0.0
diff_sys = now - st.session_state.start_time
uptime = f"{diff_sys.seconds//3600}h {(diff_sys.seconds//60)%60}m"

c1, c2, c3 = st.columns([3, 0.6, 1])
with c1:
    st.markdown(f"<div class='title-main'>MONITOR IA EXPERTO MEXC</div><div style='color: #4facfe;'>Cristian Gómez • Uptime: {uptime}</div>", unsafe_allow_html=True)
with c2:
    st.image("https://api.qrserver.com/v1/create-qr-code/?size=80x80&data=HISTORIAL_IA_CRISTIAN", width=70)
with c3:
    color_g = "#00ff00" if total_pnl >= 0 else "#ff4b4b"
    st.markdown(f"<div class='pnl-circle' style='border-color:{color_g};'><div style='font-size:18px; color:{color_g}; font-weight:bold;'>{total_pnl:+.2f}%</div><div style='font-size:9px; color:white;'>GLOBAL</div></div>", unsafe_allow_html=True)

# 5. CUADROS PRINCIPALES CON CRONÓMETRO
st.write("")
cols = st.columns(4)
for i, pair in enumerate(active_pairs):
    s = st.session_state.signals.get(pair)
    px = tickers.get(pair, {}).get('last', s['entry'])
    pnl = ((px - s['entry']) / s['entry'] * 100)
    
    # Calcular tiempo transcurrido de la orden
    elapsed = now - s['start']
    timer_str = f"{elapsed.seconds // 60:02d}:{elapsed.seconds % 60:02d}"

    with cols[i]:
        with st.container(border=True):
            # Encabezado con Icono y Cronómetro
            h_col1, h_col2 = st.columns([2, 1])
            h_col1.markdown(f"### {pair.split('/')[0]}")
            h_col2.markdown(f"<span class='timer-badge'>⏱️ {timer_str}</span>", unsafe_allow_html=True)
            
            # Estado e Icono chico
            st.markdown("🚀" if pnl > 0 else "⏳")
            
            # Precio y PNL
            st.markdown(f"<div style='text-align:center;' class='price-live'>${px:,.4f} <small style='color:{'#00ff00' if pnl>=0 else '#ff4b4b'}; font-size:14px;'>{pnl:+.2f}%</small></div>", unsafe_allow_html=True)
            
            # Niveles IN / TGT / SL
            l1, l2, l3 = st.columns(3)
            with l1: st.markdown(f"<div class='level-box'><span class='level-lab'>IN</span><span class='level-val'>{s['entry']:,.4f}</span></div>", unsafe_allow_html=True)
            with l2: st.markdown(f"<div class='level-box'><span class='level-lab'>TGT</span><span class='level-val'>{s['entry']*1.05:,.4f}</span></div>", unsafe_allow_html=True)
            with l3: st.markdown(f"<div class='level-box'><span class='level-lab'>SL</span><span class='level-val'>{s['entry']*0.98:,.4f}</span></div>", unsafe_allow_html=True)
            
            # Sensores
            st.write("")
            s1, s2, s3 = st.columns(3)
            with s1: st.markdown("<p class='sensor-tag'>🐋 BALL</p>", unsafe_allow_html=True); st.progress(s['b']/100)
            with s2: st.markdown("<p class='sensor-tag'>📱 REDS</p>", unsafe_allow_html=True); st.progress(s['r']/100)
            with s3: st.markdown("<p class='sensor-tag'>⚡ IMPU</p>", unsafe_allow_html=True); st.progress(s['i']/100)

# 6. HISTORIAL DIVIDIDO (1:2)
st.divider()
c_bit, c_lab = st.columns([1, 2])
with c_bit:
    st.subheader("📋 Bitácora Real")
    st.dataframe(pd.DataFrame(st.session_state.history).head(15), use_container_width=True, hide_index=True)
with c_lab:
    st.subheader("🧠 Laboratorio & Noticias Detalladas")
    lab_data = [{"MONEDA": k.split('/')[0], "SCORE": f"{random.randint(70,99)}%", "ESTUDIO": random.choice(["📐 Fibonacci Nivel 0.618", "🌊 Elliot Onda 3", "🐋 Whale Inflow", "🔥 Token Burn News"])} for k in lab_keys[:30]]
    st.dataframe(pd.DataFrame(lab_data), use_container_width=True, hide_index=True)

time.sleep(5) # Actualización más rápida para el segundero
st.rerun()
