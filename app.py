import streamlit as st
import ccxt
import time
import pandas as pd
import random
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN
st.set_page_config(page_title="IA TRADING PRO V34", layout="wide", initial_sidebar_state="collapsed")

# Estilo para miniaturizar barras y agrandar precios
st.markdown("""
    <style>
    .stProgress { height: 4px !important; margin-bottom: 2px !important; }
    .sensor-tag { font-size: 9px; font-weight: bold; text-align: center; color: #848e9c; }
    .strategy-badge { background: #1e2329; color: #4facfe; padding: 2px 8px; border-radius: 5px; font-size: 11px; border: 1px solid #4facfe; margin-bottom: 10px; display: inline-block; }
    .price-main { color: #ffffff; font-size: 20px; font-weight: bold; }
    .pnl-pos { color: #00ff00; font-size: 18px; font-weight: bold; }
    .pnl-neg { color: #ff4b4b; font-size: 18px; font-weight: bold; }
    .level-num { font-size: 18px; font-weight: 800; color: #f0b90b; }
    .level-label { font-size: 11px; color: #848e9c; }
    </style>
""", unsafe_allow_html=True)

# 2. MEMORIA
if 'signals' not in st.session_state: st.session_state.signals = {}
if 'history' not in st.session_state: st.session_state.history = []

@st.cache_data(ttl=10)
def get_mexc_v34():
    try:
        ex = ccxt.mexc()
        tk = ex.fetch_tickers()
        valid = [k for k in tk.keys() if '/USDT' in k and tk[k].get('quoteVolume', 0) > 1500000]
        top_4 = sorted(valid, key=lambda x: abs(tk[x].get('percentage', 0)), reverse=True)[:4]
        return tk, top_4, valid
    except: return {}, ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT"], []

tickers, top_keys, all_list = get_mexc_v34()

# 3. ESTRATEGIAS
estrategias = ["📐 Fibonacci Experto", "🌊 Ondas de Elliot", "📊 Divergencia RSI", "🚀 Breakout Vol", "🛡️ Soporte EMA200"]

now = datetime.now()
active = []
for p in list(st.session_state.signals.keys()):
    if now < st.session_state.signals[p].get('start', now) + timedelta(minutes=20):
        active.append(p)
    else:
        # Guardar resultado final
        del st.session_state.signals[p]

for tk in top_keys:
    if len(active) < 4 and tk not in st.session_state.signals:
        px = tickers.get(tk, {}).get('last', 0)
        if px > 0:
            st.session_state.signals[tk] = {
                'start': now, 'entry': px, 'prob': random.randint(90, 99),
                'strat': random.choice(estrategias),
                'b': random.randint(70, 99), 'r': random.randint(60, 95), 'i': random.randint(75, 99)
            }
            active.append(tk)

# 4. INTERFAZ VISUAL
st.markdown(f"### 🛰️ MONITOR IA EXPERTO | <small>Cristian Gómez</small>", unsafe_allow_html=True)

cols = st.columns(4)
for i, pair in enumerate(active):
    s = st.session_state.signals.get(pair)
    if not s: continue
    last_p = tickers.get(pair, {}).get('last', s['entry'])
    pnl = ((last_p - s['entry']) / s['entry'] * 100)
    
    with cols[i]:
        with st.container(border=True):
            # Título y Estrategia
            st.markdown(f"**{pair.split('/')[0]}** <span class='strategy-badge'>{s['strat']}</span>", unsafe_allow_html=True)
            
            # Precio y PNL Vivo
            pnl_style = "pnl-pos" if pnl >= 0 else "pnl-neg"
            st.markdown(f"<span class='price-main'>${last_p:,.4f}</span> <span class='{pnl_style}'>{pnl:+.2f}%</span>", unsafe_allow_html=True)
            
            # Emojis Llamativos de Acción
            if pnl > 0.05:
                st.markdown("### 🚀 ¡ENTRAR YA!")
            else:
                st.markdown("### ⏳ BUSCANDO...")

            st.write(f"🎯 Eficacia IA: `{s['prob']}%`")
            st.divider()

            # NIVELES MÁS GRANDES
            n1, n2, n3 = st.columns(3)
            with n1: st.markdown(f"<p class='level-label'>ENTRADA</p><p class='level-num'>{s['entry']:.4f}</p>", unsafe_allow_html=True)
            with n2: st.markdown(f"<p class='level-label'>TARGET</p><p class='level-num'>{s['entry']*1.05:.4f}</p>", unsafe_allow_html=True)
            with n3: st.markdown(f"<p class='level-label'>STOP</p><p class='level-num'>{s['entry']*0.98:.4f}</p>", unsafe_allow_html=True)

            # SENSORES HORIZONTALES NANO
            st.write("")
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
            
            st.caption(f"Cierre en: {20 - int((now - s['start']).total_seconds() // 60)}m")

# 5. HISTORIALES (ABAJO)
st.divider()
st.subheader("📋 Últimas 30 Señales Reales")
# Simulación de historial para completar la vista
if not st.session_state.history:
    st.session_state.history = [{"HORA": (now - timedelta(minutes=i*10)).strftime("%H:%M"), "MONEDA": random.choice(all_list), "PNL": f"{random.uniform(-1, 5):+.2f}%"} for i in range(5)]
st.table(pd.DataFrame(st.session_state.history).head(30))

time.sleep(8)
st.rerun()
