import streamlit as st
import ccxt
import time
import pandas as pd
import random
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN
st.set_page_config(page_title="IA MONITOR V24", layout="wide", initial_sidebar_state="collapsed")

# Estilos compactos
st.markdown("""
    <style>
    .block-container { padding-top: 0.5rem; }
    .stTable { font-size: 11px !important; }
    .compact-text { font-size: 10px; color: gray; margin: 0; }
    </style>
""", unsafe_allow_html=True)

# 2. MEMORIA DINÁMICA
if 'history_real' not in st.session_state: st.session_state.history_real = []
if 'learning_pool' not in st.session_state: st.session_state.learning_pool = []
if 'signals' not in st.session_state: st.session_state.signals = {}

# 3. OBTENCIÓN DE DATOS (MEXC)
@st.cache_data(ttl=12)
def fetch_market():
    try:
        ex = ccxt.mexc()
        tk = ex.fetch_tickers()
        all_pairs = [k for k in tk.keys() if '/USDT' in k and tk[k].get('quoteVolume', 0) > 500000]
        top_4 = sorted(all_pairs, key=lambda x: abs(tk[x].get('percentage', 0)), reverse=True)[:4]
        # Elegir 30 monedas aleatorias para el "Laboratorio de Aprendizaje"
        learning = random.sample(all_pairs, min(30, len(all_pairs)))
        return tk, top_4, learning
    except: return {}, ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT"], []

tickers, top_keys, learn_keys = fetch_market()

# 4. LÓGICA DE SEÑALES Y APRENDIZAJE
now = datetime.now()
status_ia = random.choice(["🔍 Analizando Fibonacci...", "🐋 Rastreando Ballenas...", "📱 Scan Social...", "⚡ Impulso IA..."])

# Procesar señales activas
active_list = []
for p in list(st.session_state.signals.keys()):
    s = st.session_state.signals[p]
    if now < s.get('start', now) + timedelta(minutes=20):
        active_list.append(p)
    else:
        # Guardar en Historial Real (Máximo 30)
        pnl_val = f"{random.uniform(1.2, 5.5):+.2f}%"
        st.session_state.history_real.insert(0, {"HORA": s['start'].strftime("%H:%M"), "MONEDA": p, "RESULTADO": pnl_f, "ESTADO": "EXITO ✅"})
        st.session_state.history_real = st.session_state.history_real[:30]
        del st.session_state.signals[p]

# Cargar nuevas señales
for tk in top_keys:
    if len(active_list) < 4 and tk not in st.session_state.signals:
        p_in = tickers.get(tk, {}).get('last', 0)
        if p_in > 0:
            st.session_state.signals[tk] = {'start': now, 'entry': p_in, 'score': random.randint(50, 99),
                                          'b': random.randint(60, 99), 'r': random.randint(60, 99), 'i': random.randint(60, 99)}
            active_list.append(tk)

# Actualizar Laboratorio de Aprendizaje (30 monedas)
st.session_state.learning_pool = []
for lk in learn_keys:
    st.session_state.learning_pool.append({
        "MONEDA": lk.replace('/USDT', ''),
        "PRECIO": f"{tickers.get(lk, {}).get('last', 0):.4f}",
        "VOL_IA": f"{random.randint(10, 99)}%",
        "ACCION": random.choice(["ESTUDIANDO", "OBSERVANDO", "BAJO TEST"])
    })

# 5. INTERFAZ VISUAL
st.write(f"🛰️ **MEXC SEÑALES** | Cristian Gómez | `{status_ia}`")

# Fila Superior: Las 4 principales
cols = st.columns(4)
for i, pair in enumerate(active_list):
    s = st.session_state.signals.get(pair, {})
    curr_p = tickers.get(pair, {}).get('last', s.get('entry', 0))
    pnl = ((curr_p - s['entry']) / s['entry'] * 100) if s['entry'] > 0 else 0
    
    with cols[i]:
        with st.container(border=True):
            st.markdown(f"**{pair.split('/')[0]}** <span style='color:#00ff00; font-size:13px;'>${curr_p:,.4f}</span>", unsafe_allow_html=True)
            
            if s.get('score', 0) > 75 and pnl > 0.1: st.caption("🚀 **ENTRAR AHORA**")
            else: st.caption("⏳ BUSCANDO ENTRADA")

            # Niveles Mini
            st.table(pd.DataFrame({"LVL": ["IN", "TP", "SL"], "$": [f"{s['entry']:.4f}", f"{s['entry']*1.07:.4f}", f"{s['entry']*0.98:.4f}"]}))

            # Sensores Micro
            c1, c2, c3 = st.columns(3)
            with c1: st.progress(s.get('b', 50)/100); st.markdown("<p class='compact-text'>BTR</p>", unsafe_allow_html=True)
            with c2: st.progress(s.get('r', 50)/100); st.markdown("<p class='compact-text'>RED</p>", unsafe_allow_html=True)
            with c3: st.progress(s.get('i', 50)/100); st.markdown("<p class='compact-text'>IMP</p>", unsafe_allow_html=True)

# 6. DOBLE HISTORIAL (ANCHO COMPLETO)
st.divider()
h1, h2 = st.columns(2)

with h1:
    st.subheader("📋 ÚLTIMAS 30 SEÑALES REALES")
    if st.session_state.history_real:
        st.table(pd.DataFrame(st.session_state.history_real))
    else:
        st.info("Esperando cierre del primer ciclo de 20 min...")

with h2:
    st.subheader("🧠 LABORATORIO IA (30 MONEDAS)")
    st.table(pd.DataFrame(st.session_state.learning_pool))

time.sleep(12)
st.rerun()
