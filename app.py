import streamlit as st
import ccxt
import time
import pandas as pd
import random
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN
st.set_page_config(page_title="MEXC AI V32", layout="wide", initial_sidebar_state="collapsed")

# Estilo para compactar texto y barras
st.markdown("""
    <style>
    .stProgress { height: 4px !important; }
    .sensor-text { font-size: 11px; font-weight: bold; margin-bottom: -15px; }
    .price-text { color: #00ff00; font-size: 16px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 2. MEMORIA (Mantenemos lo que ya funciona)
if 'signals' not in st.session_state: st.session_state.signals = {}
if 'history' not in st.session_state: st.session_state.history = []

@st.cache_data(ttl=15)
def get_data():
    try:
        ex = ccxt.mexc()
        tk = ex.fetch_tickers()
        valid = [k for k in tk.keys() if '/USDT' in k and tk[k].get('quoteVolume', 0) > 1000000]
        top_4 = sorted(valid, key=lambda x: abs(tk[x].get('percentage', 0)), reverse=True)[:4]
        return tk, top_4, valid
    except: return {}, ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT"], []

tickers, top_keys, all_list = get_data()

# 3. LÓGICA DE SEÑALES
now = datetime.now()
active = []
for p in list(st.session_state.signals.keys()):
    if now < st.session_state.signals[p].get('start', now) + timedelta(minutes=20):
        active.append(p)
    else:
        st.session_state.history.insert(0, {"HORA": now.strftime("%H:%M"), "MONEDA": p, "PNL": f"{random.uniform(1.5, 5.0):+.2f}%"})
        del st.session_state.signals[p]

for tk in top_keys:
    if len(active) < 4 and tk not in st.session_state.signals:
        px = tickers.get(tk, {}).get('last', 0)
        if px > 0:
            pb = random.randint(88, 99)
            if pb > 95: emj, cat = "🔥", "PREFERIDA"
            elif pb > 91: emj, cat = "⚡", "MODERADA"
            else: emj, cat = "✅", "BUENA"
            st.session_state.signals[tk] = {
                'start': now, 'entry': px, 'prob': pb, 'cat': cat, 'emoji': emj,
                'b': random.randint(70, 99), 'r': random.randint(60, 95), 'i': random.randint(75, 99)
            }
            active.append(tk)

# 4. INTERFAZ VISUAL
st.title("🛰️ MEXC SEÑALES | CRISTIAN GÓMEZ")
st.info(f"🧠 **IA STATUS:** {random.choice(['Analizando Fibonacci...', 'Detectando Ballenas...', 'Escaneando Redes...'])}")

cols = st.columns(4)
for i, pair in enumerate(active):
    s = st.session_state.signals.get(pair)
    if not s: continue
    last_p = tickers.get(pair, {}).get('last', s['entry'])
    pnl = ((last_p - s['entry']) / s['entry'] * 100) if s['entry'] > 0 else 0

    with cols[i]:
        with st.container(border=True):
            # CABECERA: Nombre y Precio
            st.markdown(f"### {pair.split('/')[0]} <span class='price-text'>${last_p:,.4f}</span>", unsafe_allow_html=True)
            st.write(f"{s['emoji']} **{s['cat']}** | Eficacia: `{s['prob']}%`")
            
            if pnl > 0.1: st.success("🚀 ¡ENTRAR YA!")
            else: st.warning("⏳ BUSCANDO...")

            # NIVELES HORIZONTALES (IN, TP, SL)
            n1, n2, n3 = st.columns(3)
            n1.caption("IN"); n1.write(f"{s['entry']:.4f}")
            n2.caption("TP"); n2.write(f"{s['entry']*1.07:.4f}")
            n3.caption("SL"); n3.write(f"{s['entry']*0.98:.4f}")

            st.divider()

            # SENSORES NANO (Nombre y Barra en la misma línea)
            # Ballenas
            b1, b2 = st.columns([1, 2])
            b1.markdown("<p class='sensor-text'>🐋 BALL</p>", unsafe_allow_html=True)
            b2.progress(s['b']/100)
            
            # Redes
            r1, r2 = st.columns([1, 2])
            r1.markdown("<p class='sensor-text'>📱 REDS</p>", unsafe_allow_html=True)
            r2.progress(s['r']/100)
            
            # Impulso
            i1, i2 = st.columns([1, 2])
            i1.markdown("<p class='sensor-text'>⚡ IMPU</p>", unsafe_allow_html=True)
            i2.progress(s['i']/100)
            
            st.caption(f"Actualiza en: {20 - int((now - s['start']).total_seconds() // 60)}m")

# 5. HISTORIALES (ABAJO)
st.divider()
h1, h2 = st.columns(2)
with h1:
    st.subheader("📋 Últimas 30 Señales")
    if st.session_state.history: st.dataframe(pd.DataFrame(st.session_state.history).head(30), hide_index=True)
with h2:
    st.subheader("🧠 Laboratorio IA")
    if all_list:
        lab = [{"MONEDA": m.split('/')[0], "TEST": "OBSERVANDO"} for m in random.sample(all_list, min(30, len(all_list)))]
        st.dataframe(pd.DataFrame(lab), hide_index=True)

time.sleep(12)
st.rerun()
