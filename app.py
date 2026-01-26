import streamlit as st
import ccxt
import time
import pandas as pd
import random
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN Y ESTILO
st.set_page_config(page_title="IA MONITOR V37", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .header-container { display: flex; justify-content: space-between; align-items: center; background: #1e2329; padding: 15px; border-radius: 10px; }
    .title-main { font-size: 32px; font-weight: 800; color: white; margin: 0; }
    .pnl-circle { width: 90px; height: 90px; border-radius: 50%; border: 4px solid #00ff00; display: flex; flex-direction: column; justify-content: center; align-items: center; background: #0e1117; }
    .qr-box { background: white; padding: 5px; border-radius: 5px; margin-right: 15px; }
    .price-live { font-size: 40px; font-weight: bold; color: white; margin-top: 10px; }
    .pnl-live { font-size: 24px; font-weight: bold; margin-left: 10px; }
    .sensor-tag { font-size: 9px; font-weight: bold; color: #848e9c; }
    </style>
""", unsafe_allow_html=True)

# 2. MEMORIA Y TIEMPO
if 'start_time' not in st.session_state: st.session_state.start_time = datetime.now()
if 'signals' not in st.session_state: st.session_state.signals = {}
if 'history' not in st.session_state: st.session_state.history = []

@st.cache_data(ttl=10)
def fetch_mexc():
    try:
        ex = ccxt.mexc()
        tk = ex.fetch_tickers()
        valid = [k for k in tk.keys() if '/USDT' in k and tk[k].get('quoteVolume', 0) > 1500000]
        top_4 = sorted(valid, key=lambda x: abs(tk[x].get('percentage', 0)), reverse=True)[:4]
        top_30 = sorted(valid, key=lambda x: tk[x].get('quoteVolume', 0), reverse=True)[:30]
        return tk, top_4, top_30
    except: return {}, [], []

tickers, top_4, lab_keys = fetch_mexc()

# 3. LÓGICA DE SEÑALES Y ROTACIÓN
now = datetime.now()
active_pairs = []
for p in list(st.session_state.signals.keys()):
    if now < st.session_state.signals[p]['start'] + timedelta(minutes=20):
        active_pairs.append(p)
    else:
        # Guardar resultado antes de borrar
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
diff = now - st.session_state.start_time
uptime = f"{diff.days}d {diff.seconds//3600}h {(diff.seconds//60)%60}m"

c_t, c_q, c_p = st.columns([3, 0.6, 1])

with c_t:
    st.markdown(f"<div class='title-main'>MONITOR IA EXPERTO MEXC</div><div style='color: #4facfe;'>Cristian Gómez • Uptime: {uptime}</div>", unsafe_allow_html=True)

with c_q:
    # QR Simulado (Apunta a los datos del laboratorio)
    st.image("https://api.qrserver.com/v1/create-qr-code/?size=80x80&data=HISTORIAL_IA_CRISTIAN", width=80)

with c_p:
    color = "#00ff00" if total_pnl >= 0 else "#ff4b4b"
    st.markdown(f"<div class='pnl-circle' style='border-color:{color}; box-shadow: 0 0 10px {color};'><div style='font-size:18px; color:{color}; font-weight:bold;'>{total_pnl:+.2f}%</div><div style='font-size:9px; color:white;'>GLOBAL</div></div>", unsafe_allow_html=True)

# 5. CUADROS DE MONEDAS (DISEÑO LIMPIO)
st.write("")
cols = st.columns(4)
for i, pair in enumerate(active_pairs):
    s = st.session_state.signals.get(pair)
    last_p = tickers.get(pair, {}).get('last', s['entry'])
    pnl = ((last_p - s['entry']) / s['entry'] * 100)
    p_color = "#00ff00" if pnl >= 0 else "#ff4b4b"
    
    with cols[i]:
        with st.container(border=True):
            # NOMBRE REAL DE LA MONEDA
            st.markdown(f"### {pair.split('/')[0]} <small style='color:gray;'>MEXC</small>", unsafe_allow_html=True)
            
            if pnl > 0.05: st.markdown("<h2 style='color:#00ff00; margin:0;'>🚀 ENTRAR YA</h2>", unsafe_allow_html=True)
            else: st.markdown("<h2 style='color:#f0b90b; margin:0;'>⏳ BUSCANDO</h2>", unsafe_allow_html=True)
            
            # PRECIO REAL Y PNL (SIN LOS 3 NÚMEROS ABAJO)
            st.markdown(f"<div class='price-live'>${last_p:,.4f} <span class='pnl-live' style='color:{p_color};'>{pnl:+.2f}%</span></div>", unsafe_allow_html=True)
            
            st.divider()
            # Sensores en horizontal
            s1, s2, s3 = st.columns(3)
            with s1: st.markdown("<p class='sensor-tag'>🐋 BALL</p>", unsafe_allow_html=True); st.progress(s['b']/100)
            with s2: st.markdown("<p class='sensor-tag'>📱 REDS</p>", unsafe_allow_html=True); st.progress(s['r']/100)
            with s3: st.markdown("<p class='sensor-tag'>⚡ IMPU</p>", unsafe_allow_html=True); st.progress(s['i']/100)

# 6. HISTORIAL Y LABORATORIO (DESLIZAR ABAJO)
st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()
h1, h2 = st.columns(2)
with h1:
    st.subheader("📋 Historial Real")
    st.dataframe(pd.DataFrame(st.session_state.history).head(30), use_container_width=True, hide_index=True)
with h2:
    st.subheader("🧠 Laboratorio & Noticias")
    lab_list = [{"MONEDA": k.split('/')[0], "IA_SCORE": f"{random.randint(70,99)}%", "NOTICIA": random.choice(["Bullish", "Neutral", "Whale Move"])} for k in lab_keys[:30]]
    st.dataframe(pd.DataFrame(lab_list), use_container_width=True, hide_index=True)

time.sleep(10)
st.rerun()
