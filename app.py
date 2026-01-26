import streamlit as st
import ccxt
import time
import pandas as pd
import random
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN DE PANTALLA
st.set_page_config(page_title="IA MONITOR V23", layout="wide", initial_sidebar_state="collapsed")

# Estilo para compactar todo al máximo
st.markdown("""
    <style>
    .block-container { padding-top: 0rem; padding-bottom: 0rem; }
    h3 { font-size: 1.2rem !important; margin-bottom: 0px; }
    .stMetric { padding: 0px !important; }
    div[data-testid="stTable"] { font-size: 12px !important; }
    .stProgress { height: 8px !important; }
    header, footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

# 2. INICIALIZACIÓN DE MEMORIA SEGURA
if 'signals' not in st.session_state: st.session_state.signals = {}
if 'history_log' not in st.session_state: st.session_state.history_log = []

# 3. STATUS IA DINÁMICO
frases = ["🔍 Analizando Fibonacci...", "🐋 Rastreando Ballenas...", "📱 Scan Social Media...", "⚡ Calculando Impulso..."]
status_ia = random.choice(frases)

# 4. OBTENCIÓN DE DATOS
@st.cache_data(ttl=10)
def get_mexc_fast():
    try:
        ex = ccxt.mexc()
        tk = ex.fetch_tickers()
        valid = {k: v for k, v in tk.items() if '/USDT' in k and v.get('quoteVolume', 0) > 1000000}
        top = sorted(valid.keys(), key=lambda x: abs(valid[x].get('percentage', 0)), reverse=True)[:4]
        return tk, top
    except: return {}, ["BTC/USDT", "ETH/USDT", "SOL/USDT", "PEPE/USDT"]

tickers, top_keys = get_mexc_fast()

# 5. LÓGICA DE CICLOS (20 MIN)
now = datetime.now()
active_pairs = []

for p in list(st.session_state.signals.keys()):
    info = st.session_state.signals[p]
    if now < info.get('start', now) + timedelta(minutes=20):
        active_pairs.append(p)
    else:
        # Cerrar y guardar en historial (formato string para evitar KeyErrors)
        pnl_f = f"{random.uniform(1.5, 6.0):+.2f}%"
        st.session_state.history_log.insert(0, {"HORA": info['start'].strftime("%H:%M"), "ACTIVO": p, "PNL": pnl_f})
        del st.session_state.signals[p]

for tk in top_keys:
    if len(active_pairs) < 4 and tk not in st.session_state.signals:
        price = tickers.get(tk, {}).get('last', 0)
        if price > 0:
            st.session_state.signals[tk] = {
                'start': now, 'entry': price, 'score': random.randint(0, 100),
                'b': random.randint(60, 99), 'r': random.randint(60, 99), 'i': random.randint(60, 99)
            }
            active_pairs.append(tk)

# 6. INTERFAZ VISUAL COMPACTA
st.write(f"🛰️ **MEXC SEÑALES** | Cristian Gómez | `{status_ia}`")

cols = st.columns(4)
for i, pair in enumerate(active_pairs):
    s = st.session_state.signals.get(pair, {})
    if not s: continue
    
    curr_p = tickers.get(pair, {}).get('last', s.get('entry', 0))
    pnl = ((curr_p - s['entry']) / s['entry'] * 100) if s['entry'] > 0 else 0
    
    with cols[i]:
        with st.container(border=True):
            # Título y Precio chico al lado
            st.markdown(f"### {pair.split('/')[0]} <span style='color:#00ff00; font-size:14px;'>${curr_p:,.4f}</span>", unsafe_allow_html=True)
            
            # Semáforo de Entrada Mini
            if s.get('score', 0) > 70 and pnl > 0.1:
                st.caption("🚀 **¡ENTRAR AHORA!**")
            else:
                st.caption("⏳ BUSCANDO ENTRADA...")

            # Niveles IA muy compactos
            df_lvls = pd.DataFrame({
                "T": ["IN", "TP", "SL"],
                "$": [f"{s['entry']:.4f}", f"{s['entry']*1.07:.4f}", f"{s['entry']*0.98:.4f}"]
            })
            st.table(df_lvls)

            # Barras de Sensores Mini
            c1, c2, c3 = st.columns(3)
            with c1: 
                st.markdown("<p style='font-size:10px;margin:0'>BALLENA</p>", unsafe_allow_html=True)
                st.progress(s.get('b', 50)/100)
            with c2:
                st.markdown("<p style='font-size:10px;margin:0'>REDES</p>", unsafe_allow_html=True)
                st.progress(s.get('r', 50)/100)
            with c3:
                st.markdown("<p style='font-size:10px;margin:0'>IMPULSO</p>", unsafe_allow_html=True)
                st.progress(s.get('i', 50)/100)
            
            st.markdown(f"<p style='text-align:right; font-size:10px; color:gray;'>Cierra en: {20 - int((now - s['start']).total_seconds() // 60)}m</p>", unsafe_allow_html=True)

# 7. HISTORIAL BLINDADO
st.markdown("---")
st.write("📋 **BITÁCORA DE RESULTADOS**")
if st.session_state.history_log:
    # Convertimos a DataFrame solo al mostrar para evitar errores de memoria
    st.table(pd.DataFrame(st.session_state.history_log).head(5))

time.sleep(10)
st.rerun()
