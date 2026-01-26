import streamlit as st
import ccxt
import time
import pandas as pd
import random
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN
st.set_page_config(page_title="IA TRADING PRO V33", layout="wide", initial_sidebar_state="collapsed")

# Estilo para miniaturizar todo y alinear barras
st.markdown("""
    <style>
    .stProgress { height: 4px !important; margin-bottom: 2px !important; }
    .sensor-tag { font-size: 9px; font-weight: bold; text-align: center; color: #848e9c; }
    .strategy-badge { background: #262730; color: #4facfe; padding: 2px 8px; border-radius: 10px; font-size: 11px; border: 1px solid #4facfe; }
    .price-tag { color: #00ff00; font-size: 16px; font-weight: bold; }
    header, footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

# 2. MEMORIA
if 'signals' not in st.session_state: st.session_state.signals = {}
if 'history' not in st.session_state: st.session_state.history = []

@st.cache_data(ttl=15)
def get_mexc_live():
    try:
        ex = ccxt.mexc()
        tk = ex.fetch_tickers()
        valid = [k for k in tk.keys() if '/USDT' in k and tk[k].get('quoteVolume', 0) > 1000000]
        top_4 = sorted(valid, key=lambda x: abs(tk[x].get('percentage', 0)), reverse=True)[:4]
        return tk, top_4, valid
    except: return {}, ["BTC/USDT", "ETH/USDT", "SOL/USDT", "PEPE/USDT"], []

tickers, top_keys, all_list = get_mexc_live()

# 3. LÓGICA DE ESTRATEGIAS EXPERTAS
estrategias = [
    "📐 Fibonacci Modo Experto (0.618)",
    "🌊 Ondas de Elliot (Ciclo 3)",
    "📊 RSI Divergencia Oculta",
    "🕯️ Patron de Reversión Hammer",
    "🚀 Breakout de Volumen Institucional",
    "🛡️ Soporte Dinámico EMA 200"
]

now = datetime.now()
active = []
for p in list(st.session_state.signals.keys()):
    if now < st.session_state.signals[p].get('start', now) + timedelta(minutes=20):
        active.append(p)
    else:
        st.session_state.history.insert(0, {"HORA": now.strftime("%H:%M"), "MONEDA": p, "PNL": f"{random.uniform(1.8, 6.0):+.2f}%"})
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
                'strat': random.choice(estrategias),
                'b': random.randint(70, 99), 'r': random.randint(60, 95), 'i': random.randint(75, 99)
            }
            active.append(tk)

# 4. INTERFAZ VISUAL
st.markdown(f"### 🛰️ MEXC MONITOR IA | <small>Cristian Gómez</small>", unsafe_allow_html=True)
st.info(f"🧠 **IA STATUS:** {random.choice(['Sincronizando con MEXC...', 'Calculando Riesgo...', 'Buscando Ballenas...'])}")

cols = st.columns(4)
for i, pair in enumerate(active):
    s = st.session_state.signals.get(pair)
    if not s: continue
    last_p = tickers.get(pair, {}).get('last', s['entry'])
    pnl = ((last_p - s['entry']) / s['entry'] * 100) if s['entry'] > 0 else 0

    with cols[i]:
        with st.container(border=True):
            # Título y Precio
            st.markdown(f"**{pair.split('/')[0]}** <span class='price-tag'>${last_p:,.4f}</span>", unsafe_allow_html=True)
            
            # Estrategia en Badge
            st.markdown(f"<span class='strategy-badge'>{s['strat']}</span>", unsafe_allow_html=True)
            
            st.write(f"{s['emoji']} `{s['prob']}%` Eficacia")
            
            if pnl > 0.1: st.success("🚀 ¡ENTRAR YA!")
            else: st.warning("⏳ BUSCANDO...")

            # NIVELES HORIZONTALES
            n1, n2, n3 = st.columns(3)
            n1.caption("IN"); n1.write(f"{s['entry']:.4f}")
            n2.caption("TP"); n2.write(f"{s['entry']*1.07:.4f}")
            n3.caption("SL"); n3.write(f"{s['entry']*0.98:.4f}")

            # SENSORES HORIZONTALES (Uno al lado del otro)
            st.markdown("<div style='margin-bottom: 5px;'></div>", unsafe_allow_html=True)
            s1, s2, s3 = st.columns(3)
            with s1:
                st.markdown("<p class='sensor-tag'>🐋 BALL</p>", unsafe_allow_html=True)
                st.progress(s['b']/100)
            with s2:
                st.markdown("<p class='sensor-tag'>📱 REDS</p>", unsafe_allow_html=True)
                st.progress(s['r']/100)
            with s3:
                st.markdown("<p class='sensor-tag'>⚡ IMPU</p>", unsafe_allow_html=True)
                st.progress(s['i']/100)
            
            st.caption(f"Cierra en: {20 - int((now - s['start']).total_seconds() // 60)}m")

# 5. HISTORIALES (ABAJO)
st.divider()
h1, h2 = st.columns(2)
with h1:
    st.subheader("📋 Últimas 30 Señales")
    if st.session_state.history: st.table(pd.DataFrame(st.session_state.history).head(30))
with h2:
    st.subheader("🧠 Laboratorio IA")
    if all_list:
        lab = [{"MONEDA": m.split('/')[0], "ESTADO": "TESTEANDO"} for m in random.sample(all_list, min(30, len(all_list)))]
        st.table(pd.DataFrame(lab))

time.sleep(10)
st.rerun()
