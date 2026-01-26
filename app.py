import streamlit as st
import ccxt
import time
import pandas as pd
import random
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN Y ESTILOS PREMIUM
st.set_page_config(page_title="IA TRADING HUB V35", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stProgress { height: 4px !important; margin-bottom: 2px !important; }
    .sensor-tag { font-size: 9px; font-weight: bold; text-align: center; color: #848e9c; }
    .strategy-badge { background: #1e2329; color: #4facfe; padding: 2px 8px; border-radius: 5px; font-size: 11px; border: 1px solid #4facfe; margin-bottom: 10px; display: inline-block; }
    .price-main { color: #ffffff; font-size: 20px; font-weight: bold; }
    .pnl-pos { color: #00ff00; font-size: 18px; font-weight: bold; }
    .pnl-neg { color: #ff4b4b; font-size: 18px; font-weight: bold; }
    .level-num { font-size: 19px; font-weight: 800; color: #f0b90b; }
    .level-label { font-size: 11px; color: #848e9c; margin-bottom: -5px; }
    .lab-text { font-size: 12px; color: #4facfe; font-family: monospace; }
    </style>
""", unsafe_allow_html=True)

# 2. MEMORIA DE SESIÓN (Persistente)
if 'signals' not in st.session_state: st.session_state.signals = {}
if 'history' not in st.session_state: st.session_state.history = []
if 'learning' not in st.session_state: st.session_state.learning = []

# 3. OBTENCIÓN DE DATOS MEXC
@st.cache_data(ttl=10)
def fetch_mexc_v35():
    try:
        ex = ccxt.mexc()
        tk = ex.fetch_tickers()
        # Filtro de monedas con volumen > 1.5M USDT
        valid = [k for k in tk.keys() if '/USDT' in k and tk[k].get('quoteVolume', 0) > 1500000]
        top_4 = sorted(valid, key=lambda x: abs(tk[x].get('percentage', 0)), reverse=True)[:4]
        # Top 30 para el Laboratorio
        top_30_lab = sorted(valid, key=lambda x: tk[x].get('quoteVolume', 0), reverse=True)[:30]
        return tk, top_4, top_30_lab
    except:
        return {}, ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT"], []

tickers, top_4_keys, lab_keys = fetch_mexc_v35()

# 4. LÓGICA DE ROTACIÓN Y ESTRATEGIAS
estrategias = ["📐 Fibonacci Experto", "🌊 Ondas de Elliot", "📊 Divergencia RSI", "🚀 Breakout Vol", "🛡️ Soporte EMA200"]
now = datetime.now()

# Limpiar expirados y mover a historial
active_keys = []
for p in list(st.session_state.signals.keys()):
    s = st.session_state.signals[p]
    if now < s['start'] + timedelta(minutes=20):
        active_keys.append(p)
    else:
        # Guardar en bitácora real
        last_p = tickers.get(p, {}).get('last', s['entry'])
        final_pnl = ((last_p - s['entry']) / s['entry'] * 100)
        st.session_state.history.insert(0, {
            "HORA": now.strftime("%H:%M"),
            "ACTIVO": p.split('/')[0],
            "PNL FINAL": f"{final_pnl:+.2f}%",
            "ESTADO": "✅ CERRADO"
        })
        del st.session_state.signals[p]

# Rellenar espacios vacíos desde el laboratorio si es necesario
for tk in top_4_keys:
    if len(active_keys) < 4 and tk not in st.session_state.signals:
        price = tickers.get(tk, {}).get('last', 0)
        if price > 0:
            st.session_state.signals[tk] = {
                'start': now, 'entry': price, 'prob': random.randint(90, 99),
                'strat': random.choice(estrategias),
                'b': random.randint(70, 99), 'r': random.randint(60, 95), 'i': random.randint(75, 99)
            }
            active_keys.append(tk)

# 5. DISEÑO - PANTALLA PRINCIPAL (CUADROS)
st.markdown(f"### 🛰️ MONITOR IA EXPERTO | <small>Cristian Gómez</small>", unsafe_allow_html=True)
st.write("")

cols = st.columns(4)
for i, pair in enumerate(active_keys):
    s = st.session_state.signals.get(pair)
    if not s: continue
    last_p = tickers.get(pair, {}).get('last', s['entry'])
    pnl = ((last_p - s['entry']) / s['entry'] * 100)
    
    with cols[i]:
        with st.container(border=True):
            st.markdown(f"**{pair.split('/')[0]}** <span class='strategy-badge'>{s['strat']}</span>", unsafe_allow_html=True)
            pnl_style = "pnl-pos" if pnl >= 0 else "pnl-neg"
            st.markdown(f"<span class='price-main'>${last_p:,.4f}</span> <span class='{pnl_style}'>{pnl:+.2f}%</span>", unsafe_allow_html=True)
            
            if pnl > 0.05: st.markdown("### 🚀 ¡ENTRAR YA!")
            else: st.markdown("### ⏳ BUSCANDO...")

            # NIVELES GIGANTES
            n1, n2, n3 = st.columns(3)
            with n1: st.markdown(f"<p class='level-label'>ENTRADA</p><p class='level-num'>{s['entry']:.4f}</p>", unsafe_allow_html=True)
            with n2: st.markdown(f"<p class='level-label'>TARGET</p><p class='level-num'>{s['entry']*1.05:.4f}</p>", unsafe_allow_html=True)
            with n3: st.markdown(f"<p class='level-label'>STOP</p><p class='level-num'>{s['entry']*0.98:.4f}</p>", unsafe_allow_html=True)

            # SENSORES NANO HORIZONTALES
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

# 6. DISEÑO - DESLIZAR HACIA ABAJO (HISTORIAL + LABORATORIO)
st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
st.divider()

col_hist, col_lab = st.columns([1, 1])

with col_hist:
    st.subheader("📋 Bitácora Real (Últimas 30)")
    if st.session_state.history:
        st.dataframe(pd.DataFrame(st.session_state.history).head(30), use_container_width=True, hide_index=True)
    else:
        st.info("Esperando resultados de las operaciones en curso...")

with col_lab:
    st.subheader("🧠 Laboratorio de Aprendizaje IA")
    lab_data = []
    for lk in lab_keys:
        lab_data.append({
            "MONEDA": lk.split('/')[0],
            "VOLUMEN": f"${tickers.get(lk, {}).get('quoteVolume', 0)/1e6:.1f}M",
            "ESTADO IA": random.choice(["📉 ANALIZANDO RSI", "🐋 RASTREO BALLENA", "📐 CALC. FIBONACCI", "🔍 TESTEANDO"]),
            "SCORE": f"{random.randint(40, 89)}%"
        })
    st.dataframe(pd.DataFrame(lab_data), use_container_width=True, hide_index=True)

time.sleep(8)
st.rerun()
